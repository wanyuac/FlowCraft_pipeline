#! /usr/bin/env python
"""
Submit ARIBA jobs to an HPC. Supports SGE and PBS job schedulers.

Notes:
    1. Dependencies: anaconda, Python >= 3.6 (for the use of f-strings).
    2. A Conda environment for ARIBA.
    3. Users may need to edit this script for their HPCs. For example, renaming conda environments.

Copyright (C) 2021 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
First version: 22 Oct 2021; the latest update: 22 Oct 2021
"""

import os
import sys
import time
import subprocess
from argparse import ArgumentParser
from pipeline_modules import import_readsets, check_dir, write_job_script

def parse_arguments():
    parser = ArgumentParser(description = "Submit ARIBA jobs to the HPC")
    
    # Gene-detection parameters
    parser.add_argument('--readsets', '-r', dest = 'readsets', type = str, required = True, help = "A tab-delimited, header-free file of three columns ID\\tRead_1\\tRead_2")
    parser.add_argument('--db', '-b', dest = 'db', type = str, required = True, help = "Path to a reference database prepared using command 'ariba prepareref'")
    parser.add_argument('--cov', '-c', dest = 'cov', type = str, required = False, default = '80', help = "ARIBA argument --assembly_cov (default: 80)")
    parser.add_argument('--min_id', '-i', dest = 'min_id', type = str, required = False, default = '90', help = "ARIBA argument --nucmer_min_id (default: 90)")
    parser.add_argument('--kmers', '-k', dest = 'kmers', type = str, required = False, default = '21,33,55,77', help = "Comma-delimited k-mer sizes for ARIBA (default: '21,33,55,77')")

    # Job parameters
    parser.add_argument('--conda', '-e', dest = 'conda', type = str, required = True, help = "Name of the conda environment for ARIBA")
    parser.add_argument('--outdir', '-o', dest = 'outdir', type = str, required = False, default = 'output', help = "Absolute path to the parental output directory")
    parser.add_argument('--cpus', '-n', dest = 'cpus', type = str, required = False, default = '8', help = "Number of computational cores to be requested (default: 8)")
    parser.add_argument('--mem', '-m', dest = 'mem', type = str, required = False, default = '8', help = "Memory size (GB) to be requested (default: 8)")
    parser.add_argument('--queue', '-q', dest = 'queue', type = int, required = False, default = 10, help = "Size of each serial job queue")
    parser.add_argument('--scheduler', '-s', dest = 'scheduler', type = str, required = False, default = 'SGE', help = "Job scheduler (SGE/PBS); default: SGE")
    parser.add_argument('--debug', '-d', dest = 'debug', action = 'store_true', help = "Only generate job script but do not submit it")
    return parser.parse_args()


def main():
    args = parse_arguments()
    readsets = import_readsets(args.readsets)
    check_dir(args.outdir)  # Check existance of the parental output directory
    queue = list()
    scripts = list()
    k = 0  # Counter of isolates in a queue
    n = 0  # Number of scripts to be written
    for i in readsets.keys():  # Create and submit scripts of serial jobs based on args.queue
        k += 1
        queue.append(i)
        if k == args.queue:  # When the current queue becomes full
            n += 1
            scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.conda, args.db, args.cov, args.min_id, args.kmers,\
                                                               args.outdir, args.mem, args.cpus, args.scheduler),\
                                            k, n, args.outdir, args.scheduler))  # Append the path of the new script to list 'scripts'
            queue = list()
            k = 0
    if k > 0:  # When there are remaining tasks in the last queue.
        n += 1
        scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.conda, args.db, args.cov, args.min_id, args.kmers,\
                                                           args.outdir, args.mem, args.cpus, args.scheduler),\
                                        k, n, args.outdir, args.scheduler))
    if not args.debug:
        for s in scripts:
            print("Submit job script " + s, file = sys.stdout)
            p = subprocess.Popen(["qsub", s])  # Do not use parameters 'shell = True, stdin = None, stdout = None, stderr = None, close_fds = True', or the job will not be submitted successfully.
            time.sleep(1)
    return


def create_job_script(readsets, conda_env, db, cov, min_id, kmers, outdir, mem, cpus, scheduler):
    outdir = os.path.abspath(outdir)
    if scheduler == "SGE":
        script = f"""#!/bin/bash
# SGE configurations
#$ -N ARIBA
#$ -S /bin/bash
#$ -pe multithread {cpus}
#$ -l h_vmem={mem}G

# Environmental settings
source $HOME/.bash_profile
source /etc/profile.d/modules.sh
module purge
module load anaconda/5.3.1_python3
conda activate {conda_env}
cd {outdir}

# ARIBA jobs"""
    else:  # PBS job script
        script = f"""#!/bin/bash
# PBS configurations
#PBS -N ARIBA
#PBS -l select=1:ncpus=1:mem={mem}gb:ompthreads={cpus}
#PBS -l walltime=24:00:00

# Environmental settings
module load anaconda3/personal
source activate {conda_env}
cd {outdir}

# ARIBA jobs"""

    genomes = list(readsets.keys())
    for g in genomes:
        reads = readsets[g]
        tmp = f'{outdir}/tmp_{g}'
        script += f"""\nmkdir {tmp}
ariba run --assembler spades --spades_mode wgs --assembly_cov {cov} --nucmer_min_id {min_id} --force --spades_options "-k {kmers}" --threads {cpus} --tmp_dir {tmp} {db} {reads.r1} {reads.r2} {outdir}/{g}
rm -rf {tmp}\n"""
    return script


if __name__ == '__main__':
    main()