import os

import pandas as pd

from ..constants import Constants

const = Constants()

PATHWAY_TABS = ['Gene Ontology', 'Trait Ontology', 'Plant Ontology',
                'Pathways (Overrepresentation)', 'Pathway-Express', 'SPIA']


def convert_genomic_intervals_to_filename(genomic_intervals):
    return genomic_intervals.replace(":", "_").replace(";", "_")


def write_genes_to_file(genes, genomic_intervals):
    subdirectory = convert_genomic_intervals_to_filename(genomic_intervals)

    if not os.path.exists(f'{const.IMPLICATED_GENES}/{subdirectory}'):
        os.makedirs(f'{const.IMPLICATED_GENES}/{subdirectory}')

        with open(f'{const.IMPLICATED_GENES}/{subdirectory}/genes.txt', 'w') as f:
            f.write('\t'.join(genes))
            f.write('\n')

    return subdirectory


def fetch_enriched_modules(output_dir):
    modules = []
    with open(f'{output_dir}/enriched_modules/ora-df.tsv') as modules_file:
        for line in modules_file:
            line = line.rstrip()
            line = line.split('\t')

            if line[0] != 'ID':
                modules.append('Module ' + line[0])

    return modules


def do_module_enrichment_analysis(gene_ids, genomic_intervals):
    genes = list(set(gene_ids))
    subdirectory = write_genes_to_file(genes, genomic_intervals)

    OUTPUT_DIR = f'{const.IMPLICATED_GENES}/{subdirectory}'
    if not os.path.exists(f'{OUTPUT_DIR}/enriched_modules'):
        INPUT_GENES = f'{const.IMPLICATED_GENES}/{subdirectory}/genes.txt'
        BACKGROUND_GENES = f'{const.NETWORKS}/OS-CX.txt'
        MODULE_TO_GENE_MAPPING = f'{const.NETWORKS_DISPLAY_CLUSTERONE}/modules-to-genes.tsv'

        COMMAND = f'Rscript --vanilla {const.ORA_ENRICHMENT_ANALYSIS_PROGRAM} -g {INPUT_GENES} -b {BACKGROUND_GENES} -m {MODULE_TO_GENE_MAPPING} -o {OUTPUT_DIR}'
        os.system(COMMAND)

    return fetch_enriched_modules(OUTPUT_DIR)


def convert_to_df(active_tab, module_idx):
    results = None

    active_tab = active_tab.split('-')[1]
    if PATHWAY_TABS[int(active_tab)] == 'Gene Ontology':
        results = pd.read_csv(
            f'{const.ENRICHMENT_ANALYSIS_OUTPUT_ONTOLOGY}/go/results/go-df-{module_idx}.tsv',
            delimiter='\t'
        )
    elif PATHWAY_TABS[int(active_tab)] == 'Trait Ontology':
        results = pd.read_csv(
            f'{const.ENRICHMENT_ANALYSIS_OUTPUT_ONTOLOGY}/to/results/to-df-{module_idx}.tsv',
            delimiter='\t'
        )
    elif PATHWAY_TABS[int(active_tab)] == 'Plant Ontology':
        results = pd.read_csv(
            f'{const.ENRICHMENT_ANALYSIS_OUTPUT_ONTOLOGY}/po/results/po-df-{module_idx}.tsv',
            delimiter='\t'
        )
    elif PATHWAY_TABS[int(active_tab)] == 'Pathways (Overrepresentation)':
        results = pd.read_csv(
            f'{const.ENRICHMENT_ANALYSIS_OUTPUT_PATHWAY}/ora/results/ora-df-{module_idx}.tsv',
            delimiter='\t'
        )
    elif PATHWAY_TABS[int(active_tab)] == 'Pathway-Express':
        results = pd.read_csv(
            f'{const.ENRICHMENT_ANALYSIS_OUTPUT_PATHWAY}/pe/results/pe-df-{module_idx}.tsv',
            delimiter='\t'
        )
    elif PATHWAY_TABS[int(active_tab)] == 'SPIA':
        results = pd.read_csv(
            f'{const.ENRICHMENT_ANALYSIS_OUTPUT_PATHWAY}/spia/results/spia-df-{module_idx}.tsv',
            delimiter='\t'
        )

    return results
