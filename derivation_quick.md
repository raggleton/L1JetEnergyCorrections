#Quick guide

Basic steps:

1) Make Ntuples **without** L1JEC applied

2) Run Matcher to make "pairs" file

3) Run other scripts on pairs file:

  * [bin/runCalibration.py](bin/runCalibration.py) to make calibration curves

  * [bin/checkCalibration.py](bin/checkCalibration.py) to make response plots

  * [bin/makeResolutionPlots.py](bin/makeResolutionPlots.py) to make energy resolution plots

  * [showoffPlots.py](bin/showoffPlots.py) to put the above into PDF/PNGs

4) Make new LUTs: [bin/corrections_LUT_plot.py](bin/corrections_LUT_plot.py)

5) Make another set of NTuples with your new corrections (LUT or functions)

6) Rerun [bin/checkCalibration.py](bin/checkCalibration.py) to ensure all tickety boo

**NB currently assumes Stage 2 setup**

## More pointers

**1: Making Ntuples without L1JEC**

- If running over MC, ensure you have the genJets there - now in Generator Tree?

- To turn off L1JEC, you will need to add to your CMSSW config file:

```
process.caloStage2Params.jetCalibrationType = cms.string("None")
```

**2: Running the matcher**

- There are several matchers, depending on what you're matching:

    * L1 w/ GenJet: [bin/RunMatcherStage2L1Gen](bin/RunMatcherStage2L1Gen.cpp)
    * L1 w/ PF (MC): [bin/RunMatcherStage2L1PF](bin/RunMatcherStage2L1PF.cpp)
    * L1 w/ PF (data): [bin/RunMatcherData](bin/RunMatcherData.cpp)
    * GenJet w/ PFJet: [bin/RunMatcherStage2PFGen](bin/RunMatcherStage2PFGen.cpp)

- Show options with `-h` flag

- There is a script to run this on LXBATCH ([bin/submit_lxbatchRunMatcher.sh](bin/submit_lxbatchRunMatcher.sh) or [/bin/local_L1JEC_scripts/lxbatchRunMatcher.py](/bin/local_L1JEC_scripts/lxbatchRunMatcher.py)???) or HTCondor (Bristol only, [bin/HTCondor/submit_matcher_dag.py](bin/HTCondor/submit_matcher_dag.py))

**3: Running other scripts**

- Again, use `-h` on commandline to show options

- Most have PU flags to specify PU bin

- Also LXBATCH scripts and HTCondor scripts

- Use [showoffPlots.py](bin/showoffPlots.py) to dump ROOT files produced by other scripts to plots

**4: Make new LUTs**

- Requires `matplotlib`

- Can either use existing PT binning, or derive new set

**5: Make another set of Ntuples**

- Use the human-readable output from the LUT maker script, of the functional form

**6: Rerun checkCalibration.py**

- As before