# Bioinformatics pipelines

*Yu Wan*
Last update: 7 Nov 2021.


This repository contains my pipelines created for research and training purposes. Often in this repository I only include files that were manually modified for system compatibility or a specific analysis. Click each subdirectory for details. An adaptation is often necessary when migrating these pipelines to other platforms since components of every pipeline may be system-dependent.



**System configuration**

- Python >=3.5
- Nextflow 19.01.0.5050
- FlowCraft 1.4.1



**Abbreviations**

- High-performance (computer) cluster (HPC)
- Sun Grid Engine (SGE)
- Protable batch system (PBS)


## Scripts

### assembleReadSubsetsForTrycycler.sh
This is a helper script for [Trycycler](https://github.com/rrwick/Trycycler/), and it uses [Flye](https://github.com/fenderglass/Flye/), [Minipolish](https://github.com/rrwick/Minipolish), and [Raven](https://github.com/lbcb-sci/raven/) to assemble the 12 subsets of long reads as the input of Trycycler. This script is more sophisticated and perhaps more versatile than the example code on Trycycler's [wiki](https://github.com/rrwick/Trycycler/wiki/Generating-assemblies).

### UKHSA's Genefinder pipeline
- `run_genefinder.py`: runs the [Genefinder](https://github.com/phe-bioinformatics/gene_finder) pipeline through the SGE/PBG job scheduler.
- `genefinder_xml2tsv.py`: compiles Genefinder's output XML files into a TSV file.
