#!/usr/bin/env nextflow

/*
Nextflow searches for nextflow.config when it is running this pipeline script.
To run this pipeline:
    nextflow run -profile pbs_job pbs_job.nf

Yu Wan (13/2/2020)
*/

// Create a channel object fasta_files, which holds the path given in the argument of the fromPath method
fasta_files = Channel.fromPath("$HOME/nf/NC_028700__StrepPhageT2.fasta")

process basic_io {
    input:
    file fasta from fasta_files  // Create a file object from fasta_files
    
    script:
    x = fasta.name
    
    """
    echo $x > name.txt
    """
}
