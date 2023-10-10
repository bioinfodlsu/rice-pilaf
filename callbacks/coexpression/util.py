from dash import html
from ..constants import Constants
from ..file_util import *
from ..general_util import *
from ..links_util import *
import os
import pickle

import pandas as pd
import networkx as nx
from scipy.stats import fisher_exact, false_discovery_control

from collections import namedtuple


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
        100, 0.3, '1 (Looser Modules)', '4 (Denser Modules)'),
    'coach': Module_detection_algo(
        1000, 0.225, '1 (Looser Modules)', '4 (Denser Modules)'),
    'demon': Module_detection_algo(
        100, 0.25, '1 (Looser Modules)', '4 (Denser Modules)'),
    'fox': Module_detection_algo(
        100, 0.05, '1 (Looser Modules)', '4 (Denser Modules)'),
}


MODULE_DETECTION_ALGOS_VALUE_LABEL = [
    {'value': 'clusterone', 'label': 'ClusterONE',
     'label_id': 'clusterone'},
    {'value': 'coach', 'label': 'COACH', 'label_id': 'coach'},
    {'value': 'demon', 'label': 'DEMON', 'label_id': 'demon'},
    {'value': 'fox', 'label': 'FOX', 'label_id': 'fox'}
]

COEXPRESSION_NETWORKS_VALUE_LABEL = [
    {'value': 'OS-CX', 'label': 'RiceNet v2', 'label_id': 'os-cx'},
    {'value': 'RCRN',
     'label': 'Rice Combined Mutual Ranked Network (RCRN)', 'label_id': 'rcrn'},
]

Enrichment_tab = namedtuple('Enrichment_tab', ['enrichment', 'path'])
enrichment_tabs = [Enrichment_tab('Gene Ontology', 'ontology_enrichment/go'),
                   Enrichment_tab('Trait Ontology', 'ontology_enrichment/to'),
                   Enrichment_tab('Plant Ontology', 'ontology_enrichment/po'),
                   Enrichment_tab('Pathways (Over-Representation)',
                                  'pathway_enrichment/ora'),
                   Enrichment_tab('Pathway-Express', 'pathway_enrichment/pe'),
                   Enrichment_tab('SPIA', 'pathway_enrichment/spia')]


def get_user_facing_parameter(algo, parameter, network='OS-CX'):
    parameters = sorted(
        map(int, os.listdir(f'{Constants.NETWORK_MODULES}/{network}/MSU/{algo}')))

    return parameters.index(parameter) + 1


def get_user_facing_algo(algo):
    for entry in MODULE_DETECTION_ALGOS_VALUE_LABEL:
        if entry['value'] == algo:
            return entry['label']


def get_user_facing_network(network):
    for entry in COEXPRESSION_NETWORKS_VALUE_LABEL:
        if entry['value'] == network:
            return entry['label']


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
    parameters = sorted(
        map(int, os.listdir(f'{Constants.NETWORK_MODULES}/{network}/MSU/{algo}')))

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


def create_module_enrichment_results_dir(genomic_intervals, addl_genes, network, algo, parameters):
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
        genomic_intervals, Constants.TEMP_COEXPRESSION, f'{shorten_name(addl_genes)}/{network}/{algo}/{parameters}')

    if not path_exists(temp_output_folder_dir):
        make_dir(temp_output_folder_dir)

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
    with open(f'{output_dir}/enriched_modules.tsv') as modules_file:
        for line in modules_file:
            line = line.rstrip().split('\t')
            idx = line[0]
            p_value = float(line[1])

            modules.append(
                f'Module {idx} (Adj. p-value = {display_in_sci_notation(p_value)})')

    return modules


