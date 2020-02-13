#!/usr/bin/env nextflow

/*
A Nextflow job taking as input multiple files and prints each of their names to a separate file.
Therefore, the pipeline processes FASTA files in a parallel manner.

To run this pipeline:
    nextflow run multiple_inputs.nf -profile pbs_shifter

Yu Wan (13/2/2020)
*/

params.input = "${PWD}/input/*.fasta"

/*
Create a channel object holding multiple paths of FASTA files. In order to get a unique ID from
each file name, we need to have the channel emit a tuple containing both the file's base name and
the full path. (See https://www.nextflow.io/docs/latest/faq.html)
*/
fasta_files = Channel
                    .fromPath(params.input)
                    .map { file -> tuple(file.baseName, file) }

process basic_io {
    input:
    set file_name, file(file_path) from fasta_files  // Extract the value and key from each tuple in the channel
    
    script:
    
    outdir = "$PWD/output"
    
    """
    if [ ! -d $outdir ]; then
        mkdir $outdir
    fi
    
    echo "FASTA file ID: ${file_name}" > ${outdir}/${file_name}.txt
    """
}
