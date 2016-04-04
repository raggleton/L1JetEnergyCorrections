#!/usr/bin/env python

"""
Submit makeResolutionPlots jobs on HTCondor.

- add in any pairs files you wish to run over (use absolute path)
- modify settings below (PU bins, append, etc)

Output files will be produced as follows: for pairs file, DATASET/pairs/pairs.root,
the output files will be put in DATASET/resolution/

Requires the htcondenser package: https://github.com/raggleton/htcondenser
"""


import argparse
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))  # to import binning.py
import binning
from binning import pairwise
from time import strftime
import htcondenser as ht
import condorCommon as cc
import logging
from itertools import chain


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


# List of pairs files to run over
PAIRS_FILES = [
# '/hdfs/user/ra12451/L1JEC/CMSSW_7_6_0_pre7/L1JetEnergyCorrections/Stage2_QCDFlatSpring15BX25HCALFix_26Nov_76X_mcRun2_asymptotic_v5_jetSeed1p5_noJec_v2/pairs/pairs_QCDFlatSpring15BX25PU10to30HCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4_testCalibratePU15to25_2048bins_maxCorr5.root'
'/hdfs/user/ra12451/L1JEC/CMSSW_8_0_0_pre5/L1JetEnergyCorrections/Stage2_HF_QCDFlatSpring15BX25HCALFix_10Feb_2dd1043_noJEC_v2/pairs/pairs_QCDFlatSpring15BX25FlatNoPUHCALFix_MP_ak4_ref10to5000_l10to5000_dr0p4.root'
]

# Maximum L1 pt to be included in plots (to avoid saturation effects)
MAX_L1_PT = 1022

# Select eta bins to run over
ETA_BINS = binning.eta_bins

# Select PU bins to run over
PU_BINS = None  # None if you don't want to cut on PU
# PU_BINS = binning.pu_bins

# String to append to output ROOT filename, depending on PU
# Note that the things in {} get formatted out later, see below
# Bit of dodgy magic
APPEND = "_PU{puMin}to{puMax}_maxPt{maxL1Pt}" if PU_BINS else "_maxPt{maxL1Pt}"

# Directory for logs (should be on /storage)
# Will be created automatically by htcondenser
datestamp = strftime("%d_%b_%y")
LOG_DIR = '/storage/%s/L1JEC/%s/L1JetEnergyCorrections/jobs/res/%s' % (os.environ['LOGNAME'], os.environ['CMSSW_VERSION'], datestamp)


def submit_all_resolution_dags(pairs_files, max_l1_pt, log_dir, append,
                               pu_bins, eta_bins, force_submit):
    """Create and submit DAG makeResolutionPlots jobs for all pairs files.

    Parameters
    ----------
    pairs_files : list[str], optional
        List of pairs files to process. Must be full path.

    max_l1_pt : int, optional
        Maximum L1 pt to consider when making plots.

    log_dir : str, optional
        Directory for STDOUT/STDERR/LOG files. Should be on /storage.

    append : str, optional
        String to append to filenames to track various settings (e.g. PU bin).

    pu_bins : list[list[int, int]], optional
        List of PU bin edges.

    eta_bins : list[float], optional
        List of eta bin edges, including upper edge of last bin.

    force_submit : bool, optional
        If True, forces job submission even if proposed output files already exists.
        Otherwise, program quits before submission.
    """
    # Update the matcher script for the worker nodes
    setup_script = 'worker_setup.sh'
    cc.update_setup_script(setup_script, os.environ['CMSSW_VERSION'], os.environ['ROOTSYS'])

    # Update the hadd script for the worker node
    hadd_setup_script = 'cmssw_setup.sh'
    cc.update_hadd_setup_script(hadd_setup_script, os.environ['CMSSW_VERSION'])

    # Additional files to copy across - other modules. etc
    common_input_files = ['makeResolutionPlots.py', 'binning.py', 'common_utils.py']
    common_input_files = [os.path.join(os.path.dirname(os.getcwd()), f) for f in common_input_files]

    status_files = []

    # Submit a DAG for each pairs file
    for pfile in pairs_files:
        print 'Processing', pfile
        sfile = submit_resolution_dag(pairs_file=pfile, max_l1_pt=max_l1_pt,
                                      log_dir=log_dir, append=append,
                                      pu_bins=pu_bins, eta_bins=eta_bins,
                                      common_input_files=common_input_files,
                                      force_submit=force_submit)
        status_files.append(sfile)

    if len(status_files) > 0:
        if not isinstance(status_files[0], str):
            # flatten the list
            status_files = list(chain.from_iterable(status_files))
        print 'All statuses:'
        print 'DAGstatus.py ', ' '.join(status_files)


