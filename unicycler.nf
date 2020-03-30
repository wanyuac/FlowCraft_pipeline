#!/usr/bin/env nextflow

/*
Assemble Illumina short reads using Unicycler. This script is a simplified version of the pipeline
assemble_PEreads.

[Use guide]
To run this pipeline in a screen session:
    nextflow -Djava.io.tmpdir=$PWD run unicycler.nf --fastq "./reads/*_{1,2}.fastq.gz" \
                              --assemblyDir assembly --condaUnicycler "$HOME/anaconda3/envs/unicycler" \
                              -c unicycler.config -profile pbs

[Declaration]
Copyright (C) 2020 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public License v3.0
Publication: 28/03/2020
*/

def mkdir(dir_path) {
    /*
    Creates a directory and returns a File object.
    */
    def dir_obj = new File(dir_path)
    
    if ( !dir_obj.exists() ) {
        result = dir_obj.mkdir()
        println result ? "Successfully created directory ${dir_obj}" : "Cannot create directory ${dir_obj}"
    } else {
        println "Directory ${dir_obj} exists."
    }
    
    return dir_obj
}

assembly_dir = mkdir(params.assemblyDir)

read_sets = Channel.fromFilePairs(params.fastq)

process Unicycler {
    input:
    set genome, file(paired_fastq) from read_sets
    
    script:    
    """
    export PATH=${params.unicycler}:\${PATH}
    ${params.unicycler}/unicycler --short1 ${paired_fastq[0]} --short2 ${paired_fastq[1]} --no_correct --mode normal --threads 8 --keep 0 --out .
    mv assembly.fasta ${assembly_dir}/${genome}.fasta
    mv assembly.gfa ${assembly_dir}/${genome}.gfa
    mv unicycler.log ${assembly_dir}/${genome}.log
    """
}
