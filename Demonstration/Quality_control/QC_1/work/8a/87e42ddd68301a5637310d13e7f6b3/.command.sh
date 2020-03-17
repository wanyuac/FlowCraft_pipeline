#!/bin/bash -ue
/rds/general/user/ywan1/home/.conda/envs/qc/bin/fastqc --dir . --outdir /rds/general/user/ywan1/home/qc/output/fastqc --noextract --format fastq ERR137805_1.fastq.gz ERR137805_2.fastq.gz
