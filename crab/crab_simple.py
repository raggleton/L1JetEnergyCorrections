"""
CRAB3 simple config, setup for MC. For DATA, uncomment the relevant section below

Blank strings should be filled in!

Change storageSite to somewhere you have write permissions.
"""

from CRABClient.UserUtilities import config
config = config()

config.General.transferLogs = True
config.General.requestName = ""  # put some descriptive name for the set of jobs here

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = ""  # the cmssw config file path
config.JobType.inputFiles = ['Fall15_25nsV2_MC.db']

config.Data.publication = False

config.Data.inputDataset = ""  # your AOD/RECO dataset here
config.Data.useParent = True  # for 2-file solution

# select one of the below
config.Data.splitting = 'FileBased'
# config.Data.splitting = 'LumiBased'

# this changes with the size of each
config.Data.unitsPerJob = 1  

# For processing DATA:
# -------------------------------------------------
# config.JobType.inputFiles = ['Fall15_25nsV2_DATA.db']
# config.Data.splitting = 'LumiBased'  # use this for data
# config.Data.unitsPerJob = 4
# config.Data.lumiMask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions15/13TeV/Reprocessing/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt'
# config.Data.runRange = '260627'  # Select input data based on run-ranges

# Where the output files will be transmitted to
config.Site.storageSite = 'T2_UK_SGrid_Bristol'
