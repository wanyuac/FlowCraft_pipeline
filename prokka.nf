#!/usr/bin/env nextflow

/*
Annotate genome assemblies using Prokka. This script is a simplification of the pipeline assemble_PEreads.

[Use guide]
To run this pipeline in a screen session:
    nextflow -Djava.io.tmpdir=$PWD run prokka.nf --queueSize 25 --fasta "*.fasta" --annotDir annot \
                              --globalProkkaParams '--force --addgenes --kingdom Bacteria --genus Escherichia --species coli --gcode 11 --rfam --usegenus' \
                              --condaProkka "$HOME/anaconda3/envs/prokka"
                              -c prokka.config -profile pbs

[Declaration]
Copyright (C) 2020 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public License v3.0
Publication: 28/03/2020
*/

def mkdir(dir_path) {
    /*
    Creates a directory and returns a File object.
    */
    def dir_obj = new File(dir_path)
    
    if ( !dir_obj.exists() ) {
        result = dir_obj.mkdir()
        println result ? "Successfully created directory ${dir_obj}" : "Cannot create directory ${dir_obj}"
    } else {
        println "Directory ${dir_obj} exists."
    }
    
    return dir_obj
}

annot_dir = mkdir(params.annotDir)

assemblies = Channel
    .fromPath(params.fasta)
    .map { file -> tuple(file.baseName, file) }

process Prokka {
    /*
    Cannot set Prokka's output directory to the same folder:
    https://github.com/tseemann/prokka/issues/379
    Use --proteins rather than --usegenus is recommended.
    */

    input:
    set genome, file(fasta) from assemblies
    
    script:    
    """
    perl5_env=${params.perl5lib}
    if [ ! -z "\${perl5_env}" ]; then
        export PERL5LIB=\$perl5_env
    fi
    export PATH=${params.prokka}:\${PATH}
    ${params.prokka}/prokka --cpus 8 --quiet --outdir . --prefix $genome --strain $genome ${params.globalProkkaParams} $fasta
    mv ${genome}.* ${annot_dir}/
    """
}
