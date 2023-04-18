import gffutils
db = gffutils.create_db(snakemake.input[0], snakemake.output[0],merge_strategy="warning")