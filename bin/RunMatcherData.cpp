#include <fstream>

// ROOT headers
#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TSystem.h"

// BOOST headers
#include <boost/filesystem.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/predicate.hpp>

// Headers from L1TNtuples
#include "L1Trigger/L1TNtuples/interface/L1AnalysisEventDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoJetDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1UpgradeDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisL1ExtraDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoMetFilterDataFormat.h"
#include "L1Trigger/L1TNtuples/interface/L1AnalysisRecoVertexDataFormat.h"

// Headers from this package
#include "DeltaR_Matcher.h"
#include "commonRootUtils.h"
#include "RunMatcherOpts.h"
#include "JetDrawer.h"
#include "L1GenericTree.h"
#include "runMatcherUtils.h"

using std::cout;
using std::endl;
using L1Analysis::L1AnalysisEventDataFormat;
using L1Analysis::L1AnalysisRecoJetDataFormat;
using L1Analysis::L1AnalysisL1UpgradeDataFormat;
using L1Analysis::L1AnalysisL1ExtraDataFormat;
using L1Analysis::L1AnalysisRecoMetFilterDataFormat;
using L1Analysis::L1AnalysisRecoVertexDataFormat;
using boost::lexical_cast;
namespace fs = boost::filesystem;

/**
 * @brief
 * This version is for running on data, when you want to take L1 jets from the
 * L1Upgrade collection, and reference jets from the RecoTree.
 *
 * @author Robin Aggleton, Nov 2015
 */
