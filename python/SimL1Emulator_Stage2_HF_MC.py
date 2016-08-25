"""
Config file to run the Stage 2 emulator to make Ntuples.

Now comes with HF!

Stores L1 jets, as well as ak4 GenJets
"""
# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: l1Ntuple -s RAW2DIGI --era=Run2_2016 --conditions=auto:run2_mc -n 100 --mc --customise=L1Trigger/Configuration/customiseReEmul.L1TReEmulFromRAW --geometry=Extended2016,Extended2016Reco --customise=L1Trigger/L1TNtuples/customiseL1Ntuple.L1NtupleAODEMU --customise=L1Trigger/L1JetEnergyCorrections/customiseL1JEC.L1NtupleJEC_OFF --no_output --python_filename=SimL1Emulator_Stage2_HF_Layer1_MC_test.py --no_exec --customise=L1Trigger/Configuration/customiseUtils.L1TTurnOffUnpackStage2GtGmtAndCalo --customise_commands=process.l1CaloTowerEmuTree.ecalToken = cms.untracked.InputTag('ecalDigis', 'EcalTriggerPrimitives')\nprocess.l1CustomReco.replace(process.ak4PFCHSL1FastL2L3ResidualCorrectorChain, process.ak4PFCHSL1FastL2L3CorrectorChain)\nprocess.l1JetRecoTree.jecToken = 'ak4PFCHSL1FastL2L3Corrector' --filein=/store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RECO/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/929E688D-E94E-E511-8AD2-0026189438EA.root,/store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RECO/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/C04FFC53-F14E-E511-91BA-002590593876.root,/store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RECO/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/EAB9AC8A-E94E-E511-8B45-002618943935.root --secondfilein=/store/mc/RunIISpring15DR74/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/NhcalZSHFscaleFlat10to30Asympt25ns_MCRUN2_74_V9-v1/00000/003BEF9B-C24E-E511-B4B7-0025905A609E.root
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('RAW2DIGI',eras.Run2_2016)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2016Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(200)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/AODSIM/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/4E1D11E4-1DA9-E511-AED1-001E67397EDB.root'),
    # fileNames = cms.untracked.vstring('/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/8A409B34-02A9-E511-ABBE-002590A8882C.root')
    secondaryFileNames = cms.untracked.vstring(
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/000E1488-EDA8-E511-8A50-001E67E6F65C.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/0079B9F8-F3A8-E511-83C8-001E67397D91.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/14F3000C-F2A8-E511-AA7A-002590A3CA16.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/26BA9318-F2A8-E511-9148-001E67397F3F.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/2E9032FE-F3A8-E511-8BE2-001E67398E6C.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/4C5BCB7D-EDA8-E511-90DD-001E67396E1E.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/602142F9-F3A8-E511-86A0-001E67E71417.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/8856AFCA-F3A8-E511-94DA-001E67E6F7CE.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/8A409B34-02A9-E511-ABBE-002590A8882C.root',
        '/store/mc/RunIIFall15DR76/QCD_Pt-15to3000_TuneCUETP8M1_Flat_13TeV_pythia8/GEN-SIM-RAW/25nsFlat0to50NzshcalRaw_76X_mcRun2_asymptotic_v12-v1/20000/B2C35BD7-F3A8-E511-BAD2-001E67E6F616.root',
        )
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

process.MessageLogger.cerr.FwkReport.reportEvery = 200
process.MessageLogger.suppressWarning = cms.untracked.vstring(
    "l1UpgradeEmuTree",
    'l1ExtraTreeGenAk4'
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1Ntuple nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.endjob_step)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseReEmul
from L1Trigger.Configuration.customiseReEmul import L1TReEmulFromRAW

#call to customisation function L1TReEmulFromRAW imported from L1Trigger.Configuration.customiseReEmul
process = L1TReEmulFromRAW(process)

# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleAODEMU

#call to customisation function L1NtupleAODEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleAODEMU(process)

# Automatic addition of the customisation function from L1Trigger.L1JetEnergyCorrections.customiseL1JEC
from L1Trigger.L1JetEnergyCorrections.customiseL1JEC import L1NtupleJEC 

#call to customisation function L1NtupleJEC_OFF imported from L1Trigger.L1JetEnergyCorrections.customiseL1JEC
process = L1NtupleJEC(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseUtils
from L1Trigger.Configuration.customiseUtils import L1TTurnOffUnpackStage2GtGmtAndCalo, L1TTurnOffGtAndGmtEmulation

#call to customisation function L1TTurnOffUnpackStage2GtGmtAndCalo imported from L1Trigger.Configuration.customiseUtils
process = L1TTurnOffUnpackStage2GtGmtAndCalo(process)

# process = L1TTurnOffGtAndGmtEmulation(process)

# End of customisation functions

# Customisation from command line
process.l1CaloTowerEmuTree.ecalToken = cms.untracked.InputTag('ecalDigis', 'EcalTriggerPrimitives')
process.l1CustomReco.replace(process.ak4PFCHSL1FastL2L3ResidualCorrectorChain, process.ak4PFCHSL1FastL2L3CorrectorChain)
process.l1JetRecoTree.jecToken = 'ak4PFCHSL1FastL2L3Corrector'

# Modify the jet seed threshold, default was 1.5
# jet_seed_threshold = 1.5
# process.caloStage2Params.jetSeedThreshold = cms.double(jet_seed_threshold)

# Set the NTuple filename
process.TFileService.fileName = cms.string("L1Ntuple.root")
#process.TFileService.fileName = cms.string("L1Ntuple_Stage2_Fall15MC_HF_layer1_noL1Jec_%s_jst%s.root" % (process.GlobalTag.globaltag.value(), str(jet_seed_threshold).replace('.', 'p')))

