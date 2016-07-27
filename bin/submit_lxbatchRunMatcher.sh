#!/bin/bash
# run with $ bsub -q 8nh "sh submit_lxbatchRunMatcher.sh <options in space seperated list>"
# $ bsub -q 8nh "sh submit_lxbatchRunMatcher.sh"
cd /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/
eval `scramv1 runtime -sh`
cd /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/
eval "scram b"

totalCommand="RunMatcherData -I $1 -O $2" 
eval $totalCommand
# echo $totalCommand