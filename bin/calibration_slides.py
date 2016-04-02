#!/usr/bin/env python
"""
This script outputs all the calibration plots in the ROOT file output by
runCalibration.py as one long pdf, cos TBrowser sucks.

It will make the PDF in the same directory as the ROOT file, under a directory
named output_<ROOT file stem>
"""


import glob
import ROOT
import os
import argparse
import subprocess
import binning
import beamer_slide_templates as bst
import common_utils as cu


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.gErrorIgnoreLevel = ROOT.kWarning


# Update me if necessary!
AUTHOR = 'Robin Aggleton'


def plot_to_file(f, plotname, filename, xtitle="", ytitle="", title="",
                 drawopts="", drawfit=True, extend_fit=True):
    """Draw `plotname` to canvas and save. Can also draw fitted function on top.

    Parameters
    ----------
    f : TFile
        Output file from runCalibration.py
    plotname : str
        Name of object draw.
    filename : list[str]
        Output filenames, can be a list of filenames (e.g. for .tex, .pdf, .png)
    xtitle : str, optional
        Title for x axis
    ytitle : str, optional
        Title for y axis
    title : str, optional
        Title for plot
    drawopts : str, optional
        Options to pass to Draw().
    drawfit : bool, optional
        Whether to draw the fitted function or not (should be called `plotname`_fit)
    extend_fit : bool, optional
        Whether to extend the fit to high and low pT, beyond the fitted range.

    Returns
    -------
    bool
        True if `plotname` found in file, othrwise False
    """
    ROOT.gStyle.SetPaperSize(10., 10.)
    ROOT.gStyle.SetOptStat("mre")
    ROOT.gStyle.SetOptFit(0101)  # MAGIC COMBO FOR PARAMS+ERRORS
    print plotname
    obj = f.Get(plotname)
    obj2 = f.Get(plotname + "_fit")
    if not obj:
        print "Can't find", obj
        return False

    if (drawfit and not obj2):
        print "Can't find", plotname + "_fit, not drawing fit function"
        drawfit = False

    plot = obj.Clone()
    plot.SetTitle(';'.join([title, xtitle, ytitle]))
    plot.Draw(drawopts)
    # plot.GetYaxis().SetRangeUser(0.5, 1.2*ROOT.TMath.MaxElement(plot.GetN(), plot.GetY()))
    plot.GetYaxis().SetRangeUser(0.5, 2)
    if drawfit:
        plot2 = obj2.Clone()
        plot2.SetTitle(';'.join([title, xtitle, ytitle]))
        fn = plot2.GetListOfFunctions().At(0)
        if fn:
            fn.SetLineWidth(2)
        plot2.Draw(drawopts + "SAME")

        # draw fit over full range, not just fitted range
        if extend_fit:
            fn2 = fn.Clone()
            fn2.SetRange(0, 1000)
            fn2.SetLineStyle(3)
            fn2.SetLineWidth(2)
            fn2.Draw("SAME")
        plot.Draw(drawopts + "SAME")

    ROOT.gPad.Update()
    ROOT.gPad.SetTicks(1, 1)

    # Draw fit stats box
    if drawfit:
        st = plot2.FindObject("stats")
        st.SetFillStyle(0)
        st.SetX1NDC(0.6)
        st.SetX2NDC(0.9)
        st.SetY1NDC(0.55)
        st.SetY2NDC(0.9)

    for f in filename:
        ROOT.gPad.Print(f)

    ROOT.gPad.Clear()

    return True


def make_main_tex_file(frontpage_title='Correction value plots', subtitle='',
                       author=os.environ['LOGNAME'],
                       main_tex_file='', slides_tex_file=''):
    """Generate main TeX file for set of slides, usign a template.

    Parameters
    ----------
    frontpage_title : str, optional
        Title for title slide
    subtitle : str, optional
        Subtitle for title slide
    main_tex_file : str, optional
        Filename for main TeX file to be written.
    slides_tex_file : str, optional
        Filename for slides file to be included.
    """
    with open("beamer_template.tex", "r") as template:
        with open(main_tex_file, "w") as f:
            substitute = {"@TITLE": frontpage_title, "@SUBTITLE": subtitle,
                          "@FILE": slides_tex_file, "@AUTHOR": author}
            for line in template:
                for k in substitute:
                    if k in line:
                        line = line.replace(k, substitute[k])
                f.write(line)


