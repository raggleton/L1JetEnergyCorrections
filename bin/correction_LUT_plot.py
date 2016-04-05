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
from runCalibration import generate_eta_graph_name
from correction_LUT_GCT import print_GCT_lut_file
from correction_LUT_stage1 import print_Stage1_lut_file
from correction_LUT_stage2 import print_Stage2_lut_files, print_Stage2_func_file, do_constant_fit
from multifunc import MultiFunc


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
ROOT.gStyle.SetOptFit(1111)
ROOT.TH1.SetDefaultSumw2(True)


def print_function_code(function, lang="cpp"):
    """Print TF1 to screen so can replicate in ROOT or numpy

    Can choose language (py, cpp, numpy)
    """

    rangemin = ROOT.Double()  # eurghhhhh - fixes pass by reference
    rangemax = ROOT.Double()
    function.GetRange(rangemin, rangemax)
    params = [function.GetParameter(i) for i in range(function.GetNumberFreeParameters())]
    name = function.GetName().replace(".", "p")

    print ""

    if lang.lower() == "py" or lang.lower() == "cpp":
        if lang.lower() == 'py':
            print "import ROOT"
            print '%s = ROOT.TF1("%s", "%s", %g, %g);' % (name, name, function.GetExpFormula(), rangemin, rangemax)
        elif lang.lower() == 'cpp':
            print 'TF1 %s("%s", "%s", %g, %g);' % (name, name, function.GetExpFormula(), rangemin, rangemax)
        for i, param in enumerate(params):
            print "%s.SetParameter(%d, %.8f)" % (name, i, param)
    elif lang.lower() == "numpy":
        print "import numpy as np"
        print "import matplotlib.pyplot as plt"
        print "et = np.arange(%g, %g, 0.1)" % (0, 250)
        for i, param in enumerate(params):
            print "p%d = %.8f" % (i, param)
        print "def pf_func(et, p0, p1, p2, p3, p4, p5):"
        print "    return p0 + (p1/(np.power(np.log10(et), 2)+p2)) + p3 * np.exp(-1.*p4*np.power(np.log10(et)-p5, 2))"
        print ""
        print ""
        print "plt.plot(et, pf_func(et, p0, p1, p2, p3, p4, p5), lw=2, color='red')"
        print "plt.xlabel(r'$E_T$');plt.ylabel('Correction Factor')"
        print "plt.show()"
        # print "plt.savefig('plot.pdf')"

    print ""


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


def do_fancy_fits(fits, graphs, const_hf, condition=0.1, look_ahead=4, plot_dir=None):
    """Do fancy plateau/constant fits for graphs. """
    new_functions = []
    for i, (fit, gr) in enumerate(zip(fits, graphs)):
        print "Eta bin", str(i)
        if (i >= len(binning.eta_bins_central) - 1) and const_hf:
            new_fn = do_constant_fit(gr, binning.eta_bins[i], binning.eta_bins[i+1], plot_dir)
            new_functions.append(new_fn)
        else:
            new_fn = do_fancy_fit(fit, gr, condition, look_ahead)
            new_functions.append(new_fn)
    return new_functions


