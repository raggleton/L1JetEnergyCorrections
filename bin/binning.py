"""
Centralised way to keep track of pt & eta binning.

For future, may need to split up into GCT/Stage1 Vs Stage 2...
"""


import ROOT
import numpy as np
from itertools import tee, izip


ROOT.PyConfig.IgnoreCommandLineOptions = True


# taken from https://docs.python.org/2.7/library/itertools.html#recipes
def pairwise(iterable):
    """s -> (s0, s1), (s1, s2), (s2, s3) ...

    Example:
    >>> for eta_min, eta_max in pairwise(binning.eta_bins):
    ...     print eta_min, eta_max
    (0, 0.348)
    (0.348, 0.695)
    (0.695, 1.044)
    ...

    Parameters
    ----------
    iterable : Any iterable collection.

    Returns
    -------
    The type stored in iterable
    """
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

############
# PT BINS
############
pt_bins = list(np.arange(14, 254, 4))
# wider binning at higher pt for low stats regions
pt_bins_wide = list(np.concatenate((np.arange(14, 50, 4),
                                    np.arange(50, 270, 20))))
pt_bins_stage2_old = list(np.arange(10, 1026, 4))
# wider binning for high pt
pt_bins_stage2 = list(np.concatenate((np.arange(10, 342, 4),
                                      np.arange(342, 1040, 20))))
# wider binning for HF
pt_bins_stage2_hf = list(np.concatenate((np.arange(10, 62, 4),
                                         np.arange(62, 1040, 20))))

# 8 GeV bins for resolution plots
pt_bins_8 = list(np.arange(14, 246, 8))
pt_bins_8.append(250)
# and wider ones for low stat bins
pt_bins_8_wide = list(np.concatenate((np.arange(14, 54, 8),
                                      np.arange(54, 242, 20))))
pt_bins_8_wide.append(250)

# stage 2 version for higher pt
pt_bins_stage2_8 = list(np.concatenate((np.arange(10, 320, 8),
                                        np.arange(320, 1020, 20))))
pt_bins_stage2_8_wide = list(np.concatenate((np.arange(10, 50, 8),
                                             np.arange(50, 1020, 20))))



# pt bins for doing checkCalibration.py
# check_pt_bins = [[0, 20], [20, 40], [40, 60], [60, 80], [80, 120], [120, 200], [200, 300], [300, 500], [500, 1000]]
check_pt_bins = [[0, 20], [20, 30], [30, 40], [40, 50], [50, 60], [60, 80], [80, 100], [100, 300], [300, 500], [500, 1000]]  # for HTT studies, focussing on low pt

############
# ETA BINS
############
eta_bins = [0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5]
eta_bins_all = [-5, -4.5, -4.0, -3.5, -3.0, -2.172, -1.74, -1.392, -1.044, -0.695, -0.348,
                0.0, 0.348, 0.695, 1.044, 1.392, 1.74, 2.172, 3.0, 3.5, 4.0, 4.5, 5]
eta_bins_central = [eta for eta in eta_bins if eta < 3.1]
eta_bins_forward = [eta for eta in eta_bins if eta > 2.9]
# a handy palette of colours
eta_bin_colors = [ROOT.kRed,
                  ROOT.kBlue,
                  ROOT.kGreen + 2,
                  ROOT.kBlack,
                  ROOT.kMagenta,
                  ROOT.kOrange + 7,
                  ROOT.kAzure + 1,
                  ROOT.kRed + 3,
                  ROOT.kViolet + 1,
                  ROOT.kOrange,
                  ROOT.kTeal - 5]

##########
# PU BINS
##########
pu_bins = [[0, 10], [15, 25], [30, 40]]  # usual binning used for MC studies
pu_bins_lower = [[0, 5], [8, 12], [15, 25]] # run260627 lower PU overall - mean 10
