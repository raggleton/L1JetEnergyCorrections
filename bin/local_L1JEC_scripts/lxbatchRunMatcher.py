import os
import eosComfort

# requires eosComfort.py to be set up correctly...<--ATTENTION
# TORUN, do so from jobLogs directory
# $ python /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/local_L1JEC_scripts/lxbatchRunMatcher.py

#######################################
#######################################

outputDirectory = "/afs/cern.ch/user/t/taylor/L1TriggerStudies/output_jets/pairs_crab_QCDFlatFall15PU0to50NzshcalRaw_QCDFall15_genEmu_22Jul2016_809v70_L1JECinFuncFormdc669_L1JEC8f68e_v2/"

#######################################
#######################################

os.system("mkdir %s" % outputDirectory)




######################
# for running from eos
###################### 

# for i in range (0, len(eosComfort.fullPaths)): # real thing
# # for i in range (0, 2): # for testing

# 	for j in range (0, len(eosComfort.ntupleNames[i])):

# 		inputFilePath = "root://eoscms.cern.ch/" + eosComfort.fullPaths[i] + eosComfort.ntupleNames[i][j]
# 		outputFilesPath = outputDirectory + "pairs_" + eosComfort.daughterDirs[i][:-1] + "_" + str(j) + ".root" #nb: the numerical label does not correspond to the original ntuple label

# 		# for testing output command
# 		# print('bsub -q 8nh "sh /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcher.sh %s %s"' % (inputFilePath, outputFilesPath) )
# 		# print ""

# 		# for testing outut command when fed into submission script
# 		# os.system("source /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcher.sh %s %s" % (inputFilePath, outputFilesPath) )

# 		# for the real thing
		# os.system('bsub -q 8nh "sh /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcherData.sh %s %s"' % (inputFilePath, outputFilesPath) )
		# os.system('bsub -q 8nh "sh /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcher.sh %s %s"' % (inputFilePath, outputFilesPath) )




##############################
# more of a brute force method
##############################

