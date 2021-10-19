#! /usr/bin/env python
"""
Submit Prokka jobs to an HPC. Supports SGE and PBS job schedulers. This script assumes all isolates
are bacteria.

Notes:
    1. Dependencies: anaconda, Python >= 3.6 (for the use of f-strings)
    2. A Conda environment for Prokka.
    3. Users may need to edit this script for their HPCs. For example, renaming conda environments.
    4. No rRNA or tRNA search will be performed.

Copyright (C) 2021 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
First version: 18 Oct 2021; the latest update: 19 Oct 2021
"""

import os
import sys
import time
import subprocess
from argparse import ArgumentParser
from pipeline_modules import import_assemblies, check_dir, write_job_script


def parse_arguments():
    parser = ArgumentParser(description = "Submit Prokka jobs to the HPC for annotating bacterial genomes")
    
    # Annotation parameters
    parser.add_argument('--assemblies', '-a', dest = 'assemblies', type = str, required = True, help = "A tab-delimited, header-free file of two columns ID\\tFile_path")
    parser.add_argument('--conda', '-c', dest = 'conda', type = str, required = True, help = "Name of the conda environment for Prokka")
    parser.add_argument('--genus', '-g', dest = 'genus', type = str, required = True, help = "Genus name")
    parser.add_argument('--species', '-sp', dest = 'species', type = str, required = True, help = "Species name")
    parser.add_argument('--proteins', '-p', dest = 'proteins', type = str, required = True, help = "A FASTA or GenBank file to use for first-priority annotation searches")
    parser.add_argument('--mincontiglen', '-l', dest = 'mincontiglen', type = str, required = False, default = '200', help = "Minimum length of contigs to keep (default: 200 bp)")
    
    # Job parameters
    parser.add_argument('--outdir', '-o', dest = 'outdir', type = str, required = False, default = 'output', help = "Absolute path to the parental output directory")
    parser.add_argument('--ncpus', '-n', dest = 'ncpus', type = str, required = False, default = '8', help = "Number of computational cores to be requested (default: 8)")
    parser.add_argument('--mem', '-m', dest = 'mem', type = str, required = False, default = '16', help = "Memory size (GB) to be requested (default: 16)")
    parser.add_argument('--queue', '-q', dest = 'queue', type = int, required = False, default = 20, help = "Size of each serial job queue (default: 20)")
    parser.add_argument('--scheduler', '-s', dest = 'scheduler', type = str, required = False, default = 'SGE', help = "Job scheduler (SGE/PBS) (default: SGE)")
    parser.add_argument('--debug', '-d', dest = 'debug', action = 'store_true', help = "Only generate job script but do not submit it")
    return parser.parse_args()


def main():
    args = parse_arguments()
    assemblies = import_assemblies(args.assemblies)  # Dictionary {i : path}
    check_dir(args.outdir)
    queue = list()
    scripts = list()
    k = 0  # Counter of genomes of a queue
    n = 0  # Number of scripts to be written
    for i in assemblies.keys():  # Create and submit scripts of serial jobs based on args.queue
        k += 1
        queue.append(i)
        if k == args.queue:
            n += 1
            scripts.append(write_job_script(create_job_script({genome : assemblies[genome] for genome in queue}, args.conda, args.genus, args.species,\
                                                              args.proteins, args.mincontiglen, args.ncpus, args.mem, args.outdir, args.scheduler),\
                                            k, n, args.outdir, args.scheduler))  # Append the path of the new script to list 'scripts'
            queue = list()
            k = 0
    if k > 0:  # When there are remaining tasks in the last queue.
        n += 1
        scripts.append(write_job_script(create_job_script({genome : assemblies[genome] for genome in queue}, args.conda, args.genus, args.species,\
                                                          args.proteins, args.mincontiglen, args.ncpus, args.mem, args.outdir, args.scheduler),\
                                        k, n, args.outdir, args.scheduler))
    if args.debug:
        print("Debugging mode: no job is submitted.", file = sys.stdout)
    else:
        for s in scripts:
            print("Submit job script " + s, file = sys.stdout)
            p = subprocess.Popen(['qsub', s])  # Do not use parameters 'shell = True, stdin = None, stdout = None, stderr = None, close_fds = True', or the job will not be submitted successfully.
            time.sleep(1)
    return


def create_job_script(assemblies, conda_env, genus, species, proteins, mincontiglen, ncpus, mem, outdir, scheduler):
    outdir = os.path.abspath(outdir)
    if scheduler == 'SGE':
        script = f"""#!/bin/bash
# SGE configurations
#$ -N Prokka
#$ -S /bin/bash
#$ -pe multithread {ncpus}
#$ -l h_vmem={mem}G

# Environmental settings
source $HOME/.bash_profile
source /etc/profile.d/modules.sh
module purge
module load anaconda/5.3.1_python3
conda activate {conda_env}

# Prokka jobs"""
    else:  # PBS job script
        script = f"""#!/bin/bash
# PBS configurations
#PBS -N Prokka
#PBS -l select=1:ncpus={ncpus}:mem={mem}gb:ompthreads={ncpus}
#PBS -l walltime=24:00:00

# Environmental settings
module load anaconda3/personal
source activate {conda_env}

# Prokka jobs"""

    for g in assemblies.keys():
        fasta = assemblies[g]
        subdir = os.path.join(outdir, g)  # Do not need to run check_dir(subdir) as SPAdes creates an output directory if it does not exist.
        script += f"""\nprokka --outdir {subdir} --prefix {g} --locustag {g} --increment 1 --kingdom Bacteria --genus {genus} --species {species} --strain {g} --gcode 11 --force --addgenes --proteins {proteins} --cpus {ncpus} --mincontiglen {mincontiglen} --norrna --notrna --quiet {fasta}"""
    return script


if __name__ == '__main__':
    main()