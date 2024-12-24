import os

# Resolve Network Dependency
for key, path in config['networks'].items():
    config["networks"][key] = path.format(network_dir=config["network_dir"])

def get_module_count(network, algo):
    ## TODO: Modify to retrieve first value in list of params:
    if algo == "clusterone":
        value = 30
    else:
        value = 1

    file_path = "{0}/temp/{1}/{2}/{3}/module_count.txt".format(
        config["raw_enrich_dir"],
        network,
        algo,
        value
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

def get_entries(network, algo):
    return expand(
        "{0}/{1}/output/{2}/{{value}}/ontology_enrichment/go/results/go-df-{{index}}.tsv".format(config["app_enrich_dir"], network, algo),
        value = get_params_of_algo(algo),
        index = range(1, get_module_count(network, algo) + 1)
    )

def get_all_GO_results():
    result = []
    for network in config["networks"].keys():
        for algo in ["clusterone", "fox"]:
            result.extend(get_entries(network, algo))
    return result

result = get_all_GO_results()
print(result)
print(len(result))


# TODO:
# Find a way to integrate network and index (dynamically)
# Revise count_module to refer to only the FIRST PARAM (arbitrary) since its all the same anyways
# Make the FIRST PARAM global (or in config)

rule execute_enrichment:
    input:
        expand(
            "{0}/temp/{{network}}/{1}/{{value}}/module_count.txt".format(config["raw_enrich_dir"], "clusterone"),
            network = config["networks"].keys(),
            value = config["clusterone_min_density"].keys()
        ),
        expand(
            "{0}/temp/{{network}}/{1}/{{value}}/module_count.txt".format(config["raw_enrich_dir"], "fox"),
            network = config["networks"].keys(),
            value = config["wcc_threshold"].keys()
        ),
        # dynamic(go_result_list)

rule count_modules:
    input:
        mod_list="{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"])
    output:
        count_file="{0}/temp/{{network}}/{{algo}}/{{value}}/module_count.txt".format(config["raw_enrich_dir"])
    run:
        with open(input.mod_list) as f:
            line_count = sum(1 for line in f)
        with open(output.count_file, "w") as f:
            f.write(str(line_count))

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
        "Rscript --vanilla enrichment_analysis/ontology_enrichment/go-enrichment.r " \
        "-g {input.mod_list} -i {wildcards.index} -b {input.all_genes} -m {input.go_annotations} " \
        "-o {params.output_dir}"

# rule gene_ontology:
#     input:
#         mod_list="{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"]),
#         all_genes="{0}/all_genes/{{network}}/MSU/all-genes.txt".format(config["raw_enrich_dir"]),
#         go_annotations="{0}/go/{{network}}/go-annotations.tsv".format(config["raw_enrich_dir"]),
#         mod_count="{0}/temp/{{network}}/{{algo}}/{{value}}/module_count.txt".format(config["raw_enrich_dir"])
#     output:
#         "{0}/{{network}}/output/{{algo}}/{{value}}/ontology_enrichment/go/results/go-df-{{index}}.tsv".format(config["app_enrich_dir"])
#     params:
#         output_dir="{0}/{{network}}/output/{{algo}}/{{value}}/ontology_enrichment/go".format(config["app_enrich_dir"])
#     run:
#         with open(input.mod_count) as f:
#             module_count = int(f.read().strip())

#         for index in range(1, module_count + 1):
#             shell(
#                 """
#                 Rscript --vanilla enrichment_analysis/ontology_enrichment/go-enrichment.r \
#                 -g {input.mod_list} -i {index} -b {input.all_genes} -m {input.go_annotations} \
#                 -o {params.output_dir}
#                 """
#             )