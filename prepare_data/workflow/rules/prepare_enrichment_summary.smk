# Resolve Network Dependency
for key, path in config['networks'].items():
    config["networks"][key] = path.format(network_dir=config["network_dir"])

rule prep_for_summary_table:
    input:
        expand(
            "{0}/{{network}}/MSU_to_modules/{{algo}}/{{value}}/genes_to_modules.pickle".format(config["network_mod_dir"]),
            network = config["networks"].keys(),
            algo = "clusterone",
            value = config["clusterone_min_density"].keys()
        ),
        expand(
            "{0}/{{network}}/MSU_to_modules/{{algo}}/{{value}}/genes_to_modules.pickle".format(config["network_mod_dir"]),
            network = config["networks"].keys(),
            algo = "fox",
            value = config["wcc_threshold"].keys()
        )

rule map_genes_to_modules:
    input:
        mod_list="{0}/{{network}}/{{algo}}/{{value}}/MSU/{{algo}}-module-list.tsv".format(config["network_mod_dir"])
    output:
        "{0}/{{network}}/MSU_to_modules/{{algo}}/{{value}}/genes_to_modules.pickle".format(config["network_mod_dir"])
    shell:
        "python scripts/network_util/map-genes-to-modules.py " \
        "{{input.mod_list}} " \
        "{0}/{{wildcards.network}}/MSU_to_modules/{{wildcards.algo}}/{{wildcards.value}} ".format(config["network_mod_dir"])