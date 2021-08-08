#! /usr/bin/env python
"""
Submit SPAdes jobs to an HPC. Supports SGE and PBS job schedulers.

Notes:
    1. Dependencies: anaconda, Python >= 3.6 (for the use of f-strings)
    2. Users may need to edit this script for their HPCs. For example, renaming conda environments.

Copyright (C) 2021 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
First version: 18 Mar 2021; the latest update: 6 Aug 2021
"""

import os
import sys
import time
import subprocess
from argparse import ArgumentParser
from pipeline_modules import import_readsets, check_dir, write_job_script


def parse_arguments():
    parser = ArgumentParser(description = "Submit SPAdes jobs to the HPC")
    parser.add_argument("--readsets", "-r", dest = "readsets", type = str, required = True, help = "A tab-delimited, header-free file of three columns ID\\tRead_1\\tRead_2")
    parser.add_argument("--kmers", "-k", dest = "kmers", type = str, required = False, default = "21,33,55,77", help = "Comma-delimited k-mer sizes for SPAdes (default: '21,33,55,77')")
    parser.add_argument("--outdir", "-o", dest = "outdir", type = str, required = False, default = "output", help = "Parental output directory")
    parser.add_argument("--highcov", "-hc", dest = "highcov", action = "store_true", help = "Set the flag when high-coverage multi-cell Illumina data is used as input (cf. SPAdes option '--isolate')")
    parser.add_argument("--ncpus", "-n", dest = "ncpus", type = str, required = False, default = "8", help = "Number of computational cores to be requested (default: 8)")
    parser.add_argument("--mem", "-m", dest = "mem", type = str, required = False, default = "16", help = "Memory size (GB) to be requested (default: 16)")
    parser.add_argument("--queue", "-q", dest = "queue", type = int, required = False, default = 10, help = "Size of each serial job queue")
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
    k = 0  # Counter of genomes of a queue
    n = 0  # Number of scripts to be written
    for i in readsets.keys():  # Create and submit scripts of serial jobs based on args.queue
        k += 1
        queue.append(i)
        if k == args.queue:
            n += 1
            scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.ncpus, args.mem,\
                                                              args.kmers, args.outdir, args.scheduler, args.highcov), k, n, args.outdir, args.scheduler))  # Append the path of the new script to list 'scripts'
            queue = list()
            k = 0
    if k > 0:  # When there are remaining tasks in the last queue.
        n += 1
        scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.ncpus, args.mem,\
                                        args.kmers, args.outdir, args.scheduler, args.highcov), k, n, args.outdir, args.scheduler))
    if submit:
        for s in scripts:
            print("Submit job script " + s, file = sys.stdout)
            p = subprocess.Popen(["qsub", s])  # Do not use parameters 'shell = True, stdin = None, stdout = None, stderr = None, close_fds = True', or the job will not be submitted successfully.
            #stdout, stderr = p.communicate()  # The script stucks at the first submission and keeps waiting for it to finish if p.communicate() is called.
            #print(stdout, file = sys.stdout)
            #print(stderr, file = sys.stderr)
            time.sleep(1)
    return


def create_job_script(readsets, ncpus, mem, kmers, outdir, scheduler, highcov):
    outdir = os.path.abspath(outdir)
    if scheduler == "SGE":
        script = f"""#!/bin/bash
# SGE configurations
#$ -N SPAdes
#$ -S /bin/bash
#$ -pe multithread {ncpus}
#$ -l h_vmem={mem}G

# Environmental settings
source $HOME/.bash_profile
source /etc/profile.d/modules.sh
module purge
module load anaconda/5.3.1_python3
conda activate spades
export PATH=$HOME/code/SPAdes-3.15.2/bin:$PATH

# SPAdes jobs"""
    else:  # PBS job script
        script = f"""#!/bin/bash
# PBS configurations
#PBS -N SPAdes
#PBS -l select=1:ncpus={ncpus}:mem={mem}gb:ompthreads={ncpus}
#PBS -l walltime=24:00:00

# Environmental settings
module load anaconda3/personal
source activate spades3.15

# SPAdes jobs"""

    genomes = list(readsets.keys())
    method = "--isolate" if highcov else "--careful"  # See https://github.com/ablab/spades#isolate for details.
    for g in genomes:
        reads = readsets[g]
        subdir = os.path.join(outdir, g)  # Do not need to run check_dir(subdir) as SPAdes creates an output directory if it does not exist.
        script += f"""\nspades.py -1 {reads.r1} -2 {reads.r2} -o {subdir} --phred-offset 33 {method} --threads {ncpus} --memory {mem} -k '{kmers}'"""
    
    script += """\n
# Move output files
cd %s

genomes=(%s)

for g in ${genomes[@]}
do
    if [ -f "$g/scaffolds.fasta" ]
    then
        mv $g/scaffolds.fasta ${g}__scaffolds.fna
        mv $g/assembly_graph_with_scaffolds.gfa ${g}__scaffolds.gfa
        mv $g/scaffolds.paths ${g}__scaffolds.paths
        mv $g/contigs.fasta ${g}__contigs.fna
        mv $g/contigs.paths ${g}__contigs.paths
        mv $g/assembly_graph.fastg ${g}.fastg
        mv $g/spades.log ${g}.log
    else
        echo "Warning: The genome of isolate $g could not be assembled."
    fi
done
""" % (outdir, " ".join(genomes))  # This command line cannot use the f-string because of the braces used in the string.
    return script


if __name__ == "__main__":
    main()