def plot_corr_results(in_name):
    """Puts correction plots from ROOT file in one pdf.

    Parameters
    ----------
    in_name : str
        Name of ROOT file to process (output from runCalibration.py)
    """
    print "Opening", in_name
    in_stem = os.path.basename(in_name).replace(".root", "")
    input_file = cu.open_root_file(in_name)

    # Setup output directory & filenames
    odir = os.path.join(os.path.dirname(os.path.abspath(in_name)), in_stem)
    cu.check_dir_exists_create(odir)

    out_name = os.path.join(odir, in_stem + ".pdf")
    out_stem = out_name.replace(".pdf", "")
    print "Writing to", out_name

    # Start beamer file - make main tex file
    # Use template - change title, subtitle, include file
    frontpage_title = "Correction value plots, binned by $|\eta|$"
    sub = in_stem.replace("output_", "").replace("_", "\_").replace("_ak", r"\\_ak")
    subtitle = "{\\tt " + sub + "}"
    main_file = out_stem + ".tex"
    slides_file = out_stem + "_slides.tex"
    make_main_tex_file(frontpage_title, subtitle, AUTHOR, main_file, slides_file)

    # Now make the slides file to be included in main file
    with open(slides_file, "w") as slides:
        titles = []
        plotnames = []
        etaBins = binning.eta_bins
        for i, (eta_min, eta_max) in enumerate(binning.pairwise(etaBins)):
            plotname = "l1corr_eta_%g_%g" % (eta_min, eta_max)
            bin_title = "%g <  |\eta^{L1}| < %g" % (eta_min, eta_max)
            xtitle = "<p_{T}^{L1}> [GeV]"
            ytitle = "Correction = 1/#langle p_{T}^{L1}/p_{T}^{Ref}#rangle"
            output_plots = [os.path.join(odir, plotname + ext) for ext in ['.tex', '.pdf']]
            if plot_to_file(input_file, plotname, output_plots,
                            xtitle=xtitle, ytitle=ytitle, title="",
                            drawfit=True, extend_fit=True):
                titles.append("$%s$" % bin_title)
                plotnames.append(os.path.join(odir, plotname + ".tex"))
            # When we have 4 plots, or reached the end, write to a slide
            if (((i + 1) % 4 == 0) and (i != 0)) or (i == len(etaBins) - 2):
                print "Writing slide"
                slidetitle = "Correction value"
                slides.write(bst.make_slide(bst.four_plot_slide, titles, plotnames, slidetitle))
                titles = []
                plotnames = []

    compile_pdf(main_file, out_name, odir, 1)


def compile_pdf(tex_filename, pdf_filename, outdir, num_compilation=1, latex_cmd='lualatex'):
    """Compile the pdf. Deletes all non-tex/pdf files afterwards.

    Parameters
    ----------
    tex_filename : str
        Name of TeX file to compile
    pdf_filename : str
        Name of output PDF file
    outdir : str
        Output directory for PDF file
    num_compilation : int, optional
        Number of times to run tex command
    latex_cmd : str, optional
        Which latex command to run.
    """

    output = "-output-directory=%s" % outdir
    for i in range(num_compilation):
        subprocess.call(["nice", "-n", "19", latex_cmd, "-interaction", "nonstopmode",
                         output, tex_filename])

    # Tidy up all the non .tex or .pdf files
    for f in glob.glob(os.path.join(outdir, tex_filename.replace(".tex", ".*"))):
        if os.path.splitext(f)[1] not in [".tex", ".pdf"]:
            print 'deleting', f
            os.remove(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=cu.CustomFormatter)
    parser.add_argument("input", help="input ROOT filename")
    args = parser.parse_args()

    plot_corr_results(in_name=args.input)
