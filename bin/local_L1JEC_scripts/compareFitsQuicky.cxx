#include "TFile.h"
#include "TF1.h"
#include <iostream>
#include "TLegend.h"
#include "TStyle.h"
#include "TAxis.h"
#include <TCanvas.h>

// script for plotting all fits for all eta bins together
// good for studying variation with eta
// 
// TO RUN: just set the directory, and the input and output files
// $ root -q -b -l "/users/jt15104/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/compareFitsQuicky.cxx+"

void makePlots_allTTetaBinning(std::string,std::string,std::string);
void makePlots_sel16etaBinning(std::string,std::string,std::string);

void compareFitsQuicky(){

	std::string directory = "/users/jt15104/local_L1JEC_store/30June2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_809v70_noJEC_893ca_etaBinsSel16/runCalib_jetMetFitErr/";
	
	std::string addOnInfo = "_sel16";

	std::string inputFile1 = "fitsPU0to10.root";
	std::string outputName1 = "plotFitsPU0to10" + addOnInfo + ".pdf";

	std::string inputFile2 = "fitsPU15to25.root";
	std::string outputName2 = "plotFitsPU15to25" + addOnInfo + ".pdf";

	std::string inputFile3 = "fitsPU30to40.root";
	std::string outputName3 = "plotFitsPU30to40" + addOnInfo + ".pdf";

	std::string inputFile4 = "fitsPU45to55.root";
	std::string outputName4 = "plotFitsPU45to55" + addOnInfo + ".pdf";

	// makePlots_allTTetaBinning(inputFile1, outputName1, directory);
	// makePlots_allTTetaBinning(inputFile2, outputName2, directory);
	// makePlots_allTTetaBinning(inputFile3, outputName3, directory);
	// makePlots_allTTetaBinning(inputFile4, outputName4, directory);

	// makePlots_sel16etaBinning(inputFile1, outputName1, directory);
	// makePlots_sel16etaBinning(inputFile2, outputName2, directory);
	makePlots_sel16etaBinning(inputFile3, outputName3, directory);
	// makePlots_sel16etaBinning(inputFile4, outputName4, directory);	
}

