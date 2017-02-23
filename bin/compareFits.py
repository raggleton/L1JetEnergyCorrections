#!/bin/usr/env python
"""
Little script to plot several graphs and/or fit functions on the same canvas.
Can take any graph, from any file.

For calibration curve plots

TODO: expand to hists?
"""


import os
import ROOT
import binning
from binning import pairwise
from comparator import Contribution, Plot
from copy import deepcopy
from itertools import izip
import common_utils as cu

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(55)


<<<<<<< HEAD
# a set of 11 varying colours
colors = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen+2, ROOT.kMagenta,
          ROOT.kOrange+7, ROOT.kAzure+1, ROOT.kRed+3, ROOT.kViolet+1,
          ROOT.kOrange-3, ROOT.kTeal-5, ROOT.kViolet, ROOT.kCyan+4]

# x limits for "zoomed" plots
zoom_pt = [0, 150]

def setup_new_graphs(old_graphs, name_dict):
    """Create copy of graphs in old_graphs,
    renaming them by applying .format(name_dict)"""
    new_graphs = deepcopy(old_graphs)
    for ng, og in izip(new_graphs, old_graphs):
        ng.obj_name = og.obj_name.format(**name_dict)
    return new_graphs


def compare_PU_by_eta_bins(graphs, title, oDir, ylim=None, lowpt_zoom=True):
    """Plot graph contributions, with a different plot for each eta bin.
    Relies on each Contribution.obj_name in graphs being templated with the
    variables `eta_min` and `eta_max`.

    Parameters
    ----------
    graphs : list[Contribution]
        List of Contribution objects to be included on any one plot.
    title : str
        Title to put on plots
    oDir : str
        Output directory for plots
    ylim : list, optional
        Set y axis range
    lowpt_zoom : bool, optional
        Zoom in on low pt range
    """
    cu.check_dir_exists_create(oDir)
    for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins)):
        rename_dict = dict(eta_min=eta_min, eta_max=eta_max)
        eta_min_str = '{:g}'.format(eta_min).replace('.', 'p')
        eta_max_str = '{:g}'.format(eta_max).replace('.', 'p')

        # make a copy as we have to change the graph names
        new_graphs = setup_new_graphs(graphs, rename_dict)

        if not ylim:
            ylim = [0.5, 3] if eta_min > 2 else [0.5, 3]
        p = Plot(contributions=new_graphs, what="graph", xtitle="<p_{T}^{L1}>",
                 ytitle="Correction value (= 1/response)",
                 title=title.format(**rename_dict), ylim=ylim)
        p.plot()
        p.save(os.path.join(oDir, "compare_PU_eta_%s_%s.pdf" % (eta_min_str, eta_max_str)))

        if lowpt_zoom:
            # zoom in on low pT
            p = Plot(contributions=new_graphs, what="graph", xtitle="<p_{T}^{L1}>",
                     ytitle="Correction value (= 1/response)",
                     title=title.format(**rename_dict), xlim=zoom_pt, ylim=ylim)
            p.plot()
            p.save(os.path.join(oDir, "compare_PU_eta_%s_%s_pTzoomed.pdf" % (eta_min_str, eta_max_str)))


def compare_by_eta_pu_bins(graphs_list, file_identifier, pu_labels, title, oDir, ylim=None, lowpt_zoom=True):
    """Compare graphs for each (eta, PU) bin.

    Parameters
    ----------
    graphs_list : list[list[Contribution]]
        List of list of contributions, so you can any
        number of sets of contributions on a graph.
    file_identifier : str
        String to be inserted into resultant plot filename.
    title : str
        Title to put on plots
    oDir : str
        Output directory for plots
    ylim : list, optional
        Set y axis range
    lowpt_zoom : bool, optional
        Zoom in on low pt range
    """
    cu.check_dir_exists_create(oDir)
    for (eta_min, eta_max) in pairwise(binning.eta_bins):
        rename_dict = dict(eta_min=eta_min, eta_max=eta_max)
        eta_min_str = '{:g}'.format(eta_min).replace('.', 'p')
        eta_max_str = '{:g}'.format(eta_max).replace('.', 'p')
        new_graphs_list = [setup_new_graphs(g, rename_dict) for g in graphs_list]

        if not ylim:
            ylim = [0.5, 3.5] if eta_min > 2 else [0.5, 4]
        for i, pu_label in enumerate(pu_labels):
            rename_dict['pu_label'] = pu_label
            p = Plot(contributions=[ng[i] for ng in new_graphs_list], what="graph",
                     xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                     title=title.format(**rename_dict), ylim=ylim)
            p.plot()
            p.legend.SetX1(0.5)
            p.save(os.path.join(oDir, "compare_%s_eta_%s_%s_%s.pdf" % (file_identifier, eta_min_str, eta_max_str, pu_label)))
            if lowpt_zoom:
                # zoom in on low pT
                p = Plot(contributions=[ng[i] for ng in new_graphs_list], what="graph",
                         xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                         title=title.format(**rename_dict), xlim=zoom_pt, ylim=ylim)
                p.plot()
                p.legend.SetX1(0.5)
                p.save(os.path.join(oDir, "compare_%s_eta_%s_%s_%s_pTzoomed.pdf" % (file_identifier, eta_min_str, eta_max_str, pu_label)))


