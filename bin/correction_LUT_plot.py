#!/usr/bin/env python
"""
This script uses the correction functions from the ROOT file
output by runCalibration.py and:

- makes a LUT with them
- prints them in py/cpp format so the user can play with it
- makes various plots to check they are sensible

See options with python correction_LUT_plot.py -h

Robin Aggleton
"""

import ROOT
import sys
import numpy as np
from itertools import izip
import os
import argparse
import binning
import common_utils as cu
from runCalibration import generate_eta_graph_name, set_fit_params
from correction_LUT_GCT import print_GCT_lut_file
from correction_LUT_stage1 import print_Stage1_lut_file
from correction_LUT_stage2 import print_Stage2_lut_files, print_Stage2_func_file
from multifunc import MultiFunc
import csv
from pprint import pprint


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)


def get_functions_graphs_params_rootfile(root_filename):
    """Get function parameters from ROOT file

    Gets object based on name in runCalibration.py

    Parameters
    ----------
    root_filename : str
        Name of ROOT file to get things from

    Returns
    -------
    all_fits : list[TF1]
        Collection of TF1 objects, one per line of file ( = 1 eta bin)
    all_fit_params : list[list[float]]
        Collection of fit parameters, one per line of file ( = 1 eta bin)
    all_graphs : list[TGraphErrors]
        Colleciton of correction graphs, one per eta bin
    """
    print 'Reading functions from ROOT file'
    in_file = cu.open_root_file(root_filename)
    all_fit_params = []
    all_fits = []
    all_graphs = []
    # Get all the fit functions from file and their corresponding graphs
    etaBins = binning.eta_bins
    for i, (eta_min, eta_max) in enumerate(izip(etaBins[:-1], etaBins[1:])):
        print "Eta bin:", eta_min, "-", eta_max

        # get the fitted TF1
        try:
            fit_func = cu.get_from_file(in_file, "fitfcneta_%g_%g" % (eta_min, eta_max))
            fit_params = [fit_func.GetParameter(par) for par in range(fit_func.GetNumberFreeParameters())]
            print "Fit fn evaluated at 5 GeV:", fit_func.Eval(5)
        except IOError:
            print "No fit func"
            fit_func = None
            fit_params = []
        all_fits.append(fit_func)
        all_fit_params.append(fit_params)
        # print "Fit parameters:", fit_params

        # get the corresponding fit graph
        fit_graph = cu.get_from_file(in_file, generate_eta_graph_name(eta_min, eta_max))
        all_graphs.append(fit_graph)

    in_file.Close()
    return all_fits, all_fit_params, all_graphs


def get_functions_params_textfile(text_filename):
    """Get function parameters from textfile, create MultiFunc objects from them.

    IMPORTANT: if you change fit function, you **MUST** change this here!!!

    Parameters
    ----------
    text_filename : str
        Name of text file to get params from. Should be comma-separated,
        with one line per eta bin

    Returns
    -------
    all_fits : list[MultiFunc]
        Collection of MultiFunc objects, one per line of file ( = 1 eta bin)
    all_fit_params : list[list[float]]
        Collection of fit parameters, one per line of file ( = 1 eta bin)

    """
    print 'Reading functions from text file'
    with open(text_filename) as f:
        freader = csv.reader(f)
        all_fits = []
        all_fit_params = []
        for ind, row in enumerate(freader):
            nentries = 11
            if len(row) != nentries:
                raise IndexError('Row must have %d rows' % nentries)
            # construct MultiFunc object from fit params
            row = [float(f.strip()) for f in row]
            all_fit_params.append(row)
            low_plateau = row[7]
            low_plateau_end = row[8]
            low_plateau_fn = ROOT.TF1("lower_%d" % ind, "%f" % low_plateau, 0, low_plateau_end)

            high_plateau = row[9]
            high_plateau_start = row[10]
            high_plateau_fn = ROOT.TF1("higher_%d" % ind, "%f" % high_plateau, high_plateau_start, 1024)

            main_fn = ROOT.TF1("fitfcn_%d" % ind, "[0]+[1]*TMath::Erf([2]*(log10(x)-[3])+[4]*exp([5]*(log10(x)-[6])*(log10(x)-[6])))")
            main_fn.SetRange(low_plateau_end, high_plateau_start)
            set_fit_params(main_fn, row[0:7])

            fn = MultiFunc({
                (0, low_plateau_end): low_plateau_fn,
                (low_plateau_end, high_plateau_start): main_fn,
                (high_plateau_start, 1024): high_plateau_fn
            })
            all_fits.append(fn)

        return all_fits, all_fit_params


