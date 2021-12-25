# Bioinformatics pipelines

By Yu Wan  
Last update: 12 Dec 2021.


This repository contains my pipelines created for research and training purposes. Often in this repository I only include files that were manually modified for system compatibility or a specific analysis. Click each subdirectory for details. An adaptation is often necessary when migrating these pipelines to other platforms since components of every pipeline may be system-dependent.



**System configuration**

- Python >=3.5
- Nextflow 19.01.0.5050
- FlowCraft 1.4.1
- SGE or PBS job scheduling system on an HPC, or Linux bash.



**Abbreviations**

- High-performance (computer) cluster (HPC)
- Sun Grid Engine (SGE)
- Protable batch system (PBS)


## Scripts

### Assembling subsets of long reads for [Trycycler](https://github.com/rrwick/Trycycler/)
See the manual in subdirectory `trycycler`.


### UKHSA's Genefinder pipeline
- `run_genefinder.py`: Runs the [Genefinder](https://github.com/phe-bioinformatics/gene_finder) pipeline through the SGE/PBG job scheduler.
- `genefinder_xml2tsv.py`: Compiles Genefinder's output XML files into a TSV file.


### UKHSA's PHEnix mapping pipeline
- `run_phenix.py`: Runs the [PHEnix](https://github.com/phe-bioinformatics/PHEnix) pipeline that aligns short reads against a reference genome.
