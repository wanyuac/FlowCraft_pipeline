#!/usr/bin/env nextflow

/*
nextflow run qc1.nf --fastq "*_{1,2}.fastq.gz" --trimSlidingWindow "5:20" --trimMinLength 50 -profile pbs_conf -with-report qc1_report.html -with-trace
Yu Wan (14/02/2020)
*/

/*
 Define the input channel.
 Access FASTQ files through the parameter fastq defined in nextflow.config
 The following command line creates an input channel read_sets from several pairs of paths.
*/
Channel
    .fromFilePairs(params.fastq)  // params.fastq should be "../../*_[1,2].fastq.gz
    .set { read_sets }  // Cannot use read_sets = Channel ..., which returns a null value.
    // Cannot add the third command here, such as println().

/*
Since a channel can only be consumed by one process, we must duplicate it in order that
fastqc and Trimmomatic can share the same input files.
*/
read_sets.into{ reads_fastqc; reads_trimmomatic }
    
process fastqc {    
    input:
    set genome_id, file(paired_fastq) from reads_fastqc
    
    script:
    
    """
    $HOME/.conda/envs/qc/bin/fastqc --dir . --outdir $PWD/output/fastqc --noextract --format fastq $paired_fastq
    """
}


process trimmomatic {    
    // N processes will be launched for N pairs of input files
    
    input:
    set genome_id, file(paired_fastq) from reads_trimmomatic  // Create objects genome_id and paired_fastq from the input channel read_sets
    
    script:
    
    // In every process, each element in the list paired_fastq can be accessed using $paired_fastq[0] or $paired_fastq[1].
    """
    java -Xmx4g -jar $HOME/.conda/envs/qc/share/trimmomatic/trimmomatic.jar PE -phred33 -threads 2 ${paired_fastq} ${genome_id}_paired_1.fastq.gz ${genome_id}_unpaired_1.fastq.gz ${genome_id}_paired_2.fastq.gz ${genome_id}_unpaired_2.fastq.gz SLIDINGWINDOW:${params.trimSlidingWindow} MINLEN:${params.trimMinLength}
    """
}
