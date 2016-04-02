#!/usr/bin/env python
"""
This script takes as input the output file from RunMatcher, and loops over
matched reference jet/L1 jet pairs, making resolution plots.

Does 5 types of "resolution":

- (pT(L1) - pT(Ref))/pT(L1), calculated on a pair-by-pair basis, binned in pT(L1).
Stored as `resL1_<eta_min>_<eta_max>`.

- (pT(L1) - pT(Ref))/pT(Ref), calculated on a pair-by-pair basis, binned in pT(L1).
Stored as `resRefL1_<eta_min>_<eta_max>`.

- (pT(L1) - pT(Ref))/pT(Ref), calculated on a pair-by-pair basis, binned in pT(L1).
Stored as `resRefRef_<eta_min>_<eta_max>`.

- use the width of the pT(L1) - pT(Ref) distribution, then divide by the average pT(L1).
This is done in bins of pT(L1). Stored as `resL1_<eta_min>_<eta_max>_diff`.

- use the width of the pT(L1) - pT(Ref) distribution, then divide by the average pT(Ref).
This is done in bins of pT(Ref). Stored as `resRefRef_<eta_min>_<eta_max>_diff`.
This is the correct one for performance plots, and is the one used by `showoffPlots.py`.

Usage:

python makeResolutionPlots -h

"""

import ROOT
import sys
from array import array
import numpy
from pprint import pprint
from itertools import izip
import os
import argparse
import binning
from binning import pairwise
import common_utils as cu


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2()
# ROOT.gROOT.ProcessLine('.L tdrStyle.C')
# ROOT.setTDRStyle()
ROOT.gStyle.SetOptTitle(0);
ROOT.gStyle.SetOptStat(1);
# ROOT.gROOT.ForceStyle();


def check_var_stored(tree, var):
    """Check to see if TTree has branch with name var"""
    return tree.GetListOfBranches().FindObject(var)

def check_fit_mean(fit_res, hist):
    """Check fit ok by comparing means - ASSUMES GAUSSIAN"""
    pass

def check_fit_peaks(fit_res, hist):
    """Check fit ok by comparing peaks - ASSUMES GAUSSIAN"""
    peak = hist.GetBinCenter(hist.GetMaximumBin())
    return abs(peak - fit_res.Parameters()[1]) < 0.2 * abs(peak)

def check_fit_width(fit_res, hist):
    """Check fit ok by comparing widths - ASSUMES GAUSSIAN"""
    rms = hist.GetRMS()
    return abs(rms - fit_res.Parameters()[2]) < 0.2 * abs(rms)

def plot_bin_fit(res_2d, ptmin, ptmax, hist_title, hist_name, graph, output, divide=False):
    """
    Does a resolution plot for one pt bin, and fits a Gaussian to it.

    res_2d is a 2D plot of resolution vs pt

    ptmin & ptmax are bin limits
    hist_title is title of resultant hist
    hist_name is name of resultant hist
    graph is TGraphErrors object to add point to, adds new point at (pt, width)
    output is where you want to write hist + fit to
    divide is flag, whether to divide the width by the mean pt (default is False)
    """

    # Get average pt value - could be lazy and use midpoint of bin,
    # or project 2D hist and get average
    # Lazy:
    pt_mid = 0.5 * (ptmin + ptmax)
    pt_width = 0.5 * (ptmax - ptmin)

    # Proper:
    h_pt = res_2d.ProjectionX("pt_%g_%g" % (ptmin, ptmax))
    h_pt.GetXaxis().SetRangeUser(ptmin, ptmax)
    pt_mid = h_pt.GetMean()

    # Projection of res values for given pt range
    # Get bin indices corresponding to physical pt values
    bin_low = res_2d.GetXaxis().FindBin(ptmin)
    bin_high = res_2d.GetXaxis().FindBin(ptmax)-1
    h_res = res_2d.ProjectionY(hist_name, bin_low, bin_high)
    h_res.SetTitle(hist_title)

    if h_res.GetEntries() > 0:
        peak = h_res.GetBinCenter(h_res.GetMaximumBin())
        fit_res = h_res.Fit("gaus", "QESR", "R", peak - (1. * h_res.GetRMS()), peak + (1. * h_res.GetRMS()))
        # fit_res = h_res.Fit("gaus", "QESR", "R", h_res.GetMean() - 1. * h_res.GetRMS(), h_res.GetMean() + 1. * h_res.GetRMS())
        # fit_res = h_res.Fit("gaus", "QMS")
        print "gaus prob:", fit_res.Prob(), hist_name
        # default values for the width & its error - safe if the fit went wrong
        width = h_res.GetRMS()
        width_err = h_res.GetRMSError()

        # check fit converged, and is sensible
        if fit_res and int(fit_res) == 0: # and check_fit_width(fit_res, h_res):
            width =  fit_res.Parameters()[2]
            width_err = fit_res.Errors()[2]
            # add point to graph
            if graph:
                count = graph.GetN()
                if divide:
                    width = width / pt_mid
                    width_err = width_err / pt_mid # important
                graph.SetPoint(count, pt_mid, width)
                graph.SetPointError(count, pt_width, width_err)
        else:
            print "Poor fit to l1 res - using raw values"

    else:
        print "0 entries in resolution plot"
    output.WriteTObject(h_res)