int main(int argc, char* argv[]) {

    cout << "Running Matcher for data" << std::endl;

    // deal with user args
    RunMatcherOpts opts(argc, argv);

    ///////////////////////
    // SETUP INPUT FILES //
    ///////////////////////
    // get input TTrees
    // Reco jets
    TString refJetDirectory = opts.refJetDirectory();
    L1GenericTree<L1AnalysisRecoJetDataFormat> refJetTree(opts.inputFilename(),
                                                          "l1JetRecoTree/JetRecoTree",
                                                          "Jet");
    L1AnalysisRecoJetDataFormat * refData = refJetTree.getData();

    // L1 jets
    TString l1JetDirectory = opts.l1JetDirectory();
    L1GenericTree<L1AnalysisL1UpgradeDataFormat> l1JetTree(opts.inputFilename(),
                                                           "l1UpgradeTree/L1UpgradeTree",
                                                           "L1Upgrade");
    L1AnalysisL1UpgradeDataFormat * l1Data = l1JetTree.getData();


    // hold Event tree
    L1GenericTree<L1AnalysisEventDataFormat> eventTree(opts.inputFilename(),
                                                       "l1EventTree/L1EventTree",
                                                       "Event");
    L1AnalysisEventDataFormat * eventData = eventTree.getData();

    // hold met filter info
    L1GenericTree<L1AnalysisRecoMetFilterDataFormat> metFilterTree(opts.inputFilename(),
                                                                   "l1MetFilterRecoTree/MetFilterRecoTree",
                                                                   "MetFilters");
    L1AnalysisRecoMetFilterDataFormat * metFilterData = metFilterTree.getData();

    // hold nVtx info
    L1GenericTree<L1AnalysisRecoVertexDataFormat> recoVtxTree(opts.inputFilename(),
                                                              "l1RecoTree/RecoTree",
                                                               "Vertex");
    L1AnalysisRecoVertexDataFormat * recoVtxData = recoVtxTree.getData();

    // input filename stem (no .root)
    fs::path inPath(opts.inputFilename());
    TString inStem(inPath.stem().c_str());

    ////////////////////////
    // SETUP OUTPUT FILES //
    ////////////////////////

    // setup output file to store results
    // check that we're not overwriting the input file!
    if (opts.outputFilename() == opts.inputFilename()) {
        throw std::runtime_error("Cannot use input filename as output filename!");
    }
    TFile * outFile = openFile(opts.outputFilename(), "RECREATE");
    fs::path outPath(opts.outputFilename());
    TString outDir(outPath.parent_path().c_str());
    if (outDir != "") outDir += "/";

    // setup output tree to store raw variable for quick plotting/debugging
    TTree outTree("valid", "valid");
    // Quantities for L1 jets:
    float out_pt(-1.), out_eta(99.), out_phi(99.);
    int out_nL1(-1); // number of jets in the event,
    outTree.Branch("pt", &out_pt, "pt/F");
    outTree.Branch("eta", &out_eta, "eta/F");
    outTree.Branch("phi", &out_phi, "phi/F");
    outTree.Branch("nL1", &out_nL1, "nL1/I");
    // Quantities for reference jets (GenJet, etc):
    float out_ptRef(-1.), out_etaRef(99.), out_phiRef(99.);
    int out_nRef(-1);
    outTree.Branch("ptRef", &out_ptRef, "ptRef/F");
    outTree.Branch("etaRef", &out_etaRef, "etaRef/F");
    outTree.Branch("phiRef", &out_phiRef, "phiRef/F");
    outTree.Branch("nRef", &out_nRef, "nRef/I");
    // Cleaning vars
    float out_chef(-1.), out_nhef(-1.), out_pef(-1.), out_eef(-1.), out_mef(-1.), out_hfhef(-1.), out_hfemef(-1.);
    short out_chMult(-1), out_nhMult(-1), out_phMult(-1), out_elMult(-1), out_muMult(-1), out_hfhMult(-1), out_hfemMult(-1);
    outTree.Branch("chef", &out_chef, "chef/F");
    outTree.Branch("nhef", &out_nhef, "nhef/F");
    outTree.Branch("pef", &out_pef, "pef/F");
    outTree.Branch("eef", &out_eef, "eef/F");
    outTree.Branch("mef", &out_mef, "mef/F");
    outTree.Branch("hfhef", &out_hfhef, "hfhef/F");
    outTree.Branch("hfemef", &out_hfemef, "hfemef/F");
    outTree.Branch("chMult", &out_chMult, "chMult/S");
    outTree.Branch("nhMult", &out_nhMult, "nhMult/S");
    outTree.Branch("phMult", &out_phMult, "phMult/S");
    outTree.Branch("elMult", &out_elMult, "elMult/S");
    outTree.Branch("muMult", &out_muMult, "muMult/S");
    outTree.Branch("hfhMult", &out_hfhMult, "hfhMult/S");
    outTree.Branch("hfemMult", &out_hfemMult, "hfemMult/S");
    // Quantities to describe relationship between the two:
    float out_rsp(-1.), out_rsp_inv(-1.);
    float out_dr(99.), out_deta(99.), out_dphi(99.);
    float out_ptDiff(99999.), out_resL1(99.), out_resRef(99.);
    int out_nMatches(0);
    outTree.Branch("ptDiff", &out_ptDiff, "ptDiff/F"); // L1 - Ref
    outTree.Branch("rsp", &out_rsp, "rsp/F"); // response = l1 pT/ ref jet pT
    outTree.Branch("rsp_inv", &out_rsp_inv, "rsp_inv/F"); // response = ref pT/ l1 jet pT
    outTree.Branch("dr", &out_dr, "dr/F");
    outTree.Branch("deta", &out_deta, "deta/F");
    outTree.Branch("dphi", &out_dphi, "dphi/F");
    outTree.Branch("resL1", &out_resL1, "resL1/F"); // resolution = L1 - Ref / L1
    outTree.Branch("resRef", &out_resRef, "resRef/F"); // resolution = L1 - Ref / Ref
    outTree.Branch("nMatches", &out_nMatches, "nMatches/Int_t");

    // PU quantities
    float out_trueNumInteractions(-1.), out_numPUVertices(-1.);
    outTree.Branch("trueNumInteractions", &out_trueNumInteractions, "trueNumInteractions/F");
    outTree.Branch("numPUVertices", &out_numPUVertices, "numPUVertices/F");

    // Event info
    ULong64_t out_event(0);
    int out_ls(0);
    outTree.Branch("event", &out_event, "event/l");
    outTree.Branch("LS", &out_ls, "ls/I");

    // triggers
    // bool out_HLT_ZeroBias(true), out_HLT_IsoMu(true), out_HLT_DiMu(true), out_HLT_DiEl(true);
    // bool out_HLT_Physics(true), out_HLT_Random(true), out_HLT_Photon(true), out_HLT_Mu(true);
    // bool out_HLT_MET(true), out_HLT_PFMET(true), out_HLT_HT(true);
    // outTree.Branch("hlt_zeroBias", &out_HLT_ZeroBias, "hlt_zeroBias/Bool_t");
    // outTree.Branch("hlt_isoMu", &out_HLT_IsoMu, "hlt_isoMu/Bool_t");
    // outTree.Branch("hlt_diMu", &out_HLT_DiMu, "hlt_diMu/Bool_t");
    // outTree.Branch("hlt_diEl", &out_HLT_DiEl, "hlt_diEl/Bool_t");
    // outTree.Branch("hlt_physics", &out_HLT_Physics, "hlt_physics/Bool_t");
    // outTree.Branch("hlt_random", &out_HLT_Random, "hlt_random/Bool_t");
    // outTree.Branch("hlt_photon", &out_HLT_Photon, "hlt_photon/Bool_t");
    // outTree.Branch("hlt_mu", &out_HLT_Mu, "hlt_mu/Bool_t");
    // outTree.Branch("hlt_met", &out_HLT_MET, "hlt_met/Bool_t");
    // outTree.Branch("hlt_pfmet", &out_HLT_PFMET, "hlt_pfmet/Bool_t");
    // outTree.Branch("hlt_ht", &out_HLT_HT, "hlt_ht/Bool_t");

    // MET filters
    bool out_passCSC(true);
    bool out_HBHENoise(true), out_HBHEIsoNoise(true);
    outTree.Branch("passCSC", &out_passCSC, "passCSC/Bool_t");
    outTree.Branch("HBHENoise", &out_HBHENoise, "HBHENoise/Bool_t");
    outTree.Branch("HBHEIsoNoise", &out_HBHEIsoNoise, "HBHEIsoNoise/Bool_t");

    Long64_t nEntriesRef = refJetTree.getEntries();
    Long64_t nEntriesL1  = l1JetTree.getEntries();
    Long64_t nEntries(0);
    if (nEntriesRef != nEntriesL1) {
        throw std::range_error("Different number of events in L1 & ref trees");
    } else {
        nEntries = (opts.nEvents() > 0) ? opts.nEvents() : nEntriesL1;
        cout << "Running over " << nEntries << " events." << endl;
    }

    ///////////////////////
    // SETUP JET MATCHER //
    ///////////////////////
    double maxDeltaR(opts.deltaR()), minRefJetPt(opts.refJetMinPt()), maxRefJetPt(5000.);
    double minL1JetPt(opts.l1JetMinPt()), maxL1JetPt(5000.), maxJetEta(5);
    std::unique_ptr<Matcher> matcher(new DeltaR_Matcher(maxDeltaR, minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta));
    std::cout << *matcher << std::endl;

    ///////////////////////
    // JET CLEANING CUTS //
    ///////////////////////
    bool doCleaningCuts = opts.cleanJets() != "";
    if (doCleaningCuts) {
        cout << "Applying " << opts.cleanJets() << " jet cleaning cuts" << endl;
    }

    //////////////////////
    // LOOP OVER EVENTS //
    //////////////////////
    // produce matching pairs and store
    Long64_t drawCounter(0), matchedEvent(0), cscFail(0);
    Long64_t counter(0);
    for (Long64_t iEntry = 0; counter < nEntries; ++iEntry, ++counter) {

        if (counter % 10000 == 0) {
            cout << "Entry: " << iEntry << " at " << getCurrentTime() << endl;
        }

        // Make sure to add any other Trees here!
        if (refJetTree.getEntry(iEntry) < 1 ||
            l1JetTree.getEntry(iEntry) < 1 ||
            eventTree.getEntry(iEntry) < 1 ||
            metFilterTree.getEntry(iEntry) < 1 ||
            recoVtxTree.getEntry(iEntry) < 1)
            break;

        // event info
        out_event = eventData->event;
        out_ls = (Long64_t) eventData->lumi;
        out_numPUVertices = recoVtxData->nVtx;

        // MET filter info
        out_passCSC = metFilterData->cscTightHalo2015Filter;
        if (!out_passCSC) cscFail++;
        out_HBHENoise = metFilterData->hbheNoiseFilter;
        out_HBHEIsoNoise = metFilterData->hbheNoiseIsoFilter;
        if (doCleaningCuts && !(out_passCSC && out_HBHENoise && out_HBHEIsoNoise)) {
            continue;
        }

        // Rescale jet energy fractions to take account of the fact that they are post-JEC
        // rescaleEnergyFractions(refData);

        // Get vectors of ref & L1 jets from trees, only want BX = 0 (the collision)
        std::vector<TLorentzVector> refJets;
        if (doCleaningCuts) {
            refJets = makeRecoTLorentzVectorsCleaned(*refData, opts.cleanJets()); // with JetID filters
        } else {
            refJets = makeTLorentzVectors(refData->etCorr, refData->eta, refData->phi);
        }
        std::vector<TLorentzVector> l1Jets  = makeTLorentzVectors(l1Data->jetEt, l1Data->jetEta, l1Data->jetPhi, l1Data->jetBx);

        out_nL1 = l1Jets.size();
        out_nRef = refJets.size();

        // Pass jets to matcher, do matching
        matcher->setRefJets(refJets);
        matcher->setL1Jets(l1Jets);
        std::vector<MatchedPair> matchResults = matcher->getMatchingPairs();

        if (matchResults.size()>0) matchedEvent++;

        // store L1 & ref jet variables in tree
        out_nMatches = matchResults.size();
        for (const auto &it: matchResults) {
            // std::cout << it << std::endl;
            out_pt = it.l1Jet().Et();
            out_eta = it.l1Jet().Eta();
            out_phi = it.l1Jet().Phi();
            out_rsp = it.l1Jet().Et()/it.refJet().Et();
            out_rsp_inv =  it.refJet().Et()/it.l1Jet().Et();
            out_dr = it.refJet().DeltaR(it.l1Jet());
            out_deta = it.refJet().Eta() - it.l1Jet().Eta();
            out_dphi = it.refJet().DeltaPhi(it.l1Jet());
            out_ptRef = it.refJet().Pt();
            out_etaRef = it.refJet().Eta();
            out_phiRef = it.refJet().Phi();
            out_ptDiff = it.l1Jet().Et() - it.refJet().Et();
            out_resL1 = out_ptDiff/it.l1Jet().Et();
            out_resRef = out_ptDiff/it.refJet().Et();

            int rInd = findRecoJetIndex(out_ptRef, out_etaRef, out_phiRef, *refData);
            if (rInd < 0) throw std::range_error("No RecoJet");
            out_chef = refData->chef[rInd];
            out_nhef = refData->nhef[rInd];
            out_pef = refData->pef[rInd];
            out_eef = refData->eef[rInd];
            out_mef = refData->mef[rInd];
            out_hfhef = refData->hfhef[rInd];
            out_hfemef = refData->hfemef[rInd];
            out_chMult = refData->chMult[rInd];
            out_nhMult = refData->nhMult[rInd];
            out_phMult = refData->phMult[rInd];
            out_elMult = refData->elMult[rInd];
            out_muMult = refData->muMult[rInd];
            out_hfhMult = refData->hfhMult[rInd];
            out_hfemMult = refData->hfemMult[rInd];

            // hack on some cuts as to whether we should save for this matched pair
            // we want to keep the final file size down
            // if ( fabs(it.l1Jet().Eta())>3.00 ) // only look at forward jets
            outTree.Fill();
        }

        // debugging plot - plots eta vs phi of jets
        if (drawCounter < opts.drawNumber()) {
            if (matchResults.size() > 0) {
                TString label = TString::Format(
                    "%.1f < E^{gen}_{T} < %.1f GeV, " \
                    "L1 jet %.1f < E^{L1}_{T} < %.1f GeV, |#eta_{jet}| < %.1f",
                    minRefJetPt, maxRefJetPt, minL1JetPt, maxL1JetPt, maxJetEta);
                // get jets post pT, eta cuts
                JetDrawer drawer(matcher->getRefJets(), matcher->getL1Jets(), matchResults, label);

                TString pdfname = TString::Format("%splots_%s_%s_%s/jets_%lld.pdf",
                    outDir.Data(), inStem.Data(), "reco", "l1", iEntry);
                drawer.drawAndSave(pdfname);

                drawCounter++;
            }
        }
    }

    // save tree to new file and cleanup
    outTree.Write("", TObject::kOverwrite);
    outFile->Close();
    cout << matchedEvent << " events had 1+ matches, out of " << nEntries << endl;
    cout << cscFail << " events failed CSC check, out of " << nEntries << endl;
    return 0;
}