def plot_correction_map(corr_fn, filename="correction_map.pdf"):
    """Make plot of pt before Vs after to show mapping"""

    # jet pTs, pre calibration
    min_pre = 0
    max_pre = 52
    jet_pt_pre = np.arange(min_pre, max_pre, 0.5)

    # Post calibration
    jet_pt_post = np.array([pt * corr_fn.Eval(pt) for pt in jet_pt_pre])

    # Make coloured blocks to show the L1 pT bins
    blocks = []  # for persistence otherwise garbabe collected
    gct_bins = np.arange(4, 16 + (18 * 4), 4)
    for i, pt in enumerate(gct_bins):
        if (pt + 4) < jet_pt_post[0] or pt > jet_pt_post[-1]:
            continue
        b = ROOT.TBox(min_pre, pt, max_pre, pt + 4)
        col = 30 if i % 2 else 38
        b.SetFillColor(col)
        b.SetLineStyle(0)
        blocks.append(b)

    # Plot
    c = ROOT.TCanvas("c", "", 800, 800)
    c.SetTicks(1, 1)
    c.SetGrid(1, 1)
    gr = ROOT.TGraph(len(jet_pt_pre), jet_pt_pre, jet_pt_post)
    gr.SetMarkerColor(ROOT.kRed)
    gr.SetTitle("Input jets at 0.5 GeV intervals;p_{T}^{pre};p_{T}^{post}")
    gr.SetMarkerStyle(2)
    gr.Draw("AP")
    for bl in blocks:
        bl.Draw()
    gr.Draw("P")

    # Some helpful lines
    def draw_lines(pt):
        lx = ROOT.TLine(pt, gr.GetYaxis().GetXmin(), pt, pt * corr_fn.Eval(pt))
        lx.SetLineStyle(2)
        lx.Draw()
        ly = ROOT.TLine(0, pt * corr_fn.Eval(pt), pt, pt * corr_fn.Eval(pt))
        ly.SetLineStyle(2)
        ly.Draw()
    draw_lines(5)
    draw_lines(30)
    c.SaveAs(filename)


def plot_graph_function(eta_index, graph, function, filename):
    """Plot both graph and function on the same canvas. Useful for fancy fits.

    Parameters
    ----------
    eta_index: int
        Which eta bin this plot refers to, just for labelling

    graph: TGraphErrors
        Graph to be plotted

    function: MultiFunc
        Function to be drawn

    filename: str
        Path & filename for plot
    """
    c = ROOT.TCanvas("c%d" % eta_index, "SCREW ROOT", 800, 600)
    c.SetTicks(1, 1)
    graph.Draw("ALP")
    y_ax = graph.GetYaxis()
    y_ax.SetRangeUser(0.9 * y_ax.GetXmin(), 1.1 * y_ax.GetXmax())
    graph.SetTitle("%g < #eta^{L1} < %g" % (binning.eta_bins[eta_index], binning.eta_bins[eta_index + 1]))
    # Print the functions in a text box
    text = ROOT.TPaveText(0.2, 0.7, 0.88, 0.88, "NDC NB")
    # TPaveText ignores \n, sigh...
    for line in str(function).split("\n"):
        text.AddText(line)
    text.SetFillColor(ROOT.kWhite)
    text.SetFillStyle(0)
    text.SetLineStyle(0)
    text.Draw()
    if function:
        function.Draw('SAME')
    graph.GetXaxis().SetLimits(0, 250)

    # y_ax.SetRangeUser(0.5, ROOT.TMath.MaxElement(graph.GetN(), graph.GetY()) * 1.2)
    y_ax.SetRangeUser(0.5, 3)
    c.SaveAs(filename)


