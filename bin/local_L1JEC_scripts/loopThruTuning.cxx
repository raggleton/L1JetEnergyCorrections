#include <iostream>
#include <string>
#include "/users/jt15104/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/tuneFits.h"

using std::cout;
using std::endl;
using std::vector;

// works well in theory...
// but draw only works in the interactive mode...

void individualTune(string,string);

void loopThruTuning()
{
	vector<string> listOfEtaRanges;
	listOfEtaRanges.push_back("0_0.174");
	listOfEtaRanges.push_back("0.174_0.348");
	listOfEtaRanges.push_back("2.65_3.139");	
	// listOfEtaRanges.push_back("2.65_3.139");
	// listOfEtaRanges.push_back("2.65_3.139");
	// listOfEtaRanges.push_back("2.65_3.139");
	// listOfEtaRanges.push_back("2.65_3.139");
	// listOfEtaRanges.push_back("2.65_3.139");
	// listOfEtaRanges.push_back("2.65_3.139");	

	typedef vector<string>::size_type vec_sz;
	vec_sz size = listOfEtaRanges.size();

	string inputFile = "/users/jt15104/local_L1JEC_store/26May2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_jbntuples_dr0p25_etaBinningVersion4/runCalib_jetMetFitErr/testABC.root";
	cout << endl;
	cout << "Welcome to loopThruTuning" << endl;
	cout << "We shall be ammending the following file: " << inputFile << endl;
	cout << "We shall be massaging corrections fits for the following eta bins:" << endl;
	for (vec_sz i = 0; i < size; i++) cout << listOfEtaRanges[i] << endl; 

	for (vec_sz i = 0; i < size; i++) {
		cout << endl << endl;
		cout << "Doing fit " << i+1 << " of " << size << endl;
		cout << "Massaging correction fit for eta bin: " << listOfEtaRanges[i] << endl;
		cout << "Setting up..." << endl;
		individualTune(inputFile.c_str(), listOfEtaRanges[i]);
	}
	cout << endl << endl;
	cout << "All done:) Have a nice day" << endl << endl;
}


void individualTune(string inputRootFileName, string etaRange)
{
	tuneFits fitObject;
	fitObject.setup(inputRootFileName, etaRange);

	while(true){

		int choice=0;
		cout << "Press 1: To redo the fit" << endl;
		cout << "Press 2: To save the fit and exit" << endl;
		cout << "Press 3: To exit without saving fit" << endl;	
		cin >> choice;

		if (choice==1) {
			double posRelToXmin;
			double posRelToXmax;
			cout << "Redo-ing the fit" << endl;
			cout << "Please input: posRelToXmin, posRelToXmax" << endl;
			cin >> posRelToXmin >> posRelToXmax;
			fitObject.redoFit(posRelToXmin, posRelToXmax);
		}

		if (choice==2) {
			cout << "Saving and exiting" << endl;
			fitObject.save();
			return;
		}

		if (choice==3) {
			cout << "Exiting w/o saving fit for eta bin " << etaRange << endl;
			return;
		}				
	} // continuous while loop
} // closes the function

