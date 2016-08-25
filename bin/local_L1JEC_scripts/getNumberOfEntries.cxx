#include "TFile.h"
#include "TH2F.h"
#include <iostream>
// $ root -q -b -l "/users/jt15104/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/getNumberOfEntries.cxx+"


void getNumberOfEntries()
{
	std::string filename = "/users/jt15104/local_L1JEC_store/30June2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_809v70_noJEC_893ca_etaBinsAllTT/runCalib_jetMetFitErr/output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsAllTT_PU30to40.root";
	TFile * f = TFile::Open(filename.c_str());

	TH2F * h01 = (TH2F*)f->Get("eta_0_0.087/Histograms/h2d_rsp_l1");
	TH2F * h02 = (TH2F*)f->Get("eta_0.087_0.174/Histograms/h2d_rsp_l1");
	TH2F * h03 = (TH2F*)f->Get("eta_0.174_0.261/Histograms/h2d_rsp_l1");
	TH2F * h04 = (TH2F*)f->Get("eta_0.261_0.348/Histograms/h2d_rsp_l1");
	TH2F * h05 = (TH2F*)f->Get("eta_0.348_0.435/Histograms/h2d_rsp_l1");
	TH2F * h06 = (TH2F*)f->Get("eta_0.435_0.522/Histograms/h2d_rsp_l1");
	TH2F * h07 = (TH2F*)f->Get("eta_0.522_0.609/Histograms/h2d_rsp_l1");
	TH2F * h08 = (TH2F*)f->Get("eta_0.609_0.696/Histograms/h2d_rsp_l1");
	TH2F * h09 = (TH2F*)f->Get("eta_0.696_0.783/Histograms/h2d_rsp_l1");
	TH2F * h10 = (TH2F*)f->Get("eta_0.783_0.87/Histograms/h2d_rsp_l1");
	TH2F * h11 = (TH2F*)f->Get("eta_0.87_0.957/Histograms/h2d_rsp_l1");
	TH2F * h12 = (TH2F*)f->Get("eta_0.957_1.044/Histograms/h2d_rsp_l1");
	TH2F * h13 = (TH2F*)f->Get("eta_1.044_1.131/Histograms/h2d_rsp_l1");
	TH2F * h14 = (TH2F*)f->Get("eta_1.131_1.218/Histograms/h2d_rsp_l1");
	TH2F * h15 = (TH2F*)f->Get("eta_1.218_1.305/Histograms/h2d_rsp_l1");
	TH2F * h16 = (TH2F*)f->Get("eta_1.305_1.392/Histograms/h2d_rsp_l1");
	TH2F * h17 = (TH2F*)f->Get("eta_1.392_1.479/Histograms/h2d_rsp_l1");
	TH2F * h18 = (TH2F*)f->Get("eta_1.479_1.566/Histograms/h2d_rsp_l1");
	TH2F * h19 = (TH2F*)f->Get("eta_1.566_1.653/Histograms/h2d_rsp_l1");
	TH2F * h20 = (TH2F*)f->Get("eta_1.653_1.74/Histograms/h2d_rsp_l1");
	TH2F * h21 = (TH2F*)f->Get("eta_1.74_1.83/Histograms/h2d_rsp_l1");
	TH2F * h22 = (TH2F*)f->Get("eta_1.83_1.93/Histograms/h2d_rsp_l1");
	TH2F * h23 = (TH2F*)f->Get("eta_1.93_2.043/Histograms/h2d_rsp_l1");
	TH2F * h24 = (TH2F*)f->Get("eta_2.043_2.172/Histograms/h2d_rsp_l1");
	TH2F * h25 = (TH2F*)f->Get("eta_2.172_2.322/Histograms/h2d_rsp_l1");
	TH2F * h26 = (TH2F*)f->Get("eta_2.322_2.5/Histograms/h2d_rsp_l1");
	TH2F * h27 = (TH2F*)f->Get("eta_2.5_2.65/Histograms/h2d_rsp_l1");
	TH2F * h28 = (TH2F*)f->Get("eta_2.65_2.964/Histograms/h2d_rsp_l1");
	TH2F * h30 = (TH2F*)f->Get("eta_2.964_3.139/Histograms/h2d_rsp_l1");
	TH2F * h31 = (TH2F*)f->Get("eta_3.139_3.314/Histograms/h2d_rsp_l1");
	TH2F * h32 = (TH2F*)f->Get("eta_3.314_3.489/Histograms/h2d_rsp_l1");
	TH2F * h33 = (TH2F*)f->Get("eta_3.489_3.664/Histograms/h2d_rsp_l1");
	TH2F * h34 = (TH2F*)f->Get("eta_3.664_3.839/Histograms/h2d_rsp_l1");
	TH2F * h35 = (TH2F*)f->Get("eta_3.839_4.013/Histograms/h2d_rsp_l1");
	TH2F * h36 = (TH2F*)f->Get("eta_4.013_4.191/Histograms/h2d_rsp_l1");
	TH2F * h37 = (TH2F*)f->Get("eta_4.191_4.363/Histograms/h2d_rsp_l1");
	TH2F * h38 = (TH2F*)f->Get("eta_4.363_4.538/Histograms/h2d_rsp_l1");
	TH2F * h39 = (TH2F*)f->Get("eta_4.538_4.716/Histograms/h2d_rsp_l1");
	TH2F * h40 = (TH2F*)f->Get("eta_4.716_4.889/Histograms/h2d_rsp_l1");
	TH2F * h41 = (TH2F*)f->Get("eta_4.889_5.191/Histograms/h2d_rsp_l1");

	std::cout << "01: " << h01->GetEntries() << std::endl;
	std::cout << "02: " << h02->GetEntries() << std::endl;
	std::cout << "03: " << h03->GetEntries() << std::endl;
	std::cout << "04: " << h04->GetEntries() << std::endl;
	std::cout << "05: " << h05->GetEntries() << std::endl;				
	std::cout << "06: " << h06->GetEntries() << std::endl;
	std::cout << "07: " << h07->GetEntries() << std::endl;
	std::cout << "08: " << h08->GetEntries() << std::endl;
	std::cout << "09: " << h09->GetEntries() << std::endl;
	std::cout << "10: " << h10->GetEntries() << std::endl;
	std::cout << "11: " << h11->GetEntries() << std::endl;
	std::cout << "12: " << h12->GetEntries() << std::endl;
	std::cout << "13: " << h13->GetEntries() << std::endl;
	std::cout << "14: " << h14->GetEntries() << std::endl;
	std::cout << "15: " << h15->GetEntries() << std::endl;
	std::cout << "16: " << h16->GetEntries() << std::endl;
	std::cout << "17: " << h17->GetEntries() << std::endl;
	std::cout << "18: " << h18->GetEntries() << std::endl;
	std::cout << "19: " << h19->GetEntries() << std::endl;
	std::cout << "20: " << h20->GetEntries() << std::endl;
	std::cout << "21: " << h21->GetEntries() << std::endl;
	std::cout << "22: " << h22->GetEntries() << std::endl;
	std::cout << "23: " << h23->GetEntries() << std::endl;
	std::cout << "24: " << h24->GetEntries() << std::endl;
	std::cout << "25: " << h25->GetEntries() << std::endl;				
	std::cout << "26: " << h26->GetEntries() << std::endl;
	std::cout << "27: " << h27->GetEntries() << std::endl;
	std::cout << "28: " << h28->GetEntries() << std::endl;
	std::cout << "30: " << h30->GetEntries() << std::endl;
	std::cout << "31: " << h31->GetEntries() << std::endl;
	std::cout << "32: " << h32->GetEntries() << std::endl;
	std::cout << "33: " << h33->GetEntries() << std::endl;
	std::cout << "34: " << h34->GetEntries() << std::endl;
	std::cout << "35: " << h35->GetEntries() << std::endl;
	std::cout << "36: " << h36->GetEntries() << std::endl;
	std::cout << "37: " << h37->GetEntries() << std::endl;
	std::cout << "38: " << h38->GetEntries() << std::endl;
	std::cout << "39: " << h39->GetEntries() << std::endl;
	std::cout << "40: " << h40->GetEntries() << std::endl;
	std::cout << "41: " << h41->GetEntries() << std::endl;						

}