def compare_eta_by_pu_bins(graphs, pu_labels, title, oDir, ylim=None, lowpt_zoom=True):
    """Compare eta bins for graphs for a given PU bin. Does central, fowrad, and central+forward.

    Parameters
    ----------
    graphs : list[Contribution]
        Contributions corresponding to eta bins (0PU, PU0to10, 15to25, 30to40)
    title : str
        Title to put on plots
    oDir : str
        Output directory for plots
    ylim : list, optional
        Set y axis range
    lowpt_zoom : bool, optional
        Zoom in on low pt range
    """
    cu.check_dir_exists_create(oDir)
    eta_scenarios = [binning.eta_bins_central, binning.eta_bins_forward, binning.eta_bins]
    eta_scenario_labels = ['central', 'forward', 'all']
    for eta_bins, eta_label in izip(eta_scenarios, eta_scenario_labels):
        for pu_ind, pu_label in enumerate(pu_labels):
            new_graphs = []
            rename_dict = dict(pu_label=pu_label)
            for eta_ind, (eta_min, eta_max) in enumerate(pairwise(eta_bins)):
                rename_dict['eta_min'] = eta_min
                rename_dict['eta_max'] = eta_max
                contr = deepcopy(graphs[pu_ind])
                contr.obj_name = graphs[pu_ind].obj_name.format(**rename_dict)
                contr.line_color = colors[eta_ind]
                contr.marker_color = colors[eta_ind]
                contr.label = "%g < |#eta^{L1}| < %g" % (eta_min, eta_max)
                new_graphs.append(contr)
            if not ylim:
                ylim = [0.5, 4]
            p = Plot(contributions=new_graphs, what='graph',
                     xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                     title=title.format(**rename_dict), ylim=ylim)
            p.plot()
            p.save(os.path.join(oDir, 'compare_%sEta_%s.pdf' % (eta_label, pu_label)))

            if lowpt_zoom:
                p = Plot(contributions=new_graphs, what='graph',
                         xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                         title=title.format(**rename_dict), xlim=zoom_pt, ylim=ylim)
                p.plot()
                p.save(os.path.join(oDir, 'compare_%sEta_%s_pTzoomed.pdf' % (eta_label, pu_label)))


