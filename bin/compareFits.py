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


ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(55)


def compare():
    """Make all da plots"""

    # a set of 11 varying colours
    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen+2, ROOT.kMagenta,
              ROOT.kOrange+7, ROOT.kAzure+1, ROOT.kRed+3, ROOT.kViolet+1,
              ROOT.kOrange-3, ROOT.kTeal-5]

    s2_new = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_12Feb_85a0ccf_noJEC_fixedPUS/output'
    f_0PU_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25FlatNoPUHCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    f_PU0to10_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_new = os.path.join(s2_new, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    # s2_old = '/users/ra12451/L1JEC/CMSSW_7_6_0_pre7/src/L1Trigger/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/output/'
    # f_0PU_old = os.path.join(s2_old, 'output_QCDFlatSpring15BX25FlatNoPUHCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_orig.root')
    # f_PU0to10_old = os.path.join(s2_old, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10_orig.root')
    # f_PU15to25_old = os.path.join(s2_old, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25_orig.root')
    # f_PU30to40_old = os.path.join(s2_old, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40_orig.root')

    # s2_buggy = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_10Feb_2dd1043_noJEC_v2/output'
    # f_0PU_buggy = os.path.join(s2_buggy, 'output_QCDFlatSpring15BX25FlatNoPUHCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    # f_PU0to10_buggy = os.path.join(s2_buggy, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    # f_PU15to25_buggy = os.path.join(s2_buggy, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    # f_PU30to40_buggy = os.path.join(s2_buggy, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    # s2_maxPUS = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre5/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_13Feb_85a0ccf_noJEC_PUSmax/output'
    # f_PU0to10_maxPUS = os.path.join(s2_maxPUS, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    # f_PU15to25_maxPUS = os.path.join(s2_maxPUS, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    # f_PU30to40_maxPUS = os.path.join(s2_maxPUS, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    # s2_data = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/run260627_SingleMuReReco_HF_noL1JEC_3bf1b93_20Feb_Bristol_v3/output'
    # f_PU0to5_data = os.path.join(s2_data, 'output_SingleMuReReco_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO_PU0to5.root')
    # f_PU8to12_data = os.path.join(s2_data, 'output_SingleMuReReco_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO_PU8to12.root')
    # f_PU15to25_data = os.path.join(s2_data, 'output_SingleMuReReco_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO_PU15to25.root')
    # f_allPU_data = os.path.join(s2_data, 'output_SingleMuReReco_ak4_ref10to5000_l10to5000_dr0p4_cleanTIGHTLEPVETO.root')

    # s2_L1PF = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDSpring15_20Feb_3bf1b93_noL1JEC_PFJets_V7PFJEC/output'
    # f_PU0to10_L1PF = os.path.join(s2_L1PF, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_PF10to5000_l10to5000_dr0p4_noCleaning_PU0to10.root')
    # f_PU15to25_L1PF = os.path.join(s2_L1PF, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_PF10to5000_l10to5000_dr0p4_noCleaning_PU15to25.root')
    # f_PU30to40_L1PF = os.path.join(s2_L1PF, 'output_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_PF10to5000_l10to5000_dr0p4_noCleaning_PU30to40.root')

    # s2_fall15_dummyLayer1 = '/users/ra12451/L1JEC/CMSSW_8_0_0_pre6/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_Fall15_9Mar_integration-v9_NoL1JEC_jst1p5_v2/output'
    # f_PU0_fall15_dummyLayer1 = os.path.join(s2_fall15_dummyLayer1, 'output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4.root')

    s2_fall15_newLayer1_jst2 = '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst2_RAWONLY/output'
    f_0PU_fall15_newLayer1_jst2 = os.path.join(s2_fall15_newLayer1_jst2, 'output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    f_PU0to10_fall15_newLayer1_jst2 = os.path.join(s2_fall15_newLayer1_jst2, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_fall15_newLayer1_jst2 = os.path.join(s2_fall15_newLayer1_jst2, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_fall15_newLayer1_jst2 = os.path.join(s2_fall15_newLayer1_jst2, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    s2_fall15_newLayer1_jst3 = '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst3_RAWONLY/output'
    f_0PU_fall15_newLayer1_jst3 = os.path.join(s2_fall15_newLayer1_jst3, 'output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    f_PU0to10_fall15_newLayer1_jst3 = os.path.join(s2_fall15_newLayer1_jst3, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_fall15_newLayer1_jst3 = os.path.join(s2_fall15_newLayer1_jst3, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_fall15_newLayer1_jst3 = os.path.join(s2_fall15_newLayer1_jst3, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    s2_fall15_newLayer1_jst4 = '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst4_RAWONLY/output'
    f_0PU_fall15_newLayer1_jst4 = os.path.join(s2_fall15_newLayer1_jst4, 'output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    f_PU0to10_fall15_newLayer1_jst4 = os.path.join(s2_fall15_newLayer1_jst4, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_fall15_newLayer1_jst4 = os.path.join(s2_fall15_newLayer1_jst4, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_fall15_newLayer1_jst4 = os.path.join(s2_fall15_newLayer1_jst4, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    s2_fall15_newLayer1_jst5 = '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst5_RAWONLY/output'
    f_0PU_fall15_newLayer1_jst5 = os.path.join(s2_fall15_newLayer1_jst5, 'output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    f_PU0to10_fall15_newLayer1_jst5 = os.path.join(s2_fall15_newLayer1_jst5, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_fall15_newLayer1_jst5 = os.path.join(s2_fall15_newLayer1_jst5, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_fall15_newLayer1_jst5 = os.path.join(s2_fall15_newLayer1_jst5, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    s2_fall15_newLayer1_jst6 = '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst6_RAWONLY/output'
    f_0PU_fall15_newLayer1_jst6 = os.path.join(s2_fall15_newLayer1_jst6, 'output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4.root')
    f_PU0to10_fall15_newLayer1_jst6 = os.path.join(s2_fall15_newLayer1_jst6, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU0to10.root')
    f_PU15to25_fall15_newLayer1_jst6 = os.path.join(s2_fall15_newLayer1_jst6, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU15to25.root')
    f_PU30to40_fall15_newLayer1_jst6 = os.path.join(s2_fall15_newLayer1_jst6, 'output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU30to40.root')

    zoom_pt = [0, 150]
    pu_labels = ['0PU', 'PU0to10', 'PU15to25', 'PU30to40']


    def setup_new_graphs(old_graphs, name_dict):
        """Rename"""
        new_graphs = deepcopy(old_graphs)
        for ng, og in izip(new_graphs, old_graphs):
            ng.obj_name = og.obj_name.format(**name_dict)
        return new_graphs


    def compare_PU_by_eta_bins(graphs, title, oDir, ylim=None, lowpt_zoom=True):
        """Plot graph contributions, with a different plot for each eta bin.

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
        for i, (eta_min, eta_max) in enumerate(pairwise(binning.eta_bins)):
            rename_dict = dict(eta_min=eta_min, eta_max=eta_max)
            # make a copy as we have to change the graph names
            new_graphs = setup_new_graphs(graphs, rename_dict)

            if not ylim:
                ylim = [0.5, 3.5] if eta_min > 2 else [0.5, 4]
            p = Plot(contributions=new_graphs, what="graph", xtitle="<p_{T}^{L1}>",
                     ytitle="Correction value (= 1/response)",
                     title=title.format(**rename_dict), ylim=ylim)
            p.plot()
            p.save(os.path.join(oDir, "compare_PU_eta_%g_%g.pdf" % (eta_min, eta_max)))

            if lowpt_zoom:
                # zoom in on low pT
                p = Plot(contributions=new_graphs, what="graph", xtitle="<p_{T}^{L1}>",
                         ytitle="Correction value (= 1/response)",
                         title=title.format(**rename_dict), xlim=zoom_pt, ylim=ylim)
                p.plot()
                p.save(os.path.join(oDir, "compare_PU_eta_%g_%g_pTzoomed.pdf" % (eta_min, eta_max)))

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
        for (eta_min, eta_max) in pairwise(binning.eta_bins):
            rename_dict = dict(eta_min=eta_min, eta_max=eta_max)
            new_graphs_list = [setup_new_graphs(g, rename_dict) for g in graphs_list]

            if not ylim:
                ylim = [0.5, 3.5] if eta_min > 2 else [0.5, 4]
            for i, pu_label in enumerate(pu_labels):
                rename_dict['pu_label'] = pu_label
                p = Plot(contributions=[ng[i] for ng in new_graphs_list], what="graph",
                         xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                         title=title.format(**rename_dict), ylim=ylim)
                p.plot()
                p.save(os.path.join(oDir, "compare_%s_eta_%g_%g_%s.pdf" % (file_identifier, eta_min, eta_max, pu_label)))
                if lowpt_zoom:
                    # zoom in on low pT
                    p = Plot(contributions=[ng[i] for ng in new_graphs_list], what="graph",
                             xtitle="<p_{T}^{L1}>", ytitle="Correction value (= 1/response)",
                             title=title.format(**rename_dict), xlim=zoom_pt, ylim=ylim)
                    p.plot()
                    p.save(os.path.join(oDir, "compare_%s_eta_%g_%g_%s_pTzoomed.pdf" % (file_identifier, eta_min, eta_max, pu_label)))

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

    # common object name
    corr_eta_graph_name = "l1corr_eta_{eta_min:g}_{eta_max:g}"

    # --------------------------------------------------------------------
    # New Stage 2 curves
    # Plot different PU scenarios for given eta bin
    # --------------------------------------------------------------------
    graphs = [
        Contribution(file_name=f_0PU_new, obj_name=corr_eta_graph_name,
                     label="0PU", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]
    """
    title = "Spring15 MC, no JEC, Stage 2, {pu_label}"
    compare_eta_by_pu_bins(graphs, pu_labels, title, s2_new, lowpt_zoom=True)
    compare_PU_by_eta_bins(graphs, title, s2_new, lowpt_zoom=True)
    """

    """
    # --------------------------------------------------------------------
    # New vs Old curves
    # --------------------------------------------------------------------
    new_graphs = [
        # Contribution(file_name=f_0PU_new, obj_name=corr_eta_graph_name,
        #              label="0PU (800pre5)", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (800pre5)", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (800pre5)", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (800pre5)", line_color=colors[3], marker_color=colors[3])
    ]

    old_graphs = [
        # Contribution(file_name=f_0PU_old, obj_name=corr_eta_graph_name,
        #              label="0PU (760pre7)", line_style=2, line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_old, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (760pre7)", line_style=2, line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_old, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (760pre7)", line_style=2, line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_old, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (760pre7)", line_style=2, line_color=colors[3], marker_color=colors[3])
    ]
    title = "Spring15 MC, no JEC, Stage 2, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_by_eta_pu_bins([new_graphs, old_graphs], '800pre5_760pre7', pu_labels, title, s2_new)
    """

    """
    # --------------------------------------------------------------------
    # Min PUS vs max PUS curves
    # --------------------------------------------------------------------
    minPUS_graphs = [
        Contribution(file_name=f_PU0to10_new, obj_name="l1corr_eta_{eta_ming:g}_{eta_max:g}",
                     label="PU: 0 - 10 (min PUS)", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name="l1corr_eta_{eta_ming:g}_{eta_max:g}",
                     label="PU: 15 - 25 (min PUS)", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name="l1corr_eta_{eta_ming:g}_{eta_max:g}",
                     label="PU: 30 - 40 (min PUS)", line_color=colors[3], marker_color=colors[3])
    ]

    maxPUS_graphs = [
        Contribution(file_name=f_PU0to10_maxPUS, obj_name="l1corr_eta_{eta_ming:g}_{eta_max:g}",
                     label="PU: 0 - 10 (max PUS)", line_style=2, line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_maxPUS, obj_name="l1corr_eta_{eta_ming:g}_{eta_max:g}",
                     label="PU: 15 - 25 (max PUS)", line_style=2, line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_maxPUS, obj_name="l1corr_eta_{eta_ming:g}_{eta_max:g}",
                     label="PU: 30 - 40 (max PUS)", line_style=2, line_color=colors[3], marker_color=colors[3])
    ]
    title = "Spring15 MC, no JEC, Stage 2, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_by_eta_pu_bins([minPUS_graphs, maxPUS_graphs], 'minPUS_maxPUS', title, s2_maxPUS)
    """

    """
    # --------------------------------------------------------------------
    # Plot diff PU scenarios for given eta bin, for max PUS ntuples
    # --------------------------------------------------------------------
    graphs = [
        Contribution(file_name=f_PU0to10_maxPUS, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_maxPUS, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_maxPUS, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]
    title = "Spring15 MC, no JEC, Stage 2, max PUS, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, s2_maxPUS, lowpt_zoom=True)
    """

    """
    # --------------------------------------------------------------------
    # New Stage 2 curves for DATA
    # Plot different PU scenarios for given eta bin
    # --------------------------------------------------------------------
    graphs = [
        Contribution(file_name=f_PU0to5_data, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 5", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU8to12_data, obj_name=corr_eta_graph_name,
                     label="PU: 8 - 12", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU15to25_data, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[3], marker_color=colors[3]),
        Contribution(file_name=f_allPU_data, obj_name=corr_eta_graph_name,
                     label="All PU", line_color=colors[4], marker_color=colors[4])
    ]
    title = "Run 260627 (SingleMu, no JEC, TightLepVeto + elMult0 + muMult0), Stage 2, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, s2_data, lowpt_zoom=True)
    """

    """
    # --------------------------------------------------------------------
    # DATA vs MC (L1-Gen) curves (all PU for data, PU binned for MC)
    # --------------------------------------------------------------------
    graphs = [
        Contribution(file_name=f_allPU_data, obj_name=corr_eta_graph_name,
                     label="DATA: All PU (<nVtx> ~ 10)", line_color=colors[4], marker_color=colors[4]),
        Contribution(file_name=f_0PU_new, obj_name=corr_eta_graph_name,
                     label="MC, 0PU", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
                     label="MC, PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
                     label="MC, PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
                     label="MC, PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]
    title = "Run 260627 (SingleMu, no JEC, TightLepVeto + elMult0 + muMult0) VS Spring 15 QCD MC L1 vs GenJet, Stage 2, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, s2_data, lowpt_zoom=True)
    """

    """
    # --------------------------------------------------------------------
    # DATA vs MC (L1-PF) curves (all PU for data, PU binned for MC)
    # --------------------------------------------------------------------
    graphs = [
        Contribution(file_name=f_allPU_data, obj_name=corr_eta_graph_name,
                     label="DATA: All PU (<nVtx> ~ 10)", line_color=colors[4], marker_color=colors[4]),
        Contribution(file_name=f_PU0to10_L1PF, obj_name=corr_eta_graph_name,
                     label="MC, PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_L1PF, obj_name=corr_eta_graph_name,
                     label="MC, PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_L1PF, obj_name=corr_eta_graph_name,
                     label="MC, PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]
    title = "Run 260627 (SingleMu, no JEC, TightLepVeto + elMult0 + muMult0) VS Spring 15 QCD MC L1 vs PF, Stage 2, L1 vs PF, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_PU_by_eta_bins(graphs, title, s2_data, lowpt_zoom=True)
    """

    """
    # --------------------------------------------------------------------
    # L1-Gen vs L1-PF curves
    # --------------------------------------------------------------------
    L1Gen_graphs = [
        Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (L1-Gen)", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (L1-Gen)", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (L1-Gen)", line_color=colors[3], marker_color=colors[3])
    ]

    L1PF_graphs = [
        Contribution(file_name=f_PU0to10_L1PF, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10 (L1-PF)", line_style=2, line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_L1PF, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25 (L1-PF)", line_style=2, line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_L1PF, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40 (L1-PF)", line_style=2, line_color=colors[3], marker_color=colors[3])
    ]
    title = "Spring15 MC, no L1JEC, Stage 2, no PF JetID, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_by_eta_pu_bins([L1Gen_graphs, L1PF_graphs], 'L1Gen_L1PF', pu_labels, title, s2_L1PF)
    """

    """
    # --------------------------------------------------------------------
    # Spring15 vs Fall15, dummy Layer 1
    # --------------------------------------------------------------------
    spring15_graphs = [
        Contribution(file_name=f_0PU_new, obj_name=corr_eta_graph_name,
                     label="Spring15 (0PU)", line_color=colors[0], marker_color=colors[0]),
        # Contribution(file_name=f_PU0to10_new, obj_name=corr_eta_graph_name,
        #              label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        # Contribution(file_name=f_PU15to25_new, obj_name=corr_eta_graph_name,
        #              label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        # Contribution(file_name=f_PU30to40_new, obj_name=corr_eta_graph_name,
        #              label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]

    fall15_graphs = [
        Contribution(file_name=f_PU0_fall15_dummyLayer1, obj_name=corr_eta_graph_name,
                     label="Fall15 (0PU)", line_style=2, line_color=colors[0], marker_color=colors[0]),
        # Contribution(file_name=f_PU0to10_L1PF, obj_name=corr_eta_graph_name,
        #              label="PU: 0 - 10 (L1-PF)", line_style=2, line_color=colors[1], marker_color=colors[1]),
        # Contribution(file_name=f_PU15to25_L1PF, obj_name=corr_eta_graph_name,
        #              label="PU: 15 - 25 (L1-PF)", line_style=2, line_color=colors[2], marker_color=colors[2]),
        # Contribution(file_name=f_PU30to40_L1PF, obj_name=corr_eta_graph_name,
        #              label="PU: 30 - 40 (L1-PF)", line_style=2, line_color=colors[3], marker_color=colors[3])
    ]
    title = "Spring15 vs Fall15 MC, no L1JEC, dummy Layer1, Stage 2, {eta_min:g} < |#eta| < {eta_max:g}"
    compare_by_eta_pu_bins([spring15_graphs, fall15_graphs], 'spring15_fall15', pu_labels, title, s2_fall15_dummyLayer1)
    """

    # -------------------------------------------------------------------
    # Compare PU bins for diff Jet Seed Thresholds
    # -------------------------------------------------------------------
    fall15_jst2_graphs = [
        Contribution(file_name=f_0PU_fall15_newLayer1_jst2, obj_name=corr_eta_graph_name,
                     label="0PU", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_fall15_newLayer1_jst2, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_fall15_newLayer1_jst2, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_fall15_newLayer1_jst2, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]

    fall15_jst3_graphs = [
        Contribution(file_name=f_0PU_fall15_newLayer1_jst3, obj_name=corr_eta_graph_name,
                     label="0PU", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_fall15_newLayer1_jst3, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_fall15_newLayer1_jst3, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_fall15_newLayer1_jst3, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]

    fall15_jst4_graphs = [
        Contribution(file_name=f_0PU_fall15_newLayer1_jst4, obj_name=corr_eta_graph_name,
                     label="0PU", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_fall15_newLayer1_jst4, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_fall15_newLayer1_jst4, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_fall15_newLayer1_jst4, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]

    fall15_jst5_graphs = [
        Contribution(file_name=f_0PU_fall15_newLayer1_jst5, obj_name=corr_eta_graph_name,
                     label="0PU", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_fall15_newLayer1_jst5, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_fall15_newLayer1_jst5, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_fall15_newLayer1_jst5, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]

    fall15_jst6_graphs = [
        Contribution(file_name=f_0PU_fall15_newLayer1_jst6, obj_name=corr_eta_graph_name,
                     label="0PU", line_color=colors[0], marker_color=colors[0]),
        Contribution(file_name=f_PU0to10_fall15_newLayer1_jst6, obj_name=corr_eta_graph_name,
                     label="PU: 0 - 10", line_color=colors[1], marker_color=colors[1]),
        Contribution(file_name=f_PU15to25_fall15_newLayer1_jst6, obj_name=corr_eta_graph_name,
                     label="PU: 15 - 25", line_color=colors[2], marker_color=colors[2]),
        Contribution(file_name=f_PU30to40_fall15_newLayer1_jst6, obj_name=corr_eta_graph_name,
                     label="PU: 30 - 40", line_color=colors[3], marker_color=colors[3])
    ]

    fall15_layer1_jst2_dict = {'graphs': fall15_jst2_graphs, 'jst': 2, 'oDir': s2_fall15_newLayer1_jst2}
    fall15_layer1_jst3_dict = {'graphs': fall15_jst3_graphs, 'jst': 3, 'oDir': s2_fall15_newLayer1_jst3}
    fall15_layer1_jst4_dict = {'graphs': fall15_jst4_graphs, 'jst': 4, 'oDir': s2_fall15_newLayer1_jst4}
    fall15_layer1_jst5_dict = {'graphs': fall15_jst5_graphs, 'jst': 5, 'oDir': s2_fall15_newLayer1_jst5}
    fall15_layer1_jst6_dict = {'graphs': fall15_jst6_graphs, 'jst': 6, 'oDir': s2_fall15_newLayer1_jst6}
    fall15_layer1_jst_graphs = [fall15_layer1_jst2_dict, fall15_layer1_jst3_dict, fall15_layer1_jst4_dict, fall15_layer1_jst5_dict, fall15_layer1_jst6_dict]

    for jst_dict in fall15_layer1_jst_graphs:
        # Compare all PU for a given eta, JST bin
        title = "Fall15 MC, no L1JEC, bitwise Layer 1 + tower calibs, jet seed threshold %d GeV, {eta_min:g} < |#eta| < {eta_max:g}" % (jst_dict['jst'])
        compare_PU_by_eta_bins(jst_dict['graphs'], title, jst_dict['oDir'], lowpt_zoom=True)
        # Compare all eta for a given JST, PU bin
        title = "Fall15 MC, no L1JEC, bitwise Layer 1 + tower calibs, jet seed threshold %d GeV, {pu_label}" % (jst_dict['jst'])
        compare_eta_by_pu_bins(jst_dict['graphs'], pu_labels, title, jst_dict['oDir'], lowpt_zoom=True)

    # Relabel contributions, change up colours
    for i, jst_dict in enumerate(fall15_layer1_jst_graphs, 1):
        for contribution in jst_dict['graphs']:
            contribution.label = '(JST %d GeV)' % jst_dict['jst']
            contribution.line_color = colors[-i]
            contribution.marker_color = colors[-i]

    # Compare all JST for a given eta, PU bin
    title = "Fall15 MC, no L1JEC, bitwise Layer 1 + tower calibs, {eta_min:g} < |#eta| < {eta_max:g}"
    all_jst_graphs = [fall15_jst2_graphs, fall15_jst3_graphs, fall15_jst4_graphs, fall15_jst5_graphs, fall15_jst6_graphs]
    compare_by_eta_pu_bins(all_jst_graphs, 'jst2to6', pu_labels, title,
        '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jstCompare_RAWONLY')

    # -------------------------------------------------------------------
    # Compare Spring15 with Fall15+layer1 calibs
    # -------------------------------------------------------------------
    title = "Spring15 MC vs Fall 15 MC with Layer 1 calibs"
    # change up the labels to avoid repetition of PU label
    for pu_ind, pu in enumerate(pu_labels):
        graphs[pu_ind].label += ' (Spring 15)'
        for glist in all_jst_graphs:
            glist[pu_ind].label += ' (Fall 15)'
    compare_by_eta_pu_bins([graphs] + all_jst_graphs, 'spring15_fall15', pu_labels, title,
        '/users/ra12451/L1JEC/CMSSW_8_0_2/src/L1Trigger/L1JetEnergyCorrections/Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jstCompare_RAWONLY')

if __name__ == "__main__":
    compare()
