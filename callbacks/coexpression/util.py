from ..constants import Constants
from ..file_util import *
import os
import pickle
import subprocess

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

ALGOS_LOW = {'clusterone': '1 (Loose Modules)',
             'coach': '1 (Fewer Modules)',
             'demon': '1 (Fewer Modules)',
             'fox': '1 (Loose Modules)'}

ALGOS_HIGH = {'clusterone': '4 (Dense Modules)',
              'coach': '4 (More Modules)',
              'demon': '4 (More Modules)',
              'fox': '4 (Cohesive Modules)'}


def display_in_sci_notation(number):
    return '{:.6e}'.format(number)


def get_parameters_for_algo(algo, network='OS-CX'):
    param_dict = {}
    parameters = sorted(map(int, os.listdir(
        f'{const.NETWORKS_DISPLAY}/{network}/{algo}/modules_to_genes')))

    for idx, parameter in enumerate(parameters):
        if idx == 0:
            param_dict[int(parameter)] = ALGOS_LOW[algo]
        elif idx == len(parameters) - 1:
            param_dict[int(parameter)] = ALGOS_HIGH[algo]
        else:
            param_dict[int(parameter)] = str(idx + 1)

    return param_dict


def write_genes_to_file(genes, genomic_intervals, network, algo, parameters):
    temp_output_folder_dir = get_temp_output_folder_dir(
        genomic_intervals, const.TEMP_COEXPRESSION, f'{network}/{algo}/{parameters}')

    if not dir_exist(temp_output_folder_dir):
        create_dir(temp_output_folder_dir)

        with open(f'{temp_output_folder_dir}/genes.txt', 'w') as f:
            f.write('\t'.join(genes))
            f.write('\n')

    return temp_output_folder_dir


def fetch_enriched_modules(output_dir):
    modules = []
    with open(f'{output_dir}/enriched_modules/ora-df.tsv') as modules_file:
        for line in modules_file:
            line = line.rstrip()
            line = line.split('\t')

            if line[0] != 'ID':
                modules.append(
                    f'Module {line[0]} (Adj. p-value = {display_in_sci_notation(float(line[1]))})')

    return modules


def do_module_enrichment_analysis(implicated_gene_ids, genomic_intervals, network, algo, parameters):
    genes = list(set(implicated_gene_ids))
    temp_output_folder_dir = write_genes_to_file(
        genes, genomic_intervals, network, algo, parameters)

    OUTPUT_DIR = temp_output_folder_dir
    if not dir_exist(f'{OUTPUT_DIR}/enriched_modules'):
        INPUT_GENES = f'{OUTPUT_DIR}/genes.txt'
        BACKGROUND_GENES = f'{const.NETWORKS_DISPLAY}/{network}/all-genes.txt'
        MODULE_TO_GENE_MAPPING = f'{const.NETWORKS_DISPLAY}/{network}/{algo}/modules_to_genes/{parameters}/modules-to-genes.tsv'

        # TODO: Add exception handling
        subprocess.run(['Rscript', '--vanilla', const.ORA_ENRICHMENT_ANALYSIS_PROGRAM, '-g', INPUT_GENES,
                        '-b', BACKGROUND_GENES, '-m', MODULE_TO_GENE_MAPPING, '-o', OUTPUT_DIR])

    return fetch_enriched_modules(OUTPUT_DIR)


# ========================================================
# Utility functions for the display of the tables showing
# the results of the enrichment analysis
# ========================================================

def display_cols_in_sci_notation(result, numeric_columns):
    for column in numeric_columns:
        result[column] = result[column].apply(display_in_sci_notation)


def create_empty_df(cols):
    cols_dict = {}
    for col in cols:
        cols_dict[col] = ['-']

    return pd.DataFrame(cols_dict)


def convert_transcript_to_msu_id(transcript_ids_str, network):
    transcript_ids = transcript_ids_str.split('\n')
    with open(f'{const.ENRICHMENT_ANALYSIS}/{network}/{const.TRANSCRIPT_TO_MSU_DICT}', 'rb') as f:
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


def get_genes_in_module(module_idx, network, algo, parameters):
    with open(f'{const.ENRICHMENT_ANALYSIS}/{network}/{const.ENRICHMENT_ANALYSIS_MODULES}/{algo}/{parameters}/transcript/{algo}-module-list.tsv') as f:
        for idx, module in enumerate(f):
            if idx + 1 == int(module_idx):
                return set(module.split('\t'))


