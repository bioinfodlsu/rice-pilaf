import os

import pandas as pd

from ..constants import Constants

const = Constants()

PATHWAY_TABS = [('Gene Ontology', 'ontology_enrichment/go'),
                ('Trait Ontology', 'ontology_enrichment/to'),
                ('Plant Ontology', 'ontology_enrichment/po'),
                ('Pathways (Overrepresentation)', 'pathway_enrichment/ora'),
                ('Pathway-Express', 'pathway_enrichment/pe'),
                ('SPIA', 'pathway_enrichment/spia')]

ALGOS_MULT = {'clusterone': '100',
              'coach': '1000',
              'demon': '100',
              'fox': '100'}


def get_dir_for_parameter(algo, parameters):
    return int(float(parameters) * int(ALGOS_MULT[algo]))


def convert_genomic_intervals_to_filename(genomic_intervals):
    return genomic_intervals.replace(":", "_").replace(";", "_")


def write_genes_to_file(genes, genomic_intervals, algo, parameters):
    subdirectory = f'{convert_genomic_intervals_to_filename(genomic_intervals)}/{algo}/{parameters}'

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


def do_module_enrichment_analysis(gene_ids, genomic_intervals, algo, parameters):
    # print(algo)
    # print(parameters)

    genes = list(set(gene_ids))
    subdirectory = write_genes_to_file(
        genes, genomic_intervals, algo, parameters)

    OUTPUT_DIR = f'{const.IMPLICATED_GENES}/{subdirectory}'
    if not os.path.exists(f'{OUTPUT_DIR}/enriched_modules'):
        INPUT_GENES = f'{const.IMPLICATED_GENES}/{subdirectory}/genes.txt'
        BACKGROUND_GENES = f'{const.NETWORKS_DISPLAY_OS_CX}/all-genes.txt'
        MODULE_TO_GENE_MAPPING = f'{const.NETWORKS_DISPLAY_OS_CX}/{algo}/modules_to_genes/{parameters}/modules-to-genes.tsv'

        COMMAND = f'Rscript --vanilla {const.ORA_ENRICHMENT_ANALYSIS_PROGRAM} -g {INPUT_GENES} -b {BACKGROUND_GENES} -m {MODULE_TO_GENE_MAPPING} -o {OUTPUT_DIR}'
        os.system(COMMAND)

    return fetch_enriched_modules(OUTPUT_DIR)


def convert_to_df(active_tab, module_idx, algo, parameters):
    active_tab = active_tab.split('-')[1]
    dir = PATHWAY_TABS[int(active_tab)][1]
    enrichment_type = dir.split('/')[-1]

    file = f'{const.ENRICHMENT_ANALYSIS_OUTPUT}/{algo}/{parameters}/{dir}/results/{enrichment_type}-df-{module_idx}.tsv'

    result = pd.read_csv(file, delimiter='\t')
    if algo == 'go':
        result = result[['ID', 'Description',
                         'GeneRatio', 'BgRatio', 'pvalue', 'p.adjust', 'geneID']]

    return result
