#! /usr/bin/env python
"""
Submit PHEnix jobs to an HPC (https://github.com/phe-bioinformatics/PHEnix). The script supports SGE and PBS job schedulers.

Notes:
    1. Dependencies: anaconda, Python >= 3.6 (for the use of f-strings)
    2. Users may need to edit this script for their HPCs. For example, renaming conda environments.

Copyright (C) 2021 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
First version: 8 Aug 2021; the latest update: 8 Aug 2021
"""

import os
import sys
import time
import subprocess
from argparse import ArgumentParser
from pipeline_modules import import_readsets, check_dir, write_job_script


def parse_arguments():
    parser = ArgumentParser(description = "Submit PHEnix jobs to the HPC")
    
    # Software arguments
    parser.add_argument("--readsets", "-r", dest = "readsets", type = str, required = True, help = "A tab-delimited, header-free file of three columns ID\\tRead_1\\tRead_2")
    parser.add_argument("--ref", "-e", dest = "ref", type = str, required = True, help = "Path to a reference FASTA file (Run phenix.py prepare_reference first)")
    parser.add_argument("--filters", "-f", dest = "filters", type = str, required = False, default = "qual_score:30,min_depth:10,mq_score:30,ad_ratio:0.9", help = "Quality filters for variant calling")
    parser.add_argument("--outdir", "-o", dest = "outdir", type = str, required = False, default = "output", help = "Parental output directory")
    parser.add_argument("--keep_temp", "-k", dest = "keep_temp", action = "store_true", help = "Keep temporary files")
    
    # Job arguments
    parser.add_argument("--mem", "-m", dest = "mem", type = str, required = False, default = "32", help = "Memory size (GB) to be requested (default: 32)")
    parser.add_argument("--queue", "-q", dest = "queue", type = int, required = False, default = 20, help = "Size of each serial job queue")
    parser.add_argument("--scheduler", "-s", dest = "scheduler", type = str, required = False, default = "SGE", help = "Job scheduler (SGE/PBS); default: SGE")
    parser.add_argument("--debug", "-d", dest = "debug", action = "store_true", help = "Only generate job script but do not submit it")
    return parser.parse_args()


def main():
    args = parse_arguments()
    readsets = import_readsets(args.readsets)
    submit = not args.debug
    check_dir(args.outdir)
    queue = list()
    scripts = list()
    other_args = "--json --keep-temp" if args.keep_temp else "--json"
    k = 0  # Counter of genomes of a queue
    n = 0  # Number of scripts to be written
    for i in readsets.keys():  # Create and submit scripts of serial jobs based on args.queue
        k += 1
        queue.append(i)
        if k == args.queue:  # When the current queue becomes full
            n += 1
            scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.ref, args.filters, args.mem,\
                                                              args.outdir, args.scheduler, other_args), k, n, args.outdir, args.scheduler))  # Append the path of the new script to list 'scripts'
            queue = list()
            k = 0
    if k > 0:  # When there are remaining tasks in the last queue.
        n += 1
        scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.ref, args.filters, args.mem,\
                                                           args.outdir, args.scheduler, other_args), k, n, args.outdir, args.scheduler))
    if submit:
        for s in scripts:
            print("Submit job script " + s, file = sys.stdout)
            p = subprocess.Popen(["qsub", s])  # Do not use parameters 'shell = True, stdin = None, stdout = None, stderr = None, close_fds = True', or the job will not be submitted successfully.
            time.sleep(1)
    return


def create_job_script(readsets, ref, filters, mem, outdir, scheduler, other_args):
    outdir = os.path.abspath(outdir)
    if scheduler == "SGE":
        script = f"""#!/bin/bash
# SGE configurations
#$ -N PHEnix
#$ -S /bin/bash
#$ -l h_vmem={mem}G

# Environmental settings
source $HOME/.bash_profile
source /etc/profile.d/modules.sh
module purge
module load snp_pipeline/1-4-3

# PHEnix jobs"""
    else:  # PBS job script
        script = f"""#!/bin/bash
# PBS configurations
#PBS -N PHEnix
#PBS -l select=1:ncpus=1:mem={mem}gb
#PBS -l walltime=24:00:00

# Environmental settings
module load snp_pipeline/1-4-3

# PHEnix jobs"""
    genomes = list(readsets.keys())
    for g in genomes:
        reads = readsets[g]
        script += f"""\nphenix.py run_snp_pipeline -r1 {reads.r1} -r2 {reads.r2} --reference {ref} --sample-name {g} --mapper bwa --variant gatk --filters '{filters}' --outdir {outdir} {other_args}"""
    return script


if __name__ == "__main__":
    main()