def plot_resolution(inputfile, outputfile, ptBins, absetamin, absetamax):
    """Do various resolution plots for given eta bin, for all pT bins"""

    print "Doing eta bin: %g - %g" % (absetamin, absetamax)
    print "Doing pt bins:", ptBins

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cut = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)
    # pt cut string for 2D plots
    pt_cut_all = "pt < %g" % (ptBins[-1])

    title = "%g < |#eta^{L1}| < %g" % (absetamin, absetamax)

    # First make 2D plots of pt difference and resolution Vs Et,
    # then we can project them for individual Et bins
    # This is *much* faster than just making all the plots individually
    diff_min = -200
    diff_max = 200
    nbins_diff = 200

    pt_bin_min = ptBins[0]
    pt_bin_min = 0
    pt_bin_max = ptBins[-1]
    nbins_et = 4 * (pt_bin_max - pt_bin_min)

    # Ref jet pt from tree - old ones don't store ptRef, so construct from pt/rsp
    # - or should it be pt * rsp for old style rsp?
    ptRef = "ptRef" if check_var_stored(tree_raw, "ptRef") else "(pt/rsp)"

    # 1D plot of ptDifference
    # tree_raw.Draw("ptDiff>>ptDiff(%d, %g, %g)" % (nbins_diff, diff_min, diff_max), eta_cut + "&&" + pt_cut_all)
    # ptDiff = ROOT.gROOT.FindObject("ptDiff")

    # 2d plots of pt difference vs L1 pt
    var = "ptDiff" if check_var_stored(tree_raw, "ptDiff") else "(pt-%s)" % ptRef
    tree_raw.Draw("%s:pt>>ptDiff_l1_2d(%d, %g, %g, %d, %g, %g)" % (var, nbins_et, pt_bin_min, pt_bin_max, nbins_diff, diff_min, diff_max), eta_cut + "&&" + pt_cut_all)
    ptDiff_l1_2d = ROOT.gROOT.FindObject("ptDiff_l1_2d")
    ptDiff_l1_2d.SetTitle("%s;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Ref} [GeV]" % title)
    output_f_hists.WriteTObject(ptDiff_l1_2d)

    # 1D plot of ptDiff
    ptDiff = ptDiff_l1_2d.ProjectionY("ptDiff")
    ptDiff.SetTitle(";E_{T}^{L1} - E_{T}^{Ref} [GeV];N")
    fit_res = ptDiff.Fit("gaus", "QESR", "R", ptDiff.GetMean() - 1. * ptDiff.GetRMS(), ptDiff.GetMean() + 1. * ptDiff.GetRMS())
    output_f_hists.WriteTObject(ptDiff)

    # 1D plot of L1 pt
    ptL1 = ptDiff_l1_2d.ProjectionX("pt")
    ptL1.SetTitle(";E_{T}^{L1}[GeV];N")
    fit_res = ptL1.Fit("gaus", "QESR", "R", ptL1.GetMean() - 1. * ptL1.GetRMS(), ptL1.GetMean() + 1. * ptL1.GetRMS())
    output_f_hists.WriteTObject(ptL1)

    # 2d plots of pt difference vs ref pt
    tree_raw.Draw("%s:%s>>ptDiff_ref_2d(%d, %g, %g, %d, %g, %g)" % (var, ptRef, nbins_et, pt_bin_min, pt_bin_max, nbins_diff, diff_min, diff_max), eta_cut + "&&" + pt_cut_all)
    ptDiff_ref_2d = ROOT.gROOT.FindObject("ptDiff_ref_2d")
    ptDiff_ref_2d.SetTitle("%s;E_{T}^{Ref} [GeV];E_{T}^{L1} - E_{T}^{Ref} [GeV]" % title)
    output_f_hists.WriteTObject(ptDiff_ref_2d)

    res_min = -5
    res_max = 2
    nbins_res = 210

    # 2D plot of L1-Ref/L1 VS L1
    var = "resL1" if check_var_stored(tree_raw, "resL1") else "(pt-%s)/pt" % (ptRef)  # for old pair files
    tree_raw.Draw("%s:pt>>res_l1_2d(%d, %g, %g, %d, %g, %g)" % (var, nbins_et, pt_bin_min, pt_bin_max, nbins_res, res_min, res_max), eta_cut + "&&" + pt_cut_all)
    res_l1_2d = ROOT.gROOT.FindObject("res_l1_2d")
    res_l1_2d.SetTitle("%s;E_{T}^{L1} [GeV];(E_{T}^{L1} - E_{T}^{Ref})/E_{T}^{L1}" % title)
    output_f_hists.WriteTObject(res_l1_2d)

    # 1D plot of L1-ref/L1
    res_l1 = res_l1_2d.ProjectionY("res_l1")
    res_l1.SetTitle(";E_{T}^{L1} - E_{T}^{Ref}/E_{T}^{L1};N")
    fit_res = res_l1.Fit("gaus", "QESR", "R", res_l1.GetMean() - 1. * res_l1.GetRMS(), res_l1.GetMean() + 1. * res_l1.GetRMS())
    output_f_hists.WriteTObject(res_l1)

    # 2D plot of L1-Ref/Ref VS L1
    var = "resRef" if check_var_stored(tree_raw, "resRef") else "(pt-%s)/%s" % (ptRef, ptRef)
    res_min = -2
    nbins_res = 120
    tree_raw.Draw("%s:pt>>res_refVsl1_2d(%d, %g, %g, %d, %g, %g)" % (var, nbins_et, pt_bin_min, pt_bin_max, nbins_res, res_min, res_max), eta_cut + "&&" + pt_cut_all)
    res_refVsl1_2d = ROOT.gROOT.FindObject("res_refVsl1_2d")
    res_refVsl1_2d.SetTitle("%s;E_{T}^{L1} [GeV];(E_{T}^{L1} - E_{T}^{Ref})/E_{T}^{Ref}" % title)
    output_f_hists.WriteTObject(res_refVsl1_2d)

    # 1D plot of L1-ref/ref
    res_ref = res_refVsl1_2d.ProjectionY("res_ref")
    res_ref.SetTitle(";E_{T}^{L1} - E_{T}^{Ref}/E_{T}^{L1};N")
    fit_res = res_ref.Fit("gaus", "QESR", "R", res_ref.GetMean() - 1. * res_ref.GetRMS(), res_ref.GetMean() + 1. * res_ref.GetRMS())
    output_f_hists.WriteTObject(res_ref)

    # 2D plot of L1-Ref/Ref VS Ref
    var = "resRef" if check_var_stored(tree_raw, "resRef") else "(pt-%s)/%s" % (ptRef, ptRef)
    tree_raw.Draw("%s:%s>>res_refVsref_2d(%d, %g, %g, %d, %g, %g)" % (var, ptRef, nbins_et, pt_bin_min, pt_bin_max, nbins_res, res_min, res_max), eta_cut + "&&" + pt_cut_all)
    res_refVsref_2d = ROOT.gROOT.FindObject("res_refVsref_2d")
    res_refVsref_2d.SetTitle("%s;E_{T}^{Ref} [GeV];(E_{T}^{L1} - E_{T}^{Ref})/E_{T}^{Ref}" % title)
    output_f_hists.WriteTObject(res_refVsref_2d)

    # Graphs to hold resolution for all pt bins
    res_graph_l1 = ROOT.TGraphErrors()
    res_graph_l1.SetNameTitle("resL1_%g_%g" % (absetamin, absetamax), "%s;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Ref}/E_{T}^{L1}" % title)

    res_graph_l1_diff = ROOT.TGraphErrors() #binned in l1 pt.  this fits to L1-ref, then divides by average L1 pT
    res_graph_l1_diff.SetNameTitle("resL1_%g_%g_diff" % (absetamin, absetamax), "%s;E_{T}^{L1} [GeV];#sigma(E_{T}^{L1} - E_{T}^{Ref})/<E_{T}^{L1}>" % title)

    res_graph_refVsl1 = ROOT.TGraphErrors() # binned in l1 pt
    res_graph_refVsl1.SetNameTitle("resRefL1_%g_%g" % (absetamin, absetamax), "%s;E_{T}^{L1} [GeV];E_{T}^{L1} - E_{T}^{Ref}/E_{T}^{Ref}" % title)

    res_graph_refVsref = ROOT.TGraphErrors() # binned in ref pt
    res_graph_refVsref.SetNameTitle("resRefRef_%g_%g" % (absetamin, absetamax), "%s;E_{T}^{Ref} [GeV];E_{T}^{L1} - E_{T}^{Ref}/E_{T}^{Ref}" % title)

    res_graph_refVsref_diff = ROOT.TGraphErrors() # fit to L1 - ref pT, divide by ref pT, binned in ref pt
    res_graph_refVsref_diff.SetNameTitle("resRefRef_%g_%g_diff" % (absetamin, absetamax), "%s;E_{T}^{Ref} [GeV];E_{T}^{L1} - E_{T}^{Ref}/<E_{T}^{Ref}>" % title)

    # res_graph_refVsl1_diff = ROOT.TGraphErrors() # fit to L1 - ref pT, divide by ref pT, binned in L1 pt
    # res_graph_refVsl1_diff.SetNameTitle("resRefL1_%g_%g_diff" % (absetamin, absetamax), "%s;E_{T}^{Ref} [GeV];#sigma(E_{T}^{L1} - E_{T}^{Ref})/<E_{T}^{Ref}>" % title)

    # Now go through pt bins, and plot resolution for each, fit with gaussian,
    # and add width to graph
    for i, ptmin in enumerate(ptBins[:-1]):
        ptmax = ptBins[i+1]
        # pt_cut = "pt < %g && pt > %g" % (ptmax, ptmin)
        # pt_cut_ref = "%s < %g && %s > %g" % (ptRef, ptmax, ptRef, ptmin)
        print "    Doing pt bin: %g - %g" % (ptmin, ptmax)

        l1_bin_title = title + ", %g < p_{T}^{L1} < %g" % (ptmin, ptmax)
        ref_bin_title = title + ", %g < p_{T}^{Ref} < %g" % (ptmin, ptmax)

        # Plot difference in L1 pT and Ref pT (in bin of L1 pt)
        plot_bin_fit(ptDiff_l1_2d, ptmin, ptmax,
            "%s;E_{T}^{L1} - E_{T}^{Ref} [GeV];N" % l1_bin_title,
            "ptDiff_l1_%g_%g" % (ptmin, ptmax), res_graph_l1_diff, output_f_hists, divide=True)

        # Plot difference in L1 pT and Ref pT (in bin of ref pt)
        plot_bin_fit(ptDiff_ref_2d, ptmin, ptmax,
            "%s;E_{T}^{L1} - E_{T}^{Ref} [GeV];N" % ref_bin_title,
            "ptDiff_ref_%g_%g" % (ptmin, ptmax), res_graph_refVsref_diff, output_f_hists, divide=True)

        # Plot resolution wrt L1 pT & fit
        plot_bin_fit(res_l1_2d, ptmin, ptmax,
            "%s;(E_{T}^{L1} - E_{T}^{Ref})/E_{T}^{L1};N" % l1_bin_title,
            "res_l1_%g_%g" % (ptmin, ptmax), res_graph_l1, output_f_hists)

        # Plot ref resolution wrt L1 pT & fit
        plot_bin_fit(res_refVsl1_2d, ptmin, ptmax,
            "%s;(E_{T}^{L1} - E_{T}^{Ref})/E_{T}^{Ref};N" % l1_bin_title,
            "res_ref_l1_%g_%g" % (ptmin, ptmax), res_graph_refVsl1, output_f_hists)

        # Plot ref resolution Vs ref pt
        plot_bin_fit(res_refVsref_2d, ptmin, ptmax,
            "%s;(E_{T}^{L1} - E_{T}^{Ref})/E_{T}^{Ref};N" % ref_bin_title,
            "res_ref_ref_%g_%g" % (ptmin, ptmax), res_graph_refVsref, output_f_hists)

    output_f.WriteTObject(res_graph_l1)
    output_f.WriteTObject(res_graph_l1_diff)
    output_f.WriteTObject(res_graph_refVsl1)
    output_f.WriteTObject(res_graph_refVsref)
    output_f.WriteTObject(res_graph_refVsref_diff)


