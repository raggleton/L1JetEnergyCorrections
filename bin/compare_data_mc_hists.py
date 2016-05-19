#!/usr/bin/env python

"""
Compare hists

TODO: tie into compareFits.py for a suger-general comparator
"""


import os
import ROOT
import binning
from binning import pairwise
from comparator import Contribution
from copy import deepcopy
from itertools import izip
import random


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(55)



class Plot(object):
    """
    Basic class to handle information about one plot,
    which can have several contributions.
    """

    def __init__(self, contributions=None, title="",
                 xtitle="", ytitle="", xlim=None, ylim=None,
                 legend=True, normalise=False):
        """
        contributions: list
            List of Contribution objects.
        title: str
            Title of plot.
        xtitle: str
            X axis title.
        ytitle: str
            Y axis title.
        xlim: list
            Limits of x axis. If None then determines suitable limits.
        ylim: list
            Limits of y axis. If None then determines suitable limits.
        legend: bool
            Include legend on plot.
        normalise: bool
            If plotting hists, normalise so integral = 1
        """
        self.contributions = contributions if contributions else []
        self.title = title
        self.xtitle = xtitle
        self.ytitle = ytitle
        self.xlim = xlim
        self.ylim = ylim
        self.do_legend = legend
        self.legend = ROOT.TLegend(0.65, 0.6, 0.87, 0.87) if legend else None
        self.container = None
        self.canvas = None
        self.normalise = normalise
        # self.canvas = ROOT.TCanvas("canv", "", 800, 600)
        # self.canvas.SetTicks(1, 1)

    def add_contribution(self, *contribution):
        """Add Contribution to Plot. Can be single item or list."""
        self.contributions.extend(*contribution)

    def plot(self, draw_opts=None):
        """Make the plot.

        draw_opts: str
            Same options as you would pass to Draw() in ROOT.

        Returns bool: True if OK to save, False if nothing drawn
        """

        # First make a container with unique name
        self.container = ROOT.THStack("hst%d" % random.randint(0, 100), "")

        # Now add all the contributions to the container, styling as we go
        if len(self.contributions) == 0:
            raise UnboundLocalError("contributions list is empty")

        one_good_contribution = False
        for c in self.contributions:
            try:
                obj = c.get_obj().Clone()
                if not obj:
                    print "Couldn't get", c.obj_name
                    continue
                one_good_contribution = True
            except IOError:
                print "Couldn't get", c.obj_name
                continue

            if self.normalise:
                if obj.Integral() > 0:
                    obj.Scale(1./obj.Integral())

            self.container.Add(obj)

            if self.do_legend:
                self.legend.AddEntry(obj, c.label, "L")
        if not one_good_contribution:
            print 'No contributions'
            return False

        # Plot the container
        # need different default drawing options for TF1s vs TGraphs
        # (ALP won't actually display axis for TF1)
        if draw_opts is None:
            draw_opts = "NOSTACK"

        # Need a canvas
        # If we have "SAME" then we want to draw this Plot object
        # on the current canvas
        # Otherwise, we create a new one
        if "SAME" in draw_opts:
            self.canvas = ROOT.gPad
            self.canvas.cd()
            print "Using existing canvas", self.canvas.GetName()
        else:
            self.canvas = ROOT.TCanvas("canv%s" % random.randint(0, 100), "", 800, 600)
            self.canvas.SetTicks(1, 1)

        self.container.Draw(draw_opts)

        # Customise
        modifier = self.container
        modifier.SetTitle("%s;%s;%s" % (self.title, self.xtitle, self.ytitle))
        if self.xlim:
            modifier.GetXaxis().SetRangeUser(*self.xlim)
        if self.ylim:
            modifier.GetYaxis().SetRangeUser(*self.ylim)

        # Plot legend
        if self.do_legend:
            self.legend.Draw()

        return True

    def save(self, filename):
        """Save the plot to file. Do some check to make sure dir exists."""
        filename = os.path.abspath(filename)
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        self.canvas.SaveAs(filename)


def make_comparisons():
    """Do all the comparisons"""

    s2_mc_withJEC = '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst4_RAWONLY/check/'
    f_PU0to10_check_mc_withJEC = os.path.join(s2_mc_withJEC, 'check_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU0to10_maxPt1022.root')
    f_PU15to25_check_mc_withJEC = os.path.join(s2_mc_withJEC, 'check_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU15to25_maxPt1022.root')
    mc_PU0to10_label = 'MC QCD Spring15, with L1JEC (PU 0-10)'
    mc_PU0to10_colour = ROOT.kBlue
    mc_PU15to25_label = 'MC QCD Spring15, with L1JEC (PU 15-25)'
    mc_PU15to25_colour = ROOT.kRed

    s2_data_run273301 = '/hdfs/L1JEC/L1JetEnergyCorrections/crab_Collision2016-RECO-l1t-integration-v53p1-CMSSW-807__273301_SingleMuon/check/'
    f_check_data_run273301_SingleMu_clean = os.path.join(s2_data_run273301, 'check_SingleMu_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO_maxPt1022.root')
    data_label = 'Data (run 273301, TightLepVeto cleaning)'
    data_color = ROOT.kBlack

    oDir = '/users/ra12451/L1JEC/integration/CMSSW_8_0_7/src/L1Trigger/L1JetEnergyCorrections/crab_Collision2016-RECO-l1t-integration-v53p1-CMSSW-807__273301_SingleMuon/check/data_mc_cleanTightLepVeto'

    for eta_min, eta_max in pairwise(binning.eta_bins):
        for pt_bin in binning.check_pt_bins:
            pt_lo, pt_hi = pt_bin
            for pt_var in ['pt', 'ptRef']:
                hist_name = 'eta_0_3/Histograms/hrsp_eta_%g_%g_%s_%d_%d' % (eta_min, eta_max, pt_var, pt_lo, pt_hi)
                hists = [
                    Contribution(file_name=f_check_data_run273301_SingleMu_clean, obj_name=hist_name, label=data_label, line_color=data_color, marker_color=data_color),
                    Contribution(file_name=f_PU0to10_check_mc_withJEC, obj_name=hist_name, label=mc_PU0to10_label, line_color=mc_PU0to10_colour, marker_color=mc_PU0to10_colour),
                    Contribution(file_name=f_PU15to25_check_mc_withJEC, obj_name=hist_name, label=mc_PU15to25_label, line_color=mc_PU15to25_colour, marker_color=mc_PU15to25_colour)
                ]
                pt_str = 'p_{T}^{L1}' if pt_var == 'pt' else 'p_{T}^{Ref}'
                title = 'Data vs MC, %g < #eta^{L1} < %g, %d < %s < %d' % (eta_min, eta_max, pt_lo, pt_str, pt_hi)
                p = Plot(contributions=hists,
                         xtitle="Response (L1/PF)", ytitle="AU",
                         title=title, normalise=True, xlim=[0,4])
                p.legend.SetX1(0.45)
                p.legend.SetY1(0.6)
                if p.plot('HISTE NOSTACK'):
                    p.save(os.path.join(oDir, 'compare_eta_%g_%g_%s_%d_%d.pdf' % (eta_min, eta_max, pt_var, pt_lo, pt_hi)))

if __name__ == "__main__":
    make_comparisons()

