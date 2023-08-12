from ..constants import Constants
from ..file_util import *
from ..general_util import *
import os
import pickle
import subprocess

import pandas as pd
import networkx as nx

from collections import namedtuple

const = Constants()

# Settings for the module detection algorithms:
# - multiplier: Value multiplied to the parameter to get the name of the directory
#               For example, results of running clusterone at param=0.3 are saved in 30
# - default_param: Default parameter of the module detection algorithm
# - low: User-facing display for the lowest parameter
# - high: User-facing display for the highest parameter

Module_detection_algo = namedtuple('Module_detection_algo', [
                                   'multiplier', 'default_param', 'low', 'high'])
module_detection_algos = {
    'clusterone': Module_detection_algo(
        100, 0.3, '1 (Loose Modules)', '4 (Dense Modules)'),
    'coach': Module_detection_algo(
        1000, 0.225, '1 (Fewer Modules)', '4 (More Modules)'),
    'demon': Module_detection_algo(
        100, 0.25, '1 (Fewer Modules)', '4 (More Modules)'),
    'fox': Module_detection_algo(
        100, 0.01, '1 (Loose Modules)', '4 (Cohesive Modules)'),
}

Enrichment_tab = namedtuple('Enrichment_tab', ['enrichment', 'path'])
enrichment_tabs = [Enrichment_tab('Gene Ontology', 'ontology_enrichment/go'),
                   Enrichment_tab('Trait Ontology', 'ontology_enrichment/to'),
                   Enrichment_tab('Plant Ontology', 'ontology_enrichment/po'),
                   Enrichment_tab('Pathways (Overrepresentation)',
                                  'pathway_enrichment/ora'),
                   Enrichment_tab('Pathway-Express', 'pathway_enrichment/pe'),
                   Enrichment_tab('SPIA', 'pathway_enrichment/spia')]


def get_parameters_for_algo(algo, network='OS-CX'):
    """
    Returns the user-facing parameters for the module detection algorithms

    Parameters:
    - algo: Module detection algorithm
    - network: Any of the coexpression networks supported by the app

    Returns:
    - User-facing parameters for the module detection algorithms
    """
    param_dict = {}
    parameters = sorted(map(int, os.listdir(
        f'{const.NETWORKS_DISPLAY}/{network}/{algo}/modules_to_genes')))

    # Display the user-facing parameters for the module detection algorithms
    for idx, parameter in enumerate(parameters):
        if idx == 0:
            param_dict[int(parameter)] = module_detection_algos[algo].low
        elif idx == len(parameters) - 1:
            param_dict[int(parameter)] = module_detection_algos[algo].high
        else:
            param_dict[int(parameter)] = str(idx + 1)

    return param_dict

# =================================================
# Utility functions for module enrichment analysis
# =================================================


def write_genes_to_file(genes, genomic_intervals, network, algo, parameters):
    """
    Writes the accessions of the GWAS-implicated genes to a file

    Parameters:
    - genes: Accessions of the genes implicated by GWAS
    - genomic_intervals: Genomic interval entered by the user
    - network: Coexpression network
    - algo: Module detection algorithm
    - parameters: Parameter at which module detection algorithm is run

    Returns:
    - Parent directory of the file to which the accessions of the GWAS-implicated genes are written
    """
    temp_output_folder_dir = get_path_to_temp(
        genomic_intervals, const.TEMP_COEXPRESSION, f'{network}/{algo}/{parameters}')

    if not path_exists(temp_output_folder_dir):
        make_dir(temp_output_folder_dir)

        with open(f'{temp_output_folder_dir}/genes.txt', 'w') as f:
            f.write('\t'.join(genes))
            f.write('\n')

    return temp_output_folder_dir


def fetch_enriched_modules(output_dir):
    """
    Fetches the enriched modules from the output file of the module enrichment analysis

    Parameters:
    - output_dir: Parent directory of the output file of the module enrichment analysis

    Returns:
    - Enriched modules (i.e., their respectives indices and adjust p-values)
    """
    modules = []
    with open(f'{output_dir}/enriched_modules/ora-df.tsv') as modules_file:
        # Ignore header
        next(modules_file)

        for line in modules_file:
            line = line.rstrip().split('\t')
            idx = line[0]
            p_value = float(line[1])

            modules.append(
                f'Module {idx} (Adj. p-value = {display_in_sci_notation(p_value)})')

    return modules


