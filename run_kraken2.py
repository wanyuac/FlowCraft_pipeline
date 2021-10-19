#! /usr/bin/env python
"""
Submit kraken2 jobs to an HPC for taxonomical check. Supports SGE and PBS job schedulers. This script does
not require kraken2 to produce classified or unclassified reads or kraken files.

Notes:
    1. Dependencies: anaconda, Python >= 3.6 (for the use of f-strings)
    2. Users may need to edit this script for their HPCs. For example, renaming conda environments.

Copyright (C) 2021 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
First version: 5 Aug 2021; the latest update: 10 Sep 2021
"""

import os
import sys
import time
import subprocess
from argparse import ArgumentParser
from pipeline_modules import import_readsets, check_dir, write_job_script


def parse_arguments():
    parser = ArgumentParser(description = "Submit Kraken2 jobs to the HPC")
    parser.add_argument("--readsets", "-r", dest = "readsets", type = str, required = True, help = "A tab-delimited, header-free file of three columns ID\\tRead_1\\tRead_2")
    parser.add_argument("--db", "-b", dest = "db", type = str, required = True, help = "Path to the Kraken database")
    parser.add_argument("--outdir", "-o", dest = "outdir", type = str, required = False, default = "output", help = "Parental output directory")
    parser.add_argument("--ncpus", "-n", dest = "ncpus", type = str, required = False, default = "8", help = "Number of computational cores to be requested (default: 8)")
    parser.add_argument("--mem", "-m", dest = "mem", type = str, required = False, default = "64", help = "Memory size (GB) to be requested (default: 64)")
    parser.add_argument("--queue", "-q", dest = "queue", type = int, required = False, default = 10, help = "Size of each serial job queue (Default: 10)")
    parser.add_argument("--scheduler", "-s", dest = "scheduler", type = str, required = False, default = "SGE", help = "Job scheduler (SGE/PBS); default: SGE")
    parser.add_argument("--env_module", "-e", dest = "env_module", type = str, required = False, default = "anaconda/5.3.1_python3", help = "(Optional) Environmental module to be loaded")
    parser.add_argument("--conda_env", "-c", dest = "conda_env", type = str, required = False, default = "kraken", help = "(Optional) Conda environment to be loaded")
    parser.add_argument("--debug", "-d", dest = "debug", action = "store_true", help = "Only generate job script but do not submit it")
    return parser.parse_args()


def main():
    args = parse_arguments()
    readsets = import_readsets(args.readsets)
    submit = not args.debug
    check_dir(args.outdir)
    queue = list()
    scripts = list()
    k = 0  # Counter of genomes of a queue
    n = 0  # Number of scripts to be written
    for i in readsets.keys():  # Create and submit scripts of serial jobs based on args.queue
        k += 1
        queue.append(i)
        if k == args.queue:  # When the current queue becomes full
            n += 1
            scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.db, args.ncpus,\
                                                              args.mem, args.outdir, args.scheduler, args.env_module, args.conda_env),\
                                                              k, n, args.outdir, args.scheduler))  # Append the path of the new script to list 'scripts'
            queue = list()
            k = 0
    if k > 0:  # When there are remaining tasks in the last queue.
        n += 1
        scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.db, args.ncpus,\
                                                          args.mem, args.outdir, args.scheduler, args.env_module, args.conda_env),\
                                                          k, n, args.outdir, args.scheduler))
    if submit:
        for s in scripts:
            print("Submit job script " + s, file = sys.stdout)
            p = subprocess.Popen(["qsub", s])  # Do not use parameters 'shell = True, stdin = None, stdout = None, stderr = None, close_fds = True', or the job will not be submitted successfully.
            time.sleep(1)
    return


def create_job_script(readsets, db, ncpus, mem, outdir, scheduler, env_module, conda_env):
    outdir = os.path.abspath(outdir)
    if scheduler == "SGE":
        script = f"""#!/bin/bash
# SGE configurations
#$ -N kraken2
#$ -S /bin/bash
#$ -pe multithread {ncpus}
#$ -l h_vmem={mem}G
"""
        if env_module != "":
            script += f"""
# Environmental settings
source $HOME/.bash_profile
source /etc/profile.d/modules.sh
module purge
module load {env_module}
"""
        if conda_env != "":
            script += f"""conda activate {conda_env}
"""
        script +="""
# Kraken2 jobs"""
    else:  # PBS job script
        script = f"""#!/bin/bash
# PBS configurations
#PBS -N kraken
#PBS -l select=1:ncpus={ncpus}:mem={mem}gb:ompthreads={ncpus}
#PBS -l walltime=24:00:00
"""
        if env_module != "":
            script += f"""
# Environmental settings
module load {env_module}
"""
        if conda_env != "":
            script += f"""source activate {conda_env}
"""
        script += """
# Kraken2 jobs"""

    genomes = list(readsets.keys())
    for g in genomes:
        reads = readsets[g]
        report = os.path.join(outdir, g + ".txt")
        script += f"""\nkraken2 --db {db} --paired --gzip-compressed --threads {ncpus} --output - --report {report} {reads.r1} {reads.r2}"""
    return script


if __name__ == "__main__":
    main()
