import pickle
from collections import namedtuple

import gffutils
import pandas as pd

from ..constants import Constants
from ..general_util import *
from ..links_util import *
from ..file_util import *

import regex as re


Genomic_interval = namedtuple('Genomic_interval', ['chrom', 'start', 'stop'])

# Error codes and messages triggered by a malformed genomic interval entered by the user
Error_message = namedtuple('Error_message', ['code', 'message'])
errors = {
    'NO_CHROM_INTERVAL_SEP': Error_message(1, 'A genomic interval should be entered as chrom:start-end. Use a semicolon (;) to separate multiple intervals'),
    'NO_START_STOP_SEP': Error_message(2, 'Specify a valid start and end for the genomic interval'),
    'START_STOP_NOT_INT': Error_message(3, 'The start and end of a genomic interval should be integers'),
    'START_GREATER_THAN_STOP': Error_message(4, 'The start of a genomic interval should not be past the end')
}

other_ref_genomes = {'N22': 'aus Nagina-22',
                     'MH63': 'indica Minghui-63',
                     'Azu': 'japonica Azucena',
                     'ARC': 'basmati ARC',
                     'IR64': 'indica IR64',
                     'CMeo': 'japonica CHAO MEO'}

NB_COLUMNS = ['Name', 'RAP-DB', 'Description', 'UniProtKB/Swiss-Prot', 'Pfam', 'InterPro',
              'OGI', 'Chromosome', 'Start', 'End', 'Strand', 'QTL Analyses', 'PubMed Article IDs']
OTHER_REF_COLUMNS = ['OGI', 'Name', 'Chromosome', 'Start', 'End', 'Strand']
FRONT_FACING_COLUMNS = ['Name', 'Description', 'UniProtKB/Swiss-Prot', 'OGI']
NO_REFS_COLUMNS = ['OGI']


def construct_options_other_ref_genomes():
    return [
        {'value': symbol, 'label': f'{symbol} ({name})'} for symbol, name in other_ref_genomes.items()]


# =====================================================
# Utility functions for parsing input genomic interval
# =====================================================


def is_error(genomic_interval):
    """
    Returns True if given genomic interval is malformed; False, otherwise

    This function assumes that genomic_interval is the return value of to_genomic_interval()

    Parameters:
    - genomic_interval: If its first element is an integer (i.e., the error code),
                        then the given genomic interval is malformed

    Returns:
    - True if given genomic interval is malformed; False, otherwise
    """
    return isinstance(genomic_interval[0], int)


def get_error_message(error_code):
    """
    Returns the message associated with the error code if the user inputs a malformed genomic interval

    Parameters:
    - error_code: Error code triggered by the malformed genomic interval

    Returns:
    - Message associated with the given error code
    """
    for _, code_message in errors.items():
        if code_message.code == error_code:
            return code_message.message


def is_one_digit_chromosome(chromosome):
    """
    Checks if given chromosome only has a single digit (e.g., Chr1, Chr2)

    Parameters:
    - chromosome: Chromosome to be checked

    Returns:
    - True if given chromosome only has a single digit; False, otherwise
    """
    # Examples: Chr1, Chr2
    return len(chromosome) == len('Chr') + 1


def pad_one_digit_chromosome(chromosome):
    """
    Prepends a 0 to the chromosome number if it only has a single digit
    For example, if the input is 'Chr1', it returns 'Chr01'

    This function assumes that the given chromosome only has a single digit

    Parameters:
    - chromosome: Chromosome to be padded

    Returns:
    - Chromosome with a leading 0 prepended
    """
    return chromosome[:-1] + '0' + chromosome[-1]


