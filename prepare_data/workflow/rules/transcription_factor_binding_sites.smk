rule get_promoter_sequences:
    input:
        genome = "{0}/genomes/Nipponbare/Npb.fasta".format(config["input_data_dir"]),
        gff_db = "{0}/annotations/Nb/Nb.gff.db".format(config["input_data_dir"])
    params:
        upstream_win_len = 10,
        downstream_win_len = 0
    output:
        out_fasta = "{0}/promoter_seq.fasta".format(config["tfbs_dir"]),
        promoter_gene_map = "{0}/promoter_gene_map".format(config["tfbs_dir"])
    conda:
        "../env/gff_biopython.yaml"
    shell:
        '''
        python scripts/get_promoter_sequences.py {input.genome} {input.gff_db} {params.upstream_win_len} \
        {params.downstream_win_len} {output.out_fasta} {output.promoter_gene_map}
        '''

# rule fimo_search:
#     input:
#         promoter_seq = "{0}/promoter_seq.fasta".format(config["tfbs_dir"])
#         motifs = "{0}/PlantTFDB_TF_binding_motifs_from_experiments".format(config["tfbs_dir"])
#     output:
#         fimo_out = "{0}/fimo_out".format(config["tfbs_dir"])

#rule download_tfbs_data:
#  wget -O motif
#  wget -O motif_CE
#  wget -O FunTFBS
