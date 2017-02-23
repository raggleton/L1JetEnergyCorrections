#include "TFile.h"
#include "TF1.h"
#include <iostream>
#include <fstream>

// root -q -b -l "/users/jt15104/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/writeParams.cxx+"
// currently only setup for jetMetFitErr function

void writeParams()
{

	// SELECT THE INPUT AND OUTPUT FILES
	std::string inputFile = "/users/jt15104/local_L1JEC_store/30June2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_809v70_noJEC_893ca_etaBinsSel16/runCalib_jetMetFitErr/fitsPU30to40.root";
	std::string outputFile = "/users/jt15104/local_L1JEC_store/30June2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_809v70_noJEC_893ca_etaBinsSel16/runCalib_jetMetFitErr/paramsFitsPU30to40.txt";

	TFile * f = TFile::Open(inputFile.c_str());
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

	ofstream myfile;
	myfile.open(outputFile.c_str());

	myfile << "parameters correspond to the following function:" << std::endl;
	myfile << "[0]+[1]*TMath::Erf([2]*(log10(x)-[3])+[4]*exp([5]*(log10(x)-[6])*(log10(x)-[6])))" << std::endl << std::endl;

	myfile << "***LAYOUT***" << std::endl;
	myfile << "eta range for bin:" << std::endl;
	myfile << "parameters [0], [1], [2], [3], [4], [5], [6]:" << std::endl;
	myfile << "function range (xmin, xmax):" << std::endl << std::endl << std::endl; 


	myfile << "0.000-0.435:" << std::endl;
	myfile << g00->GetParameter(0) << ", ";
	myfile << g00->GetParameter(1) << ", ";
	myfile << g00->GetParameter(2) << ", ";
	myfile << g00->GetParameter(3) << ", ";
	myfile << g00->GetParameter(4) << ", ";
	myfile << g00->GetParameter(5) << ", ";
	myfile << g00->GetParameter(6) << std::endl;
	myfile << g00->GetXmin() << ", ";
	myfile << g00->GetXmax() << std::endl << std::endl;

	myfile << "0.435-0.783:" << std::endl;
	myfile << g01->GetParameter(0) << ", ";
	myfile << g01->GetParameter(1) << ", ";
	myfile << g01->GetParameter(2) << ", ";
	myfile << g01->GetParameter(3) << ", ";
	myfile << g01->GetParameter(4) << ", ";
	myfile << g01->GetParameter(5) << ", ";
	myfile << g01->GetParameter(6) << std::endl;
	myfile << g01->GetXmin() << ", ";
	myfile << g01->GetXmax() << std::endl << std::endl;

	myfile << "0.783-1.131:" << std::endl;
	myfile << g02->GetParameter(0) << ", ";
	myfile << g02->GetParameter(1) << ", ";
	myfile << g02->GetParameter(2) << ", ";
	myfile << g02->GetParameter(3) << ", ";
	myfile << g02->GetParameter(4) << ", ";
	myfile << g02->GetParameter(5) << ", ";
	myfile << g02->GetParameter(6) << std::endl;
	myfile << g02->GetXmin() << ", ";
	myfile << g02->GetXmax() << std::endl << std::endl;

	myfile << "1.131-1.305:" << std::endl; 
	myfile << g03->GetParameter(0) << ", ";
	myfile << g03->GetParameter(1) << ", ";
	myfile << g03->GetParameter(2) << ", ";
	myfile << g03->GetParameter(3) << ", ";
	myfile << g03->GetParameter(4) << ", ";
	myfile << g03->GetParameter(5) << ", ";
	myfile << g03->GetParameter(6) << std::endl;
	myfile << g03->GetXmin() << ", ";
	myfile << g03->GetXmax() << std::endl << std::endl;

	myfile << "1.305-1.479:" << std::endl;
	myfile << g04->GetParameter(0) << ", ";
	myfile << g04->GetParameter(1) << ", ";
	myfile << g04->GetParameter(2) << ", ";
	myfile << g04->GetParameter(3) << ", ";
	myfile << g04->GetParameter(4) << ", ";
	myfile << g04->GetParameter(5) << ", ";
	myfile << g04->GetParameter(6) << std::endl;
	myfile << g04->GetXmin() << ", ";
	myfile << g04->GetXmax() << std::endl << std::endl;

	myfile << "1.479-1.653:" << std::endl;
	myfile << g05->GetParameter(0) << ", ";
	myfile << g05->GetParameter(1) << ", ";
	myfile << g05->GetParameter(2) << ", ";
	myfile << g05->GetParameter(3) << ", ";
	myfile << g05->GetParameter(4) << ", ";
	myfile << g05->GetParameter(5) << ", ";
	myfile << g05->GetParameter(6) << std::endl;
	myfile << g05->GetXmin() << ", ";
	myfile << g05->GetXmax() << std::endl << std::endl;

	myfile << "1.653-1.830:" << std::endl;
	myfile << g06->GetParameter(0) << ", ";
	myfile << g06->GetParameter(1) << ", ";
	myfile << g06->GetParameter(2) << ", ";
	myfile << g06->GetParameter(3) << ", ";
	myfile << g06->GetParameter(4) << ", ";
	myfile << g06->GetParameter(5) << ", ";
	myfile << g06->GetParameter(6) << std::endl;
	myfile << g06->GetXmin() << ", ";
	myfile << g06->GetXmax() << std::endl << std::endl;

	myfile << "1.830-1.930:" << std::endl;
	myfile << g07->GetParameter(0) << ", ";
	myfile << g07->GetParameter(1) << ", ";
	myfile << g07->GetParameter(2) << ", ";
	myfile << g07->GetParameter(3) << ", ";
	myfile << g07->GetParameter(4) << ", ";
	myfile << g07->GetParameter(5) << ", ";
	myfile << g07->GetParameter(6) << std::endl;
	myfile << g07->GetXmin() << ", ";
	myfile << g07->GetXmax() << std::endl << std::endl;

	myfile << "1.930-2.043:" << std::endl; 
	myfile << g08->GetParameter(0) << ", ";
	myfile << g08->GetParameter(1) << ", ";
	myfile << g08->GetParameter(2) << ", ";
	myfile << g08->GetParameter(3) << ", ";
	myfile << g08->GetParameter(4) << ", ";
	myfile << g08->GetParameter(5) << ", ";
	myfile << g08->GetParameter(6) << std::endl;
	myfile << g08->GetXmin() << ", ";
	myfile << g08->GetXmax() << std::endl << std::endl;

	myfile << "2.043-2.172:" << std::endl;
	myfile << g09->GetParameter(0) << ", ";
	myfile << g09->GetParameter(1) << ", ";
	myfile << g09->GetParameter(2) << ", ";
	myfile << g09->GetParameter(3) << ", ";
	myfile << g09->GetParameter(4) << ", ";
	myfile << g09->GetParameter(5) << ", ";
	myfile << g09->GetParameter(6) << std::endl;
	myfile << g09->GetXmin() << ", ";
	myfile << g09->GetXmax() << std::endl << std::endl;

	myfile << "2.172-2.322:" << std::endl;
	myfile << g10->GetParameter(0) << ", ";
	myfile << g10->GetParameter(1) << ", ";
	myfile << g10->GetParameter(2) << ", ";
	myfile << g10->GetParameter(3) << ", ";
	myfile << g10->GetParameter(4) << ", ";
	myfile << g10->GetParameter(5) << ", ";
	myfile << g10->GetParameter(6) << std::endl;
	myfile << g10->GetXmin() << ", ";
	myfile << g10->GetXmax() << std::endl << std::endl; 

	myfile << "2.322-2.500:" << std::endl;
	myfile << g11->GetParameter(0) << ", ";
	myfile << g11->GetParameter(1) << ", ";
	myfile << g11->GetParameter(2) << ", ";
	myfile << g11->GetParameter(3) << ", ";
	myfile << g11->GetParameter(4) << ", ";
	myfile << g11->GetParameter(5) << ", ";
	myfile << g11->GetParameter(6) << std::endl;
	myfile << g11->GetXmin() << ", ";
	myfile << g11->GetXmax() << std::endl << std::endl; 

	myfile << "2.500-2.964:" << std::endl;
	myfile << g12->GetParameter(0) << ", ";
	myfile << g12->GetParameter(1) << ", ";
	myfile << g12->GetParameter(2) << ", ";
	myfile << g12->GetParameter(3) << ", ";
	myfile << g12->GetParameter(4) << ", ";
	myfile << g12->GetParameter(5) << ", ";
	myfile << g12->GetParameter(6) << std::endl;
	myfile << g12->GetXmin() << ", ";
	myfile << g12->GetXmax() << std::endl << std::endl; 

	myfile << "2.964-3.489:" << std::endl;
	myfile << g13->GetParameter(0) << ", ";
	myfile << g13->GetParameter(1) << ", ";
	myfile << g13->GetParameter(2) << ", ";
	myfile << g13->GetParameter(3) << ", ";
	myfile << g13->GetParameter(4) << ", ";
	myfile << g13->GetParameter(5) << ", ";
	myfile << g13->GetParameter(6) << std::endl;
	myfile << g13->GetXmin() << ", ";
	myfile << g13->GetXmax() << std::endl << std::endl; 

	myfile << "3.489-4.191:" << std::endl;
	myfile << g14->GetParameter(0) << ", ";
	myfile << g14->GetParameter(1) << ", ";
	myfile << g14->GetParameter(2) << ", ";
	myfile << g14->GetParameter(3) << ", ";
	myfile << g14->GetParameter(4) << ", ";
	myfile << g14->GetParameter(5) << ", ";
	myfile << g14->GetParameter(6) << std::endl;
	myfile << g14->GetXmin() << ", ";
	myfile << g14->GetXmax() << std::endl << std::endl; 

	myfile << "4.191-5.191:" << std::endl;
	myfile << g15->GetParameter(0) << ", ";
	myfile << g15->GetParameter(1) << ", ";
	myfile << g15->GetParameter(2) << ", ";
	myfile << g15->GetParameter(3) << ", ";
	myfile << g15->GetParameter(4) << ", ";
	myfile << g15->GetParameter(5) << ", ";
	myfile << g15->GetParameter(6) << std::endl;
	myfile << g15->GetXmin() << ", ";
	myfile << g15->GetXmax() << std::endl << std::endl; 

	myfile.close();

}