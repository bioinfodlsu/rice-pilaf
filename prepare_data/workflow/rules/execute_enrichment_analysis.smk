import os

ENRICHMENT_CODES = {
    "gene_ontology": "GO",
    "trait_ontology": "TO",
    "plant_ontology": "PO",
    "overrep_pathway": "ORA",
    "topology_pathway_pe": "PE",
    "topology_pathway_spia": "SPIA"
}

ONTOLOGY_ANALYSIS = [
    ENRICHMENT_CODES["gene_ontology"], 
    ENRICHMENT_CODES["trait_ontology"],
    ENRICHMENT_CODES["plant_ontology"]
]

PATHWAY_ANALYSIS = [
    ENRICHMENT_CODES["overrep_pathway"], 
    ENRICHMENT_CODES["topology_pathway_pe"],
    ENRICHMENT_CODES["topology_pathway_spia"]
]

# Resolve Network Dependency
for key, path in config['networks'].items():
    config["networks"][key] = path.format(network_dir=config["network_dir"])

def get_module_count(network, algo):
    file_path = "{0}/temp/{1}/{2}/{3}/module_count.txt".format(
        config["raw_enrich_dir"],
        network,
        algo,
        config["first_param_list"][algo]
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"""
            The file {file_path} is not found. 
            Please execute data_prep_for_enrichment_analysis rule first.
            """)

    with open(file_path) as f:
        module_count = int(f.read().strip())
    return module_count

def get_params_of_algo(algo):
    if algo == "clusterone":
        return config["clusterone_min_density"].keys()
    else:
        return config["wcc_threshold"].keys()

def get_grouping_label_of_analysis(analysis):
    if analysis in ONTOLOGY_ANALYSIS:
        return "ontology_enrichment"
    else:
        return "pathway_enrichment"

def get_entries(network, algo, analysis):
    grouping = get_grouping_label_of_analysis(analysis)
    analysis_code = analysis.lower()

    return expand(
        "{dir}/{network}/output/{algo}/{{value}}/{grouping_name}/{analysis_code}/results/{analysis_code}-df-{{index}}.tsv".format(
            dir=config["app_enrich_dir"], 
            network=network, 
            algo=algo,
            grouping_name=grouping,
            analysis_code=analysis_code
            ),
        value = get_params_of_algo(algo),
        index = range(1, get_module_count(network, algo) + 1)
    )

def get_all_results(algo, analysis):
    result = []
    for network in config["networks"].keys():
        result.extend(get_entries(network, algo, analysis))
    return result


# RULES
rule execute_enrichment:
    input:
        #CLUSTERONE
        get_all_results("clusterone", ENRICHMENT_CODES["gene_ontology"]),
        get_all_results("clusterone", ENRICHMENT_CODES["trait_ontology"]),
        get_all_results("clusterone", ENRICHMENT_CODES["plant_ontology"]),
        get_all_results("clusterone", ENRICHMENT_CODES["topology_pathway_pe"]),
        get_all_results("clusterone", ENRICHMENT_CODES["topology_pathway_spia"]),
        #FOX
        get_all_results("fox", ENRICHMENT_CODES["gene_ontology"]),
        get_all_results("fox", ENRICHMENT_CODES["trait_ontology"]),
        get_all_results("fox", ENRICHMENT_CODES["plant_ontology"]),
        get_all_results("fox", ENRICHMENT_CODES["topology_pathway_pe"]),
        get_all_results("fox", ENRICHMENT_CODES["topology_pathway_spia"])

# ORA separated as it requires lower number of cores to avoid spamming the API
rule execute_ora_enrichment:
    input:
        get_all_results("clusterone", ENRICHMENT_CODES["overrep_pathway"]),
        get_all_results("fox", ENRICHMENT_CODES["overrep_pathway"]),

