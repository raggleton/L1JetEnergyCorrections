import FWCore.ParameterSet.Config as cms


"""
Customisation for MC L1NTuples, for generating ntuples suitable for L1JEC.

Only needed for MC!

For **no** L1JEC, i.e. if deriving calibrations, add to cmsDriver.py:

--customise=L1Trigger/L1JetEnergyCorrections/customiseL1JEC.L1NtupleJEC_OFF

To include L1JEC, i.e. if testing/validating calibrations, add to cmsDriver.py:

--customise=L1Trigger/L1JetEnergyCorrections/customiseL1JEC.L1NtupleJEC_ON
"""


def L1NtupleJEC_ON(process):
    """Setup L1Ntuples for L1JEC, with L1JEC applied."""
    # TODD: how to ensure it's on in caloStage2Params?
    # we dont want to change the calib mode if there is one specified, but
    # what if there isn't?
    L1NtupleJEC(process)
    L1JEC_on(process)
    return process


def L1NtupleJEC_OFF(process):
    """Setup L1Ntuples for L1JEC, with no L1JEC applied."""
    L1NtupleJEC(process)
    L1JEC_off(process)
    return process


def L1NtupleJEC(process):
    """Customise L1Ntuple for L1JEC for MC.

    Adds in:
    - GenJets (into the cenJet branch of an L1ExtraTree)
    - PU Info

    Also removes other modules we don't care about (muons, tracks).
    """
    # Convert GenJet obj to format for L1Extra
    # Such a nasty hack.
    process.genJetToL1JetAk4 = cms.EDProducer("GenJetToL1Jet",
        genJetSource = cms.InputTag("ak4GenJets")
    )

    # Put in another L1ExtraTree as cenJets
    process.load("L1Trigger.L1TNtuples.l1ExtraTree_cfi")
    process.l1ExtraTreeGenAk4 = process.l1ExtraTree.clone()
    process.l1ExtraTreeGenAk4.nonIsoEmToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.isoEmToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.tauJetToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.isoTauJetToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.cenJetToken = cms.untracked.InputTag("genJetToL1JetAk4:GenJets")
    process.l1ExtraTreeGenAk4.fwdJetToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.muonToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.metToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.mhtToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.hfRingsToken = cms.untracked.InputTag("")
    process.l1ExtraTreeGenAk4.maxL1Extra = cms.uint32(50)

    # Store PU info (nvtx, etc)
    process.puInfo = cms.EDAnalyzer("PileupInfo",
        pileupInfoSource = cms.InputTag("addPileupInfo")
    )

    # Add it all to the schedule as new Path
    process.l1jec = cms.Path(
        process.genJetToL1JetAk4 +
        process.l1ExtraTreeGenAk4 +
        process.puInfo)

    process.schedule.append(process.l1jec)

    # Use MP jets for JEC
    process.l1UpgradeEmuTree.jetToken = cms.untracked.InputTag("simCaloStage2Digis", "MP")

    # Get rid of unnecessary Stage 1 modules
    # remove_modules = [
    #     process.L1TRawToDigi,
    #     process.siPixelDigis,
    #     process.siStripDigis,
    #     process.muonCSCDigis,
    #     process.muonDTDigis,
    #     process.muonRPCDigis,
    #     process.castorDigis
    # ]
    # for mod in remove_modules:
    #     if mod.label() in process.__dict__.keys():
    #         result = process.RawToDigi.remove(mod)

    return process


def L1JEC_off(process):
    """Turn Stage 2 JEC OFF"""
    process.caloStage2Params.jetCalibrationType = cms.string("None")
    return process


def L1JEC_on(process):
    """Turn Stage 2 JEC ON"""
    process.caloStage2Params.jetCalibrationType = cms.string("function8PtParams22EtaBins")
    return process
