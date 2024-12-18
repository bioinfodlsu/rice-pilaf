rule mod_detect:
    input:
        expand(
            "{clusterone_output}/clusterone-results-{density}.csv", 
            density = config['clusterone_min_density'].keys(), 
            clusterone_output = f"{config['mod_detect_dir']}/STRING-Physical/temp/clusterone"
            )

rule clusterone:
    input:
        f"{config['network_dir']}/STRING-Physical.txt"
    output:
        "{clusterone_output}/clusterone-results-{density}.csv"
    params:
        value = lambda wildcards: config['clusterone_min_density'][int(wildcards.density)],
        clusterone_jar_path = config['clusterone_jar_path']
    shell:
        "java -jar {params.clusterone_jar_path} " \
        "--output-format csv " \
        "--min-density {params.value} " \
        "{input} > {output}"