def to_genomic_interval(genomic_interval_str):
    """
    Converts a genomic interval extracted from the user input into a Genomic_interval tuple
    If the genomic interval is malformed, it returns the error code, alongside the genomic interval

    Parameters:
    - genomic_interval_str: Genomic interval extracted from the user input

    Returns:
    - If the genomic interval is valid: Genomic_interval tuple
    - Otherwise: Tuple containing the triggered error code and the genomic interval
    """
    try:
        chrom, interval = genomic_interval_str.split(":")
        if is_one_digit_chromosome(chrom):
            chrom = pad_one_digit_chromosome(chrom)

        # Change 'chr' to 'Chr'
        chrom = re.sub(r'chr', 'Chr', chrom, flags=re.IGNORECASE)

        if not chrom.startswith('Chr') or not chrom[3].isdigit():
            return errors['NO_CHROM_INTERVAL_SEP'].code, genomic_interval_str

    except ValueError:
        return errors['NO_CHROM_INTERVAL_SEP'].code, genomic_interval_str

    try:
        start, stop = interval.split("-")
    except ValueError:
        return errors['NO_START_STOP_SEP'].code, genomic_interval_str

    try:
        start = int(start)
        stop = int(stop)
    except ValueError:
        return errors['START_STOP_NOT_INT'].code, genomic_interval_str

    if start > stop:
        return errors['START_GREATER_THAN_STOP'].code, genomic_interval_str

    return Genomic_interval(chrom, start, stop)


def sanitize_nb_intervals_str(nb_intervals_str):
    """
    Sanitizes the genomic intervals entered by the user by removing spaces and removing trailing semicolons

    Parameters:
    - nb_intervals_str: Genomic intervals entered by the user

    Returns:
    - Sanitized genomic interval
    """
    nb_intervals_str = nb_intervals_str.replace(' ', '')
    nb_intervals_str = nb_intervals_str.rstrip(';')

    return nb_intervals_str


def get_genomic_intervals_from_input(nb_intervals_str):
    """
    Extracts the Genomic_interval tuples from the genomic intervals entered by the user

    Parameters:
    - nb_intervals_str: Genomic intervals entered by the user

    Returns:
    - List of Genomic_interval tuples
    """
    nb_intervals_str = sanitize_nb_intervals_str(nb_intervals_str)
    nb_intervals = []

    nb_intervals_split = nb_intervals_str.split(";")

    for interval_str in nb_intervals_split:
        interval = to_genomic_interval(interval_str)

        # Trap if at least one of the genomic intervals is malformed
        if is_error(interval):
            return interval
        else:
            nb_intervals.append(interval)

    return nb_intervals

# ============================================================================
# Utility functions for displaying lift-over results and sanitizng accessions
# ============================================================================


def get_tabs():
    """
    Returns the tabs to be displayed in the liftover results
    The tabs do not include those that are specific to a reference

    Returns:
    - Tabs to be displayed in the liftover results (except those specific to a reference)
    """
    return ['All Genes', 'Common Genes', 'Nipponbare']


def get_tab_id(tab):
    """
    Returns the index of given tab with respect to the tabs to be displayed in the liftover results

    Parameters:
    - tab: Tab whose idnex is to be returned

    Returns:
    - Index of given tab with respect to the tabs to be displayed in the liftover results
    """
    return f'tab-{get_tabs().index(tab)}'


def sanitize_other_refs(other_refs):
    """
    Returns the references (other than Nipponbare) selected by the user

    The need for this function is motivated by the fact that, when the user only chooses one reference,
    the data type of this chosen value is string (not list)

    Parameters:
    - other_refs: References (other than Nipponbare) selected by the user

    Returns:
    - List of references (other than Nipponbare) selected by the user
    """
    if other_refs:
        if isinstance(other_refs, str):
            return [other_refs]
        else:
            return other_refs

    return []


def sanitize_gene_id(gene_id):
    """
    Removes "gene:" prefix in given accession

    Parameters:
    - gene_id: Accession

    Returns:
    - Accession without the "gene:" prefix
    """
    if gene_id[:len('gene:')] == 'gene:':
        return gene_id[len('gene:'):]

    return gene_id


# ===============================================
# Utility functions for OGI-to-reference mapping
# ===============================================


def get_ogi_list(accession_ids, ogi_mapping):
    """
    Returns the list of equivalent OGIs of given accessions

    Parameters:
    - accession_ids: Accessions
    - ogi_mapping: OGI-to-accession mapping dictionary

    Returns:
    - list of equivalent OGIs of given accessions
    """
    ogi_list = [ogi_mapping[accession_id] for accession_id in accession_ids]

    return ogi_list


