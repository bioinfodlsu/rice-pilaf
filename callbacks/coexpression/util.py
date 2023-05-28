from ..constants import Constants
import os
import pickle

import pandas as pd
import networkx as nx

const = Constants()

PATHWAY_TABS = [('Gene Ontology', 'ontology_enrichment/go'),
                ('Trait Ontology', 'ontology_enrichment/to'),
                ('Plant Ontology', 'ontology_enrichment/po'),
                ('Pathways (Overrepresentation)', 'pathway_enrichment/ora'),
                ('Pathway-Express', 'pathway_enrichment/pe'),
                ('SPIA', 'pathway_enrichment/spia')]

ALGOS_MULT = {'clusterone': 100,
              'coach': 1000,
              'demon': 100,
              'fox': 100}

ALGOS_DEFAULT_PARAM = {'clusterone': 0.3,
                       'coach': 0.225,
                       'demon': 0.25,
                       'fox': 0.01}


def get_parameters_for_algo(algo):
    param_dict = {}
    parameters = os.listdir(f'{const.NETWORKS_DISPLAY_OS_CX}/{algo}/modules')
    for parameter in parameters:
        param_dict[int(parameter)] = str(
            int(parameter) / ALGOS_MULT[algo])

    return param_dict


def get_dir_for_parameter(algo, parameters):
    return int(float(parameters) * ALGOS_MULT[algo])


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


def display_in_sci_notation(number):
    return '{:.6e}'.format(number)


def display_cols_in_sci_notation(result, numeric_columns):
    for column in numeric_columns:
        result[column] = result[column].apply(display_in_sci_notation)


def create_empty_df(cols):
    cols_dict = {}
    for col in cols:
        cols_dict[col] = ['-']

    return pd.DataFrame(cols_dict)


def convert_transcript_to_msu_id(transcript_ids_str):
    transcript_ids = transcript_ids_str.split('\n')
    with open(const.TRANSCRIPT_TO_MSU_DICT, 'rb') as f:
        mapping_dict = pickle.load(f)

    output_str = ''
    for transcript_id in transcript_ids:
        for msu_id in mapping_dict[transcript_id]:
            output_str += f'{msu_id}\n({transcript_id})\n\n'

    return output_str[:-2]


def get_genes_from_kegg_link(link):
    idx = link.find('?')
    query = link[idx:].split('+')

    return '\n'.join(query[1:])


