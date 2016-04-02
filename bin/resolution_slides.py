#!/usr/bin/env python
"""
This script outputs all the resolution plots in the ROOT file output by
makeResolutionPlots.py as one long pdf, cos TBrowser sucks.
"""

import ROOT as r
import sys
import os
import numpy
import argparse
import numpy
from itertools import izip
import subprocess
import binning
import beamer_slide_templates as bst


r.PyConfig.IgnoreCommandLineOptions = True
r.gROOT.SetBatch(1)


ptBins = binning.pt_bins_8[20:]
# etaBins = [binning.eta_bins[0], binning.eta_bins[-1]]
etaBins = binning.eta_bins_central
print etaBins


def open_root_file(filename):
    """
    Safe way to open ROOT file. Could be improved.
    """
    f = r.TFile(filename)
    if f.IsZombie():
        raise RuntimeError("Can't open file %s" % filename)
    return f


def check_dir_exists(d):
    """
    Check directory exists. If not, make it.
    """
    opath = os.path.abspath(d)
    if not os.path.isdir(opath):
        os.makedirs(opath)


def plot_to_file(infile, plotname, outfilename, xtitle="", ytitle="", xlim=None, ylim=None, drawfit=True, drawopts="", col=""):
    """
    Save plot to file (tex, png, pdf...)
    infile is a TFile
    plotname is the name of the plot in the file (incl. any directories)
    outfilename is output, can be a list of filenames (e.g. for .tex, .pdf, .png)
    Can optionally not draw the fit to the curve
    Can also provide draw options, and axis titles and limits (each as pair of values)
    """
    r.gStyle.SetPaperSize(10.,10.)
    r.gStyle.SetOptStat("mre")
    if "Diff:" in plotname:
        r.gStyle.SetOptStat(0)
        r.gStyle.SetOptFit(0)
    else:
        r.gStyle.SetOptFit(1111)
    try:
        plt = (infile.Get(plotname).Clone())
        plt.GetXaxis().SetTitle(xtitle)
        # plt.GetXaxis().SetTitleSize(0.06)
        # plt.GetXaxis().SetLabelSize(0.06)
        plt.GetYaxis().SetTitle(ytitle)
        # plt.GetYaxis().SetTitleSize(0.06)
        # plt.GetYaxis().SetLabelSize(0.06)
        plt.SetTitle("")
        plt.SetMarkerSize(0.5)
        plt.Draw(drawopts)
        if xlim:
            plt.GetXaxis().SetRangeUser(xlim[0], xlim[1])
        if ylim:
            plt.SetMaximum(ylim[1])
            plt.SetMinimum(ylim[0])
        if col != "":
            plt.SetLineColor(col)
            plt.SetMarkerColor(col)
            plt.SetFillColor(col)
        if plotname.startswith("res"):
            plt.GetXaxis().SetRangeUser(-2, 4)
        r.gPad.Update()
        # if plt.GetMaximum() > 5:
        #     plt.SetMaximum(5)
        # # if plt.GetMinimum() < 5:
        #     # plt.SetMinimum(-5)
        # if not drawfit:
        #     r.gStyle.SetOptFit(0)
        #     plt.GetListOfFunctions().Remove(plt.GetListOfFunctions().At(0))
        # plt.Draw(drawopts)

        # if plotname.startswith("res"):
        st = plt.FindObject("stats")
        st.SetX1NDC(0.12)
        st.SetX2NDC(0.35)
        for f in outfilename:
            r.gPad.Print(f)
        r.gPad.Clear()
    except ReferenceError:
        print "Cannot get plot %s" % (plotname)
        exit()


