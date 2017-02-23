"""Functions for printing LUTs for Stage 2

There are two types of output:
- Output parameters for correction function(s) (to be used in emulator):
    start from `print_Stage2_func_file`
- LUTs that can be used in emulator or hardware:
    start from `print_Stage2_lut_files`

The latter is more tricky, as it requires various levels of compression.
This makes LUTs:
- convert ieta -> compressed eta index
- convert iet -> compressed pt index
- convert address (eta index + pt index) -> correction factor (+ optionally with addend)

Data structure for holding all this is not ideal - could do better.
"""


import ROOT
import numpy as np
import os
import common_utils as cu
from collections import OrderedDict
from bisect import bisect_left
from multifunc import MultiFunc
from binning import pairwise, eta_bin_colors
from itertools import izip, ifilterfalse
from math import ceil, floor
from textwrap import wrap

USE_MPL = True
try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, inset_axes, mark_inset
    from matplotlib.ticker import MultipleLocator

    mpl.rcParams['font.size'] = 18
    print mpl.rcParams['figure.figsize']
    mpl.rcParams['figure.figsize'] = (8.0, 8.0)  # default size of plots
    mpl.rcParams['legend.scatterpoints'] = 1
    mpl.rcParams['legend.numpoints'] = 1
    mpl.rcParams['xtick.major.size'] = 12
    mpl.rcParams['xtick.major.width'] = 2
    mpl.rcParams['ytick.major.size'] = 12
    mpl.rcParams['ytick.major.width'] = 2
    mpl.rcParams['xtick.minor.size'] = 6
    mpl.rcParams['xtick.minor.width'] = 1
    mpl.rcParams['ytick.minor.size'] = 6
    mpl.rcParams['ytick.minor.width'] = 1
except ImportError:
    print "Can't use matplotlib to make sanity plots"
    print "Install it, or rewrite the plotting funcs in PyROOT"

USE_SKLEARN = True
try:
    from sklearn.cluster import KMeans
except ImportError:
    print "Can't use the K-Means algorithm from scikit-learn"
    print "Either install it (via pip / conda) or do without"
    USE_SKLEARN = False

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)

MARKERS = ["o", "v", "^", "<", ">", "8", "s", "p", "*", "h", "H", "+", "x", "D", "d"]

def round_to_half(num):
    return round(num * 2) / 2