void makePlots_allTTetaBinning(std::string inputFile, std::string outputFile, std::string directory){

	std::string inputPath = directory + inputFile;
	std::string outputPath = directory + outputFile;

	TFile * f = TFile::Open(inputPath.c_str());

	TF1 * g01 = (TF1*)f->Get("fitfcneta_0_0.087");
	TF1 * g02 = (TF1*)f->Get("fitfcneta_0.087_0.174");
	TF1 * g03 = (TF1*)f->Get("fitfcneta_0.174_0.261");
	TF1 * g04 = (TF1*)f->Get("fitfcneta_0.261_0.348");
	TF1 * g05 = (TF1*)f->Get("fitfcneta_0.348_0.435");
	TF1 * g06 = (TF1*)f->Get("fitfcneta_0.435_0.522");
	TF1 * g07 = (TF1*)f->Get("fitfcneta_0.522_0.609");
	TF1 * g08 = (TF1*)f->Get("fitfcneta_0.609_0.696");
	TF1 * g09 = (TF1*)f->Get("fitfcneta_0.696_0.783");
	TF1 * g10 = (TF1*)f->Get("fitfcneta_0.783_0.87");
	TF1 * g11 = (TF1*)f->Get("fitfcneta_0.87_0.957");
	TF1 * g12 = (TF1*)f->Get("fitfcneta_0.957_1.044");
	TF1 * g13 = (TF1*)f->Get("fitfcneta_1.044_1.131");
	TF1 * g14 = (TF1*)f->Get("fitfcneta_1.131_1.218");
	TF1 * g15 = (TF1*)f->Get("fitfcneta_1.218_1.305");
	TF1 * g16 = (TF1*)f->Get("fitfcneta_1.305_1.392");
	TF1 * g17 = (TF1*)f->Get("fitfcneta_1.392_1.479");
	TF1 * g18 = (TF1*)f->Get("fitfcneta_1.479_1.566");
	TF1 * g19 = (TF1*)f->Get("fitfcneta_1.566_1.653");
	TF1 * g20 = (TF1*)f->Get("fitfcneta_1.653_1.74");
	TF1 * g21 = (TF1*)f->Get("fitfcneta_1.74_1.83");
	TF1 * g22 = (TF1*)f->Get("fitfcneta_1.83_1.93");
	TF1 * g23 = (TF1*)f->Get("fitfcneta_1.93_2.043");
	TF1 * g24 = (TF1*)f->Get("fitfcneta_2.043_2.172");
	TF1 * g25 = (TF1*)f->Get("fitfcneta_2.172_2.322");
	TF1 * g26 = (TF1*)f->Get("fitfcneta_2.322_2.5");
	TF1 * g27 = (TF1*)f->Get("fitfcneta_2.5_2.65");
	TF1 * g28 = (TF1*)f->Get("fitfcneta_2.65_2.964");
	TF1 * g30 = (TF1*)f->Get("fitfcneta_2.964_3.139");
	TF1 * g31 = (TF1*)f->Get("fitfcneta_3.139_3.314");
	TF1 * g32 = (TF1*)f->Get("fitfcneta_3.314_3.489");
	TF1 * g33 = (TF1*)f->Get("fitfcneta_3.489_3.664");
	TF1 * g34 = (TF1*)f->Get("fitfcneta_3.664_3.839");
	TF1 * g35 = (TF1*)f->Get("fitfcneta_3.839_4.013");
	TF1 * g36 = (TF1*)f->Get("fitfcneta_4.013_4.191");
	TF1 * g37 = (TF1*)f->Get("fitfcneta_4.191_4.363");
	TF1 * g38 = (TF1*)f->Get("fitfcneta_4.363_4.538");
	TF1 * g39 = (TF1*)f->Get("fitfcneta_4.538_4.716");
	// TF1 * g40 = (TF1*)f->Get("fitfcneta_4.716_4.889");
	// TF1 * g41 = (TF1*)f->Get("fitfcneta_4.889_5.191");

	g01->SetLineColor(kBlack);
	g02->SetLineColor(kBlue+3);
	g03->SetLineColor(kBlue);
	g04->SetLineColor(kBlue-7);
	g05->SetLineColor(kCyan+2);
	g06->SetLineColor(kCyan);
	g07->SetLineColor(kGreen+4);
	g08->SetLineColor(kGreen+2);
	g09->SetLineColor(kGreen);
	g10->SetLineColor(kYellow+4);
	g11->SetLineColor(kYellow+2);
	g12->SetLineColor(kYellow);
	g13->SetLineColor(kOrange);
	g14->SetLineColor(kOrange+7);
	g15->SetLineColor(kRed+4);
	g16->SetLineColor(kRed+2);
	g17->SetLineColor(kRed);
	g18->SetLineColor(kMagenta+4);
	g19->SetLineColor(kMagenta+2);
	g20->SetLineColor(kMagenta);
	g21->SetLineColor(kBlack);
	g22->SetLineColor(kBlue+3);
	g23->SetLineColor(kBlue);
	g24->SetLineColor(kBlue-7);
	g25->SetLineColor(kCyan+2);
	g26->SetLineColor(kCyan);
	g27->SetLineColor(kGreen+4);
	g28->SetLineColor(kGreen+2);
	g30->SetLineColor(kGreen);
	g31->SetLineColor(kYellow+4);
	g32->SetLineColor(kYellow+2);
	g33->SetLineColor(kYellow);
	g34->SetLineColor(kOrange);
	g35->SetLineColor(kOrange+7);
	g36->SetLineColor(kRed+4);
	g37->SetLineColor(kRed+2);
	g38->SetLineColor(kRed);
	g39->SetLineColor(kMagenta+4);
	// g40->SetLineColor(kMagenta+2);
	// g41->SetLineColor(kMagenta);

	g17->SetLineStyle(9);
	g18->SetLineStyle(9);
	g19->SetLineStyle(9);
	g20->SetLineStyle(9);
	g21->SetLineStyle(9);
	g22->SetLineStyle(9);
	g23->SetLineStyle(9);					
	g24->SetLineStyle(9);
	g25->SetLineStyle(9);
	g26->SetLineStyle(9);
	g27->SetLineStyle(9);
	g28->SetLineStyle(9);

	TCanvas * c3 = new TCanvas("c3", "", 600, 600);
	gStyle->SetOptStat(0);
	g01->GetYaxis()->SetRangeUser(0.9,2.0);
	g01->GetXaxis()->SetRangeUser(0,300);
	g01->Draw();
	g02->Draw("same");
	g03->Draw("same");
	g04->Draw("same");
	g05->Draw("same");
	g06->Draw("same");
	g07->Draw("same");
	g08->Draw("same");
	g09->Draw("same");
	g10->Draw("same");
	g11->Draw("same");
	g12->Draw("same");
	g13->Draw("same");
	g14->Draw("same");
	g15->Draw("same");
	g16->Draw("same");
	g17->Draw("same");
	g18->Draw("same");
	g19->Draw("same");
	g20->Draw("same");
	g21->Draw("same");
	g22->Draw("same");
	g23->Draw("same");
	g24->Draw("same");
	g25->Draw("same");
	g26->Draw("same");
	g27->Draw("same");
	g28->Draw("same");
	g30->Draw("same");
	g31->Draw("same");
	g32->Draw("same");
	g33->Draw("same");
	g34->Draw("same");
	g35->Draw("same");
	g36->Draw("same");
	g37->Draw("same");
	// g38->Draw("same");
	// g39->Draw("same");
	// g40->Draw("same");
	// g41->Draw("same");

	TLegend * leg3 = new TLegend(0.43,0.53,0.88,0.88);
	leg3->AddEntry(g01, "(HB) 1");		
	leg3->AddEntry(g02, "2");
	leg3->AddEntry(g03, "3");
	leg3->AddEntry(g04, "4");
	leg3->AddEntry(g05, "5");
	leg3->AddEntry(g06, "6");
	leg3->AddEntry(g07, "7");
	leg3->AddEntry(g08, "8");
	leg3->AddEntry(g09, "9");
	leg3->AddEntry(g10, "10");
	leg3->AddEntry(g11, "11");
	leg3->AddEntry(g12, "12");
	leg3->AddEntry(g13, "13");
	leg3->AddEntry(g14, "14");
	leg3->AddEntry(g15, "15");
	leg3->AddEntry(g16, "16");
	leg3->AddEntry(g17, "(HE) 17");
	leg3->AddEntry(g18, "18");
	leg3->AddEntry(g19, "19");
	leg3->AddEntry(g20, "20");
	leg3->AddEntry(g21, "21");
	leg3->AddEntry(g22, "22");
	leg3->AddEntry(g23, "23");
	leg3->AddEntry(g24, "24");							
	leg3->AddEntry(g25, "25");
	leg3->AddEntry(g26, "26");
	leg3->AddEntry(g27, "27");
	leg3->AddEntry(g28, "28");
	leg3->AddEntry(g30, "(HF) 30");
	leg3->AddEntry(g31, "31");
	leg3->AddEntry(g32, "32");
	leg3->AddEntry(g33, "33");
	leg3->AddEntry(g34, "34");	
	leg3->AddEntry(g35, "35");
	leg3->AddEntry(g36, "36");
	leg3->AddEntry(g37, "37");
	// leg3->AddEntry(g38, "38");
	// leg3->AddEntry(g39, "39");
	// leg3->AddEntry(g40, "40");
	// leg3->AddEntry(g41, "41");
	leg3->Draw();
	c3->SaveAs(outputPath.c_str());
	c3->Close();	
}



