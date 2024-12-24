# Resolve Network Dependency
for key, path in config['networks'].items():
    config["networks"][key] = path.format(network_dir=config["network_dir"])

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
        )

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