def plot_all_graph_functions(graphs, functions, filename):
    """Plot both graph and function on the same canvas. Useful for fancy fits.

    Parameters
    ----------
    eta_index: int
        Which eta bin this plot refers to, just for labelling

    graph: TGraphErrors
        Graph to be plotted

    function: MultiFunc
        Function to be drawn

    filename: str
        Path & filename for plot
    """
    c = ROOT.TCanvas("c", "SCREW ROOT", 800, 600)
    c.SetTicks(1, 1)
    eta_bin_colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen + 2, ROOT.kBlack,
                      ROOT.kMagenta, ROOT.kOrange + 7, ROOT.kAzure + 1,
                      ROOT.kRed + 3, ROOT.kViolet + 1, ROOT.kOrange, ROOT.kTeal - 5]
    leg = ROOT.TLegend(0.7, 0.7, 0.88, 0.88)
    if graphs and not functions:
        functions = [None] * len(graphs)
    elif functions and not graphs:
        graphs = [None] * len(functions)
    elif not graphs and not functions:
        raise RuntimeError("Neither graphs nor functions - can't plot")

    for eta_index, (gr, fn) in enumerate(zip(graphs, functions)):
        col = eta_bin_colors[eta_index]
        if gr:
            gr.SetLineColor(col)
            gr.SetMarkerColor(col)
            gr.SetTitle('')
            if eta_index == 0:
                gr.Draw("ALP")
            else:
                gr.Draw("LP SAME")
            y_ax = gr.GetYaxis()
            y_ax.SetRangeUser(0.5, 3)
            leg.AddEntry(gr, "eta ind %d" % eta_index, "LP")
            gr.GetXaxis().SetLimits(0, 250)
        if fn:
            fn.SetLineColor(col)
            if eta_index == 0 and not gr:
                fn.Draw()
            else:
                fn.Draw("SAME")
            if not gr:
                leg.AddEntry(fn.functions_dict.values()[0], "eta ind %d" % eta_index, "L")
    leg.Draw()
    c.SaveAs(filename)


def do_constant_hf_fits(fits, graphs, plot_dir):
    """Do constant correction factor fits for HF bins.

    Also makes plots to check procedure.

    Parameters
    ----------
    fits : list[TF1]
        List of fit functions, one per eta bin.
    graphs : list[TGraph]
        List of graphs, one per eta bin.
    plot_dir : str
        Directory to put plots

    Returns
    -------
    list[TF1]
    """
    new_functions = []
    for i, (fit, gr) in enumerate(zip(fits, graphs)):
        print "Eta bin", str(i)
        if (i >= len(binning.eta_bins_central) - 1):
            new_fn = do_constant_fit(gr, binning.eta_bins[i], binning.eta_bins[i+1], plot_dir)
            new_functions.append(new_fn)
        else:
            new_functions.append(fit)
    return new_functions


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


def do_low_pt_plateau_fits(fits, graphs, ignore_hf, condition=0.1, look_ahead=4):
    """Do low PT plateau fits for graphs.

    Parameters
    ----------
    fits : list[TF1]
        List of fit functions, one per eta bin.
    graphs : list[TGraph]
        List of graphs, one per eta bin.
    ignore_hf : bool
        Do not apply to HF bins, returns original fit function instead
    condition : float
        Absolute difference between graph & curve to determine where curve
        becomes a constant value.
    look_ahead : int, optional
        Number of lower points to also consider when calculating
        where plateau should occur

    Returns
    -------
    list[MultiFunc, TF1]
        MultiFunc if capped rpocdure used, TF1 if not.
    """
    new_functions = []
    for i, (fit, gr) in enumerate(zip(fits, graphs)):
        print "Eta bin", str(i)
        if (i >= len(binning.eta_bins_central) - 1) and ignore_hf:
            new_functions.append(fit)
        else:
            new_fn = do_low_pt_plateau_fit(fit, gr, condition, look_ahead)
            new_functions.append(new_fn)
    return new_functions