rule gene_ontology:
    input:
        mod_list="{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        all_genes="{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"]),
        go_annotations="{0}/go/{{network}}/go-annotations.tsv".format(config["raw_enrich_dir"])
    output:
        "{0}/{{network}}/output/{{algo}}/{{value}}/ontology_enrichment/go/results/go-df-{{index}}.tsv".format(config["app_enrich_dir"])
    params:
        output_dir="{0}/{{network}}/output/{{algo}}/{{value}}/ontology_enrichment/go".format(config["app_enrich_dir"])
    shell:
        "Rscript --vanilla scripts/enrichment_analysis/ontology_enrichment/go-enrichment.r " \
        "-g {input.mod_list} -i {wildcards.index} -b {input.all_genes} -m {input.go_annotations} " \
        "-o {params.output_dir}"

rule trait_ontology:
    input:
        mod_list="{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        all_genes="{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"]),
        to_annotations="{0}/to/{{network}}/to-annotations.tsv".format(config["raw_enrich_dir"]),
        to_id_to_name="{0}/to/{{network}}/to-id-to-name.tsv".format(config["raw_enrich_dir"])
    output:
        "{0}/{{network}}/output/{{algo}}/{{value}}/ontology_enrichment/to/results/to-df-{{index}}.tsv".format(config["app_enrich_dir"])
    params:
        output_dir="{0}/{{network}}/output/{{algo}}/{{value}}/ontology_enrichment/to".format(config["app_enrich_dir"])
    shell:
        "Rscript --vanilla scripts/enrichment_analysis/ontology_enrichment/to-enrichment.r " \
        "-g {input.mod_list} -i {wildcards.index} -b {input.all_genes} " \
        "-m {input.to_annotations} -t {input.to_id_to_name} " \
        "-o {params.output_dir}"

rule plant_ontology:
    input:
        mod_list="{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        all_genes="{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"]),
        po_annotations="{0}/po/{{network}}/po-annotations.tsv".format(config["raw_enrich_dir"]),
        po_id_to_name="{0}/po/{{network}}/po-id-to-name.tsv".format(config["raw_enrich_dir"])
    output:
        "{0}/{{network}}/output/{{algo}}/{{value}}/ontology_enrichment/po/results/po-df-{{index}}.tsv".format(config["app_enrich_dir"])
    params:
        output_dir="{0}/{{network}}/output/{{algo}}/{{value}}/ontology_enrichment/po".format(config["app_enrich_dir"])
    shell:
        "Rscript --vanilla scripts/enrichment_analysis/ontology_enrichment/po-enrichment.r " \
        "-g {input.mod_list} -i {wildcards.index} -b {input.all_genes} " \
        "-m {input.po_annotations} -t {input.po_id_to_name} " \
        "-o {params.output_dir}"

rule overrep_pathway:
    input:
        mod_list="{0}/{{network}}/{{algo}}/{{value}}/rap/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        all_genes="{0}/all_genes/{{network}}/rap/all-genes.tsv".format(config["raw_enrich_dir"])
    output:
        "{0}/{{network}}/output/{{algo}}/{{value}}/pathway_enrichment/ora/results/ora-df-{{index}}.tsv".format(config["app_enrich_dir"])
    params:
        output_dir="{0}/{{network}}/output/{{algo}}/{{value}}/pathway_enrichment/ora".format(config["app_enrich_dir"])
    shell:
        "Rscript --vanilla scripts/enrichment_analysis/pathway_enrichment/ora-enrichment.r " \
        "-g {input.mod_list} -i {wildcards.index} -b {input.all_genes} " \
        "-o {params.output_dir}"

rule topology_pathway_pe:
    input:
        mod_list="{0}/{{network}}/{{algo}}/{{value}}/rap/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        all_genes="{0}/all_genes/{{network}}/rap/all-genes.tsv".format(config["raw_enrich_dir"])
    output:
        "{0}/{{network}}/output/{{algo}}/{{value}}/pathway_enrichment/pe/results/pe-df-{{index}}.tsv".format(config["app_enrich_dir"])
    params:
        output_dir="{0}/{{network}}/output/{{algo}}/{{value}}/pathway_enrichment/pe".format(config["app_enrich_dir"])
    shell:
        "Rscript --vanilla scripts/enrichment_analysis/pathway_enrichment/pe-enrichment.r " \
        "-g {input.mod_list} -i {wildcards.index} -b {input.all_genes} " \
        "-o {params.output_dir}"

rule topology_pathway_spia:
    input:
        mod_list="{0}/{{network}}/{{algo}}/{{value}}/transcript/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
        all_genes="{0}/all_genes/{{network}}/transcript/all-genes.tsv".format(config["raw_enrich_dir"])
    output:
        "{0}/{{network}}/output/{{algo}}/{{value}}/pathway_enrichment/spia/results/spia-df-{{index}}.tsv".format(config["app_enrich_dir"])
    params:
        output_dir="{0}/{{network}}/output/{{algo}}/{{value}}/pathway_enrichment/spia".format(config["app_enrich_dir"]),
        spia_path="{0}/kegg_dosa/SPIA".format(config["raw_enrich_dir"])
    shell:
        "Rscript --vanilla scripts/enrichment_analysis/pathway_enrichment/spia-enrichment.r " \
        "-g {input.mod_list} -i {wildcards.index} -b {input.all_genes} " \
        "-s {params.spia_path} -o {params.output_dir}"
