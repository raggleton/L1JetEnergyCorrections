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
import matplotlib.pyplot as plt
from binning import pairwise
from itertools import izip, ifilterfalse
from math import ceil
from string import maketrans

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


def calc_compressed_pt_mapping(pt_orig, corr_orig, target_num_bins,
                               merge_criterion, merge_above=None, merge_below=None):
    """Calculate new compressed pt mapping. Uses corrections
    to decide how to merge bins.

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
            # So skip to next pT if this one is XXX.5 GeV
            if not pt_orig[start_ind].is_integer():
                start_ind += 1
                continue

            corrs = corr_orig[start_ind: end_ind + 1]
            if corrs.max() < (merge_criterion * corrs.min()):
                len_pt_bins = len(list(unique_everseen(new_pt_mapping.values())))

                # since the merge is greedy, but we want to use all our possible bins,
                # we have to modify the last group to not go over our target number
                if (end_ind < len(pt_orig) - 1 and
                    target_num_bins > (len_pt_bins - len(corrs))):

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


def calc_new_corr_mapping(pt_orig, corr_orig, new_pt_mapping):
    """Calculate new corrections using new compressed pT mapping

    Parameters
    ----------

    Returns
    -------
    OrderedDict
        Map of {pt: new correction}
    """
    if len(pt_orig) != len(corr_orig):
        raise IndexError('Different lengths for pt_orig, corr_orig')
    # hold correction mapping
    new_corr_mapping = {p: c for p, c in zip(pt_orig, corr_orig)}
    new_corr_mapping = OrderedDict(sorted(new_corr_mapping.items(), key=lambda t: t))

    # Get indices of locations of new pt bins
    compr_pt = list(new_pt_mapping.values())
    unique_pt = unique_everseen(compr_pt)
    indices = [compr_pt.index(upt) for upt in unique_pt] + [len(corr_orig)]

    # Need to calculate new mean correction for each pt bin
    for i_low, i_high in pairwise(indices):
        mean_corr = corr_orig[i_low:i_high].mean()
        for j in xrange(i_low, i_high):
            new_corr_mapping[pt_orig[j]] = mean_corr

    # manually override
    new_corr_mapping[0] = 0.
    new_corr_mapping[0.5] = 0.
    return new_corr_mapping


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


def correct_iet(iet, corr_factor, right_shift, add_factor=None):
    """Apply correction int to HW pt."""
    iet_new = iet * corr_factor
    iet_new = np.right_shift(iet_new, right_shift)
    if add_factor == None:
        add_factor = iet
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


def calc_hw_correction_ints(hw_pts, corrections, corr_matrix, cap_correction):
    """For each pt bin calculate the integer correction factor that gives the
    closest factor to the equivalent entry in corrections.

    Parameters
    ----------
    hw_pts : list[int]
        Input hardware pTs
    corrections : list[float]
        Target correction factors
    corr_matrix : np.ndarray
        2D Matrix that maps hw pt (pre) and correction integer to hw pt (post).
    cap_correction : float
        Maximum physical correction (to stop ridiculously large factors)

    Returns
    -------
    list[int]
        List of HW correction integers, one per entry in hw_pts
    """
    print 'Assigning HW correction factors'

    hw_corrections = []

    for hw_pt_pre, corr in izip(hw_pts, corrections):
        # print hw_pt_pre, corr
        hw_pt_post = int(round(hw_pt_pre * corr))
        hw_factor = calc_hw_corr_factor(corr_matrix, hw_pt_pre, hw_pt_post)
        hw_corrections.append(hw_factor)

    return np.array(hw_corrections)


def calc_hw_correction_addition_ints(map_info, corr_matrix, right_shift, num_add_bits):
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

    Returns
    -------
    list[int], list[int]
        List of HW correction integers; and list of HW correciton additions.
        One per pt entry
    """
    print 'Assigning HW correction factors'

    hw_corrections, hw_additions = [], []
    corr_comp = list(map_info['corr_compressed'])
    corr_comp_unique = unique_everseen(corr_comp)
    corr_comp_unique_inds = [corr_comp.index(x) for x in corr_comp_unique] + [len(corr_comp)]
    print corr_comp_unique_inds

    hw_pt_orig = map_info['hw_pt_orig']
    hw_pt_post = map_info['hw_pt_post_corr_orig']
    for lo, hi in pairwise(corr_comp_unique_inds):
        print '-----'
        # average correction factor for this bin i.e. gradient
        corr_factor = (hw_pt_post[hi-1] - hw_pt_post[lo]) / (1.* hw_pt_orig[hi-1] - hw_pt_orig[lo])

        # add factor i.e. y-intercept
        intercept = int(round(hw_pt_post[lo] - (corr_factor  * hw_pt_orig[lo])))

        # get pre/post centers to get integer for this bin
        mean_hw_pt_pre = int(round(0.5 * (hw_pt_orig[hi-1] + hw_pt_orig[lo])))
        mean_hw_pt_post = int(round( (0.5 * (hw_pt_post[hi-1] + hw_pt_post[lo]))))

        # subtract intercept as want factor just for gradient
        corr_factor_int = calc_hw_corr_factor(corr_matrix, mean_hw_pt_pre, mean_hw_pt_post - intercept)

        # subtlety - if corr_factor_int is the maximum it can be (but should be larger),
        # then we will undercorrect. To compensate for this, we increase the intercept factor
        if corr_factor_int == np.size(corr_matrix, 0) - 1:
            diff = mean_hw_pt_post - correct_iet(mean_hw_pt_pre, corr_factor_int, right_shift, intercept)
            intercept += int(round(diff))

        # check interecpt (i.e addend) fits into specified num of bits
        # saturate if not. also accounts for -ve addend
        if abs(intercept) > (2**(num_add_bits-1) - 1):
            sign = 1 if intercept > 0 else -1
            intercept = (2**(num_add_bits-1) - 1) * sign
            print 'WARNING: having to saturate addend'

        for i in xrange(lo, hi):
            hw_corrections.append(corr_factor_int)
            hw_additions.append(intercept)

        print 'Pre bin edges:', hw_pt_orig[lo], hw_pt_orig[hi-1]
        print 'Post bin edges:', hw_pt_post[lo], hw_pt_post[hi-1]
        print 'Mean pre/post:', mean_hw_pt_pre, mean_hw_pt_post
        print 'Ideal corr factor, intercept:', corr_factor, intercept
        print 'Applying y = mx + c to bin edges:', (hw_pt_orig[lo]*corr_factor) + intercept, (hw_pt_orig[hi-1]*corr_factor) + intercept
        print 'Actual corr factor, add:', corr_factor_int, intercept
        print 'Applying proper integer calc to bin edges:', correct_iet(hw_pt_orig[lo], corr_factor_int, right_shift, intercept), correct_iet(hw_pt_orig[hi-1], corr_factor_int, right_shift, intercept)

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