def do_low_pt_plateau_fit(fit, graph, condition=0.1, look_ahead=4):
    """Make low pt plateau fit, by checking for deviations between graph and fit at low pT.
    Then below the pT where they differ, just use the last good correction
    factor as a constant correction factor.

    This decision can also take lower pT point into account to avoid breaking
    early due to fluctuations (see `look_ahead` arg)

    This generates a new set of correction functions, represented by MultiFunc objects.

    Parameters
    ----------
    fits : list[TF1]
        List of fit functions, one per eta bin.
    graphs : list[TGraph]
        List of graphs, one per eta bin.
    condition : float
        Absolute difference between graph & curve to determine where curve
        becomes a constant value.
    look_ahead : int, optional
        Number of lower points to also consider when calculating
        where plateau should occur

    Returns
    -------
    MultiFunc

    """
    print "Making fancy fit, using condition %f with look-ahead %d" % (condition, look_ahead)

    x_arr, y_arr = cu.get_xy(graph)

    pt_merge, corr_merge = 0, 0

    for j, (pt, corr) in enumerate(izip(x_arr[::-1], y_arr[::-1])):
        # Loop through each point of the graph in reverse,
        # only considering points with pt < 40.
        # Determine where the function and graph separate by
        # looking at the difference.
        if pt > 40:
            continue

        def get_nth_lower_point(n):
            """Return the nth lower point (x, y).
            eg n=1 returns the next lowest graph x,y"""
            return x_arr[len(x_arr) - 1 - j - n], y_arr[len(y_arr) - 1 - j - n]

        # Test the next N lowest point(s) to see if they also fulfills condition.
        # This stops a random fluctation from making the plateau too low
        # We require that all the Nth lower points also fail the condition.
        lower_points = [get_nth_lower_point(x) for x in range(1, 1 + look_ahead)]
        lower_fit_vals = [fit.Eval(x[0]) for x in lower_points]
        lower_conditions = [abs(x[1] - y) > condition for x, y in zip(lower_points, lower_fit_vals)]
        if all(lower_conditions):
            break
        else:
            pt_merge = pt
            corr_merge = fit.Eval(pt)

    print "pt_merge:", pt_merge, "corr fn value:", fit.Eval(pt_merge)

    # Make our new 'frankenstein' function: constant for pt < pt_merge,
    # then the original function for pt > pt_merge
    constant = ROOT.TF1("constant", "[0]", 0, pt_merge)
    constant.SetParameter(0, corr_merge)

    function_str = "[0]+[1]/(pow(log10(x),2)+[2])+[3]*exp(-[4]*(log10(x)-[5])*(log10(x)-[5]))"
    fit_new = ROOT.TF1("fitfcn", function_str, pt_merge * 0.75, 1024)
    for p in xrange(fit.GetNumberFreeParameters()):
        fit_new.SetParameter(p, fit.GetParameter(p))
    # set lower range below pt_merge just for drawing purposes - MultiFunc ignores it

    # add a constant above 1023.5 as truncated there
    constant_highpT = ROOT.TF1("constant_highpT", "[0]", 1023.5, ((2**16) - 1) * 0.5)
    constant_highpT.SetParameter(0, fit_new.Eval(1023.5))

    # Make a MultiFunc object to handle the different functions operating
    # over different ranges since TF1 can't do this.
    # Maybe ROOFIT can?
    functions_dict = {(0, pt_merge): constant,
                      (pt_merge, 1023.5): fit_new,
                      (1023.4, np.inf): constant_highpT}
    total_fit = MultiFunc(functions_dict)
    return total_fit


