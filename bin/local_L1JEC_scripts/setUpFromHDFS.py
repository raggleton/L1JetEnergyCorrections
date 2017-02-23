import os
import sys

# creates the framework for the local L1JEC analysis
# 
# select the new dir name
# select the directories and files we wish to copy
# 
# $ python /users/jt15104/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/setUpFromHDFS.py
# 
# watchout! you could easily overwrite...(maybe not the worst thing ever)

##################################################
# user inputs ####################################
##################################################
# make sure the new directory has a clear name
# dateOfNtupleCreation, dataType, cmssw version, dr, etaBinning
newDirectory = "30June2016_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_809v70_noJEC_893ca_etaBinsSel16/"

checkCalibDirectory = "/hdfs/L1JEC/CMSSW_8_0_9/QCDFlatFall15PU0to50NzshcalRaw_genEmu_30June2016_809v70_noJEC_893ca/check/"
# comment out files that you don't wish to copy (eg they don't exist yet)
checkCalibFiles = [
					"check_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU0to10_maxPt1022.root",
					"check_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU15to25_maxPt1022.root",
					"check_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU30to40_maxPt1022.root",
					"check_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU45to55_maxPt1022.root",
					]

runCalibDirectory = "/hdfs/L1JEC/CMSSW_8_0_9/QCDFlatFall15PU0to50NzshcalRaw_genEmu_30June2016_809v70_noJEC_893ca/output/"
# comment out files that you don't wish to copy (eg they don't exist yet)
runCalibFiles = [
					"output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU0to10.root",
					"output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU15to25.root",
					"output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU30to40.root",
					"output_QCDFlatFall15PU0to50NzshcalRaw_ak4_ref10to5000_l10to5000_dr0p25_etaBinsSel16_PU45to55.root",
					]

##################################################
##################################################
##################################################


# setup the locations required
newDirectoryPath = "/users/jt15104/local_L1JEC_store/" + newDirectory

checkCalibPath = []
for i in range(0, len(checkCalibFiles)):
	checkCalibPath.append(checkCalibDirectory + checkCalibFiles[i])

runCalibPath = []
runCalibFiles_initialCopy = []	
for i in range(0, len(runCalibFiles)):
	runCalibPath.append(runCalibDirectory + runCalibFiles[i])
	runCalibFiles_initialCopy.append(runCalibFiles[i])
	runCalibFiles_initialCopy[i] = runCalibFiles_initialCopy[i][:-5] + "_initialCopy.root"


# make the directories for the files if they don't already exist
if os.path.isdir(newDirectoryPath):
	print "the directory already exists"
	# print "The directory " + newDirectory + " already exists...\nexiting..."
	# sys.exit() # don't do this if you want to continue

else:
	os.system("mkdir " + newDirectoryPath)
	os.system("mkdir " + newDirectoryPath + "checkCalib")
	os.system("mkdir " + newDirectoryPath + "runCalib_conventionalFit")
	os.system("mkdir " + newDirectoryPath + "runCalib_jetMetFit1")
	os.system("mkdir " + newDirectoryPath + "runCalib_jetMetFitErr")	
	print "Made the directory framework"

# copy the files from /hdfs to these new locations (currently no hadoop command to copy things to local)
for i in range(0,len(checkCalibPath)):
	os.system("cp " + checkCalibPath[i] + " " + newDirectory + "checkCalib/")
	print "Copied " + str(i+1) + " of " + str(len(checkCalibPath)) + " checkCalib file sets"

for i in range(0,len(runCalibPath)):
	os.system("cp " + runCalibPath[i] + " " + newDirectoryPath + "runCalib_conventionalFit/")
	os.system("cp " + newDirectoryPath + "runCalib_conventionalFit/" + runCalibFiles[i] + " " + newDirectoryPath + "runCalib_conventionalFit/" + runCalibFiles_initialCopy[i])
	os.system("cp " + runCalibPath[i] + " " + newDirectoryPath + "runCalib_jetMetFit1/")
	os.system("cp " + newDirectoryPath + "runCalib_jetMetFit1/" + runCalibFiles[i] + " " + newDirectoryPath + "runCalib_jetMetFit1/" + runCalibFiles_initialCopy[i])
	os.system("cp " + runCalibPath[i] + " " + newDirectoryPath + "runCalib_jetMetFitErr/")
	os.system("cp " + newDirectoryPath + "runCalib_jetMetFitErr/" + runCalibFiles[i] + " " + newDirectoryPath + "runCalib_jetMetFitErr/" + runCalibFiles_initialCopy[i])
	print "Copied " + str(i+1) + " of " + str(len(runCalibPath)) + " runCalib file sets"

print "all done:)" 