def do_fancy_fit(fit, graph, condition=0.1, look_ahead=4):
    """
    Make fancy fit, by checking for deviations between graph and fit at low pT.
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
    canv = ROOT.TCanvas("canv", "", 3800, 1200)
    nrows = 2
    ncols = ((len(binning.eta_bins) - 1) / nrows) + 1
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
        fit_func.SetRange(et_min, et_max)
        fit_func.SetLineWidth(1)
        fit_func.SetTitle("%g - %g" % (eta_bins[i], eta_bins[i + 1]))
        fit_func.Draw()
        corr_5 = fit_func.Eval(5)
        vert_line.SetY1(-15)
        vert_line.SetY2(15)
        ROOT.gPad.SetTicks(1, 1)
        ROOT.gPad.SetGrid(1, 1)
        vert_line.Draw()
        l2 = hori_line.Clone()
        l2.SetY1(corr_5)
        l2.SetY2(corr_5)
        l2.Draw("SAME")

    canv.SaveAs(filename)


def main(in_args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=cu.CustomFormatter)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("lut", help="output LUT filename", default="my_lut.txt")
    parser.add_argument("--gct", help="Make LUT for GCT", action='store_true')
    parser.add_argument("--stage1", help="Make LUT for Stage 1", action='store_true')
    parser.add_argument("--stage2", help="Make LUT for Stage 2", action='store_true')
    parser.add_argument("--stage2Func", help="Make function params file for Stage 2", action='store_true')
    parser.add_argument("--fancy", help="Make fancy LUT. "
                        "This checks for low pT deviations and caps the correction value",
                        action='store_true')
    parser.add_argument("--plots", help="Make plots to check sensibility of correction functions.",
                        action='store_true')
    parser.add_argument("--cpp", help="print ROOT C++ code to screen", action='store_true')
    parser.add_argument("--python", help="print PyROOT code to screen", action='store_true')
    parser.add_argument("--numpy", help="print numpy code to screen", action='store_true')
    args = parser.parse_args(args=in_args)

    print args

    if not any([args.gct, args.stage1, args.stage2, args.stage2Func]):
        print "You didn't pick which format for the corrections - not making a corrections file unless you choose!"
        exit()

    in_file = cu.open_root_file(args.input)
    out_dir = os.path.join(os.path.dirname(args.input),
                           os.path.splitext(os.path.basename(args.lut))[0])

    cu.check_dir_exists_create(out_dir)

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

        # Print function to screen
        if args.cpp:
            print_function_code(fit_func, "cpp")
        if args.python:
            print_function_code(fit_func, "py")
        if args.numpy:
            print_function_code(fit_func, "numpy")

    # Check we have the correct number
    if len(all_fits) + 1 != len(etaBins) or len(all_fit_params) + 1 != len(etaBins):
        raise Exception("Incorrect number of fit functions/sets of parameters "
                        "for corresponding number of eta bins")

    # Plot all functions on one canvas, zommed in on low pt & whole pt range
    plot_file = os.path.join(out_dir, "all_raw_fits_ptZoomed.pdf")
    plot_all_functions(all_fits, plot_file, etaBins, et_min=0, et_max=30)
    plot_file = os.path.join(out_dir, "all_raw_fits.pdf")
    plot_all_functions(all_fits, plot_file, etaBins, et_min=0, et_max=1024)
    fits = all_fits

    # Make LUTs
    if args.gct:
        print_GCT_lut_file(all_fit_params, etaBins, args.lut)

    elif args.stage1:
        fits = do_fancy_fits(all_fits, all_graphs, const_hf=False, condition=0.05, look_ahead=0) if args.fancy else all_fits

        if args.plots:
            # plot the fancy fits
            for i, (total_fit, gr) in enumerate(izip(fits, all_graphs)):
                plot_file = os.path.join(out_dir, "fancyfit_%d.pdf" % i)
                plot_graph_function(i, gr, total_fit, plot_file)
        print_Stage1_lut_file(fits, args.lut, args.plots)

    elif args.stage2 or args.stage2Func:
        # do fancy fits, can do constant values only for HF
        fits = do_fancy_fits(all_fits, all_graphs, const_hf=True, condition=0.075, look_ahead=5, plot_dir=out_dir) if args.fancy else all_fits
        if args.plots:
            # plot the fancy fits
            for i, (total_fit, gr) in enumerate(izip(fits, all_graphs)):
                plot_file = os.path.join(out_dir, "fancyfit_%d.pdf" % i)
                plot_graph_function(i, gr, total_fit, plot_file)
            plot_all_graph_functions(all_graphs, fits, os.path.join(out_dir, "fancyfit_all.pdf"))
            plot_all_graph_functions(all_graphs, None, os.path.join(out_dir, "fancyfit_all_gr.pdf"))
            plot_all_graph_functions(None, fits, os.path.join(out_dir, "fancyfit_all_fn.pdf"))

        if args.stage2:
            lut_base, ext = os.path.splitext(args.lut)
            eta_lut_filename = lut_base + '_eta' + ext
            pt_lut_filename = lut_base + '_pt' + ext
            corr_lut_filename = lut_base + "_corr" + ext
            corr_add_lut_filename = lut_base + "_add" + ext
            print_Stage2_lut_files(fit_functions=fits,
                                   eta_lut_filename=eta_lut_filename,
                                   pt_lut_filename=pt_lut_filename,
                                   corr_lut_filename=corr_lut_filename,
                                   corr_add_lut_filename=corr_add_lut_filename,
                                   right_shift=9,
                                   num_corr_bits=10,
                                   target_num_pt_bins=2**4,
                                   merge_criterion=1.05,
                                   plot_dir=out_dir)
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
