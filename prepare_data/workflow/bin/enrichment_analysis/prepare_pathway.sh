# Generate pickle dicts for MSU to transcript id conversion
Rscript --vanilla scripts/enrichment_analysis/util/ricegeneid-msu-to-transcript-id.r \
    -g ../../static/raw_data/enrichment_analysis/all_genes/$1/MSU/all-genes.txt \
    -o ../../static/raw_data/enrichment_analysis/temp/$1

python scripts/enrichment_analysis/util/msu-to-transcript-id.py \
    ../../static/raw_data/enrichment_analysis/temp/$1/all-transcript-id.txt \
    ../../static/raw_data/enrichment_analysis/temp/$1/all-na-transcript-id.txt \
    ../../static/raw_data/enrichment_analysis/rap_db/RAP-MSU_2023-03-15.txt \
    ../../static/raw_data/enrichment_analysis/rap_db/IRGSP-1.0_representative_annotation_2023-03-15.tsv \
    ../../static/raw_data/enrichment_analysis/mapping/$1

python scripts/enrichment_analysis/util/transcript-to-msu-id.py \
    ../../static/raw_data/enrichment_analysis/mapping/$1/msu-to-transcript-id.pickle \
    ../../static/app_data/gene_id_mapping/msu_mapping/$1

# ALL PROTEINS
# Convert Proteins to Genes
# TODO: Add portion to execute prepare_uniprot_to_gene.py
# TODO: Add logic in script that will prompt an error if it already exists in dir

python scripts/ppi_util/convert_all_prot_to_gene.py \
    ../../static/raw_data/ppi/all_proteins/$1/uniprot/all-proteins.txt \
    ../../static/app_data/gene_id_mapping/msu_mapping/uniprot_to_msu.pickle \
    ../../static/raw_data/enrichment_analysis/all_genes/$1/MSU/

# Convert MSU Genes to Transcript (Universe)
python scripts/enrichment_analysis/util/file-convert-msu.py \
    ../../static/raw_data/enrichment_analysis/all_genes/$1/MSU/all-genes.txt \
    ../../static/raw_data/enrichment_analysis/mapping/$1/msu-to-transcript-id.pickle \
    ../../static/raw_data/enrichment_analysis/all_genes/$1 \
    transcript --skip_no_matches

# MODULES
# Convert Protein Modules to Genes
# Convert MSU Genes to Transcript (Modules)