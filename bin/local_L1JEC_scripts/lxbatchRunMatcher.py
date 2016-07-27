import os
import eosComfort

# requires eosComfort.py to be set up correctly...
# TORUN, do so from jobLogs directory
# $ python /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/lxbatchRunMatcher.py

#######################################
#######################################

outputDirectory = "/afs/cern.ch/user/t/taylor/L1TriggerStudies/output_jets/pairs_testing_v1/"

#######################################
#######################################

os.system("mkdir %s" % outputDirectory)

for i in range (0, len(eosComfort.fullPaths)): # real thing
# for i in range (0, 2): # for testing

	for j in range (0, len(eosComfort.ntupleNames[i])):

		inputFilePath = "root://eoscms.cern.ch/" + eosComfort.fullPaths[i] + eosComfort.ntupleNames[i][j]
		outputFilesPath = outputDirectory + "pairs_" + eosComfort.daughterDirs[i][:-1] + "_" + str(j) + ".root" #nb: the numerical label does not correspond to the original ntuple label

		# for testing output command
		# print('bsub -q 8nh "sh /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcher.sh %s %s"' % (inputFilePath, outputFilesPath) )
		# print ""

		# for testing outut command when fed into submission script
		# os.system("source /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcher.sh %s %s" % (inputFilePath, outputFilesPath) )

		# for the real thing
		os.system('bsub -q 8nh "sh /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcher.sh %s %s"' % (inputFilePath, outputFilesPath) )
