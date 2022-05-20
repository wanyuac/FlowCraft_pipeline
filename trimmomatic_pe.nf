#!/usr/bin/env nextflow

/*
[Use guide]
Structure of output directories:
    ./    where this pipeline is run
    ./[outdir]    processed paired reads
    ./[outdir]/fastqc    FastQC reports about paired reads
    ./[outdir]/multiqc    MultiQC report

Recommend to run the following command in a screen session:
    nextflow run trimmomatic.nf --outdir "./trimmed" --fastq "./reads/*_{1,2}.fastq.gz" --slidingWindow "5:30" --minLen 50 --maxLen 250 --queueSize 35 -profile pbs

Users may want to adjust queue parameters in trimmomatic_pe.config for their analyses. This pipeline uses a default queue size of 20.

[Declarations]
Copyright (C) 2020-2022 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public License v3.0
Publication: 27 Feb 2020; last modification: 20 May 2022
*/

/*
To avoid the problem: Missing workflow definition - DSL2 requires at least a workflow block in the main script #63.
See https://bytemeta.vip/repo/genomicsITER/NanoCLUST/issues/63.
*/
nextflow.enable.dsl = 1

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
Channel
    .fromFilePairs(params.fastq)
    .set { read_sets }  // Save FASTQ file objects into read_sets


/*********** Launching individual processes ***********/
process trimmomatic {
    /* Copy processed paired reads to the output directory and remove "__paired" from filenames */
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
    action_added = 0
    if ( params.maxLen > 0 ) {
        actions = "CROP:${params.maxLen}"
        action_added = 1
        println "$actions"
    }
    if ( params.slidingWindow != null ) {  // Returns true when this parameter is not null or empty.
        if ( action_added > 0) {
            actions = actions + " SLIDINGWINDOW:${params.slidingWindow}"
        } else {
            actions = "SLIDINGWINDOW:${params.slidingWindow}"
            action_added = 1
        }
        println "$actions"
    }
    if ( params.minLen > 0 ) {
        if ( action_added > 0 ) {
            actions = actions + " MINLEN:${params.minLen}"
        } else {
            actions = "MINLEN:${params.minLen}"
            action_added = 1
        }
        println "$actions"
    }

    """
    java -Xmx4g -jar ${params.trimmomaticDir}/trimmomatic.jar PE -phred33 -threads 2 ${paired_fastq} ${genome_id}__paired_1.fastq.gz ${genome_id}__unpaired_1.fastq.gz ${genome_id}__paired_2.fastq.gz ${genome_id}__unpaired_2.fastq.gz ${actions}
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
    ${params.fastqcDir}/fastqc --dir . --outdir . --noextract --nogroup --format fastq --quiet --threads 4 ${paired_fastq}
    """
}

process multiqc {  // Terminal process
    executor "local"

    // The following configuration does not work probably because the input file is not used in this procedure.
    //publishDir path: "${multiqc_outdir}", pattern: "multiqc_report.html", mode: "copy", overwrite: true
    
    /*
      Do not use .collect() as it launches the multiqc process for each input file - you only want multiqc to run only once.
      Method last() of object fastqc_reports triggers the multiqc process when the last element of fastqc_reports is generated.
    */
    input:
    file single_file from fastqc_reports.last()
    
    script:
    /*
    Since the bash script is run under the current working directory rather than where the pipeline was launched,
    ${fastqc_outdir} causes a failure of directory absence if a relative path is used for parameter "outdir".
    */
    """
    ${params.multiqcDir}/multiqc ${workflow.launchDir}/${fastqc_outdir}
    mv multiqc_data ${workflow.launchDir}/${multiqc_outdir}
    mv multiqc_report.html ${workflow.launchDir}/${multiqc_outdir}
    """
}
