# Pipelines for quality control of sequencing data

*Yu Wan*



In this collection, I demonstrate construction of pipelines for quality control (QC) of sequence data.



**Table of Content**

- [Downloading test data](#download)
- [A simple FASTQ-Trimmomatic pipeline (QC\_1)](#qc1)
- [A QC pipeline that redirects outputs to designated directories (QC\_2)](#qc2)

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

*Note that the `pbspro` executor must be used instead of `pbs` in order to avoid an error message from `qstat` (see [Issue 1106](https://github.com/nextflow-io/nextflow/issues/1106) of Nextflow).*

```bash
# This time, I run Nextflow in a screen session, for which the following command is
# necessary due to no permission to access the /tmp/nx-xxxx folder on my HPC for Nextflow.
$ export NXF_TEMP="${PWD}/temp"  # Specify Nextflow's temporary directory

# A test run
$ nextflow run qc1.nf --fastq "*_{1,2}.fastq.gz" --trimSlidingWindow "5:20" --trimMinLength 50

# A formal run with all report and tracking options turned on
$ nextflow run qc1.nf --fastq "*_{1,2}.fastq.gz" --trimSlidingWindow "5:20" --trimMinLength 50 -profile pbs_conf -with-report qc1_report.html -with-trace

N E X T F L O W  ~  version 19.01.0
Launching `qc1.nf` [scruffy_caravaggio] - revision: 3701cc42b0
[warm up] executor > pbspro
[bd/933266] Submitted process > fastqc (2)
[28/f8bc0e] Submitted process > trimmomatic (1)
[7c/f9b919] Submitted process > trimmomatic (2)
[8a/87e42d] Submitted process > fastqc (1)

# Check queue status outside of the screen session before these jobs were launched
$ qstat
   Job ID           Class            Job Name        Status     Comment
-------------- --------------- -------------------- -------- -------------
1073039        Throughput      nf-trimmomatic_      Queued   no start time estimate yet
1073040        Throughput      nf-fastqc_2          Queued   no start time estimate yet
1073041        Throughput      nf-fastqc_1          Queued   no start time estimate yet
1073042        Throughput      nf-trimmomatic_      Queued   no start time estimate yet

# Show PBS version
$ qstat --version
pbs_version = 18.2.3.20181206140456
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
28
7c
8a
bd

work/28:
.
..
f8bc0e1faa083d2a2735563dec476e

work/28/f8bc0e1faa083d2a2735563dec476e:
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

work/7c:
.
..
f9b9191577505634de986f7cf9f7b4

work/7c/f9b9191577505634de986f7cf9f7b4:
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

work/8a:
.
..
87e42ddd68301a5637310d13e7f6b3

work/8a/87e42ddd68301a5637310d13e7f6b3:
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

work/bd:
.
..
933266ae86193f1b21553685470e24

work/bd/933266ae86193f1b21553685470e24:
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



## 3. A QC pipeline that redirects outputs to designated directories

<a name = "qc2"></a>

Nextflow saves outputs from processes under the folder `work` and traces them using channels. However, it is easier to users to access results if they are organised under a directory having a more human readable structure. In this pipeline, I *creates symbolic links to output files* of Trimmomatic under a designated directory. In addition, this pipeline demonstrates *creation of output directories before launching processes*.

```bash
nextflow run qc2.nf --outdir "${PWD}/output" --fastq "*_{1,2}.fastq.gz" --trimSlidingWindow "5:20" --trimMinLength 50 -with-trace

N E X T F L O W  ~  version 19.01.0
Launching `qc2.nf` [drunk_hawking] - revision: 985deb1446
Successfully created directory /rds/general/user/ywan1/home/qc/output
Successfully created directory /rds/general/user/ywan1/home/qc/output/trimmomatic
Successfully created directory /rds/general/user/ywan1/home/qc/output/fastqc
[warm up] executor > local
[fe/d91b32] Submitted process > trimmomatic (1)
[08/9210a7] Submitted process > trimmomatic (2)
[6f/6e42ae] Submitted process > fastqc (1)
[30/7ec864] Submitted process > fastqc (2)
```

Output

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
ERR134515_paired_1_fastqc.html
ERR134515_paired_1_fastqc.zip
ERR134515_paired_2_fastqc.html
ERR134515_paired_2_fastqc.zip
ERR137805_paired_1_fastqc.html
ERR137805_paired_1_fastqc.zip
ERR137805_paired_2_fastqc.html
ERR137805_paired_2_fastqc.zip

output/trimmomatic:
.
..
ERR134515_paired_1.fastq.gz  # Symbolic links to output files under ./work/..
ERR134515_paired_2.fastq.gz
ERR137805_paired_1.fastq.gz
ERR137805_paired_2.fastq.gz

$ ls -1aR work
work:
.
..
08
30
6f
fe

work/08:
.
..
9210a7c08cec828dfe211c6142bb02

work/08/9210a7c08cec828dfe211c6142bb02:
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
ERR134515_1.fastq.gz  # Symbolic links to original read sets, created by Nextflow for inputs of Trimmomatic, because the command line (.command.sh) does not have any absolute or relative path to the original read set.
ERR134515_2.fastq.gz
ERR134515_paired_1.fastq.gz
ERR134515_paired_2.fastq.gz
ERR134515_unpaired_1.fastq.gz
ERR134515_unpaired_2.fastq.gz
.exitcode

work/30:
.
..
7ec864708656b38830b15e34648311

work/30/7ec864708656b38830b15e34648311:
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
ERR134515_paired_1.fastq.gz
ERR134515_paired_2.fastq.gz
.exitcode

work/6f:
.
..
6e42ae6740c4e2dd276fc410beb627

work/6f/6e42ae6740c4e2dd276fc410beb627:
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
ERR137805_paired_1.fastq.gz
ERR137805_paired_2.fastq.gz
.exitcode

work/fe:
.
..
d91b3270a2433a4bf11ed8f3e27430

work/fe/d91b3270a2433a4bf11ed8f3e27430:
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
```