def plot_all_functions(functions, filename, eta_bins, et_min=0, et_max=30):
    """Draw all corrections functions on one big canvas"""
    nrows = 4
    ncols = ((len(binning.eta_bins) - 1) / nrows)
    canv = ROOT.TCanvas("canv", "", 800 * ncols, 800 * nrows)
    canv.Divide(ncols, nrows)

    # vertical line to intersect graph at a certain pT
    vert_line = ROOT.TLine(5, 0, 5, 3)
    vert_line.SetLineStyle(3)
    vert_line.SetLineWidth(1)

    # horizontal line to intersect graph
    hori_line = ROOT.TLine(et_min, 2, et_max, 2)
    hori_line.SetLineStyle(3)

    for i, fit_func in enumerate(functions):
        canv.cd(i + 1)
        if not fit_func:
            continue
        if isinstance(fit_func, ROOT.TF1):
            fit_func.SetRange(et_min, et_max)
        fit_func.SetTitle("%g - %g" % (eta_bins[i], eta_bins[i + 1]))
        fit_func.SetLineWidth(1)
        if isinstance(fit_func, MultiFunc):
            fit_func.Draw(draw_range=[et_min, et_max])
        else:
            fit_func.Draw()
        # corr_5 = fit_func.Eval(5)
        # vert_line.SetY1(-15)
        # vert_line.SetY2(15)
        # vert_line.Draw()
        # l2 = hori_line.Clone()
        # l2.SetY1(corr_5)
        # l2.SetY2(corr_5)
        # l2.Draw("SAME")
        ROOT.gPad.SetTicks(1, 1)
        ROOT.gPad.SetGrid(1, 1)

    canv.SaveAs(filename)


