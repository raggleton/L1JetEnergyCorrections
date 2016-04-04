#!/usr/bin/env python

"""
Little script to plot several graphs and/or fit functions on the same canvas.
Can take any graph, from any file.

For resolution plots
"""


import os
import ROOT
import binning
from binning import pairwise
from comparator import Contribution, Plot
from copy import deepcopy
from itertools import izip


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(55)


l1_str = 'L1'
# l1_str = 'PF'

ref_str = "GenJet"
# ref_str = "PFJet"

# Some common axis labels
rsp_str = "E_{T}^{%s}/E_{T}^{%s}" % (l1_str, ref_str)
eta_str = "#eta"
eta_ref_str = "|#eta^{%s}|" % (ref_str)
eta_l1_str = "|#eta^{%s}|" % (l1_str)
dr_str = "#DeltaR(%s jet, Ref jet)" % (l1_str)
pt_str = "E_{T}[GeV]"
pt_l1_str = "E_{T}^{%s} [GeV]" % (l1_str)
pt_ref_str = "E_{T}^{%s} [GeV]" % (ref_str)
res_l1_str = "#sigma(E_{T}^{%s} - E_{T}^{%s})/<E_{T}^{%s}>" % (l1_str, ref_str, l1_str)
res_ref_str = "#sigma(E_{T}^{%s} - E_{T}^{%s})/<E_{T}^{%s}>" % (l1_str, ref_str, ref_str)
alt_res_l1_str = "(E_{T}^{%s} - E_{T}^{%s})/E_{T}^{%s}" % (l1_str, ref_str, l1_str)
pt_diff_str = "E_{T}^{%s} - E_{T}^{%s} [GeV]" % (l1_str, ref_str)



