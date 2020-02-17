#!/bin/bash -ue
/rds/general/user/ywan1/home/.conda/envs/qc/bin/fastqc --dir . --outdir /rds/general/user/ywan1/home/qc/output/fastqc --noextract --format fastq ERR134515_paired_1.fastq.gz ERR134515_paired_2.fastq.gz