void makePlots_sel16etaBinning(std::string inputFile, std::string outputFile, std::string directory){

	std::string inputPath = directory + inputFile;
	std::string outputPath = directory + outputFile;

	TFile * f = TFile::Open(inputPath.c_str());

	TF1 * g00 = (TF1*)f->Get("fitfcneta_0_0.435");
	TF1 * g01 = (TF1*)f->Get("fitfcneta_0.435_0.783");
	TF1 * g02 = (TF1*)f->Get("fitfcneta_0.783_1.131");
	TF1 * g03 = (TF1*)f->Get("fitfcneta_1.131_1.305");
	TF1 * g04 = (TF1*)f->Get("fitfcneta_1.305_1.479");
	TF1 * g05 = (TF1*)f->Get("fitfcneta_1.479_1.653");
	TF1 * g06 = (TF1*)f->Get("fitfcneta_1.653_1.83");
	TF1 * g07 = (TF1*)f->Get("fitfcneta_1.83_1.93");
	TF1 * g08 = (TF1*)f->Get("fitfcneta_1.93_2.043");
	TF1 * g09 = (TF1*)f->Get("fitfcneta_2.043_2.172");
	TF1 * g10 = (TF1*)f->Get("fitfcneta_2.172_2.322");
	TF1 * g11 = (TF1*)f->Get("fitfcneta_2.322_2.5");
	TF1 * g12 = (TF1*)f->Get("fitfcneta_2.5_2.964");
	TF1 * g13 = (TF1*)f->Get("fitfcneta_2.964_3.489");
	TF1 * g14 = (TF1*)f->Get("fitfcneta_3.489_4.191");
	TF1 * g15 = (TF1*)f->Get("fitfcneta_4.191_5.191");	

	g00->SetLineColor(kBlue+2);
	g01->SetLineColor(kBlue);
	g02->SetLineColor(kCyan+1);
	g03->SetLineColor(kGreen+2);
	g04->SetLineColor(kGreen);	
	g05->SetLineColor(kYellow+2);
	g06->SetLineColor(kOrange);
	g07->SetLineColor(kOrange+7);
	g08->SetLineColor(kRed+2);	
	g09->SetLineColor(kRed);
	g10->SetLineColor(kMagenta+3);
	g11->SetLineColor(kMagenta);
	g12->SetLineColor(kBlue+2);
	g13->SetLineColor(kCyan+1);
	g14->SetLineColor(kGreen+2);
	g15->SetLineColor(kGreen);

	TCanvas * c3 = new TCanvas("c3", "", 600, 600);
	gStyle->SetOptStat(0);
	g00->GetYaxis()->SetRangeUser(0.9,2.0);
	g00->GetXaxis()->SetRangeUser(0,300);
	g00->Draw();
	g01->Draw("same");
	g02->Draw("same");
	g03->Draw("same");
	g04->Draw("same");
	g05->Draw("same");
	g06->Draw("same");
	g07->Draw("same");
	g08->Draw("same");
	g09->Draw("same");
	g10->Draw("same");
	g11->Draw("same");
	g12->Draw("same");
	g13->Draw("same");
	g14->Draw("same");
	g15->Draw("same");
	
	TLegend * leg3 = new TLegend(0.43,0.53,0.88,0.88);	
	leg3->AddEntry(g00, "bin00");
	leg3->AddEntry(g01, "bin01");
	leg3->AddEntry(g02, "bin02");
	leg3->AddEntry(g03, "bin03");
	leg3->AddEntry(g04, "bin04");
	leg3->AddEntry(g05, "bin05");
	leg3->AddEntry(g06, "bin06");
	leg3->AddEntry(g07, "bin07");
	leg3->AddEntry(g08, "bin08");
	leg3->AddEntry(g09, "bin09");
	leg3->AddEntry(g10, "bin10");
	leg3->AddEntry(g11, "bin11");
	leg3->AddEntry(g12, "bin12");
	leg3->AddEntry(g13, "bin13");
	leg3->AddEntry(g14, "bin14");
	leg3->AddEntry(g15, "bin15");	
	leg3->Draw();		
	c3->SaveAs(outputPath.c_str());
	c3->Close();	
}