# ==================================================
# Utility function related to QTARO and Text Mining
# ==================================================


def get_qtaro_entry(gene, mapping):
    try:
        qtaro_str = '<ul style="margin-bottom: 0; padding: 0;">'
        for character_major in sorted(mapping[gene]):
            qtaro_str += '<li>' + character_major + '<ul>'
            for character_minor in sorted(mapping[gene][character_major]):
                pubs = ['<li>' + get_doi_link_single_str(
                    pub) + '</li>' for pub in mapping[gene][character_major][character_minor]]
                qtaro_str += '<li>' + character_minor + \
                    '<ul>' + ''.join(pubs) + '</ul></li>'
            qtaro_str += '</ul></li><br>'

        # Remove the line break after the last character major
        return qtaro_str[:-len("<br>")] + '</ul>'
    except KeyError:
        return NULL_PLACEHOLDER


def get_qtaro_entries(genes, qtaro_mapping):
    return [get_qtaro_entry(gene, qtaro_mapping) for gene in genes]


def get_pubmed_entry(gene, pubmed_mapping):
    try:
        pubmed_ids = [get_pubmed_link_single_str(pubmed_id[0]) for pubmed_id in sorted(
            pubmed_mapping[gene].items(), key=lambda x: x[1], reverse=True)]
    except KeyError:
        return NULL_PLACEHOLDER

    return '\n'.join(pubmed_ids)


def get_pubmed_entries(genes, pubmed_mapping):
    return [get_pubmed_entry(gene, pubmed_mapping) for gene in genes]


def get_interpro_entry(gene, interpro_mapping, iric_mapping):
    try:
        return '<br><br>'.join([get_interpro_link_single_str(entry[1], entry[0])
                                for entry in sorted(interpro_mapping[iric_mapping[gene]]) if entry[1]])
    except KeyError:
        return NULL_PLACEHOLDER


def get_interpro_entries(genes, interpro_mapping, iric_mapping):
    return [get_interpro_entry(gene, interpro_mapping, iric_mapping) for gene in genes]


def get_pfam_entry(gene, pfam_mapping, iric_mapping):
    try:
        return '<br><br>'.join([get_pfam_link_single_str(entry[1], entry[0])
                                for entry in sorted(pfam_mapping[iric_mapping[gene]]) if entry[1]])
    except KeyError:
        return NULL_PLACEHOLDER


def get_pfam_entries(genes, pfam_mapping, iric_mapping):
    return [get_pfam_entry(gene, pfam_mapping, iric_mapping) for gene in genes]


def get_rapdb_entry(gene, rapdb_mapping):
    if rapdb_mapping[gene]:
        return '<br>'.join([get_rapdb_single_str(entry)
                            for entry in sorted(rapdb_mapping[gene]) if entry])

    return NULL_PLACEHOLDER


def get_rapdb_entries(genes, rapdb_mapping):
    return [get_rapdb_entry(gene, rapdb_mapping) for gene in genes]


def get_nb_ortholog(gene, nb_ortholog_mapping):
    if nb_ortholog_mapping[gene]:
        return '<br>'.join(map(get_rgi_genecard_link_single_str, nb_ortholog_mapping[gene]))

    return NULL_PLACEHOLDER


# ========================
# Functions for lift-over
# ========================

def get_genes_in_Nb(genomic_intervals):
    temp_output_dir = get_path_to_temp(
        genomic_intervals, Constants.TEMP_LIFT_OVER)

    NB_GENES_FILENAME = f'{temp_output_dir}/nb_genes.csv'
    if path_exists(NB_GENES_FILENAME):
        nb_genes = pd.read_csv(NB_GENES_FILENAME)
        return nb_genes, nb_genes['Name'].values.tolist()

    make_dir(temp_output_dir)
    NB_GENES_FILENAME_WITH_TIMESTAMP = append_timestamp_to_filename(
        NB_GENES_FILENAME)

    nb_genes = get_genes_in_Nb_if_not_exist(genomic_intervals)
    nb_genes[0].to_csv(NB_GENES_FILENAME_WITH_TIMESTAMP, index=False)
    try:
        os.replace(NB_GENES_FILENAME_WITH_TIMESTAMP, NB_GENES_FILENAME)
    except:
        pass

    return nb_genes


