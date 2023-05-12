rule get_promoter_sequences:
    input:
        genome = "{0}/genomes/Nipponbare/Npb.fasta".format(config["input_data_dir"]),
        gff_db = "{0}/annotations/Nb/Nb.gff.db".format(config["input_data_dir"])
    params:
        upstream_win_len = 10,
        downstream_win_len = 0
    output:
        out_fasta = "{0}/trans_fac_binding_sites/promoter_seq.fasta".format(config["tfbs_dir"])
    conda:
        "../env/gff_biopython.yaml"
    shell:
        '''
        python scripts/get_promoter_sequences.py {input.genome} {input.gff_db} {params.upstream_win_len} 
        {params.downstream_win_len} {output.out_fasta}
        '''
