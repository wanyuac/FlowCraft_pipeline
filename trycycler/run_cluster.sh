#!/bin/bash
# Copyright (C) 2021 Yu Wan <wanyuac@126.com>
# Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
# Publication: 25 Dec 2021; latest update: 25 Dec 2021.

display_useage() {
    echo "Runs command \'trycycler cluster\' for multiple samples.
    Command: run_cluster.sh [samples.tsv] [parental output directory]
    The header-free tab-delimited input file samples.tsv consists of four columns: sample name, directory of curated FASTA files,
    and the path to each FASTQ file: [sample]\t[FASTA directory and wildcard]\t[FASTQ file]. Every directory path should not be finished by a forward slash.
    Examples of lines (in a single TSV file):
        isolate_1    /wgs/isolate_1/*.fna    /wgs/isolate_1.fastq.gz
        isolate_2    /wgs/isolate_2/*.fasta  /wgs/isolate_2.fastq.gz
        isolate_3    /wgs/isolate_3/*.fna    /data/isolate_3.fastq
    Please ensure trycycler is in \$PATH. Also, note that \'~\' is not supported for the paths of input FASTQ files."
}

if [ "$#" -ne 2 ]; then
    display_useage
    exit
fi

od=$2
if [ ! -d "$od" ]; then
    echo "Creating parental output directory ${od}. Contig clusters of each sample will be placed in this directory."
    mkdir -p $od
fi

if [ -f "$1" ]; then
    while read -r line; do
        IFS=$'\t' read -r -a cols <<< "$line"
        i="${cols[0]}"  # Isolate name
        fa="${cols[1]}"  # Directory of curated FASTA files of the current sample (no forward slash at the end of the path)
        fq="${cols[2]}"  # FASTQ file of the current sample
        if [ -f "$fq" ]; then
            echo "Clustering contigs of sample $i from directory $fa with FASTQ file ${fq}."
            trycycler cluster --assemblies ${fa}/*.fasta --reads $fq --out_dir ${od}/$i
        else
            echo "Input error: FASTQ file $fq is not accessible."
        fi
    done < "$1"
else
    echo "Argument error: input file $1 is not accessible."
fi