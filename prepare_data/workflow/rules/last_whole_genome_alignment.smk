rule last_db: #Rule for constructing LAST index
    input:
        reference = "{0}/genomes/Nipponbare/Npb.fasta.gz".format(config["input_data_dir"])
    output:
        touch("{0}/last_index/index.done".format(config["processed_data_dir"]))
    params:
        index_basename = "{0}/last_index/Nipponbare_db".format(config["processed_data_dir"])
    conda:
        "../env/lastal.yaml"
    shell:
        "lastdb -P4 -uNEAR {params.index_basename} {input.reference}"

rule last_score_training:
    input:
        Nb_index_flag = "{0}/last_index/index.done".format(config["processed_data_dir"]),
        query_genome= "{0}/genomes/{{other_ref}}/{{other_ref}}.fasta.gz".format(config["input_data_dir"])
    output:
        train_out = "{0}/last_training/Nb_{{other_ref}}".format(config["processed_data_dir"])
    params:
        index_basename="{0}/last_index/Nipponbare_db".format(config["processed_data_dir"])
    threads:  config["threads"]
    conda:
        "../env/lastal.yaml"
    shell:
        """
        last-train -P {threads} --revsym -E0.05 -C2 --sample-number=500 {params.index_basename} {input.query_genome} \
        > {output.train_out}
        """

rule last_align_one_to_many:
    input:
        Nb_index_flag = "{0}/last_index/index.done".format(config["processed_data_dir"]),
        other_ref = "{0}/genomes/{{other_ref}}/{{other_ref}}.fasta.gz".format(config["input_data_dir"]),
        score_training_out= "{0}/last_training/Nb_{{other_ref}}".format(config["processed_data_dir"])
    output:
        one_to_many_alignment = "{0}/alignments/Nb_{{other_ref}}/Nb_{{other_ref}}_one_to_many.maf".format(config["processed_data_dir"])
    params:
        index_basename="{0}/last_index/Nipponbare_db".format(config["processed_data_dir"])
    threads: config["threads"]
    conda:
        "../env/lastal.yaml"
    shell:
        """ 
        lastal -P {threads} -D1e8 -m20 -C2 --split-f=MAF+ -p {input.score_training_out} {params.index_basename} {input.other_ref} > {output.one_to_many_alignment}
        """

rule last_align_one_to_one:
    input:
        one_to_many_alignment = "{0}/alignments/Nb_{{other_ref}}/Nb_{{other_ref}}_one_to_many.maf".format(config["processed_data_dir"])
    output:
         one_to_one_alignment = "{0}/alignments/Nb_{{other_ref}}/Nb_{{other_ref}}_one_to_one.maf".format(config["processed_data_dir"])
    conda:
        "../env/lastal.yaml"
    shell:
        """
        last-split -r -m1e-5 {input.one_to_many_alignment} > {output.one_to_one_alignment}
        """

rule convert_gff:
    input:
        one_to_one_alignment="{0}/alignments/Nb_{{other_ref}}/Nb_{{other_ref}}_one_to_one.maf".format(config["processed_data_dir"])
    output:
        gff = "{0}/alignments/Nb_{{other_ref}}/Nb_{{other_ref}}.gff".format(config["processed_data_dir"])
    conda:
        "../env/lastal.yaml"
    shell:
        "maf-convert gff {input.one_to_one_alignment} > {output.gff}"

rule build_gff_db:
    input:
        gff = "{0}/alignments/Nb_{{other_ref}}/Nb_{{other_ref}}.gff".format(config["processed_data_dir"])
    output:
        gff_db = "{0}/alignments/Nb_{{other_ref}}/Nb_{{other_ref}}.gff.db".format(config["processed_data_dir"])
    conda:
        "../env/gffutils.yaml"
    shell:
        "python scripts/gff_db.py {input.gff} {output.gff_db}"