def write_stage2_correction_lut(lut_filename, mapping_info):
    """Write LUT that converts compressed address to correction factor.

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


def ieta_to_index(ieta):
    """Convert ieta to index"""
    if ieta == 0:
        return 0
    ieta = abs(ieta)
    if ieta <= 29:  # HBHE
        return int(ceil(ieta / 4.)) - 1
    else:  # HF
        return int(ceil((ieta - 29) / 3.)) + 6


def write_eta_compress_lut(lut_filename, nbits_in):
    """Write LUT that converts ieta to eta index.

    Parameters
    ----------
    lut_filename : str
        filename for LUT
    nbits_in : int
        Number of bits for ieta
    """
    print "Making eta compression LUT"
    with open(lut_filename, 'w') as lut:
        lut.write("# ieta compression LUT\n")
        lut.write("# Converts abs(ieta) (%d bits) into 4 bit index\n" % nbits_in)
        lut.write("# anything after # is ignored with the exception of the header\n")
        lut.write("# the header is first valid line starting with ")
        lut.write("#<header> versionStr nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 %d 4 </header>\n" % nbits_in)
        lut.write("0 0\n")  # Dummy first word as this happens in FW
        for ieta in range(1, 42):
            line = "%d %d\n" % (ieta, ieta_to_index(ieta))
            lut.write(line)
        # padding extra bits we don't need
        for ieta in range(42, (2**nbits_in)):
            line = "%d 0\n" % (ieta)
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
                           corr_lut_filename, add_lut_filename, add_mult_lut_filename,
                           right_shift, num_corr_bits, num_add_bits,
                           target_num_pt_bins,
                           merge_criterion, plot_dir,
                           merge_algorithm):
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

    corr_lut_filename: str
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

    target_num_pt_bins: int
        Number of bins to compress pt bin range into. If you have N bits for pt,
        then target_num_pt_bins = 2**N - 1

    merge_criterion: float
        Criterion factor for compressing multiple pt bins into one bin. Bins will
        be combined if the maximum correction factor = merge_criterion * minimum
        correction factor for those pt bins.

    plot_dir : str
        Directory to put checking plots.

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

    if merge_algorithm == 'kmeans' and not USE_SKLEARN:
        print 'Reverting to greedy algo'
        merge_algorithm = 'greedy'

    print 'Running Stage 2 LUT making with:'
    print ' - target num pt bins (per eta bin):', target_num_pt_bins
    print ' - merge criterion:', merge_criterion
    print ' - merge algorithm:', merge_algorithm
    print ' - # corr bits:', num_corr_bits
    print ' - # addend bits:', num_add_bits
    print ' - right shift:', right_shift

    max_pt = (2**11 - 1) * 0.5

    # decide which fit func to use for binning based on which has the curve start at the lowest pT
    eta_ind_lowest = determine_lowest_curve_start(fit_functions)

    # find min of curve and merge above that
    merge_above = fit_functions[eta_ind_lowest].functions_dict.values()[1].GetMinimumX()
    print 'Merge above', merge_above

    # find end of plateau and merge below that
    merge_below = fit_functions[eta_ind_lowest].functions_dict.keys()[0][1]
    print 'Merge below', merge_below

    pt_orig = np.arange(0, max_pt + 0.5, 0.5)
    hw_pt_orig = (pt_orig * 2).astype(int)
    # do 0 separately as it should have 0 correction factor
    corr_orig = np.array([0.] + [fit_functions[eta_ind_lowest].Eval(pt)
                                 for pt in pt_orig if pt > 0])

    with open('corr_dump.txt', 'w') as dump:
        dump.write(','.join(((str(x) for x in corr_orig))))

    # Find the optimal compressed pt binning
    if merge_algorithm == 'greedy':
        new_pt_mapping = calc_compressed_pt_mapping(pt_orig, corr_orig,
                                                    target_num_pt_bins,
                                                    merge_criterion,
                                                    merge_above, merge_below)
    elif merge_algorithm == 'kmeans':
        new_pt_mapping = calc_compressed_pt_mapping_kmeans(pt_orig, corr_orig,
                                                           target_num_pt_bins,
                                                           merge_above, merge_below)
    else:
        raise RuntimeError('merge_algorithm argument incorrect')
    pt_compressed = np.array(new_pt_mapping.values())
    hw_pt_compressed = (pt_compressed * 2).astype(int)

    # figure out pt unique indices for each pt
    pt_index = np.array(assign_pt_index(hw_pt_compressed))
    pt_index_list = list(pt_index)
    bin_edges = [pt_orig[pt_index_list.index(i)] for i in xrange(0, target_num_pt_bins)]
    print 'Compressed bin edges (physical pT in GeV):'
    print ', '.join(str(i) for i in bin_edges)

    # make a lut to convert original pt (address) to compressed (index)
    write_pt_compress_lut(pt_lut_filename, hw_pt_orig, pt_index)

    # to store {eta_index: {various pt/correction mappings}} for all eta bins
    all_mapping_info = OrderedDict()

    # Generate matrix of iet pre/post for different correction integers
    # Only need to do it once beforehand, can be used for all eta bins
    corr_matrix_add_none = generate_corr_matrix(max_iet=int(max_pt * 2),
                                                max_hw_correction=(2**num_corr_bits) - 1,
                                                right_shift=right_shift, add_factor=0)

    # figure out new correction mappings for each eta bin
    for eta_ind, func in enumerate(fit_functions):
        # if eta_ind>0:
        #     break

        # Dict to hold ALL info for this eta bin
        map_info = dict(pt_orig=pt_orig,  # original phys pt values
                        hw_pt_orig=hw_pt_orig,  # original HW pt values
                        pt_compressed=pt_compressed,  # phys pt values after compression
                        hw_pt_compressed=hw_pt_compressed,  # HW pt values after compression
                        pt_index=pt_index,  # index for compressed pt
                        corr_orig=None,  # original correction factors (phys)
                        corr_compressed=None,  # correction factors after pt compression (phys)
                        hw_corr_compressed=None,  # HW correction mult factor after pt compression
                        hw_corr_compressed_add=None,  # HW correction add factor after pt compression
                        pt_post_corr_orig=None,  # phys pt post original corrections
                        pt_post_corr_compressed=None,  # phys pt post compressed corrections
                        hw_pt_post_corr_compressed=None,  # hw pt post compressed corrections
                        hw_pt_post_hw_corr_compressed=None,  # HW pt post HW correction factor
                        pt_post_hw_corr_compressed=None  # phys pt post HW correction factor
                        )

        print 'Calculating compressed correction value for eta bin', eta_ind

        corr_orig = np.array([0.] + [func.Eval(pt) for pt in pt_orig if pt > 0.])
        map_info['corr_orig'] = corr_orig

        map_info['pt_post_corr_orig'] = pt_orig * corr_orig
        map_info['hw_pt_post_corr_orig'] = (map_info['pt_post_corr_orig'] * 2.).astype(int)

        new_corr_mapping = calc_new_corr_mapping(pt_orig, corr_orig, new_pt_mapping)
        map_info['corr_compressed'] = np.array(new_corr_mapping.values())

        map_info['pt_post_corr_compressed'] = pt_orig * map_info['corr_compressed']
        map_info['hw_pt_post_corr_compressed'] = (map_info['pt_post_corr_compressed'] * 2.).astype(int)

        # then we calculate all the necessary correction integers
        corr_ints_new, add_ints = calc_hw_correction_addition_ints(map_info, corr_matrix_add_none, right_shift, num_add_bits)
        map_info['hw_corr_compressed'], map_info['hw_corr_compressed_add'] = corr_ints_new, add_ints

        # Store the result of applying the HW correction ints
        hw_pt_post = [correct_iet(iet, cf, right_shift, add_factor=af) for iet, cf, af
                      in izip(map_info['hw_pt_orig'],
                              map_info['hw_corr_compressed'],
                              map_info['hw_corr_compressed_add'])]

        hw_pt_post = np.array(hw_pt_post)
        map_info['hw_pt_post_hw_corr_compressed'] = hw_pt_post
        map_info['pt_post_hw_corr_compressed'] = hw_pt_post * 0.5

        # for k, v in map_info.iteritems():
        #     if v is not None:
        #         print k, type(v), len(v)

        all_mapping_info[eta_ind] = map_info

        if eta_ind in [0, 7]:
            print_map_info(map_info)  # for debugging dict contents

        # Print some plots to check results.
        # Show original corr, compressed corr, compressed corr from HW
        title = 'eta bin %d, target # bins %d, ' \
                'merge criterion %.3f, %s merge algo' % (eta_ind,
                    target_num_pt_bins, merge_criterion, merge_algorithm)
        plot_pt_pre_post_mapping(map_info, eta_ind, title, plot_dir)
        plot_corr_vs_pt(map_info, eta_ind, title, plot_dir)
        plot_corr_vs_pt_clusters(map_info, eta_ind, title, plot_dir)
        plot_pt_pre_pt_post_clusters(map_info, eta_ind, title, plot_dir)
        plot_func_vs_lut_pt(map_info, eta_ind, title, plot_dir)

    # put them into a LUT
    write_stage2_correction_lut(corr_lut_filename, all_mapping_info)
    write_stage2_addition_lut(add_lut_filename, all_mapping_info)
    write_stage2_addend_multiplicative_lut(add_mult_lut_filename, all_mapping_info, num_add_bits, num_corr_bits)


def print_map_info(map_info):
    """Print out contents of dict, entry by entry"""
    keys = map_info.keys()
    print ' : '.join(keys)
    for i in range(len(map_info['pt_orig'])):
        print ' : '.join([str(map_info[k][i]) for k in keys])


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
             'bo', label='Original', markersize=5, alpha=0.7, markeredgewidth=0)
    plt.plot(map_info['pt_orig'], map_info['pt_post_corr_compressed'],
             'r^', label='Compressed', markersize=5, alpha=0.7, markeredgewidth=0)
    plt.plot(map_info['pt_orig'], map_info['pt_post_hw_corr_compressed'],
             'gv', label='HW compressed', markersize=5, alpha=0.7, markeredgewidth=0)
    plt.xlabel('Original pT [GeV]')
    plt.ylabel('Post-Correction pT [GeV]')
    plt.legend(loc=0)
    plt.minorticks_on()
    plt.grid(which='both')
    plt.suptitle(title)
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_%d.pdf' % eta_ind))

    plt.xlim(0, 150)
    plt.ylim(0, 150)
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_zoomX_%d.pdf' % eta_ind))

    plt.xlim(5, 100)
    plt.ylim(5, 100)
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_zoomX_logX_%d.pdf' % eta_ind))

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
    cm = plt.cm.get_cmap('Set1')
    plt.scatter(map_info['pt_orig'], map_info['pt_post_corr_orig'],
                c=map_info['pt_index'], linewidth=0, cmap=cm)
    plt.xlabel('Original pT [GeV]')
    plt.ylabel('Post-Correction pT [GeV]')
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    # plt.legend(loc=0)
    plt.minorticks_on()
    plt.grid(which='both')
    plt.suptitle(title)
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_clusters_%d.pdf' % eta_ind))

    plt.xlim(0, 150)
    plt.ylim(0, 150)
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_clusters_zoomX_%d.pdf' % eta_ind))

    plt.xlim(5, 100)
    plt.ylim(5, 100)
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig(os.path.join(plot_dir, 'pt_pre_vs_post_clusters_zoomX_logX_%d.pdf' % eta_ind))

    plt.clf()


def plot_corr_vs_pt(map_info, eta_ind, title, plot_dir):
    """Plot correction factor vs pT, for original corrections,
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
             'bo', label='Original', markersize=5, alpha=0.7, markeredgewidth=0)
    plt.plot(map_info['pt_orig'], map_info['corr_compressed'],
             'r^', label='Compressed', markersize=5, alpha=0.7, markeredgewidth=0)
    plt.plot(map_info['pt_orig'], map_info['hw_pt_post_hw_corr_compressed'] / (1. * map_info['hw_pt_orig']),
             'gv', label='HW compressed', markersize=5, alpha=0.7, markeredgewidth=0)
    plt.xlabel('Original pT [GeV]')
    plt.ylabel('Correction')
    plt.ylim(0.5, 2.5)
    plt.legend(loc=0)
    plt.minorticks_on()
    plt.grid(which='both')
    plt.suptitle(title)
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_%d.pdf' % eta_ind))

    plt.xlim(0, 300)
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_zoomX_%d.pdf' % eta_ind))

    plt.xlim(5, 300)
    plt.xscale('log')
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_zoomX_logX_%d.pdf' % eta_ind))

    plt.clf()