def get_genes_in_Nb_if_not_exist(genomic_intervals):
    """
    Returns a data frame containing the genes in Nipponbare

    Parameters:
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Data frame containing the genes in Nipponbare
    """
    nb_intervals = get_genomic_intervals_from_input(genomic_intervals)

    dfs = []

    # Load and search GFF_DB of Nipponbare
    db = gffutils.FeatureDB(
        f'{Constants.ANNOTATIONS}/Nb/IRGSPMSU.gff.db', keep_order=True)

    with open(f'{Constants.OGI_MAPPING}/Nb_to_ogi.pickle', 'rb') as ogi_file, open(Constants.QTARO_DICTIONARY, 'rb') as qtaro_file,  open(f'{Constants.IRIC}/interpro.pickle', 'rb') as interpro_file, open(f'{Constants.IRIC}/pfam.pickle', 'rb') as pfam_file,  open(f'{Constants.IRIC_MAPPING}/msu_to_iric.pickle', 'rb') as iric_mapping_file, open(f'{Constants.TEXT_MINING_PUBMED}', 'rb') as pubmed_file, open(f'{Constants.MSU_MAPPING}/msu_to_rap.pickle', 'rb') as rapdb_file:
        ogi_mapping = pickle.load(ogi_file)
        qtaro_mapping = pickle.load(qtaro_file)
        interpro_mapping = pickle.load(interpro_file)
        pfam_mapping = pickle.load(pfam_file)
        iric_mapping = pickle.load(iric_mapping_file)
        pubmed_mapping = pickle.load(pubmed_file)
        rapdb_mapping = pickle.load(rapdb_file)

        for nb_interval in nb_intervals:
            genes_in_interval = list(db.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                               completely_within=False, featuretype='gene'))

            gene_ids_in_interval = [sanitize_gene_id(
                gene.id) for gene in genes_in_interval]

            # Construct the data frame
            df = pd.DataFrame({
                'OGI': get_ogi_list(gene_ids_in_interval, ogi_mapping),
                'Name': gene_ids_in_interval,
                'Chromosome': [gene.chrom for gene in genes_in_interval],
                'Start': [gene.start for gene in genes_in_interval],
                'End': [gene.end for gene in genes_in_interval],
                'Strand': [gene.strand for gene in genes_in_interval],
                'QTL Analyses': get_qtaro_entries(gene_ids_in_interval, qtaro_mapping),
                'PubMed Article IDs': get_pubmed_entries(gene_ids_in_interval, pubmed_mapping),
                'InterPro': get_interpro_entries(gene_ids_in_interval, interpro_mapping, iric_mapping),
                'Pfam': get_pfam_entries(gene_ids_in_interval, pfam_mapping, iric_mapping),
                'RAP-DB': get_rapdb_entries(gene_ids_in_interval, rapdb_mapping),
            })

            dfs.append(df)

    try:
        table_gene_ids = pd.concat(dfs, ignore_index=True)

        # Read in dataframe containing gene descriptions
        gene_description_df = pd.read_csv(
            f'{Constants.GENE_DESCRIPTIONS}/Nb/Nb_gene_descriptions.csv')

        # Right merge because some genes do not have descriptions or UniProtKB/Swiss-Prot IDs
        gene_description_df = gene_description_df.set_index('Gene_ID')
        table_gene_ids = table_gene_ids.set_index('Name')
        table = gene_description_df.join(table_gene_ids, how='right')

        # Reorder columns
        table = table.reset_index()
        table = table[NB_COLUMNS]

        table['UniProtKB/Swiss-Prot'] = get_uniprot_link(
            table, 'UniProtKB/Swiss-Prot')

        table = table.fillna(
            NULL_PLACEHOLDER).drop_duplicates().sort_values('Name')

        if table.shape[0] == 0:
            return create_empty_df_with_cols(NB_COLUMNS), table['Name'].values.tolist()

        return table, table['Name'].values.tolist()

    except ValueError:      # No results to concatenate
        return create_empty_df_with_cols(NB_COLUMNS), table['Name'].values.tolist()


