#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "TBranch.h"
#include "TLegend.h"
#include "TStyle.h"
#include <TCanvas.h>
#include <iostream>
#include <string>

// script for plotting useful dr information about the matched pairs
// output's pdfs with figures of interest
// 
// TO RUN: just set the input and output directory
// $ root -q -b -l "/users/jt15104/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/dr_info_plots.cxx+"

void dr_info_plots(){

	std::string inputPairsFile = "/hdfs/L1JEC/CMSSW_8_0_9/QCDFlatFall15PU0to50NzshcalRaw_genEmu_30June2016_809v70_noJEC_893ca/pairs/pairs_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p4.root";
	std::string outputDirectory = "~/local_L1JEC_store/dr_plots/QCDFlatFall15PU0to50NzshcalRaw_genEmu_30June2016_809v70_noJEC_893ca_dr0p4/";

	TFile * f = new TFile(inputPairsFile.c_str());
	TTree * t = (TTree*)f->Get("valid");

	TH1F * h0 = new TH1F("h0", "dR: p_{T}^{L1}>0 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h5 = new TH1F("h5", "dR: p_{T}^{L1}>5 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h10 = new TH1F("h10", "dR: p_{T}^{L1}>10 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h15 = new TH1F("h15", "dR: p_{T}^{L1}>15 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h20 = new TH1F("h20", "dR: p_{T}^{L1}>20 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h25 = new TH1F("h25", "dR: p_{T}^{L1}>25 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h30 = new TH1F("h30", "dR: p_{T}^{L1}>30 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h40 = new TH1F("h40", "dR: p_{T}^{L1}>40 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h50 = new TH1F("h50", "dR: p_{T}^{L1}>50 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h70 = new TH1F("h70", "dR: p_{T}^{L1}>70 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h100 = new TH1F("h100", "dR: p_{T}^{L1}>100 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h200 = new TH1F("h200", "dR: p_{T}^{L1}>200 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h500 = new TH1F("h500", "dR: p_{T}^{L1}>500 GeV; dR; a.u.", 100, 0, 0.4);

	TH1F * h0t5 = new TH1F("h0t5", "dR: 0<p_{T}^{L1}<=5 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h5t10 = new TH1F("h5t10", "dR: 5<p_{T}^{L1}<=10 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h10t15 = new TH1F("h10t15", "dR: 10<p_{T}^{L1}<=15 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h15t20 = new TH1F("h15t20", "dR: 15<p_{T}^{L1}<=20 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h20t25 = new TH1F("h20t25", "dR: 20<p_{T}^{L1}<=25 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h25t30 = new TH1F("h25t30", "dR: 25<p_{T}^{L1}<=30 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h30t40 = new TH1F("h30t40", "dR: 30<p_{T}^{L1}<=40 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h40t50 = new TH1F("h40t50", "dR: 40<p_{T}^{L1}<=50 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h50t70 = new TH1F("h50t70", "dR: 50<p_{T}^{L1}<=70 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h70t100 = new TH1F("h70t100", "dR: 70<p_{T}^{L1}<=100 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h100t200 = new TH1F("h100t200", "dR: 100<p_{T}^{L1}<=200 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h200t500 = new TH1F("h200t500", "dR: 200<p_{T}^{L1}<=500 GeV; dR; a.u.", 100, 0, 0.4);
	TH1F * h500t1000 = new TH1F("h500t1000", "dR: 500<p_{T}^{L1}<=1000 GeV; dR; a.u.", 100, 0, 0.4);


	Int_t nentries = (Int_t)t->GetEntries();
	Float_t dr = 0;
	t->SetBranchAddress("dr", &dr);
	Float_t pt = 0;
	t->SetBranchAddress("pt", &pt);

	for (Int_t i=0; i<nentries; i++){

		if (i % 1000000 == 0) std::cout << "done " << i << " out of " << nentries << " entries" << std::endl;
		t->GetEntry(i);

		h0->Fill(dr);
		if (pt > 5) h5->Fill(dr);
		if (pt > 10) h10->Fill(dr);
		if (pt > 15) h15->Fill(dr);
		if (pt > 20) h20->Fill(dr);
		if (pt > 25) h25->Fill(dr);
		if (pt > 30) h30->Fill(dr);
		if (pt > 40) h40->Fill(dr);
		if (pt > 50) h50->Fill(dr);
		if (pt > 70) h70->Fill(dr);
		if (pt > 100) h100->Fill(dr);
		if (pt > 200) h200->Fill(dr);
		if (pt > 500) h500->Fill(dr);
	
		if (pt <= 5) h0t5->Fill(dr);
		if (pt > 5 && pt <= 10) h5t10->Fill(dr);
		if (pt > 10 && pt <= 15) h10t15->Fill(dr);
		if (pt > 15 && pt <= 20) h15t20->Fill(dr);
		if (pt > 20 && pt <= 25) h20t25->Fill(dr);
		if (pt > 25 && pt <= 30) h25t30->Fill(dr);
		if (pt > 30 && pt <= 40) h30t40->Fill(dr);
		if (pt > 40 && pt <= 50) h40t50->Fill(dr);
		if (pt > 50 && pt <= 70) h50t70->Fill(dr);
		if (pt > 70 && pt <= 100) h70t100->Fill(dr);
		if (pt > 100 && pt <= 200) h100t200->Fill(dr);
		if (pt > 200 && pt <= 500) h200t500->Fill(dr);
		if (pt > 500 && pt <= 1000) h500t1000->Fill(dr);
	}

	// normalise the histograms
	h0->Scale(1/h0->Integral());
	h5->Scale(1/h5->Integral());
	h10->Scale(1/h10->Integral());
	h15->Scale(1/h15->Integral());
	h20->Scale(1/h20->Integral());
	h25->Scale(1/h25->Integral());
	h30->Scale(1/h30->Integral());
	h40->Scale(1/h40->Integral());
	h50->Scale(1/h50->Integral());
	h70->Scale(1/h70->Integral());
	h100->Scale(1/h100->Integral());
	h200->Scale(1/h200->Integral());
	h500->Scale(1/h500->Integral());

	h0t5->Scale(1/h0t5->Integral());
	h5t10->Scale(1/h5t10->Integral());
	h10t15->Scale(1/h10t15->Integral());
	h15t20->Scale(1/h15t20->Integral());
	h20t25->Scale(1/h20t25->Integral());
	h25t30->Scale(1/h25t30->Integral());
	h30t40->Scale(1/h30t40->Integral());
	h40t50->Scale(1/h40t50->Integral());
	h50t70->Scale(1/h50t70->Integral());
	h70t100->Scale(1/h70t100->Integral());
	h100t200->Scale(1/h100t200->Integral());
	h200t500->Scale(1/h200t500->Integral());
	h500t1000->Scale(1/h500t1000->Integral());


	std::string histoSaveName = outputDirectory + "histos.root";
	TFile g(histoSaveName.c_str(), "recreate");
	h0->Write();
	h5->Write();
	h10->Write();
	h15->Write();
	h20->Write();
	h25->Write();
	h30->Write();
	h40->Write();
	h50->Write();
	h70->Write();
	h100->Write();
	h200->Write();
	h500->Write();

	h0t5->Write();
	h5t10->Write();
	h10t15->Write();
	h15t20->Write();
	h20t25->Write();
	h25t30->Write();
	h30t40->Write();
	h40t50->Write();
	h50t70->Write();
	h70t100->Write();
	h100t200->Write();
	h200t500->Write();
	h500t1000->Write();






	TCanvas * c3 = new TCanvas("c3", "", 600, 600);
	gStyle->SetOptStat(0);
	h500->SetLineColor(kBlack);
	h200->SetLineColor(kBlue+2);
	h100->SetLineColor(kBlue);
	h70->SetLineColor(kCyan+1);
	h50->SetLineColor(kGreen+2);
	h40->SetLineColor(kGreen);	
	h30->SetLineColor(kYellow+2);
	h25->SetLineColor(kOrange);
	h20->SetLineColor(kOrange+7);
	h15->SetLineColor(kRed+2);	
	h10->SetLineColor(kRed);
	h5->SetLineColor(kMagenta+3);
	h0->SetLineColor(kMagenta);
	h500->Draw();
	h500->SetTitle("");
	h500->GetYaxis()->SetTitle("");	
	h200->Draw("same");
	h100->Draw("same");
	h70->Draw("same");
	h50->Draw("same");
	h40->Draw("same");	
	h30->Draw("same");
	h25->Draw("same");
	h20->Draw("same");
	h15->Draw("same");	
	h10->Draw("same");
	h5->Draw("same");
	h0->Draw("same");
	TLegend * leg3 = new TLegend(0.4,0.5,0.85,0.85);
	leg3->AddEntry(h500,"pt>500GeV");		
	leg3->AddEntry(h200,"pt>200GeV");
	leg3->AddEntry(h100,"pt>100GeV");
	leg3->AddEntry(h70,"pt>70GeV");
	leg3->AddEntry(h50,"pt>50GeV");
	leg3->AddEntry(h40,"pt>40GeV");
	leg3->AddEntry(h30,"pt>30GeV");
	leg3->AddEntry(h25,"pt>25GeV");
	leg3->AddEntry(h20,"pt>20GeV");
	leg3->AddEntry(h15,"pt>15GeV");
	leg3->AddEntry(h10,"pt>10GeV");
	leg3->AddEntry(h5,"pt>5GeV");
	leg3->AddEntry(h0,"pt>0GeV");
	leg3->Draw();		
	std::string saveName3 = outputDirectory + "dr_lowerLimits.pdf";
	c3->SaveAs( saveName3.c_str() );
	c3->Close();	





	TCanvas * c4 = new TCanvas("c4", "", 600, 600);
	gStyle->SetOptStat(0);
	h500t1000->SetLineColor(kBlack);
	h200t500->SetLineColor(kBlue+2);
	h100t200->SetLineColor(kBlue);
	h70t100->SetLineColor(kCyan+1);
	h50t70->SetLineColor(kGreen+2);
	h40t50->SetLineColor(kGreen);	
	h30t40->SetLineColor(kYellow+2);
	h25t30->SetLineColor(kOrange);
	h20t25->SetLineColor(kOrange+7);
	h15t20->SetLineColor(kRed+2);	
	h10t15->SetLineColor(kRed);
	h5t10->SetLineColor(kMagenta+3);
	h0t5->SetLineColor(kMagenta);
	h500t1000->Draw();
	h500t1000->SetTitle("");
	h500t1000->GetYaxis()->SetTitle("");	
	h200t500->Draw("same");
	h100t200->Draw("same");
	h70t100->Draw("same");
	h50t70->Draw("same");
	h40t50->Draw("same");
	h25t30->Draw("same");
	h20t25->Draw("same");
	h15t20->Draw("same");
	h10t15->Draw("same");
	h5t10->Draw("same");
	h0t5->Draw("same");
	TLegend * leg4 = new TLegend(0.4,0.5,0.85,0.85);
	leg4->AddEntry(h500t1000,"500<pt<=1000GeV");
	leg4->AddEntry(h200t500,"200<pt<=500GeV");
	leg4->AddEntry(h100t200,"100<pt<=200GeV");
	leg4->AddEntry(h70t100,"70<pt<=100GeV");
	leg4->AddEntry(h50t70,"50<pt<=70GeV");
	leg4->AddEntry(h40t50,"40<pt<=50GeV");
	leg4->AddEntry(h30t40,"30<pt<=40GeV");
	leg4->AddEntry(h25t30,"25<pt<=30GeV");		
	leg4->AddEntry(h20t25,"20<pt<=25GeV");
	leg4->AddEntry(h15t20,"15<pt<=20GeV");
	leg4->AddEntry(h10t15,"10<pt<=15GeV");
	leg4->AddEntry(h5t10,"5<pt<=10GeV");
	leg4->AddEntry(h0t5,"0<pt<=5GeV");
	leg4->Draw();	
	std::string saveName4 = outputDirectory + "dr_lowerUpperLimits.pdf";
	c4->SaveAs( saveName4.c_str() );
	c4->Close();
}