def compare():
    """Make all da plots"""

    # New layer 1
    s2_new = '/Users/robina/Soolin_Users_L1JEC_CMSSW_8_0_7_jec_local/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_newLayer1_noL1JEC/output'
    f_PU0to10_new = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_new = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_new = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    f_PU0to10_new_ref5 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref5to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_new_ref5 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref5to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_new_ref5 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref5to5000_l10to5000_dr0p4_PU30to40.root')

    f_PU0to10_new_dr0p2 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p2_PU0to10.root')
    f_PU15to25_new_dr0p2 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p2_PU15to25.root')
    f_PU30to40_new_dr0p2 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p2_PU30to40.root')

    f_PU0to10_new_ref5_dr0p2 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref5to5000_l10to5000_dr0p2_PU0to10.root')
    f_PU15to25_new_ref5_dr0p2 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref5to5000_l10to5000_dr0p2_PU15to25.root')
    f_PU30to40_new_ref5_dr0p2 = os.path.join(s2_new, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref5to5000_l10to5000_dr0p2_PU30to40.root')

    # Old layer1, used for 2016 startup, with 1s for HE/HF
    # s2_fall15_newLayer1 = '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst4_RAWONLY/output'
    s2_fall15_old = '/Users/robina/Soolin_Users_L1JEC_CMSSW_8_0_7_jec_local/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst4_RAWONLY/output'
    f_PU0to10_fall15_old = os.path.join(s2_fall15_old, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_fall15_old = os.path.join(s2_fall15_old, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_fall15_old = os.path.join(s2_fall15_old, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    pu_labels = ['PU0to10', 'PU15to25', 'PU30to40']

    # common object name
    corr_eta_graph_name = "l1corr_eta_{eta_min:g}_{eta_max:g}"

    # --------------------------------------------------------------------
    # New Stage 2 curves
    # Plot different PU scenarios for given eta bin
    # --------------------------------------------------------------------
    graphs = [
        # Contribution(file_name=f_0PU_new, obj_name=corr_eta_graph_name,
        #              label="0PU", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]
    title = "Fall15 MC, no JEC, new layer 1 calibs, #DeltaR < 0.4, {eta_min:g} < |#eta^{{L1}}| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, os.path.join(s2_new, 'comparePU'), lowpt_zoom=True)

    """
    # The different dR/ptRef combinations:
    graphs = [
        Contribution(file_name=f_PU0to10_new_ref5, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new_ref5, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new_ref5, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]
    title = "Fall15 MC, no JEC, new layer 1 calibs, #DeltaR < 0.4, p_{{T}}^{{Gen}} > 5 GeV, {eta_min:g} < |#eta^{{L1}}| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, os.path.join(s2_new, 'ptRef5'), lowpt_zoom=True)

    graphs = [
        Contribution(file_name=f_PU0to10_new_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]
    title = "Fall15 MC, no JEC, new layer 1 calibs, #DeltaR < 0.2, p_{{T}}^{{Gen}} > 10 GeV, {eta_min:g} < |#eta^{{L1}}| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, os.path.join(s2_new, 'dr0p2'), lowpt_zoom=True)

    graphs = [
        Contribution(file_name=f_PU0to10_new_ref5_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new_ref5_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new_ref5_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]
    title = "Fall15 MC, no JEC, new layer 1 calibs, #DeltaR < 0.2, p_{{T}}^{{Gen}} > 5 GeV, {eta_min:g} < |#eta^{{L1}}| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, os.path.join(s2_new, 'ptRef5_dr0p2'), lowpt_zoom=True)

    # Comparing them
    # ------------------------------------------------------------------------
    new_graphs = [
        Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (#DeltaR < 0.4, p_{T}^{Gen} > 10 GeV)", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (#DeltaR < 0.4, p_{T}^{Gen} > 10 GeV)", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (#DeltaR < 0.4, p_{T}^{Gen} > 10 GeV)", line_color=colors[3], marker_color=colors[3])
    ]
    ref5_graphs = [
        Contribution(file_name=f_PU0to10_new_ref5, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (#DeltaR < 0.4, p_{T}^{Gen} > 5 GeV)", line_color=colors[1+3], marker_color=colors[1+3]),
        Contribution(file_name=f_PU15to25_new_ref5, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (#DeltaR < 0.4, p_{T}^{Gen} > 5 GeV)", line_color=colors[2+3], marker_color=colors[2+3]),
        Contribution(file_name=f_PU30to40_new_ref5, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (#DeltaR < 0.4, p_{T}^{Gen} > 5 GeV)", line_color=colors[3+3], marker_color=colors[3+3])
    ]
    dr0p2_graphs = [
        Contribution(file_name=f_PU0to10_new_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (#DeltaR < 0.2, p_{T}^{Gen} > 10 GeV)", line_style=2, line_color=colors[1+6], marker_color=colors[1+6]),
        Contribution(file_name=f_PU15to25_new_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (#DeltaR < 0.2, p_{T}^{Gen} > 10 GeV)", line_style=2, line_color=colors[2+6], marker_color=colors[2+6]),
        Contribution(file_name=f_PU30to40_new_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (#DeltaR < 0.2, p_{T}^{Gen} > 10 GeV)", line_style=2, line_color=colors[3+6], marker_color=colors[3+6])
    ]
    dr0p2_ref5_graphs = [
        Contribution(file_name=f_PU0to10_new_ref5_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (#DeltaR < 0.2, p_{T}^{Gen} > 5 GeV)", line_style=2, line_color=colors[1+9], marker_color=colors[1+9]),
        Contribution(file_name=f_PU15to25_new_ref5_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (#DeltaR < 0.2, p_{T}^{Gen} > 5 GeV)", line_style=2, line_color=colors[2+9], marker_color=colors[2+9]),
        Contribution(file_name=f_PU30to40_new_ref5_dr0p2, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (#DeltaR < 0.2, p_{T}^{Gen} > 5 GeV)", line_style=2, line_color=colors[3+9], marker_color=colors[3+9])
    ]

    title = "Fall15 MC, no JEC, new layer 1 calibs, {eta_min:g} < |#eta^{{L1}}| < {eta_max:g}"
    compare_by_eta_pu_bins([new_graphs, ref5_graphs, dr0p2_graphs, dr0p2_ref5_graphs], 'play_dr_ptRef', pu_labels, title, os.path.join(s2_new, 'play_dr_ptRef'))


    # --------------------------------------------------------------------
    # New vs Old curves
    # --------------------------------------------------------------------
    new_graphs = [
        Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (new Layer 1 calib)", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (new Layer 1 calib)", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (new Layer 1 calib)", line_color=colors[3], marker_color=colors[3])
    ]

    old_graphs = [
        Contribution(file_name=f_PU0to10_fall15_old, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (old Layer 1 calib)", line_style=2, line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_fall15_old, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (old Layer 1 calib)", line_style=2, line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_fall15_old, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (old Layer 1 calib)", line_style=2, line_color=colors[3], marker_color=colors[3])
    ]
    title = "Fall15 MC, no JEC, Stage 2, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_by_eta_pu_bins([new_graphs, old_graphs], 'new_old_layer1', pu_labels, title, os.path.join(s2_new, 'new_old_layer1'))
    """


if __name__ == "__main__":
    compare()
