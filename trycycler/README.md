# Helper scripts for trycycler

Yu Wan
Last update: 12 Dec 2021

[Trycycler](https://github.com/rrwick/Trycycler/) is a pipeline developed by Ryan Wick et al. for hybrid assembly of bacterial genomes. I found it helpful to generate accurate bacterial complete reference genomes, therefore, I have developed a few helper scripts to facilitate the use of Trycycler.

## Helper scripts in this directory
- `assemble_read_subsets.sh`: Uses [Flye](https://github.com/fenderglass/Flye/), [Raven](https://github.com/lbcb-sci/raven/), and [Minipolish](https://github.com/rrwick/Minipolish) to assemble subsets of long reads of a single sample as the input of Trycycler. This script is more sophisticated and perhaps more versatile than the example code on Trycycler's [wiki](https://github.com/rrwick/Trycycler/wiki/Generating-assemblies). In particular, this script instructs Raven to generate assembly graphs (GFA format) so users can determine the circularisation status of assembled contigs. Users may run this script iteratively for multiple samples.
- `run_subsample.sh`: Runs command `trycycler subsample` for multiple samples that may have distinct genome sizes.
