# Resolve Network Dependency
for key, path in config['networks'].items():
    config["networks"][key] = path.format(network_dir=config["network_dir"])

rule data_prep_for_enrichment_analysis:
    input:
        expand(
            "{ppi_dir}/all_proteins/{network}/{file_format}/{name}.txt",
            ppi_dir = config["ppi_dir"],
            network = config["networks"].keys(),
            file_format = "uniprot",
            name = "all-proteins"
        ),
        expand(
            "{gene_id_mapping_dir}/msu_mapping/{file_name}.pickle",
            gene_id_mapping_dir = config["gene_id_mapping_dir"],
            file_name = "uniprot_to_msu"
        ),
        expand(
            "{raw_enrich_dir}/all_genes/{network}/{file_format}/all-genes.txt",
            raw_enrich_dir = config["raw_enrich_dir"],
            network = config["networks"].keys(),
            file_format = "MSU"
        ),
        expand(
            "{raw_enrich_dir}/temp/{network}/{script_outputs}.txt",
            raw_enrich_dir = config["raw_enrich_dir"],
            network = config["networks"].keys(),
            script_outputs = config["ricegeneid_msu_to_transcript_outputs"]
        ),
        expand(
            "{raw_enrich_dir}/mapping/{network}/msu-to-transcript-id.pickle",
            raw_enrich_dir = config["raw_enrich_dir"],
            network = config["networks"].keys(),
        ),
        expand(
            "{gene_id_mapping_dir}/mapping/{network}/transcript-to-msu-id.pickle",
            gene_id_mapping_dir = config["gene_id_mapping_dir"],
            network = config["networks"].keys()
        ),
        expand(
            "{raw_enrich_dir}/all_genes/{network}/rap/all-genes.txt",
            raw_enrich_dir = config["raw_enrich_dir"],
            network = config["networks"].keys(),
            target_file = "all-genes"
        ),
        expand(
            "{network_mod_dir}/{network}/{algo}/{param}/MSU/{algo}-module-list.tsv",
            network_mod_dir = config["network_mod_dir"],
            network = config["networks"].keys(),
            algo = "clusterone",
            param = config["clusterone_min_density"].keys()
        ),
        expand(
            "{network_mod_dir}/{network}/{algo}/{param}/rap/{algo}-module-list.tsv",
            network_mod_dir = config["network_mod_dir"],
            network = config["networks"].keys(),
            algo = "clusterone",
            param = config["clusterone_min_density"].keys()
        )


# GENE EXTRACTION Rules
rule get_proteins_from_network:
    input:
        lambda wildcards: config['networks'][wildcards.network]
    output:
        "{ppi_dir}/all_proteins/{network}/{file_format}/{name}.txt"
    shell:
        "python scripts/network_util/get-nodes-from-network.py " \
        "{input} {wildcards.ppi_dir}/all_proteins/{wildcards.network}/{wildcards.file_format} " \
        "--name {wildcards.name}"

rule convert_all_proteins_to_genes:
    input:
        proteins_file="{0}/all_proteins/{{network}}/uniprot/all-proteins.txt".format(config["ppi_dir"]),
        protein_to_gene_mapping="{0}/msu_mapping/uniprot_to_msu.pickle".format(config["gene_id_mapping_dir"])
    output:
        "{raw_enrich_dir}/all_genes/{network}/{file_format}/all-genes.txt"
    shell:
        "python scripts/ppi_util/convert_all_prot_to_gene.py " \
        "{input.proteins_file} {input.protein_to_gene_mapping} " \
        "{wildcards.raw_enrich_dir}/all_genes/{wildcards.network}/{wildcards.file_format}"
    
rule prepare_uniprot_to_gene:
    input:
        "{0}/Nb/Nb_gene_descriptions.csv".format(config["gene_desc_dir"])
    output:
        "{gene_id_mapping_dir}/msu_mapping/{file_name}.pickle"
    shell:
        "python scripts/ppi_util/prepare_uniprot_to_gene.py " \
        "{input} {wildcards.gene_id_mapping_dir}/msu_mapping " \
        "{wildcards.file_name}"

