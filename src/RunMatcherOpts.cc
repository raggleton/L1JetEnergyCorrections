// -*- C++ -*-
//
// Package:     L1Trigger/L1JetEnergyCorrections
// Class  :     RunMatcherOpts
// 
// Implementation:
//     [Notes on implementation]
//
// Original Author:  Robin Cameron Aggleton
//         Created:  Fri, 28 Nov 2014 14:26:39 GMT
//
#include "RunMatcherOpts.h"

// system include files
#include <iostream>

// ROOT include files
#include "TString.h"

// BOOST include
#include <boost/program_options.hpp>

// user include files

using std::cout;
using std::endl;

//
// constants, enums and typedefs
//

//
// static data member definitions
//


/////////////////////////////////
// constructors and destructor //
/////////////////////////////////
RunMatcherOpts::RunMatcherOpts(int argc, char* argv[]):
    input_(""),
    refDir_(""),
    l1Dir_(""),
    output_(""),
    corrFilename_(""),
    nEvents_(-1),
    drawN_(0),
    correctionMinPt_(-1),
    deltaR_(0.3), // Stage2 defaults
    l1MinPt_(0.1),
    refMinPt_(10),
    l1MaxEta_(5.1),
    refMaxEta_(5.1),
    cleanJets_("")
{
    namespace po = boost::program_options;

    po::options_description desc("Allowed options");
    desc.add_options()
        ("help,h", "produce help message & exit")
        ("nEvents,N",
            po::value<int>(&nEvents_)->default_value(nEvents_),
            "number of events to run over. -1 for all.")
        ("input,I",
            po::value<std::string>(&input_)->default_value(input_),
            "input filename")
        ("refDir",
            po::value<std::string>(&refDir_)->default_value(refDir_),
            "reference jet TDirectory in input file")
        ("refBranches",
            po::value<std::vector<std::string>>(&refJetBranchNames_)->multitoken()->default_value(std::vector<std::string>(1,"cenJet"), "cenJet"),
            "reference jet branches in TTree (e.g. cenJet)")
        ("l1Dir",
            po::value<std::string>(&l1Dir_)->default_value(l1Dir_),
            "L1 jet TDirectory in input file")
        ("l1Branches",
            po::value<std::vector<std::string>>(&l1JetBranchNames_)->multitoken()->default_value(std::vector<std::string>(1,"cenJet"), "cenJet"),
            "l1 jet branches in TTree (e.g. cenJet)")
        ("output,O",
            po::value<std::string>(&output_)->default_value(output_),
            "output filename")
        ("correct",
            po::value<std::string>(&corrFilename_),
            "filename of ROOT file with correction functions. " \
            "By default, no corrections are applied. " \
            "If this is set to anything other than \"\", " \
            "it will apply corrections to jets, and then only store values " \
            "for the 4 central and forward jets with highest pT.")
        ("corrMinPt",
            po::value<float>(&correctionMinPt_)->default_value(correctionMinPt_),
            "Minimum L1 jet pT to apply corrections. If < 0, will use whatever " \
            "the fit limits were. Any other positive value will override this.")
        ("draw,d",
            po::value<int>(&drawN_)->default_value(drawN_),
            "number of events to draw 2D eta-phi plot of ref, L1 & matched " \
            "jets (for debugging). Plots saved in $PWD/match_plots." \
            " 0 for no plots.")
        ("deltaR",
            po::value<float>(&deltaR_)->default_value(deltaR_),
            "Maximum deltaR(RefJet, L1 Jet) to consider a match.")
        ("l1MinPt",
            po::value<float>(&l1MinPt_)->default_value(l1MinPt_),
            "Minimum pT for L1 jets")
        ("refMinPt",
            po::value<float>(&refMinPt_)->default_value(refMinPt_),
            "Minimum pT for reference jets")
        ("l1MaxEta",
            po::value<float>(&l1MaxEta_)->default_value(l1MaxEta_),
            "Maximum fabs(eta) for L1 jets")
        ("refMaxEta",
            po::value<float>(&refMaxEta_)->default_value(refMaxEta_),
            "Maximum fabs(eta) for reference jets")
        ("cleanJets",
            po::value<std::string>(&cleanJets_)->default_value(cleanJets_),
            "Specify level of cleaning cuts to apply to reference jets. Only for use on RECO (PF) jets.")
    ;
    po::variables_map vm;
    try {
        po::store(po::parse_command_line(argc, argv, desc), vm);
    } catch (const boost::program_options::unknown_option& e){
        cout << "Unrecognised option " << e.what() << endl;
        cout << desc << endl;
        std::exit(1);
    } catch (const boost::program_options::invalid_option_value& e){
        cout << "Invalid value for option " << e.what() << endl;
        cout << desc << endl;
        std::exit(1);
    }

    po::notify(vm);

    if (vm.count("help")) {
        cout << desc << endl;

        std::exit(1);
    }

    if (vm.count("correct")) {
        cout << "Will apply corrections from file: " << vm["correct"].as<std::string>()
        << " to jets with pT > " << vm["corrMinPt"].as<float>() << endl;
    }

}

// RunMatcherOpts::RunMatcherOpts(const RunMatcherOpts& rhs)
// {
//    // do actual copying here;
// }

RunMatcherOpts::~RunMatcherOpts()
{
}

//
// assignment operators
//
// const RunMatcherOpts& RunMatcherOpts::operator=(const RunMatcherOpts& rhs)
// {
//   //An exception safe implementation is
//   RunMatcherOpts temp(rhs);
//   swap(rhs);
//
//   return *this;
// }

//
// member functions
//

//
// const member functions
//

//
// static member functions
//