def do_module_enrichment_analysis(implicated_gene_ids, genomic_intervals, addl_genes, network, algo, parameters):
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
    implicated_genes = set(implicated_gene_ids)
    INPUT_GENES_DIR = create_module_enrichment_results_dir(
        genomic_intervals, addl_genes, network, algo, parameters)
    ENRICHED_MODULES_PATH = f'{INPUT_GENES_DIR}/enriched_modules.tsv'

    if not path_exists(ENRICHED_MODULES_PATH):
        ENRICHED_MODULES_PATH_WITH_TIMESTAMP = append_timestamp_to_filename(
            ENRICHED_MODULES_PATH)
        MODULES_PATH = f'{Constants.NETWORK_MODULES}/{network}/MSU/{algo}/{parameters}/{algo}-module-list.tsv'

        # ====================================================================================
        # This replicates the logic of running the universal enrichment function `enricher()`
        # provided by clusterProfiler
        # ====================================================================================

        with open(MODULES_PATH) as modules_file, open(ENRICHED_MODULES_PATH_WITH_TIMESTAMP, 'w') as enriched_modules_file:
            modules = []
            background_genes = set()
            for idx, line in enumerate(modules_file):
                module_genes = set(line.strip().split('\t'))
                background_genes = background_genes.union(module_genes)
                if implicated_genes.intersection(module_genes):
                    modules.append(idx)

            p_values_indices = []
            p_values = []
            modules_file.seek(0)
            for idx, line in enumerate(modules_file):
                if idx in modules:
                    module = line.strip().split('\t')
                    module_genes = set(module)
                    table = construct_contigency_table(
                        background_genes, implicated_genes, module_genes)

                    p_values.append(fisher_exact(
                        table, alternative='greater').pvalue)

                    # Add 1 since user-facing module number is one-based
                    p_values_indices.append(idx + 1)

            adj_p_values = false_discovery_control(p_values, method='bh')
            significant_adj_p_values = [(p_values_indices[idx], adj_p_value) for idx, adj_p_value in enumerate(
                adj_p_values) if adj_p_value < Constants.P_VALUE_CUTOFF]
            significant_adj_p_values.sort(key=lambda x: x[1])
            significant_adj_p_values = [
                f'{ID}\t{adj_p_value}' for ID, adj_p_value in significant_adj_p_values]

            enriched_modules_file.write('\n'.join(significant_adj_p_values))

        try:
            os.replace(ENRICHED_MODULES_PATH_WITH_TIMESTAMP,
                       ENRICHED_MODULES_PATH)
        except:
            pass

    return fetch_enriched_modules(INPUT_GENES_DIR)


def construct_contigency_table(background_genes, implicated_genes, module_genes):
    not_in_implicated = background_genes.difference(implicated_genes)
    not_in_module = background_genes.difference(module_genes)

    in_implicated_in_module = len(implicated_genes.intersection(module_genes))
    in_implicated_not_in_module = len(
        implicated_genes.intersection(not_in_module))

    not_in_implicated_in_module = len(
        not_in_implicated.intersection(module_genes))
    not_in_implicated_not_in_module = len(
        not_in_implicated.intersection(not_in_module))

    table = [[in_implicated_in_module, not_in_implicated_in_module],
             [in_implicated_not_in_module, not_in_implicated_not_in_module]]

    return table


# ===============================================================================================
# Utility functions for the display of the tables showing the results of the enrichment analysis
# ===============================================================================================

def add_link_to_genes(gene_ids_str):
    return '\n'.join([get_msu_browser_link_single_str(gene_id) for gene_id in gene_ids_str.split('\n')])


def convert_transcript_to_msu_id(transcript_ids_str, network):
    """
    Converts given KEGG transcript IDs to their respective MSU accessions.

    Parameters:
    - transcript_ids_str: KEGG transcript IDs
    - network: Coexpression network

    Returns:
    - Equivalent MSU accessions of the KEGG transcript IDs
    """
    with open(f'{Constants.MSU_MAPPING}/{network}/transcript-to-msu-id.pickle', 'rb') as f:
        mapping_dict = pickle.load(f)

    output_str = ''
    transcript_ids = transcript_ids_str.split('\n')
    for transcript_id in transcript_ids:
        for msu_id in mapping_dict[transcript_id]:
            output_str += f'{get_msu_browser_link_single_str(msu_id)}\n<span class="small">({get_gramene_transcript_single_str(transcript_id)})</span><br><br>'

    # Remove trailing newline characters
    return output_str[:-len('<br><br>')]


def get_genes_in_module(module_idx, network, algo, parameters):
    with open(f'{Constants.NETWORK_MODULES}/{network}/transcript/{algo}/{parameters}/{algo}-module-list.tsv') as f:
        for idx, module in enumerate(f):
            if idx + 1 == int(module_idx):
                return set(module.split('\t'))


def get_genes_in_pathway(pathway_id, network):
    with open(f'{Constants.ENRICHMENT_ANALYSIS}/{network}/{Constants.KEGG_DOSA_GENESET}', 'rb') as f:
        genes_in_pathway = pickle.load(f)

    return genes_in_pathway[pathway_id]


