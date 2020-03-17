#!/usr/bin/env nextflow

/*
[Use guide]
Structure of output directories:
    ./    where this pipeline is run
    ./trimmed    processed paired reads
    ./trimmed/fastqc    FastQC reports about paired reads
    ./trimmed/multiqc    MultiQC report

Recommend to run the following command in a screen session:
    nextflow run trimmomatic.nf --outdir "./trimmed" --fastq "./reads/*_{1,2}.fastq.gz" --slidingWindow "5:30" --minLen 50 --maxLen 250 -profile pbs

Users may want to adjust queue parameters in trimmomatic_pe.config for their analyses. This pipeline assumes a queue size of 15.

[Declarations]
Copyright (C) 2020 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public License v3.0
Publication: 27/2/2020; last modification: 17/3/2020
*/


/*********** Create output directories before main processes. ***********/
def outdir_par = new File(params.outdir)  // Parental output directory
if ( !outdir_par.exists() ) {
    result = outdir_par.mkdir()  // Command mkdir in Nextflow does not work as the bash command "mkdir -p".
    println result ? "Created parental output directory ${outdir_par}" : "Cannot create directory: ${outdir_par}"
}

def fastqc_outdir = new File(params.outdir + "/fastqc")
if ( !fastqc_outdir.exists() ) {
    result = fastqc_outdir.mkdir()  // Command mkdir in Nextflow does not work as the bash command "mkdir -p".
    println result ? "  Created subdirectory ${fastqc_outdir}" : "Cannot create directory: ${fastqc_outdir}"
}

def multiqc_outdir = new File(params.outdir + "/multiqc")
if ( !multiqc_outdir.exists() ) {
    result = multiqc_outdir.mkdir()  // Command mkdir in Nextflow does not work as the bash command "mkdir -p".
    println result ? "  Created subdirectory ${multiqc_outdir}" : "Cannot create directory: ${multiqc_outdir}"
}


/*********** Defining the input channel ***********/
Channel.fromFilePairs(params.fastq).set { read_sets }  // Save FASTQ file objects into read_sets


/*********** Launching individual processes ***********/
process trimmomatic {
    publishDir path: "${params.outdir}",
    pattern: "*__paired_{1,2}.fastq.gz",
    mode: "copy",
    saveAs: { filename -> filename.replaceAll(/__paired/, "") },
    overwrite: true
    
    input:
    set genome_id, file(paired_fastq) from read_sets  // Create a set of objects genome_id and paired_fastq from the input channel read_sets
    
    output:
    set genome_id, file("*__paired_{1,2}.fastq.gz") into trimmed_fastqs  // Feed a set into the channel. Files to be moved to the publishDir
    
    script:
    """
    java -Xmx4g -jar ${params.trimmomaticDir}/trimmomatic.jar PE -phred33 -threads 2 ${paired_fastq} ${genome_id}__paired_1.fastq.gz ${genome_id}__unpaired_1.fastq.gz ${genome_id}__paired_2.fastq.gz ${genome_id}__unpaired_2.fastq.gz CROP:${params.maxLen} SLIDINGWINDOW:${params.slidingWindow} MINLEN:${params.minLen}
    """
}
    
process fastqc {
    /*
      Waits until all output files from FastQC are generated.
      See https://github.com/nextflow-io/patterns/blob/master/docs/process-collect.adoc
      
      The pattern for publishDir must be the same as that in the defined output. Otherwise, actions
      following publishDir does not work. For example, we cannot define pattern "*.html* for publishDir
      while define file "*.zip" into fastqc_reports.
      
      In this process, probably using the mv command in the script block makes things easier.
    */
    
    publishDir path: "${fastqc_outdir}",
    pattern: "*__paired_?_fastqc.*",
    mode: "copy",
    saveAs: { filename -> filename.replaceAll(/__paired/, "") },
    overwrite: true
    
    input:
    set genome_id, file(paired_fastq) from trimmed_fastqs  // This process runs for every set in parallel, similar to R's apply function.
    
    output:
    file "*__paired_?_fastqc.*" into fastqc_reports  // Multiple output files
    
    script:
    """
    ${params.fastqcDir}/fastqc --dir . --outdir . --noextract --nogroup --format fastq --quiet --threads 2 ${paired_fastq}
    """
}

process multiqc {  // Terminal process
    executor "local"

    // The following configuration does not work probably because the input file is not used in this procedure.
    //publishDir path: "${multiqc_outdir}", pattern: "multiqc_report.html", mode: "copy", overwrite: true
    
    /*
      Do not use .collect() as it launches the multiqc process for each input file - you only want multiqc
      to run only once.      
    */
    input:
    file single_file from fastqc_reports.last()
    
    script:
    """
    ${params.multiqcDir}/multiqc ${fastqc_outdir}
    mv multiqc_data ${multiqc_outdir}
    mv multiqc_report.html ${multiqc_outdir}
    """
}
