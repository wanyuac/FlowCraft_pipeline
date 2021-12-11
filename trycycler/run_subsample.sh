#!/bin/bash
# Copyright (C) 2021 Yu Wan <wanyuac@126.com>
# Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
# Publication: 10 Dec 2021; latest update: 10 Dec 2021.

display_useage() {
    echo "Runs command \'trycycler subsample\' for multiple samples.
    Command: run_subsample.sh [samples.tsv] [parental output directory]
    The header-free tab-delimited input file samples.tsv consists of four columns: sample name, estimated genome size (e.g., '5m'),
    the path to the input FASTQ file, and the number of subsets of reads.
    Please ensure trycycler is in \$PATH. Also, note that \'~\' is not supported for the paths of input FASTQ files."
}

if [ "$#" -ne 2 ]; then
    display_useage
    exit
fi

if [ ! -d "$2" ]; then
    echo "Creating parental output directory ${2}. Subsets of reads of each sample will be stored in subdirectories of this directory."
    mkdir -p $2
fi

if [ -f "$1" ]; then
    while read -r line; do
        IFS=$'\t' read -r -a cols <<< "$line"
        i="${cols[0]}"  # Isolate name
        s="${cols[1]}"  # Genome size
        f="${cols[2]}"  # FASTQ file
        c="${cols[3]}"  # Number of subsets
        if [ -f "$f" ]; then
            echo "Creating $c subsets of long reads from $f for sample $i of genome size $s"
            trycycler subsample --reads $f --count $c --genome_size $s --min_read_depth 25 --out_dir ${2}/$i
        else
            echo "Input error: FASTQ file $f is not accessible."
        fi
    done < "$1"
else
    echo "Argument error: input file $1 is not accessible."
fi