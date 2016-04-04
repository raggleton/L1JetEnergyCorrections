#!/bin/bash -e

# startdir =
JST=(2 3 4 5 6)
PU=("0to10" "15to25" "30to40")
for j in ${JST[@]}; do
    subdir="Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst${j}_RAWONLY/check"
    if [[ ! -d "$subdir" ]]
    then
        mkdir -p "$subdir"
    fi
    echo "$subdir"
    cp /hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/$subdir/check_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_maxPt1022.root $PWD/$subdir/
    for pu in ${PU[@]}; do
        cp /hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/$subdir/check_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_fall15JEC_PU${pu}_maxPt1022.root $PWD/$subdir/
    done

    # subdir="Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst${j}_RAWONLY/output"
    # if [[ ! -d "$subdir" ]]
    # then
    #     mkdir -p "$subdir"
    # fi
    # echo "$subdir"
    # cp /hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/$subdir/output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4burr3.root $PWD/$subdir/
    # for pu in ${PU[@]}; do
    #     cp /hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/$subdir/output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU${pu}_burr3.root $PWD/$subdir/
    # done

    subdir="Stage2_HF_QCDFall15_16Mar_int-v14_layer1_noL1JEC_jst${j}_RAWONLY/res"
    if [[ ! -d "$subdir" ]]
    then
        mkdir -p "$subdir"
    fi
    echo "$subdir"
    cp /hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/$subdir/output_QCDFlatFall15NoPU_MP_ak4_ref10to5000_l10to5000_dr0p4burr3.root $PWD/$subdir/
    for pu in ${PU[@]}; do
        cp /hdfs/L1JEC/CMSSW_8_0_2/L1JetEnergyCorrections/$subdir/output_QCDFlatFall15PU0to50NzshcalRaw_MP_ak4_ref10to5000_l10to5000_dr0p4_PU${pu}_burr3.root $PWD/$subdir/
    done
done
