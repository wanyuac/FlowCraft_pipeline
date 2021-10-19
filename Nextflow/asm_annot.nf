#!/usr/bin/env nextflow

/*
Assemble Illumina short reads using Unicycler and annotate genomes using Prokka.

[Use guide]
To run this pipeline in a screen session:
    nextflow -Djava.io.tmpdir=$PWD run assemble_PEreads.nf --queueSize 25 --fastq "./reads/*_{1,2}.fastq.gz" \
                              --assemblyDir assembly --annotDir annot \
                              --globalProkkaParams '--force --addgenes --kingdom Bacteria --genus Escherichia --species coli --gcode 11 --rfam --proteins 'proteins.faa' \
                              --condaUnicycler "$HOME/anaconda3/envs/unicycler" --condaProkka "$HOME/anaconda3/envs/prokka"
                              -c assemble_PEreads.config -profile pbs

[Declaration]
Copyright (C) 2020 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public License v3.0
Publication: 30/03/2020; lastest modification: 1/4/2020
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

assembly_dir = mkdir(params.assemblyDir)
annot_dir = mkdir(params.annotDir)

/*
Import FASTQ files
*/
read_sets = Channel.fromFilePairs(params.fastq)

process Unicycler {    
    input:
    set genome, file(paired_fastq) from read_sets
    
    output:
    set genome, file("assembly.fasta") into assemblies
    
    script:    
    """
    export PATH=${params.unicycler}:\${PATH}
    ${params.unicycler}/unicycler --short1 ${paired_fastq[0]} --short2 ${paired_fastq[1]} --no_correct --mode normal --threads 8 --keep 0 --out .
    cp assembly.fasta ${assembly_dir}/${genome}.fasta
    mv assembly.gfa ${assembly_dir}/${genome}.gfa
    mv unicycler.log ${assembly_dir}/${genome}.log
    """
}

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
