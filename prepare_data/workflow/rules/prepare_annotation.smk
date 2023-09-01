def get_annot_url(wildcards):
    return config["annotation_links"][wildcards.other_ref]

rule download_annotation:
    output:
        filename = "{0}/annotations/{{other_ref}}/{{other_ref}}.gff.gz".format(config["processed_data_dir"])
    params:
        url = get_annot_url
    shell:
        "wget {params.url} -O {output.filename}"

rule build_annot_gff_db:
    input:
        gff="{0}/annotations/{{other_ref}}/{{other_ref}}.gff.gz".format(config["processed_data_dir"])
    output:
        gff_db = "{0}/annotations/{{other_ref}}/{{other_ref}}.gff.db".format(config["processed_data_dir"])
    conda:
        "../env/gffutils.yaml"
    shell:
        "python scripts/gff_db.py {input.gff} {output.gff_db}"