#!/usr/bin/env python
"""
This script extracts a constant value from a graph, by a sort of democratic process.

It takes all possible sub-graphs (without skipping points), and calculates a mean for each.
It then plots all those means in a histogram, and finds the peak. This is our 'average',
the idea being that the majority of the graph contributes to this average, and bits that
fluctuate up or down get washed out.

Improvements:
- allow skipping of points?
- fit curve to get better peak estimate?
"""


import ROOT
import os
import numpy as np
import argparse
import binning
import common_utils as cu
from runCalibration import generate_eta_graph_name
import matplotlib.pyplot as plt


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)


# filename = "../Stage2_HF_QCDFlatSpring15BX25HCALFix_10Feb_2dd1043_noJEC_v2/output/output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root"

def process_file(filename, eta_bins=binning.eta_bins_forward):
    """Process a ROOT file with graphs, print a mean & mean histogram for each.

    Parameters
    ----------
    filename : str
        Name of ROOT file to process (from runCalibration.py)
    eta_bins : list[[float, float]]
        Eta bin edges.
    """
    f = cu.open_root_file(filename)

    for eta_min, eta_max in binning.pairwise(eta_bins):
        gr = cu.get_from_file(f, generate_eta_graph_name(eta_min, eta_max))
        if not gr:
            raise RuntimeError("Can't get graph")

        xarr, yarr = cu.get_xy(gr)
        xarr, yarr = np.array(xarr), np.array(yarr)  # use numpy array for easy slicing

        # Loop over all possible subgraphs, and calculate a mean for each
        end = len(yarr)
        means = []
        while end > 0:
            start = 0
            while start < end:
                means.append(yarr[start:end].mean())
                start += 1
            end -= 1

        # Jackknife means
        jack_means = [np.delete(yarr, i).mean() for i in range(len(yarr))]

        # Do plotting & peak finding in both ROOT and MPL...not sure which is better?
        # peak = plot_find_peak_mpl(means, eta_min, eta_max, os.path.dirname(os.path.realpath(filename)))
        peak = plot_find_peak_root(means, eta_min, eta_max, os.path.dirname(os.path.realpath(filename)))
        jackpeak = plot_jacknife_root(jack_means, eta_min, eta_max, os.path.dirname(os.path.realpath(filename)))
        print 'Eta bin:', eta_min, '-', eta_max
        print peak
        print 'jackknife mean:'
        print np.array(jack_means).mean()

    f.Close()


def plot_jacknife_root(means, eta_min, eta_max, output_dir):
    """Plot histogram of mean, and extract peak, using ROOT.
    This uses jackknifing means.

    Parameters
    ----------
    means: list[float]
        Collection of mean values
    eta_min, eta_max: float
        Eta bin edges
    output_dir: str
        Output directory for plot.

    Returns
    -------
    float
        Peak mean.
    """
    means = np.array(means)
    # auto-generate histogram x axis limits using min/max of means + spacer
    num_bins = 75 if len(means) > 200 else 50
    hist = ROOT.TH1D('h_mean', '', num_bins, 0.95 * means.min(), 1.05 * means.max())
    for m in means:
        hist.Fill(m)
    # find peak
    peak_bin = hist.GetMaximumBin()
    peak = hist.GetBinCenter(peak_bin)
    # plot
    canv = ROOT.TCanvas('c', '', 600, 600)
    canv.SetTicks(1, 1)
    hist.Draw("HISTE")
    title = '%g < #eta^{L1} < %g, peak at %g;Subgraph mean correction' % (eta_min, eta_max, peak)
    hist.SetTitle(title)
    # Draw a marker for peak value
    arrow_peak = ROOT.TArrow(peak, 25, peak, 0)
    arrow_peak.SetLineWidth(2)
    arrow_peak.SetLineColor(ROOT.kRed)
    arrow_peak.Draw()
    # Draw a marker for mean value
    arrow_mean = ROOT.TArrow(means.mean(), 5, means.mean(), 0)
    arrow_mean.SetLineWidth(2)
    arrow_mean.SetLineColor(ROOT.kBlue)
    arrow_mean.Draw()
    canv.SaveAs(os.path.join(output_dir, 'means_hist_%g_%g_rootjack_.pdf' % (eta_min, eta_max)))
    return peak


def plot_find_peak_root(means, eta_min, eta_max, output_dir):
    """Plot histogrm of mean, and extract peak, using ROOT.

    Parameters
    ----------
    means: list[float]
        Collection of mean values
    eta_min, eta_max: float
        Eta bin edges
    output_dir: str
        Output directory for plot.

    Returns
    -------
    float
        Peak mean.
    """
    means = np.array(means)
    # auto-generate histogram x axis limits using min/max of means + spacer
    num_bins = 75 if len(means) > 200 else 50
    hist = ROOT.TH1D('h_mean', '', num_bins, 0.95 * means.min(), 1.05 * means.max())
    for m in means:
        hist.Fill(m)
    # find peak
    peak_bin = hist.GetMaximumBin()
    peak = hist.GetBinCenter(peak_bin)
    # plot
    canv = ROOT.TCanvas('c', '', 600, 600)
    canv.SetTicks(1, 1)
    hist.Draw("HISTE")
    title = '%g < #eta^{L1} < %g, peak at %g;Subgraph mean correction' % (eta_min, eta_max, peak)
    hist.SetTitle(title)
    # Draw a marker for peak value
    arrow = ROOT.TArrow(peak, 25, peak, 0)
    arrow.SetLineWidth(2)
    arrow.SetLineColor(ROOT.kRed)
    arrow.Draw()
    canv.SaveAs(os.path.join(output_dir, 'means_hist_%g_%g_root.pdf' % (eta_min, eta_max)))
    return peak


def plot_find_peak_mpl(means, eta_min, eta_max, output_dir):
    """Plot histogrm of mean, and extract peak, using matplotlib.

    Parameters
    ----------
    means: list[float]
        Collection of mean values
    eta_min, eta_max: float
        Eta bin edges
    output_dir: str
        Output directory for plot.

    Returns
    -------
    float
        Peak mean.
    """
    means = np.array(means)
    print len(means)
    # Plot
    num_bins = 75 if len(means) > 200 else 50
    n, bins, patches = plt.hist(means, bins=num_bins)
    plt.show()
    # Find peak
    max_ind = np.where(n == n.max())[0][0]
    peak = bins[max_ind:max_ind + 2].mean()
    # Marker for peak value
    plt.arrow(peak, 15, 0, -15, color='red', length_includes_head=True, head_length=2, head_width=0.005)
    # Aesthetics, and save
    plt.minorticks_on()
    plt.grid(which='both')
    plt.xlabel('Subgraph mean correction')
    plt.suptitle(r'$%g\ <\ \eta^{L1}\ <\ %g$, peak at %g' % (eta_min, eta_max, peak))
    plt.savefig(os.path.join(output_dir, 'means_hist_%g_%g_mpl.pdf' % (eta_min, eta_max)))
    plt.clf()
    return peak


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=cu.CustomFormatter)
    parser.add_argument("input", help="input ROOT filename")
    args = parser.parse_args()

    process_file(args.input)