def get_genes_in_other_ref(ref, nb_intervals):
    """
    Returns a data frame containing the genes in references other than Nipponbare
    Nipponbare is handled by get_genes_in_Nb()

    Parameters:
    - ref: Reference
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Data frame containing the genes in references other than Nipponbare
    """
    nb_intervals = get_genomic_intervals_from_input(nb_intervals)
    dfs = []

    # Get intervals from other refs that align to (parts) of the input loci
    db_align = gffutils.FeatureDB(
        f'{Constants.ALIGNMENTS}/Nb_{ref}/Nb_{ref}.gff.db')

    # Get corresponding intervals on ref
    db_annotation = gffutils.FeatureDB(
        f"{Constants.ANNOTATIONS}/{ref}/{ref}.gff.db")

    ogi_file_path = f'{Constants.OGI_MAPPING}/{ref}_to_ogi.pickle'

    with open(ogi_file_path, 'rb') as ogi_file:
        ogi_mapping = pickle.load(ogi_file)

        for nb_interval in nb_intervals:
            gff_intersections = list(db_align.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                                     completely_within=False))
            for intersection in gff_intersections:
                ref_interval = to_genomic_interval(
                    intersection.attributes['Name'][0])

                # Skip if assembler does not know what to do with contig
                if is_error(ref_interval):
                    continue

                genes_in_interval = list(db_annotation.region(region=(ref_interval.chrom, ref_interval.start, ref_interval.stop),
                                                              completely_within=False, featuretype='gene'))
                gene_ids_in_interval = [sanitize_gene_id(
                    gene.id) for gene in genes_in_interval]

                # Map accessions to their respective OGIs
                ogi_list = get_ogi_list(gene_ids_in_interval, ogi_mapping)

                # Construct the data frame
                df = pd.DataFrame({
                    'OGI': ogi_list,
                    'Name': gene_ids_in_interval,
                    'Chromosome': [gene.chrom for gene in genes_in_interval],
                    'Start': [gene.start for gene in genes_in_interval],
                    'End': [gene.end for gene in genes_in_interval],
                    'Strand': [gene.strand for gene in genes_in_interval]
                })

                dfs.append(df)

    try:
        table = pd.concat(dfs, ignore_index=True)
        if table.shape[0] == 0:
            return create_empty_df_with_cols(OTHER_REF_COLUMNS)

        return table

    except ValueError:      # No results to concatenate
        return create_empty_df_with_cols(OTHER_REF_COLUMNS)


def get_common_genes(refs, genomic_intervals):
    """
    Returns a data frame containing the genes common to the given references

    Parameters:
    - ref: References
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Data frame containing the genes common to the given references
    """
    # No cultivars selected
    if not refs:
        return create_empty_df_with_cols(NO_REFS_COLUMNS)

    all_genes = get_all_genes(refs, genomic_intervals)
    all_genes = all_genes[['OGI'] + refs]

    mask = True
    for ref in refs:
        mask &= (all_genes[ref] != NULL_PLACEHOLDER)

    common_genes = all_genes.loc[mask].drop_duplicates().sort_values('OGI')

    return common_genes


