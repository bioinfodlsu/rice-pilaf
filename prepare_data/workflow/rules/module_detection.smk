# Resolve Network Dependency
for key, path in config['networks'].items():
    config["networks"][key] = path.format(network_dir=config["network_dir"])

rule module_detect_clusterone:
    input:
        expand(
            "{mod_detect_dir}/{network}/temp/clusterone/clusterone-results-{density}.csv",
            density = config['clusterone_min_density'].keys(),
            mod_detect_dir = config['mod_detect_dir'],
            network = config["networks"].keys()
            ),
        expand(
            "{network_mod_dir}/{network}/MSU/clusterone/{density}/clusterone-module-list.tsv",
            density = config['clusterone_min_density'].keys(),
            network = config['networks'].keys(),
            network_mod_dir = config['network_mod_dir']
        )

rule execute_clusterone:
    input:
        lambda wildcards: config["networks"][wildcards.network]
    output:
        "{mod_detect_dir}/{network}/temp/clusterone/clusterone-results-{density}.csv"
    params:
        value = lambda wildcards: config['clusterone_min_density'][int(wildcards.density)],
        clusterone_jar_path = config['clusterone_jar_path']
    shell:
        "java -jar {params.clusterone_jar_path} " \
        "--output-format csv " \
        "--min-density {params.value} " \
        "{input} > {output}"
    
rule get_mod_clusterone:
    input:
        "{0}/{{network}}/temp/clusterone/clusterone-results-{{density}}.csv".format(config['mod_detect_dir'])
    output:
        "{network_mod_dir}/{network}/MSU/clusterone/{density}/clusterone-module-list.tsv"
    params:
        get_mod_from_clusterone_path = config['get_mod_from_clusterone_path']
    shell:
        "python {params.get_mod_from_clusterone_path} {input} " \
        "{wildcards.network_mod_dir}/{wildcards.network}/MSU/clusterone/{wildcards.density}"

rule module_detect_fox:
    input:
        expand(
            "{mod_detect_dir}/{network}/temp/fox/fox-int-module-list-{wcc}.txt",
            mod_detect_dir = config['mod_detect_dir'],
            network = config['networks'].keys(),
            wcc = config['wcc_threshold'].keys()
        )

rule execute_fox:
    input:
        "{mod_detect_dir}/{network}/mapping/int-edge-list.txt"
    output:
        "{mod_detect_dir}/{network}/temp/fox/fox-int-module-list-{wcc}.txt"
    params:
        wcc_val = lambda wildcards: config['wcc_threshold'][int(wildcards.wcc)]
    shell:
        "scripts/module_detection/execute_lazyfox.sh {input} {params.wcc_val} {output}"