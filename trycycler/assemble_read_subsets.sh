#!/bin/bash
# Assemble subsets of long reads using Flye, Raven, and Minipolish for Trycycler.
#
# Command line:
#     bash assemble_read_subsets.sh [input directory] [output directory] [number of read subsets (default: 12)] [number of threads (default: 4)]
#     Note that directories should not be ended with slashes.
#
# Dependencies:
#     - Flye (github.com/fenderglass/Flye), Raven (github.com/lbcb-sci/raven)
#     - Minipolish (github.com/rrwick/Minipolish). Please ensure exporting the path to miniasm_and_minipolish.sh to $PATH before
#       running this script.
#       *  Miniasm (github.com/lh3/miniasm), minimap2 (github.com/lh3/minimap2), and Racon (github.com/isovic/racon)
#     - any2fasta (github.com/tseemann/any2fasta)
# Please ensure these dependencies are accessible in your system. For example, you may activate the corresponding Conda environment
# before running this script.
#
# Modified from Ryan Wick's code on github.com/rrwick/Trycycler/wiki/Generating-assemblies.
# Previous name: assembleReadSubsetsForTrycycler.sh
# Copyright (C) 2021 Yu Wan <wanyuac@126.com>
# Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
# First version: 6 Nov 2021; the latest update: 12 Dec 2021

# Print help information ####################
print_help() {
    echo "Assemble 12 subsets of long reads using Flye, Raven, and Minipolish for Trycycler.
    assemble_read_subsets.sh [input directory] [output directory] [number of threads (default: 4)]
    Directory paths should not be ended with slashes. Please ensure exporting the path to miniasm_and_minipolish.sh
    to \$PATH before running this script."
}

if [ "$#" -lt 2 ]; then
    echo 'Error: at least two arguments are required.'
    print_help
    exit
fi

# Check dependencies ####################
check_dependency() {
    p=$(which "$1")
    if [ -z "$p" ]; then
        echo "Error: $1 could not be found."  # Forgot to export PATH=...:$PATH or enable the conda environment?
        exit
    fi
}

dependencies=( flye miniasm_and_minipolish.sh any2fasta raven minimap2 miniasm minipolish )
for s in ${dependencies[@]}; do
    check_dependency $s
done

# Read parameters and check dependencies ####################
indir="$1"
outdir="$2"
subsets="$3"
threads="$4"

if [ ! -d "$indir" ]; then
    echo "Error: input directory $indir does not exist."
    exit
fi

if [ ! -d "$outdir" ]; then
    echo "Create output directory $outdir"
    mkdir $outdir
fi

if [ -z "$subsets" ]; then
    echo "Set the number of read subsets to 12."
    subsets=12
fi

if [ -z "$threads" ]; then
    echo "Use four threads."
    threads=4
fi

echo "Input directory: $indir"
echo "Output directory: $outdir"
echo "Number of threads per job: $threads"

# Iteratively run assemblers ####################
assembler=1  # Selector for assembers; 1: flye; 2: raven; 3: minipolish
indices_flye=()
indices_raven=()
indices_mini=()

for i in `seq 1 $subsets`; do
    if [ "$i" -lt 10 ]; then
        i="0$i"
    fi
    if [ "$assembler" -eq 1 ]; then
        echo "Use Flye to assemble read set $i"
        flye --nano-raw ${indir}/sample_${i}.fastq --threads "$threads" --scaffold --iterations 2 --out-dir "assembly_$i"  # Option '--genome-size' is no longer required since Flye v2.8.
        mv assembly_${i}/assembly.fasta ${outdir}/assembly_${i}.fna
        mv assembly_${i}/assembly_graph.gfa ${outdir}/assembly_${i}.gfa  # Save the assembly graph for quality assessment
        mv assembly_${i}/assembly_info.txt ${outdir}/assembly_${i}.txt  # Assembly summary
        mv assembly_${i}/flye.log ${outdir}/assembly_${i}.log
        rm -rf assembly_$i  # Delete the temporary directory
        indices_flye+=($i)
    elif [ "$assembler" -eq 2 ]; then
        echo "Use Raven to assemble read set $i"
        raven --threads "$threads" --polishing-rounds 2 --graphical-fragment-assembly ${outdir}/assembly_${i}.gfa ${indir}/sample_${i}.fastq > ${outdir}/assembly_${i}.fna
        rm raven.cereal
        indices_raven+=($i)
    else
        echo "Use Minipolish to assemble read set $i"
        miniasm_and_minipolish.sh ${indir}/sample_${i}.fastq "$threads" > assembly_${i}.gfa
        any2fasta assembly_${i}.gfa > ${outdir}/assembly_${i}.fna
        mv assembly_${i}.gfa ${outdir}/assembly_${i}.gfa
        indices_mini+=($i)
    fi
    assembler=$(($assembler + 1))
    if [ "$assembler" -gt 3 ]; then
        assembler=1
    fi
    sleep 1
done

# Count the number of contigs in each assembly ####################
for i in $(ls -1 ${outdir}/*.fna); do
    n=$(grep -c '>' $i)
    j=$(basename $i '.fna')
    echo "${j}: $n contigs"
done

# Print assembler information ##########
print_asm() {
    arr=("$@")
    ids=''
    for i in ${arr[@]}; do
        ids="$ids $i"
    done
    echo "$ids"
}

echo Flye assemblies:$(print_asm "${indices_flye[@]}")
echo Raven assemblies:$(print_asm "${indices_raven[@]}")
echo Minipolish assemblies:$(print_asm "${indices_mini[@]}")
echo "All $subsets subsets of reads have been assembled successfully."