def do_module_enrichment_analysis(implicated_gene_ids, genomic_intervals, network, algo, parameters):
    """
    Determine which modules are enriched given the set of GWAS-implicated genes

    Parameters:
    - implicated_gene_ids: Accessions of the genes implicated by GWAS
    - genomic_intervals: Genomic interval entered by the user
    - network: Coexpression network
    - algo: Module detection algorithm
    - parameters: Parameter at which module detection algorithm is run

    Returns:
    - Enriched modules (i.e., their respectives indices and adjust p-values)
    """
    genes = list(set(implicated_gene_ids))
    INPUT_GENES_DIR = write_genes_to_file(
        genes, genomic_intervals, network, algo, parameters)

    if not path_exists(f'{INPUT_GENES_DIR}/enriched_modules'):
        INPUT_GENES = f'{INPUT_GENES_DIR}/genes.txt'
        BACKGROUND_GENES = f'{const.NETWORKS_DISPLAY}/{network}/all-genes.txt'
        MODULE_TO_GENE_MAPPING = f'{const.NETWORKS_DISPLAY}/{network}/{algo}/modules_to_genes/{parameters}/modules-to-genes.tsv'

        # TODO: Add exception handling
        subprocess.run(['Rscript', '--vanilla', const.ORA_ENRICHMENT_ANALYSIS_PROGRAM, '-g', INPUT_GENES,
                        '-b', BACKGROUND_GENES, '-m', MODULE_TO_GENE_MAPPING, '-o', INPUT_GENES_DIR])

    return fetch_enriched_modules(INPUT_GENES_DIR)


# ===============================================================================================
# Utility functions for the display of the tables showing the results of the enrichment analysis
# ===============================================================================================


def convert_transcript_to_msu_id(transcript_ids_str, network):
    """
    Converts given KEGG transcript IDs to their respective MSU accessions.

    Parameters:
    - transcript_ids_str: KEGG transcript IDs
    - network: Coexpression network

    Returns:
    - Equivalent MSU accessions of the KEGG transcript IDs
    """
    with open(f'{const.ENRICHMENT_ANALYSIS}/{network}/{const.TRANSCRIPT_TO_MSU_DICT}', 'rb') as f:
        mapping_dict = pickle.load(f)

    output_str = ''
    transcript_ids = transcript_ids_str.split('\n')
    for transcript_id in transcript_ids:
        for msu_id in mapping_dict[transcript_id]:
            output_str += f'{msu_id}\n({transcript_id})\n\n'

    # Remove trailing newline characters
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

# =======================================================================================
# Functions for the display of the tables showing the results of the enrichment analysis
# =======================================================================================