def get_genes_in_pathway(pathway_id, network):
    with open(f'{const.ENRICHMENT_ANALYSIS}/{network}/{const.KEGG_DOSA_GENESET}', 'rb') as f:
        genes_in_pathway = pickle.load(f)

    return genes_in_pathway[pathway_id]


def get_genes_in_module_and_pathway(pathway_id, module_idx, network, algo, parameters):
    return '\n'.join(list(get_genes_in_pathway(pathway_id, network).intersection(
        get_genes_in_module(module_idx, network, algo, parameters))))


def get_kegg_pathway_name(pathway_id, network):
    with open(f'{const.ENRICHMENT_ANALYSIS}/{network}/{const.KEGG_DOSA_PATHWAY_NAMES}') as pathways:
        for line in pathways:
            line = line.split('\t')
            if line[0].rstrip() == pathway_id:
                return line[1].strip()


def remove_rap_db_info_in_pathway_name(pathway_name):
    return pathway_name[:-len(' - Oryza sativa japonica (Japanese rice) (RAPDB)')]

# ================================================
# Functions for the display of the tables showing
# the results of the enrichment analysis
# ================================================


def convert_to_df_go(result):
    cols = ['ID', 'Gene Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_to(result):
    cols = ['ID', 'Trait Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_po(result):
    cols = ['ID', 'Plant Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_ora(result, network):
    cols = ['ID', 'KEGG Pathway', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes', 'View on KEGG']

    if result.empty:
        return create_empty_df(cols)

    result['KEGG Pathway'] = result['KEGG Pathway'].apply(
        remove_rap_db_info_in_pathway_name)

    result['View on KEGG'] = '<a href = "http://www.genome.jp/dbget-bin/show_pathway?' + \
        result['ID'] + '+' + result['Genes'].str.split(
            '/').str.join('+') + '" target = "_blank">Link</a>'

    # Prettify display of genes and convert to MSU accessions
    result['Genes'] = result['Genes'].str.split(
        '/').str.join('\n')
    result['Genes'] = result.apply(
        lambda x: convert_transcript_to_msu_id(x['Genes'], network), axis=1)

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_pe(result, module_idx, network, algo, parameters):
    cols = ['ID', 'KEGG Pathway', 'ORA p-value', 'Perturbation p-value', 'Combined p-value',
            'Adj. ORA p-value', 'Adj. Perturbation p-value',
            'Adj. Combined p-value', 'Genes', 'View on KEGG']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of ID
    result['ID'] = result['ID'].str[len('path:'):]

    result['KEGG Pathway'] = result.apply(
        lambda x: get_kegg_pathway_name(x['ID'], network), axis=1)
    result['KEGG Pathway'] = result['KEGG Pathway'].apply(
        remove_rap_db_info_in_pathway_name)

    result['Genes'] = result.apply(lambda x: get_genes_in_module_and_pathway(
        x['ID'], module_idx, network, algo, parameters), axis=1)

    result['View on KEGG'] = '<a href = "http://www.genome.jp/dbget-bin/show_pathway?' + \
        result['ID'] + '+' + result['Genes'].str.split(
            '\n').str.join('+') + '" target = "_blank">Link</a>'

    result['Genes'] = result.apply(
        lambda x: convert_transcript_to_msu_id(x['Genes'], network), axis=1)

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_spia(result, network):
    cols = ['ID', 'KEGG Pathway', 'ORA p-value', 'Total Acc. Perturbation', 'Perturbation p-value', 'Combined p-value',
            'Adj. Combined p-value', 'Pathway Status', 'Genes', 'View on KEGG']

    if result.empty:
        return create_empty_df(cols)

    # Prettify display of ID
    result['ID'] = 'dosa' + result['ID']
    result['Total Acc. Perturbation'] = result['tA']

    # Prettify display of genes and convert to MSU accessions
    result['Genes'] = result['View on KEGG'].apply(
        get_genes_from_kegg_link)
    result['Genes'] = result.apply(
        lambda x: convert_transcript_to_msu_id(x['Genes'], network), axis=1)

    result['View on KEGG'] = '<a href = "' + \
        result['View on KEGG'] + '" target = "_blank">Link</a>'

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df(active_tab, module_idx, network, algo, parameters):
    active_tab = active_tab.split('-')[1]
    dir = PATHWAY_TABS[int(active_tab)][1]
    enrichment_type = dir.split('/')[-1]

    file = f'{const.ENRICHMENT_ANALYSIS}/{network}/output/{algo}/{parameters}/{dir}/results/{enrichment_type}-df-{module_idx}.tsv'

    empty = False
    if enrichment_type == 'go':
        try:
            result = pd.read_csv(file, delimiter='\t',
                                 names=['ID', 'Gene Ontology Term', 'Gene Ratio',
                                        'BG Ratio', 'p-value', 'Adj. p-value', 'q-value', 'Genes', 'Counts'],
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
                                        'BG Ratio', 'p-value', 'Adj. p-value', 'q-value', 'Genes', 'Count'],
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
                                        'BG Ratio', 'p-value', 'Adj. p-value', 'q-value', 'Genes', 'Count'],
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
                                        'BG Ratio', 'p-value', 'Adj. p-value', 'q-value', 'Genes', 'Count'],
                                 skiprows=1)
            empty = result.empty
        except:
            result = pd.DataFrame()
            empty = True

        return convert_to_df_ora(result, network), empty

    elif enrichment_type == 'pe':
        try:
            result = pd.read_csv(file, delimiter='\t',
                                 names=['ID', 'totalAcc', 'totalPert', 'totalAccNorm', 'totalPertNorm',
                                        'Perturbation p-value',	'pAcc',	'ORA p-value', 'Combined p-value',
                                        'Adj. Perturbation p-value', 'Adj. Accumulation p-value',
                                        'Adj. ORA p-value', 'Adj. Combined p-value'],
                                 skiprows=1)
            empty = result.empty
        except:
            result = pd.DataFrame()
            empty = True

        return convert_to_df_pe(result, module_idx, network, algo, parameters), empty

    elif enrichment_type == 'spia':
        try:
            result = pd.read_csv(file, delimiter='\t',
                                 names=['KEGG Pathway',	'ID', 'pSize', 'NDE', 'ORA p-value', 'tA',
                                        'Perturbation p-value', 'Combined p-value', 'Adj. Combined p-value',
                                        'Adj. Combined p-value (Bonferroni)', 'Pathway Status', 'View on KEGG'],
                                 skiprows=1,
                                 dtype={'ID': object})      # Preserve leading 0 in KEGG pathway ID
            empty = result.empty
        except:
            result = pd.DataFrame()
            empty = True

        return convert_to_df_spia(result, network), empty


def convert_module_to_edge_list(module, network_file, output_dir, filename):
    module = set(module)
    selected_nodes = set()
    with open(network_file) as network, open(f'{output_dir}/{filename}', 'w') as output:
        for edge in network:
            edge = edge.rstrip()
            nodes = edge.split('\t')

            if nodes[0] in module and nodes[1] in module:
                selected_nodes.add(nodes[0])
                selected_nodes.add(nodes[1])
                output.write(f'{nodes[0]}\t{nodes[1]}\n')

    assert len(selected_nodes - module) == 0


def convert_modules(network_file, module_file, module_index, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(module_file) as modules:
        for idx, module in enumerate(modules):
            if idx == module_index - 1:
                module = module.rstrip()
                module = module.split('\t')
                filename = f'module-{idx + 1}.tsv'
                convert_module_to_edge_list(
                    module, network_file, output_dir, filename)

                break


def load_module_graph(implicated_gene_ids, module, network, algo, parameters, layout):
    try:
        module_idx = module.split(' ')[1]
        OUTPUT_DIR = f'{const.TEMP}/{network}/{algo}/modules/{parameters}'
        coexpress_nw = f'{OUTPUT_DIR}/module-{module_idx}.tsv'

        if not dir_exist(coexpress_nw):
            NETWORK_FILE = f'{const.NETWORKS}/{network}.txt'
            MODULE_FILE = f'{const.NETWORKS_MODULES}/{network}/module_list/{algo}/{parameters}/{algo}-module-list.tsv'

            convert_modules(NETWORK_FILE, MODULE_FILE,
                            int(module_idx), OUTPUT_DIR)

        G = nx.read_edgelist(coexpress_nw, data=(("coexpress", float),))

        elements = nx.cytoscape_data(G)['elements']
        for node in elements['nodes']:
            if node['data']['id'] in implicated_gene_ids:
                node['classes'] = 'shaded'

        return elements, {'name': layout}, {'visibility': 'visible', 'width': '100%', 'height': '100vh'}

    # Triggered when there are no enriched modules
    except:  # FileNotFoundError:
        return {}, {'name': layout}, {'visibility': 'hidden', 'width': '100%', 'height': '100vh'}
