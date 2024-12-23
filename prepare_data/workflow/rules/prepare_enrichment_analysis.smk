# Resolve Network Dependency
for key, path in config['networks'].items():
    config["networks"][key] = path.format(network_dir=config["network_dir"])

rule data_prep_for_enrichment_analysis:
    input:
        # GENE EXTRACTION RULES
        # Prepare PPI-specific conversion
        expand(
            "{0}/all_proteins/{{network}}/uniprot/all-proteins.txt".format(config["ppi_dir"]),
            network = config["networks"].keys()
        ),
        "{0}/msu_mapping/uniprot_to_msu.pickle".format(config["gene_id_mapping_dir"]),
        expand(
            "{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"]),
            network = config["networks"].keys()
        ),
        # PATHWAY ENRICHMENT RULES
        # Prepare Pickled Dicts for MSU Conversion 
        expand(
            [
                "{0}/temp/{{network}}/all-transcript-id.txt".format(config["raw_enrich_dir"]),
                "{0}/temp/{{network}}/all-na-transcript-id.txt".format(config["raw_enrich_dir"])
            ],
            network = config["networks"].keys()
        ),
        expand(
            "{0}/mapping/{{network}}/msu-to-transcript-id.pickle".format(config["raw_enrich_dir"]),
            network = config["networks"].keys(),
        ),
        expand(
            "{0}/msu_mapping/{{network}}/transcript-to-msu-id.pickle".format(config["gene_id_mapping_dir"]),
            network = config["networks"].keys()
        ),
        # CONVERSION RULES
        # Converting all-genes to other formats
        expand(
            "{0}/all_genes/{{network}}/transcript/all-genes.tsv".format(config["raw_enrich_dir"]),
            network = config["networks"].keys()
        ),
        expand(
            "{0}/all_genes/{{network}}/rap/all-genes.tsv".format(config["raw_enrich_dir"]),
            network = config["networks"].keys()
        ),

        # Converting modules per algo per param to other formats
        expand(
            "{0}/{{network}}/{1}/{{value}}/{{id_formats}}/{1}-module-list.tsv".format(config["network_mod_dir"], "clusterone"),
            network = config["networks"].keys(),
            value = config["clusterone_min_density"].keys(),
            id_formats = ["MSU", "rap", "transcript"]
        ),
        expand(
            "{0}/{{network}}/{1}/{{value}}/{{id_formats}}/{1}-module-list.tsv".format(config["network_mod_dir"], "fox"),
            network = config["networks"].keys(),
            value = config["wcc_threshold"].keys(),
            id_formats = ["MSU", "rap", "transcript"]
        )


# GENE EXTRACTION Rules
rule get_proteins_from_network:
    input:
        lambda wildcards: config['networks'][wildcards.network]
    output:
        "{0}/all_proteins/{{network}}/uniprot/all-proteins.txt".format(config["ppi_dir"])
    shell:
        "python scripts/network_util/get-nodes-from-network.py " \
        "{{input}} {0}/all_proteins/{{wildcards.network}}/uniprot " \
        "--name all-proteins".format(config["ppi_dir"])

rule prepare_uniprot_to_gene:
    input:
        "{0}/Nb/Nb_gene_descriptions.csv".format(config["gene_desc_dir"])
    output:
        "{0}/msu_mapping/uniprot_to_msu.pickle".format(config["gene_id_mapping_dir"])
    shell:
        "python scripts/ppi_util/prepare_uniprot_to_gene.py " \
        "{{input}} {0}/msu_mapping uniprot_to_msu".format(config["gene_id_mapping_dir"])

rule convert_all_proteins_to_genes:
    input:
        proteins_file="{0}/all_proteins/{{network}}/uniprot/all-proteins.txt".format(config["ppi_dir"]),
        protein_to_gene_mapping="{0}/msu_mapping/uniprot_to_msu.pickle".format(config["gene_id_mapping_dir"])
    output:
        "{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"])
    shell:
        "python scripts/ppi_util/convert_all_prot_to_gene.py " \
        "{{input.proteins_file}} {{input.protein_to_gene_mapping}} " \
        "{0}/all_genes/{{wildcards.network}}/MSU".format(config["raw_enrich_dir"])


# PATHWAY ENRICHMENT RULES
rule ricegeneid_msu_to_transcript_id:
    input:
        "{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"])
    output:
        "{0}/temp/{{network}}/all-transcript-id.txt".format(config["raw_enrich_dir"]),
        "{0}/temp/{{network}}/all-na-transcript-id.txt".format(config["raw_enrich_dir"])
    shell:
        "Rscript --vanilla scripts/enrichment_analysis/util/ricegeneid-msu-to-transcript-id.r " \
        "-g {{input}} " \
        "-o {0}/temp/{{wildcards.network}}".format(config["raw_enrich_dir"])