def convert_to_df_go(result):
    cols = ['ID', 'Gene Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value (Benjamini-Hochberg)', 'Genes']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_to(result):
    cols = ['ID', 'Trait Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value (Benjamini-Hochberg)', 'Genes']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_po(result):
    cols = ['ID', 'Plant Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value (Benjamini-Hochberg)', 'Genes']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_ora(result):
    cols = ['ID', 'KEGG Pathway', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value (Benjamini-Hochberg)', 'Genes', 'View on KEGG']

    if result.empty:
        return create_empty_df(cols)

    result['KEGG Pathway'] = result['KEGG Pathway'].str[:-
                                                        len(' - Oryza sativa japonica (Japanese rice) (RAPDB)')]

    result['View on KEGG'] = '<a href = "http://www.genome.jp/dbget-bin/show_pathway?' + \
        result['ID'] + '+' + result['Genes'].str.split(
            '/').str.join('+') + '" target = "_blank">Link</a>'

    # Prettify display of genes and convert to MSU accessions
    result['Genes'] = result['Genes'].str.split(
        '/').str.join('\n').apply(convert_transcript_to_msu_id)

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_spia(result):
    cols = ['ID', 'Name', 'ORA p-value', 'Total Acc. Perturbation', 'Perturbation p-value', 'Combined p-value',
            'Adj. Combined p-value (Benjamini-Hochberg)', 'Adj. Combined p-value (Bonferroni)', 'Pathway Status', 'Genes',
            'View on KEGG']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of ID
    result['ID'] = 'dosa' + result['ID_temp']
    result['Total Acc. Perturbation'] = result['tA']

    # Prettify display of genes and convert to MSU accessions
    result['Genes'] = result['View on KEGG'].apply(
        get_genes_from_kegg_link).apply(convert_transcript_to_msu_id)

    result['View on KEGG'] = '<a href = "' + \
        result['View on KEGG'] + '" target = "_blank">Link</a>'

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df(active_tab, module_idx, algo, parameters):
    active_tab = active_tab.split('-')[1]
    dir = PATHWAY_TABS[int(active_tab)][1]
    enrichment_type = dir.split('/')[-1]

    file = f'{const.ENRICHMENT_ANALYSIS_OUTPUT}/{algo}/{parameters}/{dir}/results/{enrichment_type}-df-{module_idx}.tsv'

    empty = False
    if enrichment_type == 'go':
        try:
            result = pd.read_csv(file, delimiter='\t',
                                 names=['ID', 'Gene Ontology Term', 'Gene Ratio',
                                        'BG Ratio', 'p-value', 'Adj. p-value (Benjamini-Hochberg)', 'q-value', 'Genes', 'Counts'],
                                 skiprows=1)
            empty = result.empty
        except:
            result = pd.DataFrame()
            empty = True

        return convert_to_df_go(result), empty

    elif enrichment_type == 'to':
        try:
            result = pd.read_csv(file, delimiter='\t',
                                 names=['ID', 'Trait Ontology Term', 'Gene Ratio',
                                        'BG Ratio', 'p-value', 'Adj. p-value (Benjamini-Hochberg)', 'q-value', 'Genes', 'Count'],
                                 skiprows=1)
            empty = result.empty
        except:
            result = pd.DataFrame()
            empty = True

        return convert_to_df_to(result), empty

    elif enrichment_type == 'po':
        try:
            result = pd.read_csv(file, delimiter='\t',
                                 names=['ID', 'Plant Ontology Term', 'Gene Ratio',
                                        'BG Ratio', 'p-value', 'Adj. p-value (Benjamini-Hochberg)', 'q-value', 'Genes', 'Count'],
                                 skiprows=1)
            empty = result.empty
        except:
            result = pd.DataFrame()
            empty = True

        return convert_to_df_po(result), empty

    elif enrichment_type == 'ora':
        try:
            result = pd.read_csv(file, delimiter='\t',
                                 names=['ID', 'KEGG Pathway', 'Gene Ratio',
                                        'BG Ratio', 'p-value', 'Adj. p-value (Benjamini-Hochberg)', 'q-value', 'Genes', 'Count'],
                                 skiprows=1)
            empty = result.empty
        except:
            result = pd.DataFrame()
            empty = True

        return convert_to_df_ora(result), empty

    elif enrichment_type == 'spia':
        try:
            result = pd.read_csv(file, delimiter='\t',
                                 names=['Name',	'ID_temp', 'pSize', 'NDE', 'ORA p-value', 'tA',
                                        'Perturbation p-value', 'Combined p-value', 'Adj. Combined p-value (Benjamini-Hochberg)',
                                        'Adj. Combined p-value (Bonferroni)', 'Pathway Status', 'View on KEGG'],
                                 skiprows=1,
                                 dtype={'ID_temp': object})      # Preserve leading 0 in KEGG pathway ID
            empty = result.empty
        except:
            result = pd.DataFrame()
            empty = True

        return convert_to_df_spia(result), empty


def load_module_graph(module, algo, parameters):
    module_idx = module.split(' ')[1]
    coexpress_nw = f'{const.NETWORKS_DISPLAY_OS_CX}/{algo}/modules/{parameters}/module-{module_idx}.tsv'
    G = nx.read_edgelist(coexpress_nw, data=(("coexpress", float),))

    return nx.cytoscape_data(G)['elements'], {'visibility': 'visible', 'width': '100%', 'height': '100vh'}
