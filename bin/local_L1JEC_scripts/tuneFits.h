#include "TFile.h"
#include "TF1.h"
#include "TGraphErrors.h"
#include "TAxis.h"
#include <iostream>
#include <TCanvas.h>
#include <vector>

// to use the class
// #include "/users/jt15104/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/tuneFits.h"
// 
// good idea to compile it to find the errors
//  $ .L /users/jt15104/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/tuneFits.h+
//  also works fine (probs my preferred method)

// HOW TO USE
// pass it a .root file name containing the fits
// pass it the eta range we wish to massage
// see if you can get a better looking fit
// if so save...and it will update the .root file

// note: currently if you work on a test file you cannot get the new fits to the total appended file
// you would have to go again:(

// The format for the etaRange: "2.65_3.139"
// note: might want to change the setting for how the graph range is done, okay for now

// DO NOT USE THE INITIAL COPIES!!!

class tuneFits{

	TFile * file;
	TGraphErrors * graph;
	TF1 * newFit;
	double xmin_init; // initial
	double xmax_init;
	double xmin_rec; // most recent
	double xmax_rec;
	string etaRangeLabel;	

public:
	void setup(string,string);
	void redoFit(double,double);
	void save();
};

void tuneFits::setup(string inputRootFileName, string etaRange)
{
	file = TFile::Open(inputRootFileName.c_str(), "update");

	etaRangeLabel = etaRange;

	string graphNameGrab = "l1corr_eta_" + etaRangeLabel;
	graph = (TGraphErrors*)file->Get(graphNameGrab.c_str());
	string graphNameUse = "l1corr_eta_" + etaRangeLabel + "_fit";
	graph->SetName(graphNameUse.c_str());

	string fitName = "fitfcneta_" + etaRangeLabel;
	TF1 * oldFit = (TF1*)file->Get(fitName.c_str());
	xmin_init = oldFit->GetXmin();
	xmax_init = oldFit->GetXmax();
	cout << endl;
	cout << "eta range = " + etaRangeLabel << endl;
	cout << "oldFit parameters: " << endl;
	cout << "p0: " << oldFit->GetParameter(0) << endl;
	cout << "p1: " << oldFit->GetParameter(1) << endl;
	cout << "p2: " << oldFit->GetParameter(2) << endl;
	cout << "p3: " << oldFit->GetParameter(3) << endl;
	cout << "p4: " << oldFit->GetParameter(4) << endl;
	cout << "p5: " << oldFit->GetParameter(5) << endl;
	cout << "p6: " << oldFit->GetParameter(6) << endl;
	cout << "oldFit xmin: " << xmin_init << endl;
	cout << "oldFit xmax: " << xmax_init << endl << endl;					

	newFit = new TF1("newFit", "[0]+[1]*TMath::Erf([2]*(log10(x)-[3])+[4]*exp([5]*(log10(x)-[6])*(log10(x)-[6])))");
	newFit->SetParameter(0, oldFit->GetParameter(0));
	newFit->SetParameter(1, oldFit->GetParameter(1));
	newFit->SetParameter(2, oldFit->GetParameter(2));
	newFit->SetParameter(3, oldFit->GetParameter(3));
	newFit->SetParameter(4, oldFit->GetParameter(4));
	newFit->SetParameter(5, oldFit->GetParameter(5));
	newFit->SetParameter(6, oldFit->GetParameter(6));
	// the 'browser range' you select here will be used going forward
	graph->Draw();
	oldFit->Draw("same");
	return;						
}


void tuneFits::redoFit(double posRelToXmin, double posRelToXmax)
{
	xmin_rec = xmin_init + posRelToXmin;
	xmax_rec = xmax_init + posRelToXmax;

	cout << endl << "Fitting between the ranges: " << xmin_rec << " and " << xmax_rec << endl << endl;
	graph->Fit(newFit, "", "", xmin_rec, xmax_rec);
	cout << endl;
	graph->Draw("AL");
}


// replaces the fit and graph&fit in the .root file
void tuneFits::save()
{ 
	// set the ranges to the fit range(ish)
	graph->GetXaxis()->SetRangeUser(0,xmax_rec); // will use the y-axis of how you were looking at it
	// Not as simple for a function
	string fitName = "fitfcneta_" + etaRangeLabel;
	TF1 * saveNewFit = new TF1(fitName.c_str(), "[0]+[1]*TMath::Erf([2]*(log10(x)-[3])+[4]*exp([5]*(log10(x)-[6])*(log10(x)-[6])))", xmin_rec, xmax_rec);
	saveNewFit->SetParameter(0, newFit->GetParameter(0));
	saveNewFit->SetParameter(1, newFit->GetParameter(1));
	saveNewFit->SetParameter(2, newFit->GetParameter(2));
	saveNewFit->SetParameter(3, newFit->GetParameter(3));
	saveNewFit->SetParameter(4, newFit->GetParameter(4));
	saveNewFit->SetParameter(5, newFit->GetParameter(5));
	saveNewFit->SetParameter(6, newFit->GetParameter(6));

	string graphNameUse = "l1corr_eta_" + etaRangeLabel + "_fit";
	string graphNameDel = graphNameUse + ";1";
	file->Delete(graphNameDel.c_str());
	string fitNameDel = fitName + ";1";
	file->Delete(fitNameDel.c_str());
	graph->Write();
	saveNewFit->Write();
	file->Close();
}

// remember to use these objects to help you
// IMPORT THESE OBJECTS FOR EASY INTERACTIVE RUNNING
string etaNames[16] = {"0_0.435", "0.435_0.783", "0.783_1.131", "1.131_1.305", "1.305_1.479", "1.479_1.653", "1.653_1.83", "1.83_1.93", "1.93_2.043", "2.043_2.172", "2.172_2.322", "2.322_2.5", "2.5_2.964", "2.964_3.489", "3.489_4.191", "4.191_5.191"}; 
tuneFits t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15;
