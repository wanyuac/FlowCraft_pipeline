#! /usr/bin/env python
"""
Submit SPAdes jobs to an HPC. Supports SGE and PBS job schedulers.

Notes:
    1. Dependencies: anaconda, Python >= 3.6 (for the use of f-strings)
    2. Users may need to edit this script for their HPCs. For example, renaming conda environments.

Author: Yu Wan <wanyuac@126.com>
First version: 18/3/2021; the latest update: 24/7/2021
"""

import os
import sys
import time
import subprocess
from argparse import ArgumentParser
from collections import namedtuple


def parse_arguments():
    parser = ArgumentParser(description = "Launching SPAdes job using spades_runner.sge")
    parser.add_argument("--readsets", "-r", dest = "readsets", type = str, required = True, help = "A tab-delimited file of three columns ID\\tRead_1\\tRead_2")
    parser.add_argument("--ncpus", "-n", dest = "ncpus", type = str, required = False, default = "8", help = "Number of computational cores to be requested (default: 8)")
    parser.add_argument("--mem", "-m", dest = "mem", type = str, required = False, default = "16", help = "Memory size (GB) to be requested (default: 16)")
    parser.add_argument("--kmers", "-k", dest = "kmers", type = str, required = False, default = "21,33,55,77", help = "Comma-delimited k-mer sizes for SPAdes (default: '21,33,55,77')")
    parser.add_argument("--outdir", "-o", dest = "outdir", type = str, required = False, default = "output", help = "Parental output directory")
    parser.add_argument("--queue", "-q", dest = "queue", type = int, required = False, default = 10, help = "Size of each serial job queue")
    parser.add_argument("--scheduler", "-s", dest = "scheduler", type = str, required = False, default = "SGE", help = "Job scheduler (SGE/PBS)")
    parser.add_argument("--highcov", "-hc", dest = "highcov", action = "store_true", help = "Set the flag when high-coverage multi-cell Illumina data is used as input (cf. SPAdes option '--isolate')")
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
                                                              args.kmers, args.outdir, args.scheduler, args.highcov),\
                           k, n, args.outdir, args.scheduler))  # Append the path of the new script to list 'scripts'
            queue = list()
            k = 0
    if k > 0:  # When there are remaining tasks in the last queue.
        n += 1
        scripts.append(write_job_script(create_job_script({genome : readsets[genome] for genome in queue}, args.ncpus, args.mem,\
                                        args.kmers, args.outdir, args.scheduler, args.highcov),\
                       k, n, args.outdir, args.scheduler))
    if submit:
        for s in scripts:
            print("Submit job script " + s, file = sys.stdout)
            p = subprocess.Popen(["qsub", s])  # Do not use parameters 'shell = True, stdin = None, stdout = None, stderr = None, close_fds = True', or the job will not be submitted successfully.
            #stdout, stderr = p.communicate()  # The script stucks at the first submission and keeps waiting for it to finish if p.communicate() is called.
            #print(stdout, file = sys.stdout)
            #print(stderr, file = sys.stderr)
            time.sleep(1)
    return


def import_readsets(r):
    Readset = namedtuple("Readset", ["r1", "r2"])  # One genome per object
    readsets = dict()
    if not os.path.exists(r):
        print("Error: Input file " + r + " is not accessible.", file = sys.stderr)
        sys.exit(1)
    with open(r, "r") as f:
        lines = f.read().splitlines()
        for line in lines:
            try:
                i, r_1, r_2 = line.split("\t")
            except ValueError:
                print("Error: line '%s' in the readset specification file cannot be correctly parsed." % line, file = sys.stderr)
                sys.exit(1)
            readsets[i] = Readset(r1 = r_1, r2 = r_2)
    return readsets


def check_dir(d):
    if not os.path.exists(d):
        os.mkdir(d)
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
#PBS -l select=1:ncpus={ncpus}:mem={mem}gb:ompthreads={ncpus}
#PBS -l walltime=24:00:00
#PBS -N SPAdes
#PBS -j oe

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


def write_job_script(script, k, i, out, scheduler):
    """ Returns the path of the output script """
    filename_ext = ".sge" if scheduler == "SGE" else ".pbs"
    f_name = os.path.join(out, "job_list_" + str(i) + filename_ext)  # In the future, the filename extension will be determined by the job scheduler.
    print("Write %i tasks into script %s" % (k, f_name))
    with open(f_name, "w") as f:
        f.write(script)
    return f_name


if __name__ == "__main__":
    main()