def compare():
    """Make all da plots"""

    # a set of 11 varying colours
    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen+2, ROOT.kMagenta,
              ROOT.kOrange+7, ROOT.kAzure+1, ROOT.kRed+3, ROOT.kViolet+1,
              ROOT.kOrange-3, ROOT.kTeal-5]

    s2_fall15_dummyLayer1_oldJEC = '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_1Apr_int-v14_dummyLayer1_L1JECSpring15_jst1p5_RAWONLY/resolution'
    f_0PU_fall15_dummyLayer1_oldJEC = os.path.join(s2_fall15_dummyLayer1_oldJEC, 'res_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4_spring15JEC_maxPt1022.root')
    f_PU0to10_fall15_dummyLayer1_oldJEC = os.path.join(s2_fall15_dummyLayer1_oldJEC, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_spring15JEC_PU0to10_maxPt1022.root')
    f_PU15to25_fall15_dummyLayer1_oldJEC = os.path.join(s2_fall15_dummyLayer1_oldJEC, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_spring15JEC_PU15to25_maxPt1022.root')
    f_PU30to40_fall15_dummyLayer1_oldJEC = os.path.join(s2_fall15_dummyLayer1_oldJEC, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_spring15JEC_PU30to40_maxPt1022.root')

    s2_fall15_newLayer1_newJEC_jst4 = '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst4_RAWONLY/resolution'
    f_0PU_fall15_newLayer1_newJEC_jst4 = os.path.join(s2_fall15_newLayer1_newJEC_jst4, 'res_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_maxPt1022.root')
    f_PU0to10_fall15_newLayer1_newJEC_jst4 = os.path.join(s2_fall15_newLayer1_newJEC_jst4, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU0to10_maxPt1022.root')
    f_PU15to25_fall15_newLayer1_newJEC_jst4 = os.path.join(s2_fall15_newLayer1_newJEC_jst4, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU15to25_maxPt1022.root')
    f_PU30to40_fall15_newLayer1_newJEC_jst4 = os.path.join(s2_fall15_newLayer1_newJEC_jst4, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU30to40_maxPt1022.root')

    s2_fall15_newLayer1_newJEC_jst5 = '/hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst5_RAWONLY/resolution'
    f_0PU_fall15_newLayer1_newJEC_jst5 = os.path.join(s2_fall15_newLayer1_newJEC_jst5, 'res_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_maxPt1022.root')
    f_PU0to10_fall15_newLayer1_newJEC_jst5 = os.path.join(s2_fall15_newLayer1_newJEC_jst5, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU0to10_maxPt1022.root')
    f_PU15to25_fall15_newLayer1_newJEC_jst5 = os.path.join(s2_fall15_newLayer1_newJEC_jst5, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU15to25_maxPt1022.root')
    f_PU30to40_fall15_newLayer1_newJEC_jst5 = os.path.join(s2_fall15_newLayer1_newJEC_jst5, 'res_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU30to40_maxPt1022.root')

    zoom_pt = [0, 150]
    pu_labels = ['0PU', 'PU0to10', 'PU15to25', 'PU30to40']

    # arrange into PU bins
    dummyLayer1_oldJEC_label = 'Dummy Layer 1, Spring15 L1JEC, JST 1.5 GeV'
    fall15_dummyLayer1_oldJEC = [
        Contribution(file_name=f_0PU_fall15_dummyLayer1_oldJEC, obj_name=None, label=dummyLayer1_oldJEC_label),
        Contribution(file_name=f_PU0to10_fall15_dummyLayer1_oldJEC, obj_name=None, label=dummyLayer1_oldJEC_label),
        Contribution(file_name=f_PU15to25_fall15_dummyLayer1_oldJEC, obj_name=None, label=dummyLayer1_oldJEC_label),
        Contribution(file_name=f_PU30to40_fall15_dummyLayer1_oldJEC, obj_name=None, label=dummyLayer1_oldJEC_label)
    ]

    jst4_label = 'New Layer 1, new L1JEC, JST 4 GeV'
    fall15_newLayer1_newJEC_jst4_graphs = [
        Contribution(file_name=f_0PU_fall15_newLayer1_newJEC_jst4, obj_name=None, label=jst4_label),
        Contribution(file_name=f_PU0to10_fall15_newLayer1_newJEC_jst4, obj_name=None, label=jst4_label),
        Contribution(file_name=f_PU15to25_fall15_newLayer1_newJEC_jst4, obj_name=None, label=jst4_label),
        Contribution(file_name=f_PU30to40_fall15_newLayer1_newJEC_jst4, obj_name=None, label=jst4_label)
    ]

    jst5_label = 'New Layer 1, new L1JEC, JST 5 GeV'
    fall15_newLayer1_newJEC_jst5_graphs = [
        Contribution(file_name=f_0PU_fall15_newLayer1_newJEC_jst5, obj_name=None, label=jst5_label),
        Contribution(file_name=f_PU0to10_fall15_newLayer1_newJEC_jst5, obj_name=None, label=jst5_label),
        Contribution(file_name=f_PU15to25_fall15_newLayer1_newJEC_jst5, obj_name=None, label=jst5_label),
        Contribution(file_name=f_PU30to40_fall15_newLayer1_newJEC_jst5, obj_name=None, label=jst5_label)
    ]

    def compare_scenarios_by_pu_eta_bins(eta_bins, pu_labels, graph_lists, title, oDir, ylim=None, lowpt_zoom=False):
        for eta_min, eta_max in pairwise(eta_bins):
            for pu_ind, pu_label in enumerate(pu_labels):
                pu_graphs = [x[pu_ind] for x in graph_lists]
                # tweak names and colors
                for i, contr in enumerate(pu_graphs):
                    contr.line_color = colors[i]
                    contr.marker_color = colors[i]
                    contr.obj_name = "eta_%g_%g/resRefRef_%g_%g_diff" % (eta_min, eta_max, eta_min, eta_max)

                fmt_dict = dict(eta_min=eta_min, eta_max=eta_max, pu_label=pu_label)
                plt_title = title.format(**fmt_dict)
                p = Plot(contributions=pu_graphs, what='graph', xtitle=pt_ref_str,
                         ytitle=res_ref_str, title=plt_title, ylim=[0, 0.7], xlim=[0, 500])
                p.legend.SetX1(0.4)
                p.plot()
                filename = 'compare_fall15_dummyLayer1_newLayer1_withJEC_eta_%g_%g_%s.pdf' % (eta_min, eta_max, pu_label)
                p.save(os.path.join(oDir, filename))
                if lowpt_zoom:
                    p = Plot(contributions=pu_graphs, what='graph', xtitle=pt_ref_str,
                             ytitle=res_ref_str, title=plt_title, ylim=[0, 0.7], xlim=zoom_pt)
                    p.legend.SetX1(0.4)
                    p.plot()
                    filename = 'compare_fall15_dummyLayer1_newLayer1_withJEC_eta_%g_%g_%s_ptZoomed.pdf' % (eta_min, eta_max, pu_label)
                    p.save(os.path.join(oDir, filename))

    graph_lists = [fall15_dummyLayer1_oldJEC, fall15_newLayer1_newJEC_jst4_graphs, fall15_newLayer1_newJEC_jst5_graphs]
    title = 'Fall 15 MC, dummy Layer 1 vs bitwise Layer 1 (w/calibs), {eta_min:g} < |#eta| < {eta_max:g}, {pu_label}'
    oDir = '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_1Apr_int-v14_dummyLayer1_L1JECSpring15_jst1p5_RAWONLY/resolution'

    compare_scenarios_by_pu_eta_bins(binning.eta_bins, pu_labels, graph_lists, title, oDir, lowpt_zoom=True)

    etaBins = [0, 3, 5]
    compare_scenarios_by_pu_eta_bins(etaBins, pu_labels, graph_lists, title, oDir, lowpt_zoom=True)


if __name__ == "__main__":
    compare()
