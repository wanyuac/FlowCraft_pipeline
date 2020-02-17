#!/bin/bash -ue
echo /rds/general/user/ywan1/home/qc
java -Xmx4g -jar /rds/general/user/ywan1/home/.conda/envs/qc/share/trimmomatic/trimmomatic.jar PE -phred33 -threads 2 ERR134515_1.fastq.gz ERR134515_2.fastq.gz ERR134515_paired_1.fastq.gz ERR134515_unpaired_1.fastq.gz ERR134515_paired_2.fastq.gz ERR134515_unpaired_2.fastq.gz SLIDINGWINDOW:5:20 MINLEN:50