def unique_everseen(iterable, key=None):
    """List unique elements, preserving order. Remember all elements ever seen.

    Taken from https://docs.python.org/2/library/itertools.html#recipes

    unique_everseen('AAAABBBCCDAABBB') --> A B C D
    unique_everseen('ABBCcAD', str.lower) --> A B C D
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def read_lut_mapping(lut_filename):
    """Read human-readable LUT into OrderedDict of key:value"""
    with open(lut_filename) as f:
        map_dict = {}
        for line in f:
            if line.startswith('#'):
                continue
            parts = [int(x) for x in line.strip().split()]
            map_dict[parts[0]] = parts[1]
        return OrderedDict(sorted(map_dict.items(), key=lambda t: t))


def complete_pt_mapping(compressed_map, hw_pt):
    """Make a full mapping of hwPt to index using the compressed version from LUT"""
    full_map = OrderedDict()
    for pt in hw_pt:
        if pt > 511:
            full_map[pt] = compressed_map.values()[-1]
        else:
            compressed_pt = int(int(pt) / 2)
            full_map[pt] = compressed_map[compressed_pt]
    return full_map


def do_pt_compression(fit_functions, pt_orig, target_num_pt_bins,
                      merge_algorithm, merge_criterion):
    """Mega function to figure out the optimal PT compression scheme using the correction curves

    Parameters
    ----------
    fit_functions : list[TF1] or list[MultiFunc]
        List of correction functions, one per compressed eta bin
    pt_orig : numpy.array
        Array of physical PT values to consider for compression
    target_num_pt_bins : int
        NUmber of bins to compress PT range into
    merge_algorithm : str
        "greedy" or "kmeans"
    merge_criterion : float
        For greedy algorithm, specifies maximum size of a bin

    Returns
    -------
    new_pt_mapping : OrderedDict{int : int}
        Mapping between original HW PT and some compressed PT

    pt_index : list[int]
        Index of integers to assign a given HW PT to a compression bin.
    """
    # decide which fit func to use for binning based on which has the curve start at the lowest pT
    eta_ind_lowest = determine_lowest_curve_start(fit_functions)

    # find min of curve and merge above that
    merge_above = fit_functions[eta_ind_lowest].functions_dict.values()[1].GetMinimumX()
    print 'Merge above', merge_above

    # find end of plateau and merge below that
    merge_below = fit_functions[eta_ind_lowest].functions_dict.keys()[0][1]
    print 'Merge below', merge_below

    # do 0 separately as it should have 0 correction factor
    corr_orig = np.array([0.] + [fit_functions[eta_ind_lowest].Eval(pt)
                                 for pt in pt_orig if pt > 0])

    with open('corr_dump.txt', 'w') as dump:
        dump.write(','.join(((str(x) for x in corr_orig))))

    # Find the optimal compressed pt binning
    if merge_algorithm == 'greedy':
        new_pt_mapping = calc_compressed_pt_mapping_greedy(pt_orig, corr_orig,
                                                           target_num_pt_bins,
                                                           merge_criterion,
                                                           merge_above, merge_below)
    elif merge_algorithm == 'kmeans':
        new_pt_mapping = calc_compressed_pt_mapping_kmeans(pt_orig, corr_orig,
                                                           target_num_pt_bins,
                                                           merge_above, merge_below)
    else:
        raise RuntimeError('merge_algorithm argument incorrect')

    hw_pt_compressed = (np.array(new_pt_mapping.values()) * 2).astype(int)
    # figure out pt unique indices for each pt
    pt_index = np.array(assign_pt_index(hw_pt_compressed))

    pt_index_list = list(pt_index)
    bin_edges = [pt_orig[pt_index_list.index(i)] for i in xrange(0, target_num_pt_bins)]
    print 'Compressed bin edges (physical pT in GeV):'
    print ', '.join(str(i) for i in bin_edges)

    return new_pt_mapping, pt_index


def calc_compressed_pt_mapping_greedy(pt_orig, corr_orig, target_num_bins,
                                      merge_criterion, merge_above=None, merge_below=None):
    """Calculate new compressed pt mapping. Uses corrections
    to decide how to merge bins via "greedy" method.

    Returns a dicts for original:quantised pt mapping, where the quantised pT
    is the centre of the pT bin (for lack of anything better)

    Parameters
    ----------
    pt_orig: numpy.array
        Array of original pt bin edges (physical pT, not HW)

    corr_orig: numpy.array
        Array of original correction factors (floats, not ints)

    target_num_bins: int
        Target number of pT bins

    merge_criterion: float
        Bins will be merged if min(bins) * merge_crit > max(bins)

    merge_above: float
        Bins above this value will be merged, ignoring merge_criterion

    merge_below: float
        Bins below this value will be merged, ignoring merge_criterion

    Returns
    -------
    new_pt_mapping: OrderedDict
        Dict of {original pt: compressed pt}, both physical pT.
    """
    print 'Calculating new mapping for compressed ET'

    # hold pt mapping
    new_pt_mapping = {p: p for p in pt_orig}
    new_pt_mapping[0] = 0.
    new_pt_mapping = OrderedDict(sorted(new_pt_mapping.items(), key=lambda t: t))

    end_ind = len(pt_orig) - 1

    # enforce truncation at 8 bits, since we only use bits 1:8
    if not merge_above or merge_above >= 255.:
        merge_above = 254.5
        print 'Overriding merge_above to', merge_above

    if merge_above:
        # set all bins above this value to merge, and set to mean pt
        merge_above_ind = bisect_left(new_pt_mapping.keys(), merge_above)
        mean_merge = round_to_half(np.array(new_pt_mapping.keys()[merge_above_ind:]).mean())
        for ind, pt in enumerate(new_pt_mapping.iterkeys()):
            if pt >= merge_above:
                new_pt_mapping[pt] = mean_merge
        end_ind = merge_above_ind

    orig_start_ind = 2

    if merge_below:
        # round to nearest 0.5
        merge_below = round_to_half(merge_below)
        # check it's a half number, then the bin above is for even number
        if float(merge_below).is_integer():
            merge_below += 0.5
        print 'Overriding merge_below to', merge_below

        # set all bins below this value to merge, and set to mean pt
        merge_below_ind = bisect_left(new_pt_mapping.keys(), merge_below)
        mean_merge = round_to_half(np.array(new_pt_mapping.keys()[1:merge_below_ind]).mean())
        for ind, pt in enumerate(new_pt_mapping.iterkeys()):
            # keep pt = 0 set to 0
            if ind == 0:
                continue
            if pt <= merge_below:
                new_pt_mapping[pt] = mean_merge
        orig_start_ind = merge_below_ind

    last_num_bins = 111111111

    def count_number_unique_ints(new_pt_mapping):
        """Count unique values, but only for whole number pts"""
        return len({v for k, v in new_pt_mapping.iteritems() if float(k).is_integer()})

    while count_number_unique_ints(new_pt_mapping) > target_num_bins:
        last_num_bins = len(list(unique_everseen(new_pt_mapping.values())))

        print 'Got', last_num_bins, 'bins'
        # start with larget number of bins, look at compatibility,
        # then reduce bin span if necessary
        start_ind = orig_start_ind

        while start_ind < end_ind and end_ind > 2:
            # Because we select bits 1:9, we can only distinguish
            # between even HW pT i.e. 1 GeV LSB
            # E.g. 0010 and 0011 are both treated the same.
            # So skip to next pT if this one is X.5 GeV
            if not pt_orig[start_ind].is_integer():
                start_ind += 1
                continue

            corrs = corr_orig[start_ind: end_ind + 1]
            if corrs.max() < (merge_criterion * corrs.min()):
                len_pt_bins = len(list(unique_everseen(new_pt_mapping.values())))

                # since the merge is greedy, but we want to use all our possible bins,
                # we have to modify the last group to not go over our target number
                if (end_ind < len(pt_orig) - 1
                    and target_num_bins > (len_pt_bins - len(corrs))):

                    start_ind += target_num_bins - (len_pt_bins - len(corrs)) - 1
                    corrs = corr_orig[start_ind:end_ind + 1]

                mean_pt = round_to_half(pt_orig[start_ind: end_ind + 1].mean())
                print 'mean pt for this bin:', mean_pt, 'from', pt_orig[start_ind: end_ind + 1]

                for i in xrange(start_ind, end_ind + 1):
                    new_pt_mapping[pt_orig[i]] = mean_pt

                end_ind = start_ind - 1

                break
            else:
                start_ind += 1

        if count_number_unique_ints(new_pt_mapping) == last_num_bins:
            print 'Stuck in a loop - you need to loosen merge_criterion, ' \
                  'or increase the number of bins'
            print 'Dumping mapping to file stuck_dump.txt'
            with open('stuck_dump.txt', 'w') as f:
                for k, v in new_pt_mapping.iteritems():
                    f.write("%f,%f\n" % (k, v))
            exit()

    # now go back and set all the half integers to have same correction as whole integers
    for i in range(len(pt_orig) / 2):
        if new_pt_mapping[i + 0.5] != new_pt_mapping[i]:
            new_pt_mapping[i + 0.5] = new_pt_mapping[i]

    mask = [k != v for k, v in new_pt_mapping.iteritems()]
    if any(mask):
        # -1 required with .index() as otherwise it picks up wrong index
        print 'Compressed above (inclusive):', pt_orig[mask.index(True) - 1]
    else:
        print 'No pT compression required'

    return new_pt_mapping


def calc_compressed_pt_mapping_kmeans(pt_orig, corr_orig, target_num_bins,
                                      merge_above=None, merge_below=None):
    """Calculate new compressed pT binning using k-means classification
    to group correction factors.

    This uses the KMeans clustering algo in scikit-learn.

    WARNING: it doesn not respect the position in the list, so if the function
    turns over it will group them together
    """
    print 'Calculating new mapping for compressed ET'

    # hold pt mapping
    new_pt_mapping = {p: p for p in pt_orig}
    new_pt_mapping[0] = 0.
    new_pt_mapping = OrderedDict(sorted(new_pt_mapping.items(), key=lambda t: t))

    end_ind = len(pt_orig) - 1

    # enforce truncation at 8 bits, since we only use bits 1:8
    if not merge_above or merge_above >= 255.:
        merge_above = 254.5
        print 'Overriding merge_above to', merge_above

    if merge_above:
        # set all bins above this value to merge, and set to mean pt
        merge_above_ind = bisect_left(new_pt_mapping.keys(), merge_above)
        mean_merge = round_to_half(np.array(new_pt_mapping.keys()[merge_above_ind:]).mean())
        for ind, pt in enumerate(new_pt_mapping.iterkeys()):
            if pt >= merge_above:
                new_pt_mapping[pt] = mean_merge
        end_ind = merge_above_ind

    start_ind = 2

    if merge_below:
        # round to nearest 0.5
        merge_below = round_to_half(merge_below)
        # check it's a half number, then the bin above is for even number
        if float(merge_below).is_integer():
            merge_below += 0.5
        print 'Overriding merge_below to', merge_below

        # set all bins below this value to merge, and set to mean pt
        merge_below_ind = bisect_left(new_pt_mapping.keys(), merge_below)
        mean_merge = round_to_half(np.array(new_pt_mapping.keys()[1:merge_below_ind]).mean())
        for ind, pt in enumerate(new_pt_mapping.iterkeys()):
            # keep pt = 0 set to 0
            if ind == 0:
                continue
            if pt <= merge_below:
                new_pt_mapping[pt] = mean_merge
        start_ind = merge_below_ind

    # actually do the clustering
    corr_data = corr_orig[start_ind: end_ind + 1]
    int_mask = np.equal(np.mod(pt_orig[start_ind: end_ind + 1], 1), 0)
    pt_int = pt_orig[start_ind: end_ind + 1][int_mask]  # remove half integer pTs
    print 'pt_int:', pt_int
    corr_int = corr_data[int_mask]  # remove half integer pTs
    new_target_num_bins = target_num_bins - 3  # to accoutn for 0, merge_below, and merge_above
    pred = KMeans(n_clusters=new_target_num_bins).fit_predict(corr_int.reshape(-1, 1))

    # this gives us the index, but now we have to calculate the new means
    # and fill the dict
    for ind in xrange(new_target_num_bins):
        cluster_mask = pred == ind
        # print cluster_mask
        # corr_mean = corr_int[cluster_mask].mean()
        pt_mean = pt_int[cluster_mask].mean()
        pt_lo = pt_int[cluster_mask][0]
        pt_hi = pt_int[cluster_mask][-1]
        for pt in np.arange(pt_lo, pt_hi +  1, 0.5):
            # new_pt_mapping[pt] = corr_mean
            new_pt_mapping[pt] = pt_mean

    # now go back and set all the half integers to have same correction as whole integers
    for i in range(len(pt_orig) / 2):
        if new_pt_mapping[i + 0.5] != new_pt_mapping[i]:
            new_pt_mapping[i + 0.5] = new_pt_mapping[i]

    unique_mask = [k != v for k, v in new_pt_mapping.iteritems()]
    if any(unique_mask):
        # -1 required with .index() as otherwise it picks up wrong index
        print 'Compressed above (inclusive):', pt_orig[unique_mask.index(True) - 1]
    else:
        print 'No pT compression required'

    return new_pt_mapping


def generate_address(iet_index, ieta_index):
    """Convert iEt, iEta indices to address. These are NOT HW values.

    Parameters
    ----------
    iet_index : int
        iEt index
    ieta_index : int
        iEta index

    Returns
    -------
    int
        Corresponding address.
    """
    return (ieta_index<<4) | iet_index


def iet_to_index(iet, hw_pt_orig, pt_index):
    """Convert iet (HW) to an index"""
    ind = np.where(hw_pt_orig == iet)[0][0]
    return pt_index[ind]


def write_pt_compress_lut(lut_filename, hw_pt_orig, pt_index):
    """Write LUT that converts HW pt to compressed index

    Note that we take bits 1:8 from the 16 bits that represent jet ET
    So we only need those values.

    Parameters
    ----------
    lut_filename : str
        Filename for output LUT
    """
    print 'Making PT compress LUT', lut_filename
    with open(lut_filename, 'w') as lut:
        lut.write('# PT compression LUT\n')
        lut.write('# maps 8 bits to 4 bits\n')
        lut.write('# the 1st column is the integer value after selecting bits 1:8\n')
        lut.write("# anything after # is ignored with the exception of the header\n")
        lut.write("# the header is first valid line starting with ")
        lut.write("#<header> versionStr nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 8 4 </header>\n")
        for pt, ind in izip(hw_pt_orig, pt_index):
            if pt > 511:
                break
            if pt % 2 == 0:
                # only want even HW values, then convert to what it would be
                # if removed LSB
                lut.write('%d %d\n' % (int(pt / 2), ind))


def correct_iet(iet, corr_factor, right_shift, add_factor=0):
    """Apply correction int to HW pt."""
    iet_new = iet * corr_factor
    iet_new = np.right_shift(iet_new, right_shift)
    # if add_factor == None:
        # add_factor = iet
    iet_new += add_factor
    return iet_new


def generate_corr_matrix(max_iet, max_hw_correction, right_shift, add_factor=None):
    """Generate a matrix of corrected pt values (HW), where indices are iEt
    before correction (HW) and correction integer.

    Parameters
    ----------
    max_iet: int

    max_hw_correction: int

    right_shift: int

    Returns
    -------
    numpy.ndarray:
        Correction matrix.
    """
    # corr_m[x, y] holds iet post-correction for correction factor x on iet y
    corr_m = np.ndarray(shape=(max_hw_correction + 1, max_iet + 1), dtype=int)
    for i in range(max_hw_correction + 1):
        iet = np.arange(0, max_iet + 1)
        corr_m[i] = correct_iet(iet, i, right_shift, add_factor=add_factor)
    return corr_m


def calc_hw_corr_factor(corr_matrix, iet_pre, iet_post):
    """Return multiplicative factor (for hardware) that gives closest
    value to iet_post for a given iet_pre.

    Parameters
    ----------
    corr_matrix: numpy.ndarray

    iet_pre: int
        HW pt before calibration

    iet_post: int
        Target HW pt post calibration

    Returns
    -------
    int:
        Correction factor that gives closest iet_post

    """
    iet_pre = int(round(iet_pre))
    iet_post = int(round(iet_post))
    # always return factor 0 when input pt = 0
    if iet_pre == 0:
        return 0
    try:
        # try and find an exact match
        ind = int(np.where(corr_matrix[:, iet_pre] == iet_post)[0][0])
        return ind
    except IndexError:
        # if not, find the closest to iet_post
        ind = bisect_left(corr_matrix[:, iet_pre], iet_post)
        if ind == len(corr_matrix[:, iet_pre]):
            return ind - 1
        diff_above = abs(corr_matrix[ind, iet_pre] - iet_post)
        diff_below = abs(corr_matrix[ind-1, iet_pre] - iet_post)
        if diff_above < diff_below:
            return ind
        else:
            return ind - 1


def calc_hw_correction_addition_ints(map_info, corr_matrix, right_shift,
                                     num_add_bits, max_hw_pt):
    """For each pt bin calculate the integer correction factor and additive
    factor that gives the closest factor to the equivalent entry in corrections.

    Parameters
    ----------
    map_info : dict
        Kitchen sink

    corr_matrix : numpy.ndarray
        Pre-filled matrix of {corr int, iet} => (iet*corr int) >> X

    right_shift : int
        Number of bits for right shift

    num_add_bits : int
        Num of bits for the addend

    max_hw_pt : int
        Maximum HW PT

    Returns
    -------
    list[int], list[int]
        List of HW correction integers; and list of HW correciton additions.
        One per pt entry
    """
    print 'Assigning HW correction factors'

    hw_corrections, hw_additions = [], []

    hw_pt_orig = map_info['hw_pt_orig']
    hw_pt_post = map_info['hw_pt_post_corr_orig']

    # Figure out indices ofr the start & end of each compressed pt bin
    pt_indices = list(map_info['pt_index'])
    unique_inds = [pt_indices.index(x) for x
                   in sorted(set(map_info['pt_index']))] + [len(pt_indices)]

    for lo, hi in pairwise(unique_inds):
        print '-----'
        # average correction factor for this bin i.e. gradient
        # we use the edges of the bin to ensure continuity between bins
        hi_orig = hi
        hw_pt_post_hi = hw_pt_post[hi-1]
        # max_hw_pt = 600
        if hw_pt_post_hi > max_hw_pt:
            hw_pt_post_hi = max_hw_pt
            # now refind the index of the entry that is closest to max_hw_pt
            hi = min(range(len(hw_pt_post)),
                     key=lambda x: abs(hw_pt_post[x] - max_hw_pt)) + 1
            print 'Upper limit of post-corrected pt >', max_hw_pt, ', setting to', hw_pt_post_hi

        corr_factor = (hw_pt_post_hi - hw_pt_post[lo]) / (1.* hw_pt_orig[hi-1] - hw_pt_orig[lo])

        # add factor i.e. y-intercept
        intercept = int(round(hw_pt_post[lo] - (corr_factor  * hw_pt_orig[lo])))
        ideal_intercept = intercept

        # apply y = mx + c to bin edges
        ideal_lo = (hw_pt_orig[lo]*corr_factor) + ideal_intercept
        ideal_hi = (hw_pt_orig[hi-1]*corr_factor) + ideal_intercept

        # get pre/post centers to get integer for this bin
        # this ensure we get the correct multiplier, esp for low pT
        mean_hw_pt_pre = int(round(0.5 * (hw_pt_orig[hi-1] + hw_pt_orig[lo])))
        mean_hw_pt_post = int(round(0.5 * (hw_pt_post_hi + hw_pt_post[lo])))

        # subtract intercept as want factor just for gradient
        corr_factor_int = calc_hw_corr_factor(corr_matrix,
                                              mean_hw_pt_pre,
                                              mean_hw_pt_post - intercept)

        # subtlety - if corr_factor_int is the maximum it can be
        # (but should be larger), then we will undercorrect.
        # To compensate for this, we increase the intercept factor
        if corr_factor_int == np.size(corr_matrix, 0) - 1:
            diff = mean_hw_pt_post - correct_iet(mean_hw_pt_pre,
                                                 corr_factor_int,
                                                 right_shift,
                                                 intercept)
            intercept += int(round(diff))

        # check interecpt (i.e addend) fits into specified num of bits
        # saturate if not. also accounts for -ve addend
        if abs(intercept) > (2**(num_add_bits-1) - 1):
            sign = np.sign(intercept)
            intercept = (2**(num_add_bits-1) - 1) * np.sign(intercept)
            print 'WARNING: having to saturate addend'

        for i in xrange(lo, hi_orig):
            hw_corrections.append(corr_factor_int)
            hw_additions.append(intercept)

        # check whether our attempt was successful
        post_corr_lo = correct_iet(hw_pt_orig[lo], corr_factor_int,
                                   right_shift, intercept)
        post_corr_hi = correct_iet(hw_pt_orig[hi-1], corr_factor_int,
                                   right_shift, intercept)

        print 'Pre bin edges:', hw_pt_orig[lo], hw_pt_orig[hi-1]
        print 'Post bin edges:', hw_pt_post[lo], hw_pt_post_hi
        print 'Mean pre/post:', mean_hw_pt_pre, mean_hw_pt_post
        print 'Ideal corr factor, intercept:', corr_factor, ideal_intercept
        print 'Applying y = mx + c to bin edges:', ideal_lo, ideal_hi
        print 'Actual corr factor & add:', corr_factor_int, intercept
        print 'Applying proper integer calc to bin edges:', post_corr_lo, post_corr_hi

        if hw_pt_post[lo] > 0 and 1. * abs(post_corr_lo - hw_pt_post[lo])/hw_pt_post[lo] > 0.1:
            print 'WARNING: integer correction deviates by more than 10% at low bin edge'

        if 1. * abs(post_corr_hi - hw_pt_post_hi)/hw_pt_post_hi > 0.1:
            print 'WARNING: integer correction deviates by more than 10% at high bin edge'

    return np.array(hw_corrections), np.array(hw_additions)


def generate_add_mult(add, mult, num_add_bits, num_mult_bits):
    """Convert addition and multiplication factors into one integer.

    Auto-handles -ve addends! (thanks Andy)

    Parameters
    ----------
    add : int
        Addend integer
    mult : int
        Multiplier integer
    num_add_bits : int
        Number of bits to hold addend
    num_mult_bits : int
        Number of bits to hold multiplier

    Returns
    -------
    int
        Combined addend & multiplier.
    """
    # andy = ( (add & 0x00FF) << num_mult_bits ) | (mult & 0x03FF)
    me = ( (add & ((2**num_add_bits) - 1)) << num_mult_bits ) | (mult & ((2**num_mult_bits)-1))
    return me


def write_stage2_addend_multiplicative_lut(lut_filename, mapping_info, num_add_bits, num_mult_bits):
    """Write LUT that converts compressed address to both addend and multiplier
    (combined into one integer)

    Parameters
    ----------
    lut_filename : str
        Filename for output LUT
    mapping_ifno : dict
        All the info
    num_add_bits : int
        Number of bits to hold addend
    """
    print 'Making add+corr LUT', lut_filename
    num_input_bits = 11
    num_tot_bits = num_add_bits + num_mult_bits
    with open(lut_filename, 'w') as lut:
        lut.write('# address to addend+multiplicative factor LUT\n')
        lut.write('# maps %d bits to %d bits\n' % (num_input_bits, num_tot_bits))
        lut.write('# %d bits = (addend<<%d) + multiplier)\n' % (num_tot_bits, num_mult_bits))
        lut.write('# addend is signed %d bits, multiplier is %d bits\n' % (num_add_bits, num_mult_bits))
        lut.write("# anything after # is ignored with the exception of the header\n")
        lut.write("# the header is first valid line starting with ")
        lut.write("#<header> versionStr nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 %d %d </header>\n" % (num_input_bits, num_tot_bits))
        counter = 0
        for eta_ind, map_info in mapping_info.iteritems():
            last_ind = -1
            for pt_ind, corr, add in izip(map_info['pt_index'],
                                          map_info['hw_corr_compressed'],
                                          map_info['hw_corr_compressed_add']):
                if pt_ind != last_ind:
                    comment = '  # eta_bin %d, pt 0' % (eta_ind) if pt_ind == 0 else ''
                    lut.write('%d %d%s\n' % (generate_address(pt_ind, eta_ind),
                                             generate_add_mult(add, corr, num_add_bits, num_mult_bits),
                                             comment))
                    last_ind = pt_ind
                    counter += 1
        # add padding
        for i in range(counter, (2**num_input_bits)):
            lut.write('%d 0 # dummy\n' % i)


def write_stage2_multiplier_lut(lut_filename, mapping_info):
    """Write LUT that converts compressed address to multiplier factor.

    Parameters
    ----------
    lut_filename : str
        Filename for output LUT
    mapping_info : TYPE
        Description
    """
    print 'Making corr LUT', lut_filename
    with open(lut_filename, 'w') as lut:
        lut.write('# address to multiplicative factor LUT\n')
        lut.write('# maps 8 bits to 10 bits\n')
        lut.write("# anything after # is ignored with the exception of the header\n")
        lut.write("# the header is first valid line starting with ")
        lut.write("#<header> versionStr nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 8 10 </header>\n")
        for eta_ind, map_info in mapping_info.iteritems():
            last_ind = -1
            for pt_ind, corr in izip(map_info['pt_index'], map_info['hw_corr_compressed']):
                if pt_ind != last_ind:
                    comment = '  # eta_bin %d, pt 0' % (eta_ind) if pt_ind == 0 else ''
                    lut.write('%d %d%s\n' % (generate_address(pt_ind, eta_ind), corr, comment))
                    last_ind = pt_ind


def write_stage2_addition_lut(lut_filename, mapping_info):
    """Write LUT that converts compressed address to correction addition.

    Parameters
    ----------
    lut_filename : str
        Filename for output LUT
    mapping_info : TYPE
        Description
    """
    print 'Making corr LUT', lut_filename
    with open(lut_filename, 'w') as lut:
        lut.write('# address to addition LUT\n')
        lut.write('# maps 8 bits to 10 bits\n')
        lut.write("# anything after # is ignored with the exception of the header\n")
        lut.write("# the header is first valid line starting with ")
        lut.write("#<header> versionStr(unused but may be in future) nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 8 8 </header>\n")
        for eta_ind, map_info in mapping_info.iteritems():
            last_ind = -1
            for pt_ind, corr in izip(map_info['pt_index'], map_info['hw_corr_compressed_add']):
                if pt_ind != last_ind:
                    comment = '  # eta_bin %d, pt 0' % (eta_ind) if pt_ind == 0 else ''
                    lut.write('%d %d%s\n' % (generate_address(pt_ind, eta_ind), corr, comment))
                    last_ind = pt_ind


def calo_ieta_to_mp_ieta(ieta):
    """Convert CALO ieta to MP ieta, due to the fact there
    is no calo ieta 29 in the MP"""
    sign = np.sign(ieta)
    if abs(ieta) <= 29:
        return ieta
    if abs(ieta) > 29:
        return (abs(ieta) - 1) * sign


def mp_ieta_to_calo_ieta(ieta):
    """Convert MP ieta to CALO ieta, to take into account ieta 29 issue"""
    sign = np.sign(ieta)
    if abs(ieta) < 29:
        return ieta
    if abs(ieta) >= 29:
        return (abs(ieta) + 1) * sign


def calo_ieta_to_index(ieta):
    """Convert CALO ieta to compressed index

    MUST be updated whenever (if) you change the eta compression
    """
    if ieta == 0:
        return 0
    if ieta > 41:
        raise IndexError("You cannot have ieta > 41!")
    ieta = abs(ieta)
    # The old "region binning":
    if ieta <= 29:  # HBHE
        return int(ceil(ieta / 4.)) - 1
    else:  # HF
        return int(ceil((ieta - 29) / 3.)) + 6

    # Joe's new binning:
    ieta_bins = [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9],
        [10, 11, 12, 13],
        [14, 15],
        [16, 17],
        [18, 19],
        [20, 21],
        [22],
        [23],
        [24],
        [25],
        [26],
        [27, 28, 29],
        [30, 31, 32],
        [33, 34, 35, 36],
        [37, 38, 39, 40, 41]
    ]
    for ind, ieta_bin in enumerate(ieta_bins, 0):
        if ieta in ieta_bin:
            return ind
    raise IndexError("Cannot find your ieta %d"  % ieta)


def write_eta_compress_lut(lut_filename, nbits_in):
    """Write LUT that converts MP ieta to eta index.

    Note that because the MP doesn't "know" about ieta 29,
    we need to convert it

    Parameters
    ----------
    lut_filename : str
        filename for LUT
    nbits_in : int
        Number of bits for ieta
    """
    print "Making eta compression LUT"
    with open(lut_filename, 'w') as lut:
        lut.write("# MP ieta compression LUT\n")
        lut.write("# Converts abs(MP ieta) (%d bits) into 4 bit index\n" % nbits_in)
        lut.write("# This is NOT calo ieta\n")
        lut.write("# anything after # is ignored with the exception of the header\n")
        lut.write("# the header is first valid line starting with ")
        lut.write("#<header> versionStr nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 %d 4 </header>\n" % nbits_in)
        lut.write("0 0\n")  # Dummy first word as this happens in FW
        end = 41
        for mp_ieta in range(1, end):
            index = calo_ieta_to_index(mp_ieta_to_calo_ieta(mp_ieta))
            line = "%d %d\n" % (mp_ieta, index)
            lut.write(line)

        # padding extra bits we don't need
        for mp_ieta in range(end, (2**nbits_in)):
            line = "%d 0\n" % (mp_ieta)
            lut.write(line)


def determine_lowest_curve_start(fit_functions):
    """Determine which fit function has the lowest pT for curve start.

    Parameters
    ----------
    fit_functions : list[MultiFunc]
        List of MultiFunc objects, one per eta bin.

    Returns
    -------
    int
        Index of MultiFunc object with curve that has lowest pT start.

    Raises
    ------
    RuntimeError
        If it picks HF bin somehow.
    """
    curve_start_pts = [f.functions_dict.keys()[0][1] for f in fit_functions]
    eta_ind_lowest = curve_start_pts.index(min(curve_start_pts))
    # make sure it's not in HF
    if eta_ind_lowest > 6:
        raise RuntimeError('Selected HF bin for pT compression')
    print 'Low pt plateaus end at:', curve_start_pts
    print 'Using eta bin %d for pT compression' % eta_ind_lowest
    return eta_ind_lowest


def assign_pt_index(pt_values):
    """Calculate an index for each pt_value. Only unique values get
    different indices.

    >>> assign_pt_index([1, 1, 2, 3, 3])
    [0, 0, 1, 2, 2]

    Parameters
    ----------
    pt_values : list[int or float]
        List of pt values

    Returns
    -------
    list[int]

    """
    pt_values = list(pt_values)
    unique_pt_values = unique_everseen(pt_values)
    unique_indices_map = {p: ind for ind, p in enumerate(unique_pt_values)}
    return [unique_indices_map[p] for p in pt_values]


def print_Stage2_lut_files(fit_functions,
                           eta_lut_filename, pt_lut_filename,
                           mult_lut_filename, add_lut_filename, add_mult_lut_filename,
                           right_shift, num_corr_bits, num_add_bits,
                           plot_dir,
                           read_pt_compression=None,
                           target_num_pt_bins=2**4,
                           merge_criterion=1.05,
                           merge_algorithm='greedy' # or 'kmeans'
                           ):
    """Make LUTs for Stage 2.

    This creates 2 LUT files:
    - one for converting (pt, eta) to an address, where pt is quantised into
    target_num_pt_bins, according to merge_criterion
    - one for mapping address to correction factor

    Parameters
    ----------
    fit_functions: list[TF1]
        List of correction functions to convert to LUT

    eta_lut_filename: str
        Filename for output LUT that converts eta to compressed index

    pt_lut_filename: str
        Filename for output LUT that converts pt to compressed index

    mult_lut_filename: str
        Filename for output LUT that converts address to multiplicative factor

    add_lut_filename: str
        Filename for output LUT that converts address to correction addend

    corr_mult_lut_filename: str
        Filename for output LUT that converts address to addend + multiplier

    right_shift: int
        Right-shift factor needed in hardware for multiplication

    num_corr_bits: int
        Number of bits to represent correction multiplicative factor.

    num_add_bits: int
        Number of bits to represent correction addend.

    plot_dir : str
        Directory to put checking plots.

    read_pt_compression : str
        Can read in PT compression table from existent human-readable LUT.
        If not None, the target_num_pt_bins/merge_criterion/merge_algorithm
        args are ignored.

    target_num_pt_bins: int
        Number of bins to compress pt bin range into. If you have N bits for pt,
        then target_num_pt_bins = 2**N - 1

    merge_criterion: float
        Criterion factor for compressing multiple pt values into one bin. Values will
        be combined if the maximum correction factor = merge_criterion * minimum
        correction factor for those pt values.

    merge_algorithm : str {'greedy' , 'kmeans'}
        Merge algorithm to use to decide upon compressed ET binning.

        greedy: my own algo, that merges bins within a certain tolerance until
            you either meet the requisite number of bins, or clustering fails.

        kmeans: use k-means algorithm in scikit-learn

    Raises
    ------
    IndexError
        If the number of fit functions is not the same as number of eta bins
    """

    # Plot LUT for eta compression
    write_eta_compress_lut(eta_lut_filename, nbits_in=6)

    if right_shift != 9:
        raise RuntimeError('right_shfit should be 9 - check with Jim/Andy!')

    if not read_pt_compression and merge_algorithm == 'kmeans' and not USE_SKLEARN:
        print 'Reverting to greedy algo'
        merge_algorithm = 'greedy'

    print 'Running Stage 2 LUT making with:'
    if read_pt_compression:
        print ' - reading PT compression from', read_pt_compression
    else:
        print ' - target num pt bins (per eta bin):', target_num_pt_bins
        print ' - merge criterion:', merge_criterion
        print ' - merge algorithm:', merge_algorithm
    print ' - # corr bits:', num_corr_bits
    print ' - # addend bits:', num_add_bits
    print ' - right shift:', right_shift

    max_hw_pt = (2**11 - 1)
    max_pt = max_hw_pt * 0.5

    pt_orig = np.arange(0, max_pt + 0.5, 0.5)
    hw_pt_orig = (pt_orig * 2).astype(int)

    if read_pt_compression:
        # Read PT compression from LUT
        pt_lut_contents = read_lut_mapping(read_pt_compression)
        new_pt_mapping = complete_pt_mapping(pt_lut_contents, hw_pt_orig)
        pt_index = new_pt_mapping.values()
    else:
        # Figure out the PT compression & make LUT
        new_pt_mapping, pt_index = do_pt_compression(fit_functions,
                                                     pt_orig,
                                                     target_num_pt_bins,
                                                     merge_algorithm,
                                                     merge_criterion)

        write_pt_compress_lut(pt_lut_filename, hw_pt_orig, pt_index)

    # to store {eta_index: {various pt/correction mappings}} for all eta bins
    all_mapping_info = OrderedDict()

    # Generate matrix of iet pre/post for different correction integers
    # Only need to do it once beforehand, can be used for all eta bins
    corr_matrix_add_none = generate_corr_matrix(max_iet=int(max_pt * 2),
                                                max_hw_correction=(2**num_corr_bits) - 1,
                                                right_shift=right_shift,
                                                add_factor=0)

    # figure out new correction mappings for each eta bin
    for eta_ind, func in enumerate(fit_functions):
        print ' *** Doing eta bin', eta_ind, '***'
        # if eta_ind not in [13]:
        #     continue
        # Dict to hold ALL info for this eta bin
        map_info = dict(pt_orig=pt_orig,  # original phys pt values
                        hw_pt_orig=hw_pt_orig,  # original HW pt values
                        pt_index=pt_index,  # index for compressed pt
                        corr_orig=None,  # original correction factors (phys)
                        hw_corr_compressed=None,  # HW correction mult factor after pt compression
                        hw_corr_compressed_add=None,  # HW correction add factor after pt compression
                        pt_post_corr_orig=None,  # phys pt post original corrections
                        hw_pt_post_hw_corr_compressed=None,  # HW pt post HW correction factor
                        pt_post_hw_corr_compressed=None  # phys pt post HW correction factor
                        )

        corr_orig = np.array([0.] + [func.Eval(pt) for pt in pt_orig if pt > 0.])
        map_info['corr_orig'] = corr_orig

        map_info['pt_post_corr_orig'] = pt_orig * corr_orig
        map_info['hw_pt_post_corr_orig'] = (map_info['pt_post_corr_orig'] * 2.).astype(int)

        # then we calculate all the necessary correction mult/add integers
        corr_ints_new, add_ints = calc_hw_correction_addition_ints(map_info,
                                                                   corr_matrix_add_none,
                                                                   right_shift,
                                                                   num_add_bits,
                                                                   max_hw_pt)
        map_info['hw_corr_compressed'], map_info['hw_corr_compressed_add'] = corr_ints_new, add_ints

        # Store the result of applying the HW correction ints
        hw_pt_post = [correct_iet(iet, cf, right_shift, add_factor=af) for iet, cf, af
                      in izip(map_info['hw_pt_orig'],
                              map_info['hw_corr_compressed'],
                              map_info['hw_corr_compressed_add'])]

        hw_pt_post = np.array(hw_pt_post)
        map_info['hw_pt_post_hw_corr_compressed'] = hw_pt_post
        map_info['pt_post_hw_corr_compressed'] = hw_pt_post * 0.5

        all_mapping_info[eta_ind] = map_info

        if eta_ind in [13, 14]:
            print_map_info(map_info)  # for debugging dict contents

        # Print some plots to check results.
        # Show original corr & compressed corr from HW
        title = 'eta bin %d, target # bins %d, ' \
                'merge criterion %.3f, %s merge algo' % (eta_ind,
                    target_num_pt_bins, merge_criterion, merge_algorithm)
        plot_pt_pre_post_mapping(map_info, eta_ind, title, plot_dir)
        plot_corr_vs_pt(map_info, eta_ind, title, plot_dir)
        plot_corr_vs_pt_clusters(map_info, eta_ind, title, plot_dir)
        plot_pt_pre_pt_post_clusters(map_info, eta_ind, title, plot_dir)
        plot_func_vs_lut_pt(map_info, eta_ind, title, plot_dir)

    # put them into a LUT
    write_stage2_multiplier_lut(mult_lut_filename, all_mapping_info)
    write_stage2_addition_lut(add_lut_filename, all_mapping_info)
    write_stage2_addend_multiplicative_lut(add_mult_lut_filename, all_mapping_info, num_add_bits, num_corr_bits)


def print_map_info(map_info):
    """Print out contents of dict, entry by entry"""
    keys = map_info.keys()
    print ' : '.join(keys)
    for i in range(len(map_info['pt_orig'])):
        print ' : '.join([str(map_info[k][i]) for k in keys])


FMT = "pdf"
SIZE = 2
TITLE_LENGTH = 80
TITLE_Y = 0.95
TITLE_FONTSIZE = 14
distinct_colours = ['red', 'blue', 'green', 'orange', 'purple', 'limegreen',
                    'dodgerblue', 'chocolate', 'magenta', 'goldenrod', 'teal',
                    'salmon', 'grey', 'crimson', 'mediumslateblue', 'olive']

def plot_pt_pre_post_mapping(map_info, eta_ind, title, plot_dir):
    """Plot map of pt (pre) -> pt (post), for original corrections,
    compressed corrections, and HW integer corrections, to compare.

    Parameters
    ----------
    map_info : dict
        Holds np.ndarrays for various values
    eta_ind : int
        eta index for plot filename
    title : str
        Title to put on plot
    plot_dir : str
        Where to save the plot
    """
    plt.plot(map_info['pt_orig'], map_info['pt_post_corr_orig'],
             'b-', label='Function', markersize=5, alpha=0.7, markeredgewidth=0, linewidth=2)
    plt.plot(map_info['pt_orig'], map_info['pt_post_hw_corr_compressed'],
             'r-', label='LUT', markersize=2, alpha=0.7, markeredgewidth=0, linewidth=2)
    plt.xlabel('Original '+r'$E_T$'+' [GeV]')
    plt.ylabel('Post-Correction '+r'$E_T$'+' [GeV]')
    plt.minorticks_on()
    plt.grid(which='major', linestyle='dashed')
    tit = plt.suptitle("\n".join(wrap(title, TITLE_LENGTH)), y=TITLE_Y, fontsize=TITLE_FONTSIZE)
    plt.vlines(1023.5, *plt.ylim(), linestyle='dotted', linewidth=2, color='green')
    plt.hlines(1023.5, *plt.xlim(), label='Saturation '+r'$E_T$', linewidth=2, linestyle='dotted', color='green')
    plt.legend(loc='upper left')
    # plt.tight_layout()

    # make a nifty zoomedin region
    ax = plt.gca()
    zoom_range = (0, 100)
    axins = zoomed_inset_axes(ax, 4, loc=4, borderpad=1.5)
    axins.plot(map_info['pt_orig'], map_info['pt_post_corr_orig'],
             'b-', label='Function', markersize=5, alpha=0.7, markeredgewidth=0, linewidth=2)
    axins.plot(map_info['pt_orig'], map_info['pt_post_hw_corr_compressed'],
             'r-', label='LUT', markersize=2, alpha=0.7, markeredgewidth=0, linewidth=2)
    axins.set_xlim(zoom_range)
    axins.set_ylim(zoom_range)
    axins.xaxis.tick_top()
    axins.tick_params(labelsize=14)
    axins.xaxis.set_major_locator(MultipleLocator(25))
    axins.yaxis.set_major_locator(MultipleLocator(25))
    axins.grid(which='major')
    pp, p1, p2 = mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="grey", lw=2)
    # plt.xticks(visible=False)
    # plt.yticks(visible=False)
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    axins.remove()
    pp.remove()
    p1.remove()
    p2.remove()
    ax.set_xlim(zoom_range)
    ax.set_ylim(zoom_range)
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_zoomX_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.xlim(5, 100)
    plt.ylim(5, 100)
    plt.xscale('log')
    plt.yscale('log')
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_zoomX_logX_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.clf()


def plot_pt_pre_pt_post_clusters(map_info, eta_ind, title, plot_dir):
    """Plot map of pt (pre) -> pt (post), for original corrections,
    compressed corrections, and HW integer corrections, to compare.

    Parameters
    ----------
    map_info : dict
        Holds np.ndarrays for various values
    eta_ind : int
        eta index for plot filename
    title : str
        Title to put on plot
    plot_dir : str
        Where to save the plot
    """
    distinct_cmap = ListedColormap(distinct_colours, N=len(set(map_info['pt_index'])))
    plt.scatter(map_info['pt_orig'], map_info['pt_post_corr_orig'],
                c=map_info['pt_index'], linewidth=0, cmap=distinct_cmap, s=25*SIZE)
    plt.xlabel('Original '+r'$E_T$'+' [GeV]')
    plt.ylabel('Post-Correction '+r'$E_T$'+' [GeV]')

    # plt.xlim(left=0)
    # plt.ylim(bottom=0)
    max_pt = 1024
    plt.xlim(0, max_pt)
    plt.ylim(0, max_pt)

    # plt.legend(loc=0)
    plt.minorticks_on()
    plt.grid(which='major', linestyle='dashed')
    tit = plt.suptitle("\n".join(wrap(title, TITLE_LENGTH)), y=TITLE_Y, fontsize=TITLE_FONTSIZE)
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_clusters_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.xlim(0, 150)
    plt.ylim(0, 150)
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_clusters_zoomX_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.xlim(5, 100)
    plt.ylim(5, 100)
    plt.xscale('log')
    plt.yscale('log')
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_clusters_zoomX_logX_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.clf()


def plot_corr_vs_pt(map_info, eta_ind, title, plot_dir):
    """Plot correction factor vs ET, for original corrections,
    compressed corrections, and HW correciton ints.

    Parameters
    ----------
    map_info : dict
        Holds np.ndarrays for various values
    eta_ind : int
        eta index for plot filename
    title : str
        Title to put on plot
    plot_dir : str
        Where to save the plot
    """
    plt.plot(map_info['pt_orig'], map_info['corr_orig'],
             'bo', label='Function', markersize=5*SIZE, alpha=1, markeredgewidth=0)
    plt.plot(map_info['pt_orig'], map_info['hw_pt_post_hw_corr_compressed'] / (1. * map_info['hw_pt_orig']),
             'v', label='LUT', markersize=5*SIZE, alpha=1, markeredgewidth=0, color='limegreen')
    plt.xlabel('Original '+r'$E_T$'+' [GeV]')
    plt.ylabel('Correction')

    plt.ylim(0.5, 2.5)
    max_pt = 1024
    plt.xlim(0, max_pt)
    plt.legend(loc=0)
    plt.minorticks_on()
    plt.grid(which='major', linestyle='dashed')
    tit = plt.suptitle("\n".join(wrap(title, TITLE_LENGTH)), y=TITLE_Y, fontsize=TITLE_FONTSIZE)
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.xlim(0, 300)
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_zoomX_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.xlim(5, 300)
    plt.xscale('log')
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_zoomX_logX_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.clf()


def plot_corr_vs_pt_clusters(map_info, eta_ind, title, plot_dir):
    """Plot correction factor vs ET, for original corrections,
    compressed corrections, and HW correciton ints.

    Parameters
    ----------
    map_info : dict
        Holds np.ndarrays for various values
    eta_ind : int
        eta index for plot filename
    title : str
        Title to put on plot
    plot_dir : str
        Where to save the plot
    """
    distinct_cmap = ListedColormap(distinct_colours, N=len(set(map_info['pt_index'])))
    plt.scatter(map_info['pt_orig'], map_info['corr_orig'],
                c=map_info['pt_index'], s=25*SIZE, linewidth=0, cmap=distinct_cmap)
    plt.xlabel('Original '+r'$E_T$'+' [GeV]')
    plt.ylabel('Correction')
    plt.xlim(0, 1024)
    plt.ylim(0.5, 2.5)
    # plt.legend(loc=0)
    plt.minorticks_on()
    plt.grid(which='major', linestyle='dashed')
    tit = plt.suptitle("\n".join(wrap(title, TITLE_LENGTH)), y=TITLE_Y, fontsize=TITLE_FONTSIZE)
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_cluster_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.xlim(0, 300)
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_zoomX_cluster_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.xlim(5, 300)
    plt.xscale('log')
    # plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_zoomX_logX_cluster_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.clf()


def plot_func_vs_lut_pt(map_info, eta_ind, title, plot_dir):
    """Plot function corrected pt vs LUT corrected pt

    Parameters
    ----------
    map_info : dict
        Holds np.ndarrays for various values
    eta_ind : int
        eta index for plot filename
    title : str
        Title to put on plot
    plot_dir : str
        Where to save the plot
    """
    plt.plot(map_info['hw_pt_post_hw_corr_compressed'], map_info['hw_pt_post_corr_orig'], 'x', label='LUT vs func')
    plt.xlabel('LUT corrected iET')
    plt.ylabel('Function corrected iET')
    max_pt = 2048
    plt.xlim(0, max_pt)
    plt.ylim(0, max_pt)
    plt.plot([0, max_pt], [0, max_pt], 'r', label='y = x', linewidth=2)
    plt.minorticks_on()
    plt.grid(which='major', linestyle='dashed')
    tit = plt.suptitle("\n".join(wrap(title, TITLE_LENGTH)), y=TITLE_Y, fontsize=TITLE_FONTSIZE)
    plt.legend(loc='upper left')

    # make a nifty zoomedin region
    ax = plt.gca()
    zoom_range = (0, 200)
    axins = zoomed_inset_axes(ax, 3.5, loc=4, borderpad=1.5)
    axins.plot(map_info['hw_pt_post_hw_corr_compressed'], map_info['hw_pt_post_corr_orig'], 'x')
    axins.plot(zoom_range, zoom_range, 'r', linewidth=2)
    axins.set_xlim(zoom_range)
    axins.set_ylim(zoom_range)
    axins.xaxis.tick_top()
    axins.tick_params(labelsize=14)
    axins.xaxis.set_major_locator(MultipleLocator(50))
    axins.yaxis.set_major_locator(MultipleLocator(50))
    axins.grid(which='major')
    pp, p1, p2 = mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="grey", lw=2)
    # plt.xticks(visible=False)
    # plt.yticks(visible=False)
    plt.savefig(os.path.join(plot_dir, 'lut_vs_func_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    axins.remove()
    pp.remove()
    p1.remove()
    p2.remove()
    ax.set_xlim(zoom_range)
    ax.set_ylim(zoom_range)
    plt.savefig(os.path.join(plot_dir, 'lut_vs_func_zoomX_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])

    plt.xlim(1, 200)
    plt.ylim(1, 200)
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig(os.path.join(plot_dir, 'lut_vs_func_zoomX_logX_%d.%s' % (eta_ind, FMT)), bbox_extra_artists=[tit])
    plt.clf()


def print_Stage2_func_file(fits, output_filename):
    """Print function info to file.
    Each line corresponds to an abs(eta) bin.
    """
    with open(output_filename, 'w') as f:
        f.write('# linear constant,linear/curve physical pt boundary,curve params\n')
        num_cols = 1 + 1 + 6  # as a safeguard
        for fit in fits:
            if not fit:
                f.write('\n')
                continue
            line_cols = []
            if isinstance(fit, MultiFunc):
                linear_const = fit.functions_dict.values()[0].GetParameter(0)
                linear_limit = fit.functions_dict.keys()[0][1]
                if len(fit.functions_dict.keys()) > 1:
                    curve_fn = fit.functions_dict.values()[1]
                    curve_params = [curve_fn.GetParameter(i) for i in range(curve_fn.GetNpar())]
                else:
                    curve_params = [1, 0, 1, 0, 1, 1]  # no correction
                line_cols = curve_params + [linear_const, linear_limit]
            else:
                if "constant" in fit.GetName():
                    line_cols = [fit.GetParameter(i) for i in range(fit.GetNpar())]
                    # pad the rest with 0s (i.e. the curve part)
                    if len(line_cols) != num_cols:
                        line_cols.extend([0 for _ in range(num_cols - len(line_cols))])
                else:
                    line_cols = [fit.GetParameter(i) for i in range(fit.GetNpar())]
                    # pad the front with 0s (i.e the constant part)
                    if len(line_cols) != num_cols:
                        padding = [0 for _ in range(num_cols - len(line_cols))]
                        line_cols = padding + line_cols

            line_cols = [str(x) for x in line_cols]
            if len(line_cols) != num_cols:
                raise RuntimeError("Incorrect number of columns to write to file")
            f.write(','.join(line_cols) + '\n')