def multiplot_to_file(plots, outfilename, xtitle="", ytitle="", xlim=None, ylim=None, drawfit=True, drawopts=""):
    """
    Put multiple plots on same canvas and save to file
    plots is a list of dicts, each with entries for TFile, name of plot in file, colour, legend text and legend style
    e.g. {'infile': file.root, 'plotname': 'hist1', 'color': r.kRed, 'legend_text': "My hist", 'legend_style': "F"}

    outfilename is output, can be a list of filenames (e.g. for .tex, .pdf, .png)
    Can optionally not draw the fit to the curve
    Can also provide draw options, and axis titles and limits (each as pair of values)
    """
    r.gStyle.SetPaperSize(10.,10.)
    r.gStyle.SetOptStat("mre")
    r.gStyle.SetOptFit(1111)

    container = None
    leg = r.TLegend(0.6, 0.7, 0.88, 0.88)

    for plot in plots:
        try:
            plt = (plot["infile"].Get(plot["plotname"]).Clone())
            # setup container depending on type
            if not container:
                hists = ["TH1", "TH2"]
                graphs = ["TGraph", "TGraphErrors", "TGraphAsymmErrors"]
                if type(plt).__name__ in hists:
                    container = r.THStack("hstack")
                elif type(plt).__name__ in graphs:
                    container = r.TMultiGraph()
            plt.GetXaxis().SetTitle(xtitle)
            plt.GetXaxis().SetTitleSize(0.06)
            plt.GetXaxis().SetLabelSize(0.06)
            plt.GetYaxis().SetTitle(ytitle)
            plt.GetYaxis().SetTitleSize(0.06)
            plt.GetYaxis().SetLabelSize(0.06)
            plt.SetTitle("")
            plt.SetMarkerSize(0.5)
            if xlim:
                plt.GetXaxis().SetRangeUser(xlim[0], xlim[1])
            if ylim:
                plt.SetMaximum(ylim[1])
                plt.SetMinimum(ylim[0])
            if "color" in plot.keys():
                col = plot["color"]
                if col != "":
                    plt.SetLineColor(col)
                    plt.SetMarkerColor(col)
                    plt.SetFillColor(col)
            container.Add(plt)
            leg_txt = plot["legend_text"] if "legend_text" in plot.keys() else ""
            leg_sty = plot["legend_style"] if "legend_style" in plot.keys() else ""
            if leg_txt != "":
                leg.AddEntry(plt, leg_txt, leg_sty)
        except ReferenceError:
            print "Cannot get plot %s from file %s" % (plot["plotname"], plot["infile"].GetName())
            exit()
    if container:
        container.Draw(drawopts)
        container.GetXaxis().SetTitle(xtitle)
        container.GetXaxis().SetTitleSize(0.06)
        container.GetXaxis().SetLabelSize(0.06)
        container.GetYaxis().SetTitle(ytitle)
        container.GetYaxis().SetTitleSize(0.06)
        container.GetYaxis().SetLabelSize(0.06)
        if xlim:
            container.GetXaxis().SetRangeUser(xlim[0], xlim[1])
        if ylim:
            container.GetYaxis().SetRangeUser(ylim[0], ylim[1])
        container.Draw(drawopts)
        if leg.GetNRows() != 0:
            leg.Draw()
        for f in outfilename:
            r.gPad.Print(f)
        r.gPad.Clear()
    else:
        raise Exception("couldn't add plots to container")