def plot_corr_vs_pt_clusters(map_info, eta_ind, title, plot_dir):
    """Plot correction factor vs pT, for original corrections,
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
    cm = plt.cm.get_cmap('Set1')
    plt.scatter(map_info['pt_orig'], map_info['corr_orig'],
                c=map_info['pt_index'], linewidth=0, cmap=cm)
    plt.xlabel('Original pT [GeV]')
    plt.ylabel('Correction')
    plt.xlim(left=0)
    plt.ylim(0.5, 2.5)
    # plt.legend(loc=0)
    plt.minorticks_on()
    plt.grid(which='both')
    plt.suptitle(title)
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_cluster_%d.pdf' % eta_ind))

    plt.xlim(0, 300)
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_zoomX_cluster_%d.pdf' % eta_ind))

    plt.xlim(5, 300)
    plt.xscale('log')
    plt.savefig(os.path.join(plot_dir, 'corr_vs_pt_zoomX_logX_cluster_%d.pdf' % eta_ind))

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
    plt.plot(map_info['hw_pt_post_hw_corr_compressed'], map_info['hw_pt_post_corr_orig'], 'x')
    plt.xlabel('LUT corrected HW pT')
    plt.ylabel('Function corrected HW pT')
    plt.xlim(0, 1024)
    plt.ylim(0, 1024)
    plt.plot([0, 1024], [0, 1024])
    plt.minorticks_on()
    plt.grid(which='both')
    plt.suptitle(title)
    plt.savefig(os.path.join(plot_dir, 'lut_vs_func_%d.pdf' % eta_ind))

    plt.xlim(0, 200)
    plt.ylim(0, 200)
    plt.savefig(os.path.join(plot_dir, 'lut_vs_func_zoomX_%d.pdf' % eta_ind))

    plt.xlim(1, 200)
    plt.ylim(1, 200)
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig(os.path.join(plot_dir, 'lut_vs_func_zoomX_log_%d.pdf' % eta_ind))
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


def do_constant_fit(graph, eta_min, eta_max, output_dir):
    """Do constant-value fit to graph and plot the jackknife procedure.

    We derive the constant fit value by jack-knifing. There are 2 forms here:
    - "my jackknifing": where we loop over all possible subgraphs, and calculate
    the mean for each.
    - "proper jackknifing": where we loop over all N-1 subgraphs, and calulate
    the mean for each.

    Using these, we can then find the peak mean, or the average mean.
    By default, we use the peak of "my jackknife" as it ignores the
    high-correction tail better, and gives the better-sampled low pT
    end more importance.

    Parameters
    ----------
    graph : TGraph
        Graph to fit
    eta_min, eta_max : float
        Eta bin boundaries, purely for the plots
    output_dir : str
        Output directory for plots.

    Returns
    -------
    MultiFunc
        MultiFunc object with a const-value function for the whole pT range.
    """
    print 'Doing constant-value fit'

    xarr, yarr = cu.get_xy(graph)
    xarr, yarr = np.array(xarr), np.array(yarr)  # use numpy array for easy slicing

    # "my jackknifing": Loop over all possible subgraphs, and calculate a mean for each
    end = len(yarr)
    means = []
    while end > 0:
        start = 0
        while start < end:
            means.append(yarr[start:end].mean())
            start += 1
        end -= 1

    # "proper" Jackknife means
    jack_means = [np.delete(yarr, i).mean() for i in range(len(yarr))]

    # Do plotting & peak finding, for both methods
    plot_name = os.path.join(output_dir, 'means_hist_%g_%g_myjackknife.pdf' % (eta_min, eta_max))
    peak, mean = find_peak_and_average_plot(means, eta_min, eta_max, plot_name, 'My jackknife')

    plot_name = os.path.join(output_dir, 'means_hist_%g_%g_root_jackknife.pdf' % (eta_min, eta_max))
    jackpeak, jackmean = find_peak_and_average_plot(jack_means, eta_min, eta_max, plot_name, 'Proper jackknife')

    print 'my jackknife peak:', peak
    print 'my jackknife mean:', mean
    print 'jackknife peak:', jackpeak
    print 'jackknfe mean:', jackmean
    const_fn = ROOT.TF1("constant", '[0]', 0, 1024)
    const_fn.SetParameter(0, peak)
    const_multifn = MultiFunc({(0, np.inf): const_fn})
    return const_multifn


def find_peak_and_average_plot(values, eta_min, eta_max, plot_filename, title='Jackknife'):
    """Plot histogram of values, and extract peak and average, using ROOT.

    Parameters
    ----------
    means: list[float]
        Collection of values
    eta_min, eta_max: float
        Eta bin edges
    plot_filename: str
        Output filepath for plot.
    title : str
        Title for plot

    Returns
    -------
    float, float
        Peak mean, and average mean.
    """
    values = np.array(values)
    # auto-generate histogram x axis limits using min/max of values + spacer
    num_bins = 75 if len(values) > 200 else 50
    hist = ROOT.TH1D('h_mean', '', num_bins, 0.95 * values.min(), 1.05 * values.max())
    for m in values:
        hist.Fill(m)
    # find peak
    peak_bin = hist.GetMaximumBin()
    peak = hist.GetBinCenter(peak_bin)
    # plot
    canv = ROOT.TCanvas('c', '', 600, 600)
    canv.SetTicks(1, 1)
    hist.Draw("HISTE")
    average = values.mean()  # average of the values
    title = '%s, %g < #eta^{L1} < %g, peak at %g, mean at %g;Subgraph mean correction' % (title, eta_min, eta_max, peak, average)
    hist.SetTitle(title)
    # Draw a marker for peak value
    arrow_peak = ROOT.TArrow(peak, 25, peak, 0)
    arrow_peak.SetLineWidth(2)
    arrow_peak.SetLineColor(ROOT.kRed)
    arrow_peak.Draw()
    # Draw a marker for average value
    arrow_mean = ROOT.TArrow(average, 5, average, 0)
    arrow_mean.SetLineWidth(2)
    arrow_mean.SetLineColor(ROOT.kBlue)
    arrow_mean.Draw()
    leg = ROOT.TLegend(0.75, 0.75, 0.88, 0.88)
    leg.AddEntry(arrow_peak, "peak", "L")
    leg.AddEntry(arrow_mean, "average", "L")
    leg.Draw()
    canv.SaveAs(plot_filename)
    return peak, average