def main(in_args=sys.argv[1:]):
    print in_args
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=cu.CustomFormatter)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("output", help="output ROOT filename")
    parser.add_argument("--incl", action="store_true", help="Do inclusive eta plots")
    parser.add_argument("--excl", action="store_true", help="Do exclusive eta plots")
    parser.add_argument("--central", action='store_true',
                        help="Do central eta bins only (eta <= 3)")
    parser.add_argument("--forward", action='store_true',
                        help="Do forward eta bins only (eta >= 3)")
    parser.add_argument("--etaInd", nargs="+",
                        help="list of eta bin INDICES to run over - " \
                        "if unspecified will do all. " \
                        "This overrides --central/--forward. " \
                        "Handy for batch mode. " \
                        "IMPORTANT: MUST PUT AT VERY END")
    args = parser.parse_args(args=in_args)

    inputf = ROOT.TFile(args.input, "READ")
    outputf = ROOT.TFile(args.output, "RECREATE")
    print "Reading from", args.input
    print "Writing to", args.output

    if not inputf or not outputf:
        raise Exception("Couldn't open input or output files")

    # Setup eta bins
    etaBins = binning.eta_bins[:]
    if args.etaInd:
        args.etaInd.append(int(args.etaInd[-1])+1) # need upper eta bin edge
        # check eta bins are ok
        etaBins = [etaBins[int(x)] for x in args.etaInd]
    elif args.central:
        etaBins = binning.eta_bins_central
    elif args.forward:
        etaBins = binning.eta_bins_forward
    print "Running over eta bins:", etaBins

    # Do plots for individual eta bins
    if args.excl:
        print "Doing individual eta bins"
        for i, (eta_min, eta_max) in enumerate(pairwise(etaBins)):

            # whether we're doing a central or forward bin (.1 is for rounding err)
            forward_bin = eta_max > 3.1

            # setup pt bins, wider ones for forward region
            # ptBins = binning.pt_bins_8 if not forward_bin else binning.pt_bins_8_wide
            ptBins = binning.pt_bins if not forward_bin else binning.pt_bins_wide

            plot_resolution(inputf, outputf, ptBins[4:], eta_min, eta_max)

    # Do plots for inclusive eta
    # Skip if doing exlcusive and only 2 bins, or if only 1 bin
    if args.incl and ((not args.excl and len(etaBins) >= 2) or (args.excl and len(etaBins)>2)):
        print "Doing inclusive eta"
        # ptBins = binning.pt_bins if not etaBins[0] > 2.9 else binning.pt_bins_wide
        plot_resolution(inputf, outputf, binning.pt_bins[4:], etaBins[0], etaBins[-1])

    if not args.incl and not args.excl:
        print "Not doing inclusive or exclusive - you must specify at least one!"
        return 1

    inputf.Close()
    outputf.Close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
