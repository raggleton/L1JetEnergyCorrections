"""Functions for printing LUTs for Stage 2

Makes 2 LUTs:

- one to convert pt to compressed index
- one to map a correction factor to each index

Gets pretty gnarly, improvements needed.
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


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)


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

    print count_number_unique_ints(new_pt_mapping), 'compressed bins:'
    print len(set(new_pt_mapping.values())), 'compressed bins:'
    print sorted(set(new_pt_mapping.values()))

    mask = [k != v for k, v in new_pt_mapping.iteritems()]
    if any(mask):
        # -1 required with .index() as otherwise it picks up wrong index
        print 'Compressed above (inclusive):', pt_orig[mask.index(True) - 1]
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
    return (ieta_index<<4) + iet_index


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
        lut.write("#<header> versionStr(unused but may be in future) nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 8 4 </header>\n")
        for pt, ind in izip(hw_pt_orig, pt_index):
            if pt > 511:
                break
            if pt % 2 == 0:
                # only want even HW values, then convert to what it would be
                # if removed LSB
                lut.write('%d %d\n' % (int(pt / 2), ind))


def correct_iet(iet, corr_factor, right_shift):
    """Apply correction int to HW pt."""
    iet_new = iet * corr_factor
    iet_new = np.right_shift(iet_new, right_shift)
    iet_new += iet
    return iet_new


def generate_corr_matrix(max_iet, max_hw_correction, right_shift):
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
        corr_m[i] = correct_iet(np.arange(0, max_iet + 1), i, right_shift)
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
        lut.write("#<header> versionStr(unused but may be in future) nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 8 10 </header>\n")
        for eta_ind, map_info in mapping_info.iteritems():
            last_ind = -1
            for pt_ind, corr in izip(map_info['pt_index'], map_info['hw_corr_compressed']):
                if pt_ind != last_ind:
                    comment = '  # eta_bin %d, pt 0' % (eta_ind) if pt_ind == 0 else ''
                    lut.write('%d %d%s\n' % (generate_address(pt_ind, eta_ind), corr, comment))
                    last_ind = pt_ind


def ieta_to_index(ieta):
    """Convert ieta to index"""
    ieta = abs(ieta)
    if ieta <= 29:  # HBHE
        return int(ceil(ieta / 4.)) - 1
    else:  # HF
        return int(ceil((ieta - 29) / 3.)) + 6


def write_eta_compress_lut(lut_filename):
    """Write LUT that converts ieta to eta index.

    Parameters
    ----------
    lut_filename : str
        filename for LUT
    """
    print "Making eta compression LUT"
    with open(lut_filename, 'w') as lut:
        lut.write("# ieta compression LUT\n")
        lut.write("# Converts abs(ieta) (6 bits) into 4 bit index\n")
        lut.write("# anything after # is ignored with the exception of the header\n")
        lut.write("# the header is first valid line starting with ")
        lut.write("#<header> versionStr(unused but may be in future) nrBitsAddress nrBitsData </header>\n")
        lut.write("#<header> v1 6 4 </header>\n")
        for ieta in range(1, 42):
            line = "%d %d\n" % (ieta, ieta_to_index(ieta))
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
                           eta_lut_filename, pt_lut_filename, corr_lut_filename,
                           corr_max, num_corr_bits, target_num_pt_bins,
                           merge_criterion, plot_dir):
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
        Filename for output LUT that converts address to factor

    corr_max: float
        Maximum for correction factors. Determines the right-shift factor needed
        in hardware

    num_corr_bits: int
        Number of bits to represent correction factor.

    target_num_pt_bins: int
        Number of bins to compress pt bin range into. If you have N bits for pt,
        then target_num_pt_bins = 2**N - 1

    merge_criterion: float
        Criterion factor for compressing multiple pt bins into one bin. Bins will
        be combined if the maximum correction factor = merge_criterion * minimum
        correction factor for those pt bins.

    plot_dir : str
        Directory to put checking plots.

    Raises
    ------
    IndexError
        If the number of fit functions is not the same as number of eta bins
    """

    # Plot LUT for eta compression
    write_eta_compress_lut(eta_lut_filename)

    if corr_max <= 2:
        right_shift = num_corr_bits
    elif corr_max <= 3:
        right_shift = num_corr_bits - 1
    elif corr_max <= 5:
        right_shift = num_corr_bits - 2
    elif corr_max <= 7:
        right_shift = num_corr_bits - 3
    else:
        raise RuntimeError('Correction factor > 7 sounds dangerous!')

    print 'Running Stage 2 LUT making with:'
    print ' - target num pt bins (per eta bin):', target_num_pt_bins
    print ' - merge criterion:', merge_criterion
    print ' - # corr bits:', num_corr_bits
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

    # Find the optimal compressed pt binning
    new_pt_mapping = calc_compressed_pt_mapping(pt_orig, corr_orig,
                                                target_num_pt_bins,
                                                merge_criterion,
                                                merge_above, merge_below)

    pt_compressed = np.array(new_pt_mapping.values())
    hw_pt_compressed = (pt_compressed * 2).astype(int)

    # figure out pt unique indices for each pt
    pt_index = np.array(assign_pt_index(hw_pt_compressed))

    # make a lut to convert original pt (address) to compressed (index)
    write_pt_compress_lut(pt_lut_filename, hw_pt_orig, pt_index)

    # to store {eta_index: {various pt/correction mappings}} for all eta bins
    all_mapping_info = OrderedDict()

    # Generate matrix of iet pre/post for different correction integers
    # Only need to do it once beforehand, can be used for all eta bins
    corr_matrix = generate_corr_matrix(max_iet=int(max_pt * 2),
                                       max_hw_correction=(2**num_corr_bits) - 1,
                                       right_shift=right_shift)

    # figure out new correction mappings for each eta bin
    for eta_ind, func in enumerate(fit_functions):
        # if eta_ind>0:
            # break

        # Dict to hold ALL info for this eta bin
        map_info = dict(pt_orig=pt_orig,  # original phys pt values
                        hw_pt_orig=hw_pt_orig,  # original HW pt values
                        pt_compressed=pt_compressed,  # phys pt values after compression
                        hw_pt_compressed=hw_pt_compressed,  # HW pt values after compression
                        pt_index=pt_index,  # index for compressed pt
                        corr_orig=None,  # original correction factors (phys)
                        corr_compressed=None,  # correction factors after pt compression (phys)
                        hw_corr_compressed=None,  # HW correction factor after pt compression
                        pt_post_corr_orig=None,  # phys pt post original corrections
                        pt_post_corr_compressed=None,  # phys pt post compressed corrections
                        hw_pt_post_hw_corr_compressed=None,  # HW pt post HW correction factor
                        pt_post_hw_corr_compressed=None  # phys pt post HW correction factor
                        )

        print 'Calculating compressed correction value for eta bin', eta_ind

        corr_orig = np.array([0.] + [func.Eval(pt) for pt in pt_orig if pt > 0.])
        map_info['corr_orig'] = corr_orig

        map_info['pt_post_corr_orig'] = pt_orig * corr_orig

        new_corr_mapping = calc_new_corr_mapping(pt_orig, corr_orig, new_pt_mapping)
        map_info['corr_compressed'] = np.array(new_corr_mapping.values())

        map_info['pt_post_corr_compressed'] = pt_orig * map_info['corr_compressed']

        # then we calculate all the necessary correction integers
        corr_ints = calc_hw_correction_ints(map_info['hw_pt_compressed'],
                                            map_info['corr_compressed'],
                                            corr_matrix,
                                            cap_correction=corr_max)
        map_info['hw_corr_compressed'] = corr_ints

        # Store the result of applying the HW correction ints
        hw_pt_post = [correct_iet(iet, cf, right_shift) for iet, cf
                      in izip(map_info['hw_pt_orig'], map_info['hw_corr_compressed'])]
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
                'merge criterion %.3f' % (eta_ind, target_num_pt_bins, merge_criterion)
        plot_pt_pre_post_mapping(map_info, eta_ind, title, plot_dir)
        plot_corr_vs_pt(map_info, eta_ind, title, plot_dir)

    # put them into a LUT
    write_stage2_correction_lut(corr_lut_filename, all_mapping_info)


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