# PATHWAY ENRICHMENT RULES
rule ricegeneid_msu_to_transcript_id:
    input:
        "{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"])
    output:
        "{raw_enrich_dir}/temp/{network}/{script_outputs}.txt"
    shell:
        "Rscript --vanilla scripts/enrichment_analysis/util/ricegeneid-msu-to-transcript-id.r " \
        "-g {input} " \
        "-o {wildcards.raw_enrich_dir}/temp/{wildcards.network}"

rule msu_to_transcript_id:
    input:
        all_transcript="{0}/temp/{{network}}/all-transcript-id.txt".format(config["raw_enrich_dir"]),
        all_na_transcript="{0}/temp/{{network}}/all-na-transcript-id.txt".format(config["raw_enrich_dir"]),
        rap_to_msu="{0}/rap_db/{1}".format(config["raw_enrich_dir"], config["rap_to_msu_file"]),
        rap_to_transcript="{0}/rap_db/{1}".format(config["raw_enrich_dir"], config["rap_to_transcript_file"])
    output:
        "{raw_enrich_dir}/mapping/{network}/msu-to-transcript-id.pickle"
    shell:
        "python scripts/enrichment_analysis/util/msu-to-transcript-id.py " \
        "{input.all_transcript} {input.all_na_transcript} {input.rap_to_msu} {input.rap_to_transcript} " \
        "{wildcards.raw_enrich_dir}/mapping/{wildcards.network}"

rule transcript_to_msu_id:
    input:
        "{0}/mapping/{{network}}/msu-to-transcript-id.pickle".format(config["raw_enrich_dir"])
    output:
        "{gene_id_mapping_dir}/mapping/{network}/transcript-to-msu-id.pickle"
    shell:
        "python scripts/enrichment_analysis/util/transcript-to-msu-id.py " \
        "{input} {wildcards.gene_id_mapping_dir}/mapping/{wildcards.network}"

rule convert_all_genes_from_msu:
    input:
        all_genes = "{raw_enrich_dir}/all_genes/{network}/MSU/all-genes.txt",
        mapping_file="{0}/msu_mapping/msu_to_{{target_format}}.pickle".format(config["gene_id_mapping_dir"])
    output:
        "{raw_enrich_dir}/all_genes/{network}/{target_format}/{target_file}.tsv"
    shell:
        "python scripts/enrichment_analysis/util/file-convert-msu.py " \
        "{input.all_genes} {input.mapping_file} " \
        "{wildcards.raw_enrich_dir}/all_genes/{wildcards.network} {wildcards.target_format}"

rule convert_modules_from_uniprot:
    input:
        module_file = "{network_mod_dir}/{network}/{algo}/{param}/MSU/{algo}-module-list.tsv",
        mapping_file="{0}/msu_mapping/uniprot_to_msu.pickle".format(config["gene_id_mapping_dir"])
    output:
        "{network_mod_dir}/{network}/{algo}/{param}/MSU/{algo}-module-list.tsv"
    shell:
        "python scripts/ppi_util/convert_mod_prot_to_gene.py " \
        "{input.module_file} {input.mapping_file} " \
        "{wildcards.network_mod_dir}/{wildcards.network}/{wildcards.algo}/{wildcards.param}/MSU "

rule convert_modules_from_msu:
    input:
        module_file = "{network_mod_dir}/{network}/{algo}/{param}/MSU/{algo}-module-list.tsv",
        mapping_file="{0}/msu_mapping/msu_to_rap.pickle".format(config["gene_id_mapping_dir"])
    output:
        "{network_mod_dir}/{network}/{algo}/{param}/rap/{algo}-module-list.tsv"
    shell:
        "python scripts/enrichment_analysis/util/file-convert-msu.py " \
        "{input.module_file} {input.mapping_file} " \
        "{wildcards.network_mod_dir}/{wildcards.network}/{wildcards.algo}/{wildcards.param} " \
        "rap"