def plot_res_results(in_name_pre="", in_name_post=""):
    """
    Put resolution plot for each eta bin in one pdf.
    If in_name_post is specified, it will plot the graphs on the
    same canvas for ease of comparison.
    """

    # Setup input file (pre calib)
    print "Opening", in_name_pre
    in_stem_pre = os.path.basename(in_name_pre).replace(".root", "")
    input_file_pre = open_root_file(in_name_pre)

    # Setup input file (post calib)
    mode = ""
    if in_name_post:
        print "Opening", in_name_post
        in_stem_post = os.path.basename(in_name_post).replace(".root", "")
        input_file_post = open_root_file(in_name_post)
        mode = "_compare"
    else:
        print "Not opening post file"

    # Setup output directory & filenames
    odir = os.path.dirname(os.path.abspath(in_name_pre))+"/"+in_stem_pre+mode+"/"
    check_dir_exists(odir)

    out_name = odir+in_stem_pre+mode+".pdf"
    out_stem = out_name.replace(".pdf","")
    print "Writing to", out_name

    # Start beamer file
    # Use template - change title, subtitle, include file
    title = "Resolution plots, binned by $|\eta|$"
    sub = in_stem_pre.replace("res_", "").replace("_", "\_")
    sub += r"\\"
    if in_name_post:
        sub += "Comparing with: \\"
        sub += in_stem_post.replace("res_", "").replace("_", "\_")
    sub = sub.replace("_ak", r"\\_ak")
    subtitle = "{\\tt " + sub +"}"
    slides_file = out_stem+"_slides.tex"
    main_file = out_stem+".tex"
    with open("beamer_template.tex", "r") as t:
        with open(main_file, "w") as f:
            substitute = {"@TITLE": title, "@SUBTITLE": subtitle,
                          "@FILE": slides_file}
            for line in t:
                for k in substitute:
                    if k in line:
                        line = line.replace(k, substitute[k])
                f.write(line)

    # some common bits for plots
    txt_pre = "Pre-calib" if in_name_post else "" # incase we only have 1 plot, not nec. pre calib
    txt_post = "Post-calib"

    lim_l1 = [0, 0.9]
    lim_ref = [0, 0.5]

    # Now make the slides file
    with open(slides_file, "w") as slides:
        titles = []
        plotnames = []
        # Do the L1 resolution plot alongside its corresponding genjet resolution plot
        for i, eta in enumerate(etaBins[0:-1]):
            emin = eta
            emax = etaBins[i+1]

            # PLOT - L1 resolution (L1 - ref / L1) as binned by L1 jet pt
            name = "resL1_%g_%g" % (emin, emax)
            pre_dict = dict(infile=input_file_pre, plotname="eta_%g_%g/" %(emin, emax)+name, color=r.kRed, legend_text=txt_pre, legend_style="LPE")
            plots = [pre_dict]
            if in_name_post:
                post_dict = dict(infile=input_file_post, plotname="eta_%g_%g/" %(emin, emax)+name, color=r.kBlue, legend_text=txt_post, legend_style="LPE")
                plots.append(post_dict)

            multiplot_to_file(plots, outfilename=[odir+name+".tex", odir+name+".pdf"],
                xtitle="p_{T}^{L1} [GeV]", ytitle="(p_{T}^{L1} - p_{T}^{Gen})/ p_{T}^{L1}", drawfit=True, drawopts="ALP", ylim=lim_l1)
            titles.append("$%g <  |\eta^{L1}| < %g$" % (emin, emax))
            plotnames.append(odir+name+".tex")

            # PLOT - ref resolution (L1 - ref / ref) as binned by ref jet pt
            name = "resRefRef_%g_%g" % (emin, emax)
            pre_dict = dict(infile=input_file_pre, plotname="eta_%g_%g/" %(emin, emax)+name, color=r.kRed, legend_text=txt_pre, legend_style="LPE")
            plots = [pre_dict]
            if in_name_post:
                post_dict = dict(infile=input_file_post, plotname="eta_%g_%g/" %(emin, emax)+name, color=r.kBlue, legend_text=txt_post, legend_style="LPE")
                plots.append(post_dict)

            multiplot_to_file(plots, outfilename=[odir+name+".tex", odir+name+".pdf"],
                xtitle="p_{T}^{Gen} [GeV]", ytitle="(p_{T}^{L1} - p_{T}^{Gen})/ p_{T}^{Gen}", drawfit=True, drawopts="ALP", ylim=lim_ref)
            titles.append("$%g <  |\eta^{L1}| < %g$" % (emin, emax))
            plotnames.append(odir+name+".tex")

            print titles
            print plotnames
            if (len(plotnames) == 4):
                print "Writing", emin, emax
                slidetitle = "Resolution"
                slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                titles = []
                plotnames = []

        # # Do the inclusive eta plot
        # emin = etaBins[0]
        # emax = etaBins[-1]

        # # PLOT - L1 resolution (L1 - ref / L1) as binned by L1 jet pt
        # name = "resL1_%g_%g" % (emin, emax)
        # pre_dict = dict(infile=input_file_pre, plotname="eta_%g_%g/" %(emin, emax)+name, color=r.kRed, legend_text=txt_pre, legend_style="LPE")
        # plots = [pre_dict]
        # if in_name_post:
        #     post_dict = dict(infile=input_file_post, plotname="eta_%g_%g/" %(emin, emax)+name, color=r.kBlue, legend_text=txt_post, legend_style="LPE")
        #     plots.append(post_dict)

        # multiplot_to_file(plots, outfilename=[odir+name+".tex", odir+name+".pdf"],
        #     xtitle="p_{T}^{L1} [GeV]", ytitle="(p_{T}^{L1} - p_{T}^{Gen})/ p_{T}^{L1}", drawfit=True, drawopts="ALP", ylim=lim_l1)
        # titles.append("$%g <  |\eta^{L1}| < %g$" % (emin, emax))
        # plotnames.append(odir+name+".tex")

        # # PLOT - ref resolution binned by ref pt
        # name = "resRefRef_%g_%g" % (emin, emax)
        # pre_dict = dict(infile=input_file_pre, plotname="eta_%g_%g/" %(emin, emax)+name, color=r.kRed, legend_text=txt_pre, legend_style="LPE")
        # plots = [pre_dict]
        # if in_name_post:
        #     post_dict = dict(infile=input_file_post, plotname="eta_%g_%g/" %(emin, emax)+name, color=r.kBlue, legend_text=txt_post, legend_style="LPE")
        #     plots.append(post_dict)

        # multiplot_to_file(plots, outfilename=[odir+name+".tex", odir+name+".pdf"],
        #     xtitle="p_{T}^{L1} [GeV]", ytitle="(p_{T}^{L1} - p_{T}^{Gen})/ p_{T}^{Gen}", drawfit=True, drawopts="ALP", ylim=lim_ref)
        # titles.append("$%g <  |\eta^{L1}| < %g$" % (emin, emax))
        # plotnames.append(odir+name+".tex")

        # print "Writing", emin, emax
        # slidetitle = "Resolution comparison pre \\& post calibration (L1 \\& GenJet)"
        slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))

    compile_pdf(main_file, out_name, odir)


