#!/bin/bash
# Copyright (C) 2021 Yu Wan <wanyuac@126.com>
# Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
# Publication: 10 Dec 2021; latest update: 18 Dec 2021.

display_useage() {
    echo "Runs command \'trycycler subsample\' for multiple samples.

    Command: run_subsample.sh [sampling_settings.tsv] [parental output directory]

    The header-free tab-delimited input file sampling_settings consists of five columns: (1) sample name, (2) estimated genome size
    (e.g., '5m'), (3) the path to the input FASTQ file, (4) the number of subsets of reads, and (5) the minimum read depth for
    calculating the size of the subset (Note: the default depth of the \'trycycler subsample\' command is 25 folds).
    Please ensure trycycler is in \$PATH. Also, note that \'~\' is not supported for the paths of input FASTQ files."
}

if [ "$#" -lt 2 ]; then
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
        d="${cols[4]}"  # Minimum read depth of each subset for the current genome.
        if [ -f "$f" ]; then
            echo "Creating $c subsets of ${d}-fold long reads from $f for sample $i of genome size $s"
            trycycler subsample --reads $f --count $c --genome_size $s --min_read_depth $d --out_dir ${2}/$i
        else
            echo "Input error: FASTQ file $f is not accessible."
        fi
    done < "$1"
else
    echo "Argument error: input file $1 is not accessible."
fi