#!/bin/bash -ue
java -Xmx4g -jar /rds/general/user/ywan1/home/.conda/envs/qc/share/trimmomatic/trimmomatic.jar PE -phred33 -threads 2 ERR137805_1.fastq.gz ERR137805_2.fastq.gz ERR137805_paired_1.fastq.gz ERR137805_unpaired_1.fastq.gz ERR137805_paired_2.fastq.gz ERR137805_unpaired_2.fastq.gz SLIDINGWINDOW:5:20 MINLEN:50