dirPath = "/afs/cern.ch/work/t/taylor/public/L1TriggerNtuples/l1ntuple_QCDFall15_genEmu_22Jul2016_809v70_L1JECinFuncFormdc669_L1JEC8f68e_v2/crab_QCDFlatFall15PU0to50NzshcalRaw_QCDFall15_genEmu_22Jul2016_809v70_L1JECinFuncFormdc669_L1JEC8f68e_v2/results/"
rootFiles = [
"L1Ntuple_1.root",    "L1Ntuple_172.root",	"L1Ntuple_241.root",  "L1Ntuple_316.root",	"L1Ntuple_387.root",  "L1Ntuple_462.root",
"L1Ntuple_100.root",  "L1Ntuple_173.root",	"L1Ntuple_242.root",  "L1Ntuple_317.root",	"L1Ntuple_388.root",  "L1Ntuple_463.root",
"L1Ntuple_102.root",  "L1Ntuple_174.root",	"L1Ntuple_244.root",  "L1Ntuple_318.root",	"L1Ntuple_389.root",  "L1Ntuple_464.root",
"L1Ntuple_103.root",  "L1Ntuple_175.root",	"L1Ntuple_245.root",  "L1Ntuple_319.root",	"L1Ntuple_39.root",   "L1Ntuple_465.root",
"L1Ntuple_104.root",  "L1Ntuple_176.root",	"L1Ntuple_246.root",  "L1Ntuple_32.root",	"L1Ntuple_391.root",  "L1Ntuple_466.root",
"L1Ntuple_106.root",  "L1Ntuple_177.root",	"L1Ntuple_247.root",  "L1Ntuple_320.root",	"L1Ntuple_392.root",  "L1Ntuple_467.root",
"L1Ntuple_108.root",  "L1Ntuple_178.root",	"L1Ntuple_248.root",  "L1Ntuple_321.root",	"L1Ntuple_393.root",  "L1Ntuple_468.root",
"L1Ntuple_109.root",  "L1Ntuple_179.root",	"L1Ntuple_249.root",  "L1Ntuple_323.root",	"L1Ntuple_394.root",  "L1Ntuple_469.root",
"L1Ntuple_11.root",   "L1Ntuple_18.root",	"L1Ntuple_25.root",   "L1Ntuple_324.root",	"L1Ntuple_395.root",  "L1Ntuple_47.root",
"L1Ntuple_110.root",  "L1Ntuple_180.root",	"L1Ntuple_250.root",  "L1Ntuple_325.root",	"L1Ntuple_396.root",  "L1Ntuple_470.root",
"L1Ntuple_111.root",  "L1Ntuple_181.root",	"L1Ntuple_251.root",  "L1Ntuple_326.root",	"L1Ntuple_397.root",  "L1Ntuple_471.root",
"L1Ntuple_112.root",  "L1Ntuple_182.root",	"L1Ntuple_252.root",  "L1Ntuple_327.root",	"L1Ntuple_398.root",  "L1Ntuple_472.root",
"L1Ntuple_113.root",  "L1Ntuple_183.root",	"L1Ntuple_253.root",  "L1Ntuple_328.root",	"L1Ntuple_399.root",  "L1Ntuple_473.root",
"L1Ntuple_114.root",  "L1Ntuple_184.root",	"L1Ntuple_254.root",  "L1Ntuple_33.root",	"L1Ntuple_4.root",    "L1Ntuple_475.root",
"L1Ntuple_115.root",  "L1Ntuple_185.root",	"L1Ntuple_255.root",  "L1Ntuple_330.root",	"L1Ntuple_40.root",   "L1Ntuple_476.root",
"L1Ntuple_116.root",  "L1Ntuple_186.root",	"L1Ntuple_256.root",  "L1Ntuple_332.root",	"L1Ntuple_400.root",  "L1Ntuple_477.root",
"L1Ntuple_117.root",  "L1Ntuple_187.root",	"L1Ntuple_257.root",  "L1Ntuple_333.root",	"L1Ntuple_401.root",  "L1Ntuple_48.root",
"L1Ntuple_118.root",  "L1Ntuple_188.root",	"L1Ntuple_258.root",  "L1Ntuple_334.root",	"L1Ntuple_402.root",  "L1Ntuple_49.root",
"L1Ntuple_119.root",  "L1Ntuple_189.root",	"L1Ntuple_259.root",  "L1Ntuple_335.root",	"L1Ntuple_403.root",  "L1Ntuple_5.root",
"L1Ntuple_120.root",  "L1Ntuple_19.root",	"L1Ntuple_26.root",   "L1Ntuple_337.root",	"L1Ntuple_404.root",  "L1Ntuple_50.root",
"L1Ntuple_121.root",  "L1Ntuple_190.root",	"L1Ntuple_260.root",  "L1Ntuple_338.root",	"L1Ntuple_406.root",  "L1Ntuple_51.root",
"L1Ntuple_122.root",  "L1Ntuple_191.root",	"L1Ntuple_261.root",  "L1Ntuple_339.root",	"L1Ntuple_407.root",  "L1Ntuple_52.root",
"L1Ntuple_123.root",  "L1Ntuple_192.root",	"L1Ntuple_262.root",  "L1Ntuple_34.root",	"L1Ntuple_408.root",  "L1Ntuple_53.root",
"L1Ntuple_124.root",  "L1Ntuple_193.root",	"L1Ntuple_263.root",  "L1Ntuple_340.root",	"L1Ntuple_409.root",  "L1Ntuple_54.root",
"L1Ntuple_125.root",  "L1Ntuple_194.root",	"L1Ntuple_264.root",  "L1Ntuple_341.root",	"L1Ntuple_41.root",   "L1Ntuple_55.root",
"L1Ntuple_126.root",  "L1Ntuple_195.root",	"L1Ntuple_265.root",  "L1Ntuple_342.root",	"L1Ntuple_410.root",  "L1Ntuple_56.root",
"L1Ntuple_127.root",  "L1Ntuple_196.root",	"L1Ntuple_266.root",  "L1Ntuple_343.root",	"L1Ntuple_411.root",  "L1Ntuple_57.root",
"L1Ntuple_128.root",  "L1Ntuple_197.root",	"L1Ntuple_267.root",  "L1Ntuple_344.root",	"L1Ntuple_412.root",  "L1Ntuple_58.root",
"L1Ntuple_129.root",  "L1Ntuple_198.root",	"L1Ntuple_268.root",  "L1Ntuple_345.root",	"L1Ntuple_413.root",  "L1Ntuple_59.root",
"L1Ntuple_13.root",   "L1Ntuple_199.root",	"L1Ntuple_269.root",  "L1Ntuple_346.root",	"L1Ntuple_414.root",  "L1Ntuple_6.root",
"L1Ntuple_131.root",  "L1Ntuple_2.root",	"L1Ntuple_27.root",   "L1Ntuple_347.root",	"L1Ntuple_415.root",  "L1Ntuple_60.root",
"L1Ntuple_132.root",  "L1Ntuple_20.root",	"L1Ntuple_270.root",  "L1Ntuple_348.root",	"L1Ntuple_416.root",  "L1Ntuple_61.root",
"L1Ntuple_133.root",  "L1Ntuple_201.root",	"L1Ntuple_271.root",  "L1Ntuple_349.root",	"L1Ntuple_417.root",  "L1Ntuple_62.root",
"L1Ntuple_134.root",  "L1Ntuple_202.root",	"L1Ntuple_272.root",  "L1Ntuple_35.root",	"L1Ntuple_42.root",   "L1Ntuple_63.root",
"L1Ntuple_135.root",  "L1Ntuple_203.root",	"L1Ntuple_273.root",  "L1Ntuple_350.root",	"L1Ntuple_420.root",  "L1Ntuple_64.root",
"L1Ntuple_136.root",  "L1Ntuple_204.root",	"L1Ntuple_274.root",  "L1Ntuple_351.root",	"L1Ntuple_421.root",  "L1Ntuple_65.root",
"L1Ntuple_137.root",  "L1Ntuple_206.root",	"L1Ntuple_275.root",  "L1Ntuple_352.root",	"L1Ntuple_424.root",  "L1Ntuple_66.root",
"L1Ntuple_138.root",  "L1Ntuple_207.root",	"L1Ntuple_276.root",  "L1Ntuple_353.root",	"L1Ntuple_425.root",  "L1Ntuple_67.root",
"L1Ntuple_139.root",  "L1Ntuple_208.root",	"L1Ntuple_277.root",  "L1Ntuple_354.root",	"L1Ntuple_426.root",  "L1Ntuple_68.root",
"L1Ntuple_14.root",   "L1Ntuple_209.root",	"L1Ntuple_279.root",  "L1Ntuple_355.root",	"L1Ntuple_427.root",  "L1Ntuple_69.root",
"L1Ntuple_140.root",  "L1Ntuple_21.root",	"L1Ntuple_28.root",   "L1Ntuple_356.root",	"L1Ntuple_428.root",  "L1Ntuple_7.root",
"L1Ntuple_141.root",  "L1Ntuple_210.root",	"L1Ntuple_280.root",  "L1Ntuple_357.root",	"L1Ntuple_429.root",  "L1Ntuple_70.root",
"L1Ntuple_142.root",  "L1Ntuple_211.root",	"L1Ntuple_281.root",  "L1Ntuple_358.root",	"L1Ntuple_432.root",  "L1Ntuple_71.root",
"L1Ntuple_143.root",  "L1Ntuple_212.root",	"L1Ntuple_282.root",  "L1Ntuple_359.root",	"L1Ntuple_433.root",  "L1Ntuple_72.root",
"L1Ntuple_144.root",  "L1Ntuple_213.root",	"L1Ntuple_284.root",  "L1Ntuple_36.root",	"L1Ntuple_434.root",  "L1Ntuple_73.root",
"L1Ntuple_145.root",  "L1Ntuple_215.root",	"L1Ntuple_286.root",  "L1Ntuple_360.root",	"L1Ntuple_435.root",  "L1Ntuple_74.root",
"L1Ntuple_146.root",  "L1Ntuple_216.root",	"L1Ntuple_288.root",  "L1Ntuple_361.root",	"L1Ntuple_437.root",  "L1Ntuple_75.root",
"L1Ntuple_147.root",  "L1Ntuple_217.root",	"L1Ntuple_289.root",  "L1Ntuple_362.root",	"L1Ntuple_438.root",  "L1Ntuple_76.root",
"L1Ntuple_148.root",  "L1Ntuple_218.root",	"L1Ntuple_29.root",   "L1Ntuple_363.root",	"L1Ntuple_44.root",   "L1Ntuple_77.root",
"L1Ntuple_149.root",  "L1Ntuple_219.root",	"L1Ntuple_291.root",  "L1Ntuple_364.root",	"L1Ntuple_440.root",  "L1Ntuple_78.root",
"L1Ntuple_15.root",   "L1Ntuple_22.root",	"L1Ntuple_292.root",  "L1Ntuple_365.root",	"L1Ntuple_441.root",  "L1Ntuple_79.root",
"L1Ntuple_150.root",  "L1Ntuple_220.root",	"L1Ntuple_293.root",  "L1Ntuple_366.root",	"L1Ntuple_442.root",  "L1Ntuple_8.root",
"L1Ntuple_151.root",  "L1Ntuple_221.root",	"L1Ntuple_294.root",  "L1Ntuple_367.root",	"L1Ntuple_443.root",  "L1Ntuple_80.root",
"L1Ntuple_152.root",  "L1Ntuple_222.root",	"L1Ntuple_295.root",  "L1Ntuple_368.root",	"L1Ntuple_444.root",  "L1Ntuple_81.root",
"L1Ntuple_154.root",  "L1Ntuple_223.root",	"L1Ntuple_297.root",  "L1Ntuple_369.root",	"L1Ntuple_445.root",  "L1Ntuple_82.root",
"L1Ntuple_155.root",  "L1Ntuple_224.root",	"L1Ntuple_299.root",  "L1Ntuple_37.root",	"L1Ntuple_446.root",  "L1Ntuple_83.root",
"L1Ntuple_156.root",  "L1Ntuple_225.root",	"L1Ntuple_3.root",    "L1Ntuple_370.root",	"L1Ntuple_447.root",  "L1Ntuple_84.root",
"L1Ntuple_157.root",  "L1Ntuple_226.root",	"L1Ntuple_30.root",   "L1Ntuple_371.root",	"L1Ntuple_448.root",  "L1Ntuple_85.root",
"L1Ntuple_158.root",  "L1Ntuple_227.root",	"L1Ntuple_300.root",  "L1Ntuple_372.root",	"L1Ntuple_449.root",  "L1Ntuple_86.root",
"L1Ntuple_159.root",  "L1Ntuple_228.root",	"L1Ntuple_301.root",  "L1Ntuple_373.root",	"L1Ntuple_45.root",   "L1Ntuple_87.root",
"L1Ntuple_16.root",   "L1Ntuple_229.root",	"L1Ntuple_303.root",  "L1Ntuple_375.root",	"L1Ntuple_450.root",  "L1Ntuple_88.root",
"L1Ntuple_160.root",  "L1Ntuple_23.root",	"L1Ntuple_304.root",  "L1Ntuple_376.root",	"L1Ntuple_451.root",  "L1Ntuple_89.root",
"L1Ntuple_161.root",  "L1Ntuple_230.root",	"L1Ntuple_305.root",  "L1Ntuple_377.root",	"L1Ntuple_452.root",  "L1Ntuple_9.root",
"L1Ntuple_163.root",  "L1Ntuple_231.root",	"L1Ntuple_306.root",  "L1Ntuple_378.root",	"L1Ntuple_453.root",  "L1Ntuple_90.root",
"L1Ntuple_164.root",  "L1Ntuple_232.root",	"L1Ntuple_307.root",  "L1Ntuple_379.root",	"L1Ntuple_454.root",  "L1Ntuple_91.root",
"L1Ntuple_165.root",  "L1Ntuple_233.root",	"L1Ntuple_308.root",  "L1Ntuple_38.root",	"L1Ntuple_455.root",  "L1Ntuple_92.root",
"L1Ntuple_166.root",  "L1Ntuple_235.root",	"L1Ntuple_31.root",   "L1Ntuple_380.root",	"L1Ntuple_456.root",  "L1Ntuple_93.root",
"L1Ntuple_167.root",  "L1Ntuple_236.root",	"L1Ntuple_310.root",  "L1Ntuple_381.root",	"L1Ntuple_457.root",  "L1Ntuple_94.root",
"L1Ntuple_168.root",  "L1Ntuple_237.root",	"L1Ntuple_311.root",  "L1Ntuple_382.root",	"L1Ntuple_458.root",  "L1Ntuple_95.root",
"L1Ntuple_169.root",  "L1Ntuple_238.root",	"L1Ntuple_312.root",  "L1Ntuple_383.root",	"L1Ntuple_459.root",  "L1Ntuple_96.root",
"L1Ntuple_17.root",   "L1Ntuple_239.root",	"L1Ntuple_313.root",  "L1Ntuple_384.root",	"L1Ntuple_46.root",   "L1Ntuple_97.root",
"L1Ntuple_170.root",  "L1Ntuple_24.root",	"L1Ntuple_314.root",  "L1Ntuple_385.root",	"L1Ntuple_460.root",  "L1Ntuple_98.root",
"L1Ntuple_171.root",  "L1Ntuple_240.root",	"L1Ntuple_315.root",  "L1Ntuple_386.root",	"L1Ntuple_461.root",  "L1Ntuple_99.root",
]

for rootFile in rootFiles:
	inputFilePath = dirPath + rootFile
	outputFilesPath = outputDirectory + "pairs_" + rootFile
	os.system('bsub -q 8nh "sh /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcher.sh %s %s"' % (inputFilePath, outputFilesPath) )
	# os.system('bsub -q 8nh "sh /afs/cern.ch/user/t/taylor/CMSSW_8_0_9/src/L1Trigger/L1JetEnergyCorrections/bin/submit_lxbatchRunMatcherData.sh %s %s"' % (inputFilePath, outputFilesPath) )