def get_genes_in_module_and_pathway(pathway_id, module_idx, network, algo, parameters):
    return '\n'.join(list(get_genes_in_pathway(pathway_id, network).intersection(
        get_genes_in_module(module_idx, network, algo, parameters))))


def get_kegg_pathway_name(pathway_id, network):
    with open(f'{Constants.ENRICHMENT_ANALYSIS}/{network}/{Constants.KEGG_DOSA_PATHWAY_NAMES}') as pathways:
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
    result['Genes'] = result.apply(
        lambda x: add_link_to_genes(x['Genes']), axis=1)

    result['ID'] = get_go_link(result, 'ID')

    result = result.sort_values('Adj. p-value')

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
    result['Genes'] = result.apply(
        lambda x: add_link_to_genes(x['Genes']), axis=1)

    result['ID'] = get_to_po_link(result, 'ID')

    result = result.sort_values('Adj. p-value')

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
    result['Genes'] = result.apply(
        lambda x: add_link_to_genes(x['Genes']), axis=1)

    result['ID'] = get_to_po_link(result, 'ID')

    result = result.sort_values('Adj. p-value')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_ora(result, network):
    cols = ['ID', 'KEGG Pathway', 'Gene Ratio',
            'BG Ratio', 'p-value', 'Adj. p-value', 'Genes']

    if result.empty:
        return create_empty_df_with_cols(cols)

    result['KEGG Pathway'] = result['KEGG Pathway'].apply(
        remove_rap_db_info_in_pathway_name)

    # Construct link before appending the MSU accession
    result['ID'] = get_kegg_link(result, 'ID', 'Genes')

    # Prettify display of genes and convert to MSU accessions
    result['Genes'] = result['Genes'].str.split(
        '/').str.join('\n')
    result['Genes'] = result.apply(
        lambda x: convert_transcript_to_msu_id(x['Genes'], network), axis=1)

    result = result.sort_values('Adj. p-value')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_pe(result, module_idx, network, algo, parameters):
    cols = ['ID', 'KEGG Pathway', 'ORA p-value', 'Perturbation p-value', 'Combined p-value',
            'Adj. ORA p-value', 'Adj. Perturbation p-value',
            'Adj. Combined p-value', 'Genes']

    if result.empty:
        return create_empty_df_with_cols(cols)

    result = result.loc[result['Adj. Combined p-value']
                        < Constants.P_VALUE_CUTOFF]

    # IMPORTANT: Do not change ordering of instructions

    # Prettify display of ID
    result['ID'] = result['ID'].str[len('path:'):]

    result['KEGG Pathway'] = result.apply(
        lambda x: get_kegg_pathway_name(x['ID'], network), axis=1)
    result['KEGG Pathway'] = result['KEGG Pathway'].apply(
        remove_rap_db_info_in_pathway_name)

    result['Genes'] = result.apply(lambda x: get_genes_in_module_and_pathway(
        x['ID'], module_idx, network, algo, parameters), axis=1)

    # Construct link before appending the MSU accession
    result['ID'] = get_kegg_link(result, 'ID', 'Genes')

    result['Genes'] = result.apply(
        lambda x: convert_transcript_to_msu_id(x['Genes'], network), axis=1)

    result = result.sort_values('Adj. Combined p-value')

    display_cols_in_sci_notation(
        result, [col for col in cols if 'p-value' in col])

    return result[cols].dropna()


def convert_to_df_spia(result, network):
    cols = ['ID', 'KEGG Pathway', 'ORA p-value', 'Total Acc. Perturbation', 'Perturbation p-value', 'Combined p-value',
            'Adj. Combined p-value', 'Pathway Status', 'Genes']

    if result.empty:
        return create_empty_df_with_cols(cols)

    result = result.loc[result['Adj. Combined p-value']
                        < Constants.P_VALUE_CUTOFF]

    # Prettify display of ID
    result['ID'] = 'dosa' + result['ID']
    result['Total Acc. Perturbation'] = result['tA']

    # Prettify display of genes and convert to MSU accessions
    result['Genes'] = result['View on KEGG'].apply(
        get_genes_from_kegg_link)

    # Construct link before appending the MSU accession
    result['ID'] = get_kegg_link(result, 'ID', 'Genes')

    result['Genes'] = result.apply(
        lambda x: convert_transcript_to_msu_id(x['Genes'], network), axis=1)

    result = result.sort_values('Adj. Combined p-value')

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

    file = f'{Constants.ENRICHMENT_ANALYSIS}/{network}/output/{algo}/{parameters}/{dir}/results/{enrichment_type}-df-{module_idx}.tsv'

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
        if enrichment_type.lower() == 'spia':
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
        OUTPUT_DIR = f'{Constants.TEMP}/{network}/{algo}/modules/{parameters}'
        coexpress_nw = f'{OUTPUT_DIR}/module-{module_idx}.tsv'

        if not path_exists(coexpress_nw):
            NETWORK_FILE = f'{Constants.NETWORKS}/{network}.txt'
            MODULE_FILE = f'{Constants.NETWORK_MODULES}/{network}/MSU/{algo}/{parameters}/{algo}-module-list.tsv'

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
        return {}, {'name': layout}, {'display': 'none', 'width': '100%', 'height': '100vh'}

