#!/usr/bin/env nextflow

/*
In this example, the pipeline trims reads first and then send the trimmed paired-end reads to FastQC.
nextflow run qc2.nf --outdir "${PWD}/output" --fastq "*_{1,2}.fastq.gz" --trimSlidingWindow "5:20" --trimMinLength 50 -with-trace
For the option outdir, an absolute path is required as the working directory of Nextflow processes
differ from the directory where the pipeline (.nf) is launched.
Yu Wan (17/02/2020)
*/

// Environment settings: the follow commands are executed before the processes.
def output_dir_par = new File(params.outdir)
if ( !output_dir_par.exists() ) {
    result = output_dir_par.mkdir()  // Command mkdir in Nextflow does not work as the bash command "mkdir -p".
    println result ? "Successfully created directory ${output_dir_par}" : "Cannot create directory: ${output_dir_par}"
}

def output_dir_trim = new File("${params.outdir}/trimmomatic")
if ( !output_dir_trim.exists() ) {
    result = output_dir_trim.mkdir()
    println result ? "Successfully created directory ${output_dir_trim}" : "Cannot create directory: ${output_dir_trim}"
}

def output_dir_fastqc = new File("${params.outdir}/fastqc")
if ( !output_dir_fastqc.exists() ) {
    result = output_dir_fastqc.mkdir()
    println result ? "Successfully created directory ${output_dir_fastqc}" : "Cannot create directory: ${output_dir_fastqc}"
}

// Defining the input channel
Channel.fromFilePairs(params.fastq).set { read_sets }  // Save FASTQ file objects into read_sets

// Launching individual processes
process trimmomatic {    
    // N processes will be launched for N pairs of input files
    publishDir "${params.outdir}/trimmomatic", mode: "symlink", overwrite: true
    
    input:
    set genome_id, file(paired_fastq) from read_sets  // Create objects genome_id and paired_fastq from the input channel read_sets
    
    output:
    set genome_id, file("*_paired_{1,2}.fastq.gz") into trimmed_fastqs
    
    script:
    def out_dir = "${params.outdir}/trimmomatic"
    """
    echo $PWD
    java -Xmx4g -jar $HOME/.conda/envs/qc/share/trimmomatic/trimmomatic.jar PE -phred33 -threads 2 ${paired_fastq} ${genome_id}_paired_1.fastq.gz ${genome_id}_unpaired_1.fastq.gz ${genome_id}_paired_2.fastq.gz ${genome_id}_unpaired_2.fastq.gz SLIDINGWINDOW:${params.trimSlidingWindow} MINLEN:${params.trimMinLength}
    """
}
    
process fastqc {
    input:
    set genome_id, file(paired_fastq) from trimmed_fastqs
    
    script:
    def out_dir = "${params.outdir}/fastqc"
    """
    $HOME/.conda/envs/qc/bin/fastqc --dir . --outdir ${out_dir} --noextract --format fastq $paired_fastq
    """
}
