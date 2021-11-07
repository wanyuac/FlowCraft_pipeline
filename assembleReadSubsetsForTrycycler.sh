#!/bin/bash
# Assemble 12 subsets of long reads using Flye, Raven, and Miniasm for Trycycler.
#
# Dependencies:
#     - Flye (github.com/fenderglass/Flye), Raven (github.com/lbcb-sci/raven), Miniasm (github.com/lh3/miniasm)
#     - minimap2 (github.com/lh3/minimap2) and Racon (github.com/isovic/racon)
#     - Minipolish (github.com/rrwick/Minipolish). Of note, path to miniasm_and_minipolish.sh needs to be exported to $PATH before
#       running this script.
#     - any2fasta (github.com/tseemann/any2fasta)
# Please ensure these dependencies are accessible in your system. For example, you may activate the corresponding Conda environment
# before running this script.
#
# Command line
#     bash assemble_longread_subsets.sh [input directory] [output directory] [number of threads (default: 4)]
#
# Modified from Ryan Wick's code on github.com/rrwick/Trycycler/wiki/Generating-assemblies.
# Copyright (C) 2021 Yu Wan <wanyuac@126.com>
# Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
# First version: 6 Nov 2021; the latest update: 7 Nov 2021

# Check dependencies ####################
check_dependency() {
    p=$(which "$1")
    if [ -z "$p" ]
    then
        echo "Error: $1 could not be found."  # Forgot to export PATH=...:$PATH or enable the conda environment?
        #exit
    fi
}

dependencies=( flye miniasm_and_minipolish.sh any2fasta raven minimap2 miniasm minipolish )

for s in ${dependencies[@]}
do
    check_dependency $s
done

# Read parameters and check dependencies ####################
indir="$1"
outdir="$2"
threads="$3"

if [ ! -d "$indir" ]
then
    echo "Error: input directory $indir does not exist."
    exit
fi

if [ ! -d "$outdir" ]
then
    echo "Create output directory $outdir"
    mkdir $outdir
fi

if [ -z "$threads" ]
then
    threads=4
fi

echo "Input directory: $indir"
echo "Output directory: $outdir"
echo "Number of threads per job: $threads"
if [ ! -z "$size" ]
then
    echo "Reference genome size: $size"
fi

# Flye ####################
for i in 01 04 07 10
do
    flye --nano-raw ${indir}/sample_${i}.fastq --threads "$threads" --iterations 2 --out-dir "assembly_$i"  # Option '--genome-size' is no longer required since Flye v2.8.
    cp assembly_${i}/assembly.fasta ${outdir}/assembly_${i}.fasta
    mv assembly_${i}/assembly.gfa ${outdir}/assembly_${i}.gfa  # Save the assembly graph for quality assessment
    rm -rf assembly_$i
    sleep 1
done

# Miniasm ####################
for i in 02 05 08 11
do
    miniasm_and_minipolish.sh ${indir}/sample_${i}.fastq "$threads" > assembly_${i}.gfa
    any2fasta assembly_${i}.gfa > ${outdir}/assembly_${i}.fasta
    mv assembly_${i}.gfa ${outdir}/assembly_${i}.gfa
    sleep 1
done

# Raven-assembler ####################
for i in 03 06 09 12
do
    raven --threads "$threads" --polishing-rounds 2 ${indir}/sample_${i}.fastq > ${outdir}/assembly_${i}.fasta
    rm raven.cereal
    sleep 1
done

# Count the number of contigs in each assembly ####################
for i in $(ls -1 ${outdir}/*.fasta)
do
    n=$(grep -c '>' $i)
    j=$(basename $i '.fasta')
    echo "${j}: $n contigs"
done