def plot_bin_results(in_name=""):
    """
    To plot X for each pt/eta bin.
    Yes that's a lot of plots.
    """
    # Setup input file
    print "Opening", in_name
    in_stem = os.path.basename(in_name).replace(".root", "")
    input_file = open_root_file(in_name)

    # Setup output directory & filenames
    odir = os.path.dirname(os.path.abspath(in_name))+"/"+in_stem+"/"
    check_dir_exists(odir)

    # only have to change output name here - reflected automatically in tex files etc
    out_name = odir+in_stem+"_bin.pdf"
    out_stem = out_name.replace(".pdf","")
    print "Writing to", out_name

    # Start beamer file
    # Use template - change title, subtitle, include file
    title = "Results for each bin"
    sub = in_stem.replace("output_", "")
    sub = sub.replace("_", "\_")
    sub = sub.replace("_ak", r"\\_ak")
    subtitle = "{\\tt " + sub +"}"
    slides_file = out_stem+"_slides.tex"
    main_file = out_stem+".tex"
    with open("beamer_template.tex", "r") as t:
        with open(main_file, "w") as f:
            substitute = {"@TITLE": title, "@SUBTITLE": subtitle,
                          "@FILE": slides_file}
            for line in t:
                for k in substitute:
                    if k in line:
                        line = line.replace(k, substitute[k])
                f.write(line)

    # Now make the slides file
    with open(slides_file, "w") as slides:
        titles = []
        plotnames = []
        for i, eta in enumerate(etaBins[0:-1]):
            emin = eta
            emax = etaBins[i+1]
            out_dir_eta = odir+"/eta_%g_%g/" % (emin, emax)
            check_dir_exists(out_dir_eta)
            if emin >= 3.:
                ptBins = binning.pt_bins_8_wide
            else:
                ptBins = binning.pt_bins_8
            print ptBins
            for j, pt in enumerate(ptBins[:-1]):
                ptmin = pt
                ptmax = ptBins[j+1]
                print ptmin, ptmax
                # for each pt bin we have a L1 pt plot, and a response plot w/fit
                name = "res_l1_%g_%g" % (ptmin, ptmax)
                plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, name), [out_dir_eta+name+".tex", out_dir_eta+name+".pdf"], xtitle="(p_{T}^{L1} - p_{T}^{Gen}) / p_{T}^{L1}", ytitle="", drawfit=True, xlim=[-2,5])
                plotnames.append(out_dir_eta+name+".tex")
                titles.append("$%g < |p_{T}^{L1}| < %g GeV$" % (ptmin, ptmax))

                # name = "res_ref_ref_%g_%g" % (ptmin, ptmax)
                # plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, name), [out_dir_eta+name+".tex", out_dir_eta+name+".pdf"], xtitle="(p_{T}^{L1} - p_{T}^{Gen}) / p_{T}^{Gen}", ytitle="", drawfit=True, xlim=[-2,5])
                # plotnames.append(out_dir_eta+name+".tex")

                # Plot pt diff
                name = "ptDiff_l1_%g_%g" % (ptmin, ptmax)
                plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, name), [out_dir_eta+name+".tex", out_dir_eta+name+".pdf"], xtitle="p_{T}^{L1} - p_{T}^{Gen}", ytitle="", drawfit=True, xlim=[-100,50])
                plotnames.append(out_dir_eta+name+".tex")

                titles.append("")

                if (len(plotnames) == 4):
                    print "Writing", emin, emax, ptmin, ptmax
                    slidetitle = "$%g <  |\eta| < %g$" % (emin, emax)
                    slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                    titles = []
                    plotnames = []
            slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
        slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))

        # the inclusive eta bin:
        # emin = eta
        # emax = etaBins[-1]
        # out_dir_eta = odir+"/eta_%g_%g/" % (emin, emax)
        # check_dir_exists(out_dir_eta)
        # for j, pt in enumerate(ptBins[0:-1]):
        #     ptmin = pt
        #     ptmax = ptBins[j+1]
        #     # for each pt bin we have a L1 pt plot, and a response plot w/fit
        #     name = "res_l1_%g_%g" % (ptmin, ptmax)
        #     plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, name), [out_dir_eta+name+".tex", out_dir_eta+name+".pdf"], xtitle="(p_{T}^{L1} - p_{T}^{Gen}) / p_{T}^{L1}", ytitle="", drawfit=True)
        #     plotnames.append(out_dir_eta+name+".tex")

        #     name = "res_ref_ref_%g_%g" % (ptmin, ptmax)
        #     plot_to_file(input_file, "eta_%g_%g/Histograms/%s" % (emin, emax, name), [out_dir_eta+name+".tex", out_dir_eta+name+".pdf"], xtitle="(p_{T}^{L1} - p_{T}^{Gen}) / p_{T}^{Gen}", ytitle="", drawfit=True)
        #     plotnames.append(out_dir_eta+name+".tex")

        #     titles.append("$%g < p_{T}^{L1} < %g GeV$" % (ptmin, ptmax))
        #     titles.append("")

        #     print "Writing", emin, emax, ptmin, ptmax
        #     slidetitle = "$%g <  |\eta| < %g$" % (emin, emax)
        #     slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))

    compile_pdf(main_file, out_name, odir, n=1)


def compile_pdf(texfile, pdffile, outdir, n=2):
    """
    Compile the pdf
    Use lualatex for custom font. Can do it specified n times
    (n=2 makes page num correct but slower)
    """

    output = "-output-directory=%s" % outdir
    for i in range(n):
        subprocess.call(["pdflatex", "-interaction", "nonstopmode", output, texfile])
        # subprocess.call(["lualatex", output, texfile])
    # Open the result
    subprocess.call(["open", pdffile])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=cu.CustomFormatter)
    parser.add_argument("input", help="input ROOT filename")
    parser.add_argument("--detail", action="store_true", help="do all pt bin plots as well (takes much longer!)")
    parser.add_argument("--compare", help="filename to compare to <input> (e.g post-calibration)")
    args = parser.parse_args()

    if args.compare != "":
        # Plot result for each eta bin & overall, comparing pre and post calib
        plot_res_results(in_name_pre=args.input, in_name_post=args.compare)
    else:
        # Same but no comparison, only 1 file
        plot_res_results(in_name=args.input)

    # Plot each pt bin in every eta bin (i.e. A LOT)
    if args.detail:
        plot_bin_results(in_name=args.input)
