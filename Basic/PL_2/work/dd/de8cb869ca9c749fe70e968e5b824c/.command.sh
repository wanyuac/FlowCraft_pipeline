#!/bin/bash -ue
if [ ! -d /rds/general/user/ywan1/home/nf/output ]; then
    mkdir /rds/general/user/ywan1/home/nf/output
fi

echo "FASTA file ID: 4" > /rds/general/user/ywan1/home/nf/output/4.txt
