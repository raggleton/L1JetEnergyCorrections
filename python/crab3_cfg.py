"""
CRAB3 template config for more specific configs (See crab dir)
"""

from CRABClient.UserUtilities import config
config = config()

config.General.transferLogs = True

config.JobType.pluginName  = 'Analysis'

config.Data.splitting = 'FileBased'
config.Data.publication = False

# Where the output files will be transmitted to
config.Site.storageSite = 'T2_UK_SGrid_Bristol'
#config.Site.storageSite = 'T2_UK_SGrid_RALPP'
