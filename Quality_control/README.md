# Pipelines for quality control of sequencing data

*Yu Wan*



In this collection, I demonstrate construction of pipelines for quality control (QC) of sequence data.



**Table of Content**

- [Downloading test data](#download)
- [A simple FASTQ-Trimmomatic pipeline (QC\_1)](#qc1)

<br/>

## 1. Download test data

<a name = "download"></a>

```bash
module load sra-toolkit/2.8.1-3

fastq-dump --gzip --readids --split-3 ERR134515 &
fastq-dump --gzip --readids --split-3 ERR137805 &
```

<br/>

## 2. A simple FASTQ-Trimmomatic pipeline (QC\_1)

<a name = "qc1"></a>

This demonstration involves the following new features that I had not explored before:

- Paired input files
- Read user-specified parameters
- Enabling trace and report functions
- Co-existence of local and PBS profiles
- Split an input channel for two processes
- Run Nextflow pipelines under a screen session
- Run Shell command lines with user-specified parameters



```bash
# This time, I run Nextflow in a screen session, for which the following command is
# necessary due to no permission to access the /tmp/nx-xxxx folder on my HPC for Nextflow.
$ export NXF_TEMP="${PWD}/temp"  # Specify Nextflow's temporary directory

# A test run
$ nextflow run qc1.nf --fastq "*_{1,2}.fastq.gz" --trimSlidingWindow "5:20" --trimMinLength 50

# A formal run with all report and tracking options turned on
$ nextflow run qc1.nf --fastq "*_{1,2}.fastq.gz" --trimSlidingWindow "5:20" --trimMinLength 50 -profile pbs_conf -with-report qc1_report.html -with-trace

N E X T F L O W  ~  version 19.01.0
Launching `qc1.nf` [sad_khorana] - revision: ae273cea88
[warm up] executor > pbs
[8e/3c50c5] Submitted process > trimmomatic (1)
[b7/271267] Submitted process > fastqc (2)
[8d/f44922] Submitted process > fastqc (1)
[6b/eb77ce] Submitted process > trimmomatic (2)

# Check queue status outside of the screen session before these jobs were launched
$ qstat
   Job ID           Class            Job Name        Status     Comment
-------------- --------------- -------------------- -------- -------------
1073039        Throughput      nf-trimmomatic_      Queued   no start time estimate yet
1073040        Throughput      nf-fastqc_2          Queued   no start time estimate yet
1073041        Throughput      nf-fastqc_1          Queued   no start time estimate yet
1073042        Throughput      nf-trimmomatic_      Queued   no start time estimate yet
```

**Structure of output files**

```bash
$ ls -1aR output
output:
.
..
fastqc
trimmomatic

output/fastqc:
.
..
ERR134515_1_fastqc.html
ERR134515_1_fastqc.zip
ERR134515_2_fastqc.html
ERR134515_2_fastqc.zip
ERR137805_1_fastqc.html
ERR137805_1_fastqc.zip
ERR137805_2_fastqc.html
ERR137805_2_fastqc.zip

output/trimmomatic:
.
..

$ ls -1 -R -a work
work:
.
..
12
22
58
74

work/12:
.
..
04a2439657919dbaf5d27b1b70402a

work/12/04a2439657919dbaf5d27b1b70402a:
.
..
.command.begin
.command.err
.command.log
.command.out
.command.run
.command.sh
.command.stub
.command.trace
ERR137805_1.fastq.gz
ERR137805_2.fastq.gz
.exitcode

work/22:
.
..
123a9f82b505b70f8a0c322e5f9adf

work/22/123a9f82b505b70f8a0c322e5f9adf:
.
..
.command.begin
.command.err
.command.log
.command.out
.command.run
.command.sh
.command.stub
.command.trace
ERR137805_1.fastq.gz
ERR137805_2.fastq.gz
ERR137805_paired_1.fastq.gz
ERR137805_paired_2.fastq.gz
ERR137805_unpaired_1.fastq.gz
ERR137805_unpaired_2.fastq.gz
.exitcode

work/58:
.
..
807ce8f8c0617fd9df0b6a31973014

work/58/807ce8f8c0617fd9df0b6a31973014:
.
..
.command.begin
.command.err
.command.log
.command.out
.command.run
.command.sh
.command.stub
.command.trace
ERR134515_1.fastq.gz
ERR134515_2.fastq.gz
ERR134515_paired_1.fastq.gz
ERR134515_paired_2.fastq.gz
ERR134515_unpaired_1.fastq.gz
ERR134515_unpaired_2.fastq.gz
.exitcode

work/74:
.
..
dd7cadf0e36703f9379b85e91fc742

work/74/dd7cadf0e36703f9379b85e91fc742:
.
..
.command.begin
.command.err
.command.log
.command.out
.command.run
.command.sh
.command.stub
.command.trace
ERR134515_1.fastq.gz
ERR134515_2.fastq.gz
.exitcode
```