# ====================================
# Functions for displaying statistics
# ====================================


def count_modules(network, algo, parameters):
    with open(f'{Constants.NETWORK_MODULES}/{network}/MSU/{algo}/{parameters}/{algo}-module-list.tsv') as f:
        return len(f.readlines())


Noun = namedtuple('Noun', ['singular', 'plural'])


def get_noun_for_active_tab(active_tab):
    tab_idx = get_tab_index(active_tab)
    if 0 <= tab_idx and tab_idx <= 2:
        return Noun('ontology term', 'ontology terms')
    else:
        return Noun('pathway', 'pathways')


def count_genes_in_module(implicated_genes, module_idx, network, algo, parameters):
    with open(f'{Constants.NETWORK_MODULES}/{network}/MSU/{algo}/{parameters}/{algo}-module-list.tsv') as modules:
        for idx, module in enumerate(modules):
            if idx == module_idx - 1:
                module_genes = module.strip().split('\t')
                return len(module_genes), len(set.intersection(set(module_genes), set(implicated_genes)))


# =========================================
# Functions related to graph interactivity
# =========================================

def get_rapdb_entry(gene, rapdb_mapping):
    if rapdb_mapping[gene]:
        return html.Ul([html.Li(get_rapdb_single_str(entry, dash=True)) for entry in sorted(rapdb_mapping[gene]) if entry],
                       className='no-bottom-space')

    return html.Span([NULL_PLACEHOLDER, html.Br()])


def get_gene_description_entry(gene, gene_descriptions_mapping):
    try:
        return gene_descriptions_mapping[gene][0]
    except KeyError:
        return NULL_PLACEHOLDER


def get_uniprot_entry(gene, gene_descriptions_mapping):
    try:
        return get_uniprot_link_single_str(gene_descriptions_mapping[gene][1], dash=True)
    except KeyError:
        return NULL_PLACEHOLDER


def get_pfam_entry(gene, pfam_mapping, iric_mapping):
    try:
        return html.Ul([html.Li(get_pfam_link_single_str(entry[1], entry[0], dash=True)) for entry in sorted(pfam_mapping[iric_mapping[gene]]) if entry[1]],
                       className='no-bottom-space')
    except KeyError:
        return NULL_PLACEHOLDER


def get_interpro_entry(gene, interpro_mapping, iric_mapping):
    try:
        return html.Ul([html.Li(get_interpro_link_single_str(entry[1], entry[0], dash=True)) for entry in sorted(interpro_mapping[iric_mapping[gene]]) if entry[1]],
                       className='no-bottom-space')
    except KeyError:
        return html.Span([NULL_PLACEHOLDER, html.Br()])


def get_qtaro_entry(gene, mapping):
    try:
        character_majors_list = []
        for character_major in sorted(mapping[gene]):
            character_minors_list = []
            for character_minor in sorted(mapping[gene][character_major]):
                pubs = [html.Li(get_doi_link_single_str(pub, dash=True)) for pub in sorted(mapping[gene]
                        [character_major][character_minor])]
                character_minors_list.append(
                    html.Li([character_minor, html.Ul(pubs)]))

            character_majors_list.append(
                html.Li([character_major, html.Ul(character_minors_list)]))

        return html.Ul(character_majors_list, className='no-bottom-space')

    except KeyError:
        return NULL_PLACEHOLDER


def get_pubmed_entry(gene, pubmed_mapping):
    try:
        return html.Ul([html.Li(get_pubmed_link_single_str(pubmed_id[0], dash=True)) for pubmed_id in sorted(
            pubmed_mapping[gene].items(), key=lambda x: x[1], reverse=True)],
            className='no-bottom-space')
    except KeyError:
        return html.Span([NULL_PLACEHOLDER, html.Br()])
