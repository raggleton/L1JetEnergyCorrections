#!/usr/bin/env python
"""
This script takes as input the output file from RunMatcher, and loops over
matched genjet/L1 jet pairs, producing some plots that show off how
calibrated (or uncalibrated) the jets are.

Usage: python checkCalibration.py -h

"""


import ROOT
import sys
from array import array
import numpy as np
import argparse
import binning
from binning import pairwise
import common_utils as cu


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)


def plot_checks(inputfile, outputfile, absetamin, absetamax, max_pt, pu_min, pu_max):
    """
    Do all the relevant response 1D and 2D hists, for one eta bin.

    Can optionally impose maximum pt cut on L1 jets (to avoid problems with saturation),
    and on number of PU vertices.
    """

    print "Doing eta bin: %g - %g, max L1 jet pt: %g" % (absetamin, absetamax, max_pt)

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = output_f.mkdir("Histograms")

    # Eta cut string
    eta_cutStr = " TMath::Abs(eta)<%g && TMath::Abs(eta) > %g " % (absetamax, absetamin)
    # Pt cut string
    pt_cutStr = "pt < %g" % max_pt
    # PU cut string
    pu_cutStr = "numPUVertices <= %f && numPUVertices >= %f" % (pu_max, pu_min)
    cutStr = " && ".join([eta_cutStr, pt_cutStr, pu_cutStr])

    # Draw response (pT^L1/pT^Gen) for all pt bins
    tree_raw.Draw("rsp>>hrsp_eta_%g_%g(100,0,5)" % (absetamin, absetamax), cutStr)
    hrsp_eta = ROOT.gROOT.FindObject("hrsp_eta_%g_%g" % (absetamin, absetamax))
    hrsp_eta.SetTitle(";response (p_{T}^{L1}/p_{T}^{Ref});")
    if absetamin < 2.9:
        fit_result = hrsp_eta.Fit("gaus", "QER", "",
                                  hrsp_eta.GetMean() - hrsp_eta.GetRMS(),
                                  hrsp_eta.GetMean() + hrsp_eta.GetRMS())
    else:
        peak = hrsp_eta.GetBinCenter(hrsp_eta.GetMaximumBin())
        fit_result = hrsp_eta.Fit("gaus", "QER", "",
                                  peak - (0.5 * hrsp_eta.GetRMS()),
                                  peak + (0.5 * hrsp_eta.GetRMS()))

    # mean = hrsp_eta.GetFunction("gaus").GetParameter(1)
    # err = hrsp_eta.GetFunction("gaus").GetParError(1)
    output_f_hists.WriteTObject(hrsp_eta)

    # nb_pt, pt_min, pt_max = 63, 0, 252  # for GCT/Stage 1
    nb_pt, pt_min, pt_max = 512, 0, 1024  # for Stage 2
    nb_rsp, rsp_min, rsp_max = 100, 0, 5

    # Draw rsp (pT^L1/pT^Gen) Vs GenJet pT
    tree_raw.Draw("rsp:ptRef>>h2d_rsp_gen(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_rsp, rsp_min, rsp_max), cutStr)
    h2d_rsp_gen = ROOT.gROOT.FindObject("h2d_rsp_gen")
    h2d_rsp_gen.SetTitle(";p_{T}^{Ref} [GeV];response (p_{T}^{L1}/p_{T}^{Ref})")
    output_f_hists.WriteTObject(h2d_rsp_gen)

    h2d_rsp_gen_norm = cu.norm_vertical_bins(h2d_rsp_gen)
    output_f_hists.WriteTObject(h2d_rsp_gen_norm)

    # Draw rsp (pT^L1/pT^Gen) Vs L1 pT
    tree_raw.Draw("rsp:pt>>h2d_rsp_l1(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_rsp, rsp_min, rsp_max), cutStr)
    h2d_rsp_l1 = ROOT.gROOT.FindObject("h2d_rsp_l1")
    h2d_rsp_l1.SetTitle(";p_{T}^{L1} [GeV];response (p_{T}^{L1}/p_{T}^{Ref})")
    output_f_hists.WriteTObject(h2d_rsp_l1)

    h2d_rsp_l1_norm = cu.norm_vertical_bins(h2d_rsp_l1)
    output_f_hists.WriteTObject(h2d_rsp_l1_norm)

    # Draw pT^Gen Vs pT^L1
    tree_raw.Draw("pt:ptRef>>h2d_gen_l1(%d,%g,%g,%d,%g,%g)" % (nb_pt, pt_min, pt_max, nb_pt, pt_min, pt_max), cutStr)
    h2d_gen_l1 = ROOT.gROOT.FindObject("h2d_gen_l1")
    h2d_gen_l1.SetTitle(";p_{T}^{Ref} [GeV];p_{T}^{L1} [GeV]")
    output_f_hists.WriteTObject(h2d_gen_l1)


def plot_rsp_eta(inputfile, outputfile, eta_bins, pt_min, pt_max, pt_var, pu_min, pu_max):
    """Plot graph of response in bins of eta

    If the response hist for each bin exists already, then we use that.
    If not, we make the hist.

    pt_min and pt_max are so that the graph can be made for a given pt interval
    pt_var is the variable to bin on (pt or ptRef)
    """

    gr_rsp_eta = ROOT.TGraphErrors()

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.GetDirectory('eta_%g_%g' % (eta_bins[0], eta_bins[-1]))
    output_f_hists = None
    if not output_f:
        output_f = outputfile.mkdir('eta_%g_%g' % (eta_bins[0], eta_bins[-1]))
        output_f_hists = output_f.mkdir("Histograms")
    else:
        output_f_hists = output_f.GetDirectory("Histograms")

    # Go through eta bins, get response hist, fit with Gaussian and add to
    # the overall graph
    for i, eta in enumerate(eta_bins[:-1]):
        absetamin = eta
        absetamax = eta_bins[i + 1] # Eta cut string

        # Cut strings
        eta_cutStr = "TMath::Abs(eta) < %f && TMath::Abs(eta) > %f" % (absetamax, absetamin)
        pt_cutStr = "%s < %g && %s > %g" % (pt_var, pt_max, pt_var, pt_min)
        pu_cutStr = "numPUVertices <= %f && numPUVertices >= %f" % (pu_max, pu_min)
        cutStr = " && ".join([eta_cutStr, pt_cutStr, pu_cutStr])
        print cutStr

        nb_rsp = 100
        rsp_min, rsp_max = 0, 5
        rsp_name = 'hrsp_eta_%g_%g_%s_%g_%g' % (absetamin, absetamax, pt_var, pt_min, pt_max)
        tree_raw.Draw("rsp>>%s(%d,%g,%g)" % (rsp_name, nb_rsp, rsp_min, rsp_max), cutStr)
        h_rsp = ROOT.gROOT.FindObject(rsp_name)
        h_rsp.SetTitle(";response (p_{T}^{L1}/p_{T}^{Ref});")

        print 'Integral', h_rsp.Integral()

        if h_rsp.Integral() <= 0:
            print "No entries - skipping"
            continue

        # Fit with Gaussian
        peak = h_rsp.GetBinCenter(h_rsp.GetMaximumBin())
        if absetamin < 2.9:
            fit_result = h_rsp.Fit("gaus", "QER", "",
                                   h_rsp.GetMean() - h_rsp.GetRMS(),
                                   h_rsp.GetMean() + h_rsp.GetRMS())
        else:
            fit_result = h_rsp.Fit("gaus", "QER", "",
                                   peak - (0.5 * h_rsp.GetRMS()),
                                   peak + (0.5 * h_rsp.GetRMS()))

        mean = h_rsp.GetMean()
        err = h_rsp.GetMeanError()

        check_fit = True
        if check_fit:
            if int(fit_result) == 0:
                mean = h_rsp.GetFunction("gaus").GetParameter(1)
                err = h_rsp.GetFunction("gaus").GetParError(1)
            else:
                print "cannot fit with Gaussian - using raw mean instead"

        output_f_hists.WriteTObject(h_rsp)

        # add to graph
        N = gr_rsp_eta.GetN()
        print absetamin, "-", absetamax, mean, err
        gr_rsp_eta.SetPoint(N, 0.5 * (absetamin + absetamax), mean)
        gr_rsp_eta.SetPointError(N, 0.5 * (absetamax - absetamin), err)

    gr_rsp_eta.SetTitle(";|#eta^{L1}|; <response> = <p_{T}^{L1}/p_{T}^{Ref}>")
    gr_rsp_eta.SetName("gr_rsp_eta_%g_%g_%s_%g_%g" % (eta_bins[0], eta_bins[-1], pt_var, pt_min, pt_max))
    output_f.WriteTObject(gr_rsp_eta)


def check_gaus_fit(hist):
    """Find peak of hist, check against fitted gaus"""
    s = ROOT.TSpectrum(1)
    s.Search(hist, 1, "new")
    peaks_buff = s.GetPositionX()
    x_peak = peaks_buff[0]

    return (abs(hist.GetFunction('gaus').GetParameter(1) - x_peak) / abs(x_peak)) < 0.1


def plot_rsp_pt(inputfile, outputfile, absetamin, absetamax, pt_bins, pt_var, pt_max, pu_min, pu_max):
    """Make a graph of response Vs pt for given eta bin

    pt_var allows the user to specify which pT to bin in & plot against.
    Should be the name of a variable in the tree
    pt_max is a cut on maxmimum value of pt (applied to l1 pt to
        avoid including saturation effects)
    """

    # Input tree
    tree_raw = inputfile.Get("valid")

    # Output folders
    output_f = outputfile.GetDirectory('eta_%g_%g' % (absetamin, absetamax))
    output_f_hists = None
    if not output_f:
        output_f = outputfile.mkdir('eta_%g_%g' % (absetamin, absetamax))
        output_f_hists = output_f.mkdir("Histograms")
    else:
        output_f_hists = output_f.GetDirectory("Histograms")

    gr_rsp_pt = ROOT.TGraphErrors()

    # Cut strings
    eta_cutStr = "TMath::Abs(eta) < %f && TMath::Abs(eta) > %f" % (absetamax, absetamin)
    # keep the pt < pt_max to safeguard against staurated L1 jets
    pt_cutStr = "%s < %g && pt < %g" % (pt_var, pt_bins[-1], pt_max)
    pu_cutStr = "numPUVertices <= %f && numPUVertices >= %f" % (pu_max, pu_min)
    cutStr = " && ".join([eta_cutStr, pt_cutStr, pu_cutStr])

    n_rsp_bins = 100
    rsp_min = 0
    rsp_max = 5

    pt_array = array('d', pt_bins)

    # First make a 2D plot
    h2d_rsp_pt = ROOT.TH2D("h2d_rsp_%s_%g_%g" % (pt_var, absetamin, absetamax),
                           "%g < |#eta| < %g;p_{T};response" % (absetamin, absetamax),
                           len(pt_bins) - 1, pt_array,
                           n_rsp_bins, rsp_min, rsp_max)
    tree_raw.Draw("rsp:%s>>h2d_rsp_%s_%g_%g" % (pt_var, pt_var, absetamin, absetamax), cutStr)

    output_f_hists.WriteTObject(h2d_rsp_pt)

    # Now for each pt bin, do a projection on 1D hist of response and fit a Gaussian
    print pt_bins
    for i, (pt_min, pt_max) in enumerate(pairwise(pt_bins)):
        h_rsp = h2d_rsp_pt.ProjectionY("rsp_%s_%g_%g" % (pt_var, pt_min, pt_max), i + 1, i + 1)
        print i, pt_min, pt_max

        if h_rsp.Integral() <= 0:
            print "No entries - skipping"
            continue

        # Fit with Gaussian
        mean = h_rsp.GetMean()
        err = h_rsp.GetMeanError()

        peak = h_rsp.GetBinCenter(h_rsp.GetMaximumBin())
        # if h_rsp.GetRMS() < 0.2:
        #    fit_result = h_rsp.Fit("gaus", "QER", "", peak - h_rsp.GetRMS(), peak + h_rsp.GetRMS())
        # else:
        # fit_result = h_rsp.Fit("gaus", "QER", "", peak - 0.5*h_rsp.GetRMS(), peak + 0.5*h_rsp.GetRMS())
        fit_result = h_rsp.Fit("gaus", "QER", "", peak - h_rsp.GetRMS(), peak + h_rsp.GetRMS())
        # fit_result = h_rsp.Fit("gaus", "QER", "", mean - h_rsp.GetRMS(), mean + h_rsp.GetRMS())

        output_f_hists.WriteTObject(h_rsp)

        # TODO: better check against Gaussian fit - are peaks ~ similar?
        # if int(fit_result) == 0 and check_gaus_fit(h_rsp):
        if int(fit_result) == 0 and abs(h_rsp.GetFunction("gaus").GetParameter(1) - peak) / peak < 0.1:
            mean = h_rsp.GetFunction("gaus").GetParameter(1)
            err = h_rsp.GetFunction("gaus").GetParError(1)
            # Add the Gaussian to the total graph
            N = gr_rsp_pt.GetN()
            gr_rsp_pt.SetPoint(N, 0.5 * (pt_min + pt_max), mean)
            gr_rsp_pt.SetPointError(N, 0.5 * (pt_max - pt_min), err)
        else:
            print "Cannot fit Gaussian in plot_rsp_pt, using raw mean instead"

    # Save the graph
    gr_rsp_pt.SetTitle("%g < |#eta^{L1}| < %g;p_{T}; <response> = <p_{T}^{L1}/p_{T}^{Ref}>" % (absetamin, absetamax))
    gr_rsp_pt.SetName("gr_rsp_%s_eta_%g_%g" % (pt_var, absetamin, absetamax))

    output_f.WriteTObject(gr_rsp_pt)


def main(in_args=sys.argv[1:]):
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
                        help="list of eta bin INDICES to run over - "
                        "if unspecified will do all. "
                        "This overrides --central/--forward. "
                        "Handy for batch mode. "
                        "IMPORTANT: MUST PUT AT VERY END")
    parser.add_argument("--maxPt", default=500, type=float,
                        help="Maximum pT for L1 Jets")
    parser.add_argument("--PUmin", default=-99, type=float,
                        help="Minimum number of PU vertices (refers to *actual* "
                             "number of PU vertices in the event, not the centre "
                             "of of the distribution)")
    parser.add_argument("--PUmax", default=999, type=float,
                        help="Maximum number of PU vertices (refers to *actual* "
                             "number of PU vertices in the event, not the centre "
                             "of of the distribution)")
    args = parser.parse_args(args=in_args)

    # Open input & output files, check
    input_file = cu.open_root_file(args.input, "READ")
    output_file = cu.open_root_file(args.output, "RECREATE")
    print "IN:", args.input
    print "OUT:", args.output
    if not input_file or not output_file:
        raise Exception("Input or output files cannot be opened")

    etaBins = binning.eta_bins
    if args.etaInd:
        args.etaInd.append(int(args.etaInd[-1]) + 1)  # need upper eta bin edge
        # check eta bins are ok
        etaBins = [etaBins[int(x)] for x in args.etaInd]
    elif args.central:
        etaBins = binning.eta_bins_central
    elif args.forward:
        etaBins = binning.eta_bins_forward
    print "Running over eta bins:", etaBins

    ptBins = binning.pt_bins
    ptBins = binning.pt_bins_stage2

    # Do plots for each eta bin
    if args.excl:
        for i, eta in enumerate(etaBins[:-1]):
            eta_min = eta
            eta_max = etaBins[i + 1]

            plot_checks(input_file, output_file, eta_min, eta_max, args.maxPt, args.PUmin, args.PUmax)
            # Do a response vs pt graph
            plot_rsp_pt(input_file, output_file, eta_min, eta_max, ptBins, "pt", args.maxPt, args.PUmin, args.PUmax)
            plot_rsp_pt(input_file, output_file, eta_min, eta_max, ptBins, "ptRef", args.maxPt, args.PUmin, args.PUmax)

    # Do an inclusive plot for all eta bins
    if args.incl and len(etaBins) > 2:
        plot_checks(input_file, output_file, etaBins[0], etaBins[-1], args.maxPt, args.PUmin, args.PUmax)
        # Do a response vs pt graph
        # ptBins_wide = list(np.arange(10, 250, 8))
        plot_rsp_pt(input_file, output_file, etaBins[0], etaBins[-1], ptBins, "pt", args.maxPt, args.PUmin, args.PUmax)
        plot_rsp_pt(input_file, output_file, etaBins[0], etaBins[-1], ptBins, "ptRef", args.maxPt, args.PUmin, args.PUmax)
        # Do a response vs eta graph, inclusive over all pt
        plot_rsp_eta(input_file, output_file, etaBins, 0, 1000, 'pt', args.PUmin, args.PUmax)

        # Sub-binned by pt
        for pt_min, pt_max in binning.check_pt_bins:
            plot_rsp_eta(input_file, output_file, etaBins, pt_min, pt_max, 'pt', args.PUmin, args.PUmax)
            plot_rsp_eta(input_file, output_file, etaBins, pt_min, pt_max, 'ptRef', args.PUmin, args.PUmax)

    input_file.Close()
    output_file.Close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