def get_all_genes(refs, genomic_intervals):
    if refs:
        temp_output_dir = get_path_to_temp(
            genomic_intervals, Constants.TEMP_LIFT_OVER, shorten_name('_'.join(refs)))
    else:
        temp_output_dir = get_path_to_temp(
            genomic_intervals, Constants.TEMP_LIFT_OVER)

    ALL_GENES_FILENAME = f'{temp_output_dir}/all_genes.csv'
    if path_exists(ALL_GENES_FILENAME):
        return pd.read_csv(ALL_GENES_FILENAME)

    make_dir(temp_output_dir)
    ALL_GENES_FILENAME_WITH_TIMESTAMP = append_timestamp_to_filename(
        ALL_GENES_FILENAME)

    all_genes = get_all_genes_if_not_exist(refs, genomic_intervals)
    all_genes.to_csv(ALL_GENES_FILENAME_WITH_TIMESTAMP, index=False)
    try:
        os.replace(ALL_GENES_FILENAME_WITH_TIMESTAMP, ALL_GENES_FILENAME)
    except:
        pass

    return all_genes


def get_all_genes_if_not_exist(refs, genomic_intervals):
    """
    Returns a data frame containing all the genes (i.e., the set-theoretic union of all the genes)
    in Nipponbare, as well as orthologous genes in the given references

    Parameters:
    - ref: References (other than Nipponbare)
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Data frame containing all the genes
    """

    # Check if all genes table has already been cached since it will be used for the computation

    genes_in_nb = get_genes_in_Nb(genomic_intervals)[0]
    genes_in_nb = genes_in_nb[['OGI', 'Name']]

    common_genes = genes_in_nb
    for ref in refs:
        if ref != 'Nipponbare':
            genes_in_other_ref = get_genes_in_other_ref(ref, genomic_intervals)
            genes_in_other_ref = genes_in_other_ref[['OGI', 'Name']]

            common_genes = common_genes.set_index('OGI')
            genes_in_other_ref = genes_in_other_ref.set_index('OGI')

            common_genes = common_genes.join(
                genes_in_other_ref, how='outer', lsuffix='_x', rsuffix='_y')

            common_genes = common_genes.reset_index()

            common_genes = common_genes.rename(
                columns={'Name_x': 'Nipponbare', 'Name_y': ref, 'Name': ref})

    common_genes = common_genes.rename(
        columns={'Name': 'Nipponbare'}).fillna(NULL_PLACEHOLDER).drop_duplicates().sort_values('OGI')

    return common_genes


def get_unique_genes_in_other_ref(refs, ref, genomic_intervals):
    """
    Returns a data frame containing the genes in a reference that are not present in Nipponbare

    Parameters:
    - ref: References
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Data frame containing the genes in a reference that are not present in Nipponbare
    """
    all_genes = get_all_genes(refs, genomic_intervals)

    unique_genes = all_genes.loc[(all_genes['Nipponbare'] ==
                                 NULL_PLACEHOLDER) & (all_genes[ref] != NULL_PLACEHOLDER)]
    unique_genes = unique_genes.rename(columns={ref: 'Name'})

    gene_description_df = pd.read_csv(
        f'{Constants.GENE_DESCRIPTIONS}/{ref}/{ref}_gene_descriptions.csv')

    # Right merge because some genes do not have descriptions or UniProtKB/Swiss-Prot IDs
    gene_description_df = gene_description_df.set_index('Gene_ID')
    unique_genes = unique_genes.set_index('Name')
    unique_genes = gene_description_df.join(unique_genes, how='right')
    unique_genes = unique_genes.reset_index()

    with open(f'{Constants.NB_MAPPING}/{ref}_to_Nb.pickle', 'rb') as f:
        nb_ortholog_mapping = pickle.load(f)

        unique_genes['Ortholog in Nipponbare'] = unique_genes.apply(
            lambda x: get_nb_ortholog(x['Name'], nb_ortholog_mapping), axis=1)

    unique_genes = unique_genes[FRONT_FACING_COLUMNS +
                                ['Ortholog in Nipponbare']]

    unique_genes['UniProtKB/Swiss-Prot'] = get_uniprot_link(
        unique_genes, 'UniProtKB/Swiss-Prot')

    unique_genes = unique_genes.fillna(
        NULL_PLACEHOLDER).drop_duplicates().sort_values('Name')

    if unique_genes.shape[0] == 0:
        return create_empty_df_with_cols(FRONT_FACING_COLUMNS + ['Ortholog in Nipponbare'])

    return unique_genes