def main(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=cu.CustomFormatter)
    parser.add_argument("input",
                        help="input ROOT/txt filename")
    parser.add_argument("lut",
                        help="output LUT filename",
                        default="my_lut.txt")
    parser.add_argument("--text",
                        help="Read correction functions from text file instead of ROOT file",
                        action='store_true')
    parser.add_argument("--gct",
                        help="Make LUT for GCT",
                        action='store_true')
    parser.add_argument("--stage1",
                        help="Make LUT for Stage 1",
                        action='store_true')
    parser.add_argument("--stage2",
                        help="Make LUT for Stage 2",
                        action='store_true')
    parser.add_argument("--stage2Func",
                        help="Make function params file for Stage 2",
                        action='store_true')
    parser.add_argument("--lowPtPlateau",
                        help="This checks for low pT turnover and caps the correction "
                        "value below that to a constant factor.",
                        action='store_true')
    parser.add_argument("--constantHF",
                        help="This calculates a constant correciton factor for HF bins.",
                        action='store_true')
    parser.add_argument("--plots",
                        help="Make plots to check sensibility of correction functions.",
                        action='store_true')
    parser.add_argument("--ptCompressionFile",
                        help="Human-readable pT compression LUT to use instead of deriving one  (Stage 2 only)",
                        default=None)
    args = parser.parse_args(args=in_args)

    print args

    if not any([args.gct, args.stage1, args.stage2, args.stage2Func]):
        print "You didn't pick which trigger version for the corrections - not making a corrections file unless you choose!"
        exit()

    out_dir = os.path.join(os.path.dirname(args.input),
                           os.path.splitext(os.path.basename(args.lut))[0])
    cu.check_dir_exists_create(out_dir)

    all_fit_params = []
    all_fits = []
    all_graphs = []

    if args.text:
        all_fits, all_fit_params = get_functions_params_textfile(args.input)
    else:
        all_fits, all_fit_params, all_graphs = get_functions_graphs_params_rootfile(args.input)

    # Check we have the correct number
    etaBins = binning.eta_bins
    if len(all_fits) + 1 != len(etaBins):
        raise Exception("Incorrect number of fit functions "
                        "for corresponding number of eta bins")
    if len(all_fit_params) + 1 != len(etaBins):
        raise Exception("Incorrect number of fit params "
                        "for corresponding number of eta bins")

    # Plot all functions on one canvas, zommed in on low pt & whole pt range
    plot_file = os.path.join(out_dir, "all_raw_fits_ptZoomed.pdf")
    plot_all_functions(all_fits, plot_file, etaBins, et_min=0, et_max=30)
    plot_file = os.path.join(out_dir, "all_raw_fits.pdf")
    plot_all_functions(all_fits, plot_file, etaBins, et_min=0, et_max=1024)

    # Make LUTs
    if args.gct:
        print_GCT_lut_file(all_fit_params, etaBins, args.lut)

    elif args.stage1:
        fits = do_low_pt_plateau_fits(all_fits, all_graphs, ignore_hf=False, condition=0.05, look_ahead=0) if args.lowPtPlateau else all_fits

        if args.plots:
            # plot the fancy fits
            for i, (total_fit, gr) in enumerate(izip(fits, all_graphs)):
                plot_file = os.path.join(out_dir, "fancyfit_%d.pdf" % i)
                plot_graph_function(i, gr, total_fit, plot_file)
        print_Stage1_lut_file(fits, args.lut, args.plots)

    elif args.stage2 or args.stage2Func:
        # do fancy fits: low Pt cap, and/or constant HF
        fits = all_fits
        if args.lowPtPlateau:
            fits = do_low_pt_plateau_fits(fits, all_graphs, ignore_hf=True, condition=0.075, look_ahead=5)
        if args.constantHF:
            fits = do_constant_hf_fits(fits, all_graphs, plot_dir=out_dir)
        if args.plots:
            # plot the fancy fits
            if not args.text:
                for i, (total_fit, gr) in enumerate(izip(fits, all_graphs)):
                    plot_file = os.path.join(out_dir, "fancyfit_%d.pdf" % i)
                    plot_graph_function(i, gr, total_fit, plot_file)
                plot_all_graph_functions(all_graphs, fits, os.path.join(out_dir, "fancyfit_all.pdf"))
                plot_all_graph_functions(all_graphs, None, os.path.join(out_dir, "fancyfit_all_gr.pdf"))
                plot_all_graph_functions(None, fits, os.path.join(out_dir, "fancyfit_all_fn.pdf"))

        if args.stage2:
            lut_base, ext = os.path.splitext(os.path.basename(args.lut))
            eta_lut_filename = os.path.join(out_dir, lut_base + '_eta' + ext)
            pt_lut_filename = os.path.join(out_dir, lut_base + '_pt' + ext)
            mult_lut_filename = os.path.join(out_dir, lut_base + "_mult" + ext)
            add_lut_filename = os.path.join(out_dir, lut_base + "_add" + ext)
            add_mult_lut_filename = os.path.join(out_dir, lut_base + "_add_mult" + ext)
            print_Stage2_lut_files(fit_functions=fits,
                                   eta_lut_filename=eta_lut_filename,
                                   pt_lut_filename=pt_lut_filename,
                                   mult_lut_filename=mult_lut_filename,
                                   add_lut_filename=add_lut_filename,
                                   add_mult_lut_filename=add_mult_lut_filename,
                                   right_shift=9,
                                   num_corr_bits=10,
                                   num_add_bits=8,
                                   plot_dir=out_dir,
                                   # read_pt_compression='lut_pt_compress.txt'
                                   read_pt_compression=args.ptCompressionFile,
                                   target_num_pt_bins=2**4,
                                   merge_criterion=1.05,
                                   merge_algorithm='greedy')  # greedy or kmeans
        else:
            print_Stage2_func_file(fits, args.lut)

    # if args.plots:
    #     # Plot function mapping
    #     for i, (eta_min, eta_max, fit_func) in enumerate(izip(etaBins[:-1], etaBins[1:], fits)):
    #         if fit_func:
    #             plot_file = os.path.join(out_dir, "correction_map_%g_%g.pdf" % (eta_min, eta_max))
    #             plot_correction_map(fit_func, plot_file)



if __name__ == "__main__":
    main()