rule msu_to_transcript_id:
    input:
        all_transcript="{0}/temp/{{network}}/all-transcript-id.txt".format(config["raw_enrich_dir"]),
        all_na_transcript="{0}/temp/{{network}}/all-na-transcript-id.txt".format(config["raw_enrich_dir"]),
        rap_to_msu="{0}/rap_db/{1}".format(config["raw_enrich_dir"], config["rap_to_msu_file"]),
        rap_to_transcript="{0}/rap_db/{1}".format(config["raw_enrich_dir"], config["rap_to_transcript_file"])
    output:
        "{0}/mapping/{{network}}/msu-to-transcript-id.pickle".format(config["raw_enrich_dir"])
    shell:
        "python scripts/enrichment_analysis/util/msu-to-transcript-id.py " \
        "{{input.all_transcript}} {{input.all_na_transcript}} {{input.rap_to_msu}} {{input.rap_to_transcript}} " \
        "{0}/mapping/{{wildcards.network}}".format(config["raw_enrich_dir"])

rule transcript_to_msu_id:
    input:
        "{0}/mapping/{{network}}/msu-to-transcript-id.pickle".format(config["raw_enrich_dir"])
    output:
        "{0}/msu_mapping/{{network}}/transcript-to-msu-id.pickle".format(config["gene_id_mapping_dir"])
    shell:
        "python scripts/enrichment_analysis/util/transcript-to-msu-id.py " \
        "{{input}} {0}/msu_mapping/{{wildcards.network}}".format(config["gene_id_mapping_dir"])


# CONVERSION RULES
# Converting MSU genes to Other Formats (i.e. transcript, rap)
# Converting All Genes
rule convert_all_genes_msu_to_transcript:
    input:
        all_genes = "{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"]),
        mapping_file="{0}/mapping/{{network}}/msu-to-transcript-id.pickle".format(config["raw_enrich_dir"])
    output:
        "{0}/all_genes/{{network}}/transcript/all-genes.tsv".format(config["raw_enrich_dir"])
    shell:
        "python scripts/enrichment_analysis/util/file-convert-msu.py " \
        "{{input.all_genes}} {{input.mapping_file}} " \
        "{0}/all_genes/{{wildcards.network}} transcript".format(config["raw_enrich_dir"])

rule convert_all_genes_msu_to_rap:
    input:
        all_genes = "{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"]),
        mapping_file="{0}/msu_mapping/msu_to_rap.pickle".format(config["gene_id_mapping_dir"])
    output:
        "{0}/all_genes/{{network}}/rap/all-genes.tsv".format(config["raw_enrich_dir"])
    shell:
        "python scripts/enrichment_analysis/util/file-convert-msu.py " \
        "{{input.all_genes}} {{input.mapping_file}} " \
        "{0}/all_genes/{{wildcards.network}} rap".format(config["raw_enrich_dir"])

# Converting Modules
rule convert_modules_uniprot_to_msu:
    input:
        module_file = "{0}/{{network}}/{{algo}}/{{value}}/uniprot/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        mapping_file="{0}/msu_mapping/uniprot_to_msu.pickle".format(config["gene_id_mapping_dir"])
    output:
        "{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"])
    shell:
        "python scripts/ppi_util/convert_mod_prot_to_gene.py " \
        "{{input.module_file}} {{input.mapping_file}} " \
        "{0}/{{wildcards.network}}/{{wildcards.algo}}/{{wildcards.value}}/MSU ".format(config["network_mod_dir"])

rule convert_modules_msu_to_rap:
    input:
        module_file = "{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        mapping_file="{0}/msu_mapping/msu_to_rap.pickle".format(config["gene_id_mapping_dir"])
    output:
        "{0}/{{network}}/{{algo}}/{{value}}/rap/{{algo}}-module-list.tsv".format(config["network_mod_dir"])
    shell:
        "python scripts/ppi_util/convert_mod_prot_to_gene.py " \
        "{{input.module_file}} {{input.mapping_file}} " \
        "{0}/{{wildcards.network}}/{{wildcards.algo}}/{{wildcards.value}}/rap ".format(config["network_mod_dir"])

rule convert_modules_msu_to_transcript:
    input:
        module_file = "{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        mapping_file="{0}/mapping/{{network}}/msu-to-transcript-id.pickle".format(config["raw_enrich_dir"])
    output:
        "{0}/{{network}}/{{algo}}/{{value}}/transcript/{{algo}}-module-list.tsv".format(config["network_mod_dir"])
    shell:
        "python scripts/ppi_util/convert_mod_prot_to_gene.py " \
        "{{input.module_file}} {{input.mapping_file}} " \
        "{0}/{{wildcards.network}}/{{wildcards.algo}}/{{wildcards.value}}/transcript ".format(config["network_mod_dir"])