def submit_resolution_dag(pairs_file, max_l1_pt, log_dir, append,
                          pu_bins, eta_bins, common_input_files,
                          force_submit=False):
    """Submit one makeResolutionPlots DAG for one pairs file.

    This will run makeResolutionPlots over exclusive and inclusive eta bins,
    and then finally hadd the results together.

    Parameters
    ----------
    pairs_files : str, optional
        Pairs file to process. Must be full path.

    max_l1_pt : int, optional
        Maximum L1 pt to consider when making plots.

    log_dir : str, optional
        Directory for STDOUT/STDERR/LOG files. Should be on /storage.

    append : str, optional
        String to append to filenames to track various settings (e.g. PU bin).

    pu_bins : list[list[int, int]], optional
        List of PU bin edges.

    eta_bins : list[float], optional
        List of eta bin edges, including upper edge of last bin.

    force_submit : bool, optional
        If True, forces job submission even if proposed output files
        already exists.
        Oherwise, program quits before submission.

    Returns
    -------
    list[str]
        List of status filenames.

    """
    cc.check_file_exists(pairs_file)

    # Setup output directory for res* files
    # e.g. if pairs file in DATASET/pairs/pairs.root
    # then output goes in DATASET/resolution/
    out_dir = os.path.dirname(os.path.dirname(pairs_file))
    out_dir = os.path.join(out_dir, 'resolution')
    cc.check_create_dir(out_dir, info=True)

    # Stem for output filename
    out_stem = os.path.splitext(os.path.basename(pairs_file))[0]
    out_stem = out_stem.replace("pairs_", "res_")

    # Loop over PU bins
    # ---------------------------------------------------------------------
    pu_bins = pu_bins or [[-99, 999]]  # set ridiculous limits if no cut on PU
    status_files = []
    for (pu_min, pu_max) in pu_bins:
        log.info('**** Doing PU bin %g - %g', pu_min, pu_max)

        log_stem = 'res.$(cluster).$(process)'
        res_jobs = ht.JobSet(exe='python',
                             copy_exe=False,
                             filename='submit_resolution.condor',
                             setup_script='worker_setup.sh',
                             share_exe_setup=True,
                             out_dir=log_dir, out_file=log_stem + '.out',
                             err_dir=log_dir, err_file=log_stem + '.err',
                             log_dir=log_dir, log_file=log_stem + '.log',
                             cpus=1, memory='100MB', disk='100MB',
                             transfer_hdfs_input=False,
                             common_input_files=common_input_files,
                             hdfs_store=out_dir)

        # For creating filenames later
        fmt_dict = dict(puMin=pu_min, puMax=pu_max, maxL1Pt=max_l1_pt)

        # Hold all output filenames
        res_output_files = []

        # Add exclusive eta bins to this JobSet
        for ind, (eta_min, eta_max) in enumerate(pairwise(eta_bins)):
            out_file = out_stem + "_%d" % ind + append.format(**fmt_dict) + '.root'
            out_file = os.path.join(out_dir, out_file)
            res_output_files.append(out_file)

            job_args = ['makeResolutionPlots.py', pairs_file, out_file,
                        '--excl', '--maxPt', max_l1_pt,
                        '--PUmin', pu_min, '--PUmax', pu_max,
                        '--etaInd', ind]

            res_job = ht.Job(name='res_%d' % ind,
                             args=job_args,
                             input_files=[pairs_file],
                             output_files=[out_file])

            res_jobs.add_job(res_job)

        # Add inclusive bins (central, forward, all)
        # remove the [0:1] to do all - currently central only 'cos HF broke
        for incl in ['central', 'forward', 'all'][0:1]:
            out_file = out_stem + "_%s" % incl + append.format(**fmt_dict) + '.root'
            out_file = os.path.join(out_dir, out_file)
            res_output_files.append(out_file)

            job_args = ['makeResolutionPlots.py', pairs_file, out_file,
                        '--incl', '--maxPt', max_l1_pt,
                        '--PUmin', pu_min, '--PUmax', pu_max]
            if incl != 'all':
                job_args.append('--%s' % incl)

            res_job = ht.Job(name='res_%s' % incl,
                             args=job_args,
                             input_files=[pairs_file],
                             output_files=[out_file])

            res_jobs.add_job(res_job)

        # Add hadd jobs
        # ---------------------------------------------------------------------
        log_stem = 'resHadd.$(cluster).$(process)'

        hadd_jobs = ht.JobSet(exe='hadd',
                              copy_exe=False,
                              filename='haddSmall.condor',
                              setup_script="cmssw_setup.sh",
                              share_exe_setup=True,
                              out_dir=log_dir, out_file=log_stem + '.out',
                              err_dir=log_dir, err_file=log_stem + '.err',
                              log_dir=log_dir, log_file=log_stem + '.log',
                              cpus=1, memory='100MB', disk='20MB',
                              transfer_hdfs_input=False,
                              hdfs_store=out_dir)

        # Construct final hadded file name
        final_file = os.path.join(out_dir, out_stem + append.format(**fmt_dict) + '.root')
        hadd_output = [final_file]
        hadd_args = hadd_output + res_output_files

        hadder = ht.Job(name='haddRes',
                        args=hadd_args,
                        input_files=res_output_files,
                        output_files=hadd_output)

        hadd_jobs.add_job(hadder)

        # Add all jobs to DAG, with necessary dependencies
        # ---------------------------------------------------------------------
        stem = 'res_%s_%s' % (strftime("%H%M%S"), cc.rand_str(3))
        res_dag = ht.DAGMan(filename=os.path.join(log_dir, '%s.dag' % stem),
                            status_file=os.path.join(log_dir, '%s.status' % stem))
        for job in res_jobs:
            res_dag.add_job(job)

        res_dag.add_job(hadder, requires=[j for j in res_jobs])

        # Check if any of the output files already exists - maybe we mucked up?
        # ---------------------------------------------------------------------
        if not force_submit:
            for f in [final_file] + res_output_files:
                if os.path.isfile(f):
                    raise RuntimeError('Output file already exists - not submitting.'
                                       '\nTo bypass, use -f flag. \nFILE: %s' % f)
        # res_dag.write()
        res_dag.submit()
        status_files.append(res_dag.status_file)

    print 'For all statuses:'
    print 'DAGstatus.py', ' '.join(status_files)
    return status_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force', '-f',
                        help='Force submit - will run jobs even if final file '
                             'with same name already exists.',
                        action='store_true')
    args = parser.parse_args()
    submit_all_resolution_dags(pairs_files=PAIRS_FILES, max_l1_pt=MAX_L1_PT,
                               log_dir=LOG_DIR, append=APPEND,
                               pu_bins=PU_BINS, eta_bins=ETA_BINS,
                               force_submit=args.force)
