# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: l1NtupleRECO -s RAW2DIGI --era=Run2_2016 --customise=L1Trigger/Configuration/customiseReEmul.L1TReEmulFromRAW --customise=L1Trigger/L1TNtuples/customiseL1Ntuple.L1NtupleAODEMU --customise=L1Trigger/Configuration/customiseUtils.L1TTurnOffUnpackStage2GtGmtAndCalo --customise=L1Trigger/Configuration/customiseUtils.L1TTurnOffGtAndGmtEmulation --conditions=auto:run2_data -n 200 --data --no_exec --no_output --filein=/store/data/Run2015D/DoubleEG/RAW-RECO/ZElectron-PromptReco-v4/000/260/627/00000/12455212-1E85-E511-8913-02163E014472.root --geometry=Extended2016,Extended2016Reco --customise=L1Trigger/Configuration/customiseReEmul.L1TEventSetupForHF1x1TPs --customise=L1Trigger/L1JetEnergyCorrections/customiseL1JEC.L1JEC_off
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('RAW2DIGI',eras.Run2_2016)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.Geometry.GeometryExtended2016Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(200)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('/store/data/Commissioning2016/ZeroBias2/AOD/PromptReco-v1/000/268/955/00000/36CC36F5-3900-E611-81A7-02163E0133A2.root'),
    secondaryFileNames = cms.untracked.vstring('/store/data/Commissioning2016/ZeroBias2/RAW/v1/000/268/955/00000/06B47904-E2FD-E511-9C11-02163E013437.root', 
    											'/store/data/Commissioning2016/ZeroBias2/RAW/v1/000/268/955/00000/10B613AA-E1FD-E511-B37E-02163E01459C.root')
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1NtupleRECO nevts:200'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.endjob_step)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseReEmul
from L1Trigger.Configuration.customiseReEmul import L1TReEmulFromRAW,L1TEventSetupForHF1x1TPs 

#call to customisation function L1TReEmulFromRAW imported from L1Trigger.Configuration.customiseReEmul
process = L1TReEmulFromRAW(process)

#call to customisation function L1TEventSetupForHF1x1TPs imported from L1Trigger.Configuration.customiseReEmul
process = L1TEventSetupForHF1x1TPs(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleAODEMU 

#call to customisation function L1NtupleAODEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleAODEMU(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseUtils
from L1Trigger.Configuration.customiseUtils import L1TTurnOffUnpackStage2GtGmtAndCalo,L1TTurnOffGtAndGmtEmulation 

#call to customisation function L1TTurnOffUnpackStage2GtGmtAndCalo imported from L1Trigger.Configuration.customiseUtils
process = L1TTurnOffUnpackStage2GtGmtAndCalo(process)

#call to customisation function L1TTurnOffGtAndGmtEmulation imported from L1Trigger.Configuration.customiseUtils
# process = L1TTurnOffGtAndGmtEmulation(process)

# Automatic addition of the customisation function from L1Trigger.L1JetEnergyCorrections.customiseL1JEC
# from L1Trigger.L1JetEnergyCorrections.customiseL1JEC import L1JEC_on

#call to customisation function L1JEC_off imported from L1Trigger.L1JetEnergyCorrections.customiseL1JEC
# process = L1JEC_on(process)

# End of customisation functions

process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
       "l1UpgradeEmuTree",
       "l1CaloTowerEmuTree"
       )

# Modify the jet seed threshold, default was 1.5
# jet_seed_threshold = 6
# process.caloStage2Params.jetSeedThreshold = cms.double(jet_seed_threshold)

# Set the NTuple filename
process.TFileService.fileName = cms.string("L1Ntuple.root")
# process.TFileService.fileName = cms.string("L1Ntuple_Stage2_ReReco_HF_noL1Jec_%s_jst%s.root" % (process.GlobalTag.globaltag.value(), str(jet_seed_threshold).replace('.', 'p')))