def convert_to_df_go(result):
    cols = ['ID', 'Gene Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes']

    if result.empty:
        return create_empty_df_with_cols(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_to(result):
    cols = ['ID', 'Trait Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes']

    if result.empty:
        return create_empty_df_with_cols(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_po(result):
    cols = ['ID', 'Plant Ontology Term', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes']

    if result.empty:
        return create_empty_df_with_cols(cols)

    # Prettify display of genes
    result['Genes'] = result['Genes'].str.split('/').str.join('\n')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_ora(result, network):
    cols = ['ID', 'KEGG Pathway', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes', 'View on KEGG']

    if result.empty:
        return create_empty_df_with_cols(cols)

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
        return create_empty_df_with_cols(cols)

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
        return create_empty_df_with_cols(cols)

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
    """
    Returns the results of ontology and pathway enrichment analysis as a data frame

    Parameters:
    - active_tab: ID of the tab corresponding to the selected enrichment analysis
    - module_idx: Index of the selected module
    - network: Coexpression network
    - algo: Module detection algorithm
    - parameters: Parameter at which module detection algorithm is run

    Returns:
    - Data frame containing the results of ontology and pathway enrichment analysis
    - True if the data frame is empty; False, otherwise
    """
    dir = enrichment_tabs[get_tab_index(active_tab)].path
    enrichment_type = dir.split('/')[-1]

    file = f'{const.ENRICHMENT_ANALYSIS}/{network}/output/{algo}/{parameters}/{dir}/results/{enrichment_type}-df-{module_idx}.tsv'

    columns = {'go': ['ID', 'Gene Ontology Term', 'Gene Ratio',
                      'BG Ratio', 'p-value', 'Adj. p-value', 'q-value', 'Genes', 'Count'],
               'to': ['ID', 'Trait Ontology Term', 'Gene Ratio',
                      'BG Ratio', 'p-value', 'Adj. p-value', 'q-value', 'Genes', 'Count'],
               'po': ['ID', 'Plant Ontology Term', 'Gene Ratio',
                      'BG Ratio', 'p-value', 'Adj. p-value', 'q-value', 'Genes', 'Count'],
               'ora': ['ID', 'KEGG Pathway', 'Gene Ratio',
                       'BG Ratio', 'p-value', 'Adj. p-value', 'q-value', 'Genes', 'Count'],
               'pe': ['ID', 'totalAcc', 'totalPert', 'totalAccNorm', 'totalPertNorm',
                      'Perturbation p-value',	'pAcc',	'ORA p-value', 'Combined p-value',
                      'Adj. Perturbation p-value', 'Adj. Accumulation p-value',
                      'Adj. ORA p-value', 'Adj. Combined p-value'],
               'spia': ['KEGG Pathway',	'ID', 'pSize', 'NDE', 'ORA p-value', 'tA',
                        'Perturbation p-value', 'Combined p-value', 'Adj. Combined p-value',
                        'Adj. Combined p-value (Bonferroni)', 'Pathway Status', 'View on KEGG']}

    try:
        result = pd.read_csv(file, delimiter='\t',
                             names=columns[enrichment_type], skiprows=1)

        # SPIA is a special case
        if enrichment_type == 'SPIA':
            # Add dtype argument to preserve leading 0 in KEGG pathway ID
            result = pd.read_csv(file, delimiter='\t',
                                 names=columns[enrichment_type], skiprows=1, dtype={'ID': object})

        empty = result.empty
    except:
        result = pd.DataFrame()
        empty = True

    # Return results data frame and whether it is empty
    if enrichment_type == 'go':
        return convert_to_df_go(result), empty

    elif enrichment_type == 'to':
        return convert_to_df_to(result), empty

    elif enrichment_type == 'po':
        return convert_to_df_po(result), empty

    elif enrichment_type == 'ora':
        return convert_to_df_ora(result, network), empty

    elif enrichment_type == 'pe':
        return convert_to_df_pe(result, module_idx, network, algo, parameters), empty

    elif enrichment_type == 'spia':
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


def convert_modules_to_edgelist(network_file, module_file, module_index, output_dir):
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
    """
    Displays the subgraph induced by the module

    Parameters:
    - implicated_gene_ids: Accessions of the genes implicated by GWAS
    - module: Gene module
    - network: Coexpression network
    - algo: Module detection algorithm
    - parameters: Parameter at which module detection algorithm is run
    - layout: Layout of the graph display

    Returns:
    - Elements (nodes and edges) of the graph
    - Dictionary storing the layout of the graph
    - Dictionary storing the visibility, width, and height of the graph
    """
    try:
        # Ignore the word "Module" at the start
        module_idx = int(module.split(' ')[1])
        OUTPUT_DIR = f'{const.TEMP}/{network}/{algo}/modules/{parameters}'
        coexpress_nw = f'{OUTPUT_DIR}/module-{module_idx}.tsv'

        if not path_exists(coexpress_nw):
            NETWORK_FILE = f'{const.NETWORKS}/{network}.txt'
            MODULE_FILE = f'{const.NETWORKS_MODULES}/{network}/module_list/{algo}/{parameters}/{algo}-module-list.tsv'

            convert_modules_to_edgelist(
                NETWORK_FILE, MODULE_FILE, module_idx, OUTPUT_DIR)

        G = nx.read_edgelist(coexpress_nw, data=(('coexpress', float)))

        # Highlight the GWAS-implicated genes
        elements = nx.cytoscape_data(G)['elements']
        for node in elements['nodes']:
            if node['data']['id'] in implicated_gene_ids:
                node['classes'] = 'shaded'

        return elements, {'name': layout}, {'visibility': 'visible', 'width': '100%', 'height': '100vh'}

    # Triggered when there are no enriched modules
    except:
        return {}, {'name': layout}, {'visibility': 'hidden', 'width': '100%', 'height': '100vh'}
