"""
Data samples to be used in CRAB3 configs

For each sample, we have a simple Dataset namedtuple. Fields are inputDataset,
unitsPerJob, and totalUnits. (see CRAB documentationf or meaning).
We then store all samples in a dict.

Usage:

from data_samples import samples

dataset = "Express_Run2015B_50ns"
config.General.requestName = dataset
config.Data.inputDataset = samples[dataset].inputDataset
config.Data.unitsPerJob = samples[dataset].unitsPerJob

totalUnits can take the values:
-1: run over all files in the dataset
0 - 1: run over this fraction of the dataset
>1: run over this many files

"""

from collections import namedtuple
import subprocess
import json
import os

# some helper functions
def get_number_files(dataset):
    """Get total number of files in dataset"""
    HOME = os.environ['HOME']
    cmds = ['das_client.py', '--query', 'summary dataset=%s' % dataset, '--format=json',
            '--key=%s/.globus/userkey.pem' % HOME, '--cert=%s/.globus/usercert.pem' % HOME]
    output = subprocess.check_output(cmds, stderr=subprocess.STDOUT)
    summary_dict = json.loads(output)
    return int(summary_dict['data'][0]['summary'][0]['nfiles'])


def check_dataset_exists(dataset):
    """Check dataset exists in DAS"""
    result = subprocess.call(['das_client.py', '--query', 'dataset dataset=%s' % dataset])
    return result == 0


# handy data structure to store some attributes for each dataset
Dataset = namedtuple("Dataset", "inputDataset unitsPerJob totalUnits useParent")

# This dict holds ALL samples
samples = {

    "SingleMuReReco_Run2015D": Dataset(inputDataset='/SingleMuon/Run2015D-16Dec2015-v1/AOD',
                                       useParent=True, unitsPerJob=4, totalUnits=-1),

    "ZeroBiasReReco_Run2015D_2": Dataset(inputDataset='/ZeroBias2/Run2015D-16Dec2015-v1/AOD', 
                                       useParent=True, unitsPerJob=4, totalUnits=-1),
    
    "ZeroBiasReReco_Run2015D_1": Dataset(inputDataset='/ZeroBias1/Run2015D-16Dec2015-v1/AOD', 
                                       useParent=True, unitsPerJob=4, totalUnits=-1),
    
    "Express_Run2015B_50ns": Dataset(inputDataset='/ExpressPhysics/Run2015B-Express-v1/FEVT',
                                     useParent=False, unitsPerJob=15, totalUnits=-1),

    "Express_Run2015D_v4_25ns": Dataset(inputDataset='/ExpressPhysics/Run2015D-Express-v4/FEVT',
                                        useParent=False, unitsPerJob=10, totalUnits=-1),

    "ZeroBiasReReco_Run2015D_0" : Dataset(inputDataset='/ZeroBias/Run2015D-16Dec2015-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasReReco_Run2015D_1" : Dataset(inputDataset='/ZeroBias1/Run2015D-16Dec2015-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasReReco_Run2015D_2" : Dataset(inputDataset='/ZeroBias2/Run2015D-16Dec2015-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasReReco_Run2015D_3" : Dataset(inputDataset='/ZeroBias3/Run2015D-16Dec2015-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasReReco_Run2015D_4" : Dataset(inputDataset='/ZeroBias4/Run2015D-16Dec2015-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBias_com2016_1" :  Dataset(inputDataset='/ZeroBias1/Commissioning2016-PromptReco-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBias_com2016_2" :  Dataset(inputDataset='/ZeroBias2/Commissioning2016-PromptReco-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBias_com2016_3" :  Dataset(inputDataset='/ZeroBias3/Commissioning2016-PromptReco-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBias_com2016_4" :  Dataset(inputDataset='/ZeroBias4/Commissioning2016-PromptReco-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBias_com2016_5" :  Dataset(inputDataset='/ZeroBias5/Commissioning2016-PromptReco-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBias_com2016_6" :  Dataset(inputDataset='/ZeroBias6/Commissioning2016-PromptReco-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBias_com2016_7" :  Dataset(inputDataset='/ZeroBias7/Commissioning2016-PromptReco-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBias_com2016_8" :  Dataset(inputDataset='/ZeroBias8/Commissioning2016-PromptReco-v1/AOD',
                                      useParent=True, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasRaw_com2016_1" :  Dataset(inputDataset='/ZeroBias1/Commissioning2016-PromptReco-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasRaw_com2016_2" :  Dataset(inputDataset='/ZeroBias2/Commissioning2016-PromptReco-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasRaw_com2016_3" :  Dataset(inputDataset='/ZeroBias3/Commissioning2016-PromptReco-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasRaw_com2016_4" :  Dataset(inputDataset='/ZeroBias4/Commissioning2016-PromptReco-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasRaw_com2016_5" :  Dataset(inputDataset='/ZeroBias5/Commissioning2016-PromptReco-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasRaw_com2016_6" :  Dataset(inputDataset='/ZeroBias6/Commissioning2016-PromptReco-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasRaw_com2016_7" :  Dataset(inputDataset='/ZeroBias7/Commissioning2016-PromptReco-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1),

    "ZeroBiasRaw_com2016_8" :  Dataset(inputDataset='/ZeroBias8/Commissioning2016-PromptReco-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1),

    "MinimumBiasRaw_Run2016B" : Dataset(inputDataset='/MinimumBias/Run2016B-v1/RAW',
                                      useParent=False, unitsPerJob=2, totalUnits=-1)

}
