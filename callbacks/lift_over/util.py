import pickle
from collections import defaultdict, namedtuple

import gffutils
import pandas as pd

from ..constants import Constants
from ..general_util import *
from ..links_util import *

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

NB_COLUMNS = ['Name', 'Description', 'UniProtKB/Swiss-Prot',
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


def get_ogi_nb(nb_intervals):
    """
    Maps Nipponbare accessions (obtained from a list of Genomic_interval tuples) to their respective OGIs

    Parameters:
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Set containing all unique OGIs after performing OGI-to-Nipponbare mapping
    - OGI-to-Nipponbare mapping dictionary
    """

    # All unique OGIs
    final_ogi_set = set()

    # OGI-to-NB mapping dictionary (one OGI can map to multiple NB accessions)
    final_ogi_dict = defaultdict(set)

    for nb_interval in nb_intervals:
        # Load and search GFF_DB of Nipponbare
        db = gffutils.FeatureDB(
            f'{Constants.ANNOTATIONS}/Nb/IRGSPMSU.gff.db', keep_order=True)
        genes_in_interval = list(db.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                           completely_within=False, featuretype='gene'))

        # Map Nipponbare accessions to OGIs
        ogi_mapping_path = f'{Constants.OGI_MAPPING}/Nb_to_ogi.pickle'
        with open(ogi_mapping_path, 'rb') as f:
            ogi_mapping = pickle.load(f)
            for gene in genes_in_interval:
                gene_id = sanitize_gene_id(gene.id)
                ogi = ogi_mapping[gene_id]

                final_ogi_set.add(ogi)
                final_ogi_dict[ogi].add(gene_id)

    return final_ogi_set, final_ogi_dict


def get_ogi_other_ref(ref, nb_intervals):
    """
    Maps reference-specific accessions (obtained from a list of Genomic_interval tuples) to their respective OGIs
    "Reference" refers to a reference other than Nipponbare
    Nipponbare reference is handled by get_ogi_nb()

    Parameters:
    - ref: Reference
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Set containing all unique OGIs after performing OGI-to-reference mapping
    - OGI-to-reference mapping dictionary
    """

    # All unique OGIs
    final_ogi_set = set()

    # OGI-to-NB mapping dictionary (one OGI can map to multiple NB accessions)
    final_ogi_dict = defaultdict(set)

    # Get intervals from other refs that align to (parts) of the input loci
    db_align = gffutils.FeatureDB(
        f'{Constants.ALIGNMENTS}/{"Nb_"+str(ref)}/{"Nb_"+str(ref)}.gff.db')

    # Get corresponding intervals on ref
    db_annotation = gffutils.FeatureDB(
        f"{Constants.ANNOTATIONS}/{ref}/{ref}.gff.db".format(ref))

    for nb_interval in nb_intervals:
        gff_intersections = list(db_align.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                                 completely_within=False))
        for intersection in gff_intersections:
            ref_interval = to_genomic_interval(
                intersection.attributes['Name'][0])
            genes_in_interval = list(db_annotation.region(region=(ref_interval.chrom, ref_interval.start, ref_interval.stop),
                                                          completely_within=False, featuretype='gene'))

            # Map reference-specific accessions to OGIs
            ogi_mapping_path = f'{Constants.OGI_MAPPING}/{ref}_to_ogi.pickle'
            with open(ogi_mapping_path, 'rb') as f:
                ogi_mapping = pickle.load(f)
                for gene in genes_in_interval:
                    gene_id = sanitize_gene_id(gene.id)
                    ogi = ogi_mapping[gene_id]

                    final_ogi_set.add(ogi)
                    final_ogi_dict[ogi].add(gene_id)

    return final_ogi_set, final_ogi_dict

# ==================================================
# Utility function related to QTARO and Text Mining
# ==================================================


def get_qtaro_entry(mapping, gene):
    try:
        qtaro_str = '<ul style="margin-bottom: 0; padding: 0;">'
        pub_idx = 1
        for character_major in mapping[gene]:
            qtaro_str += '<li>' + character_major + '<ul>'
            for character_minor in mapping[gene][character_major]:
                pubs = []
                for pub in mapping[gene][character_major][character_minor]:
                    pubs.append(
                        '<li>' + get_doi_link_single_str(pub, pub_idx) + '</li>')
                    pub_idx += 1

                qtaro_str += '<li>' + character_minor + \
                    '<ul>' + ''.join(pubs) + '</ul></li>'
            qtaro_str += '</ul></li><br>'

        # Remove the line break after the last character major
        return qtaro_str[:-len("<br>")] + '</ul>'
    except KeyError:
        return NULL_PLACEHOLDER


def get_qtaro_entries(mapping, genes):
    return [get_qtaro_entry(mapping, gene) for gene in genes]


def get_pubmed_entry(gene):
    try:
        with open(f'{Constants.TEXT_MINING_PUBMED}/{gene}.pickle', 'rb') as f:
            mapping = pickle.load(f)

        pubmed_ids = [get_pubmed_link_single_str(pubmed_id[0]) for pubmed_id in sorted(
            mapping.items(), key=lambda x: x[1], reverse=True)]
    except FileNotFoundError:
        return NULL_PLACEHOLDER

    pubmed_str = ''
    for idx, pubmed in enumerate(pubmed_ids):
        if idx % 2 == 0:
            pubmed_str += f'{pubmed}&nbsp;&nbsp;&nbsp;'
        else:
            pubmed_str += f'{pubmed}\n'

    if pubmed_str[-1] == '\n':        # Ends in a newline
        return pubmed_str[:-len('\n')]

    return pubmed_str[:-len('&nbsp;&nbsp;&nbsp;')]


def get_nb_ortholog(gene, ref):
    with open(f'{Constants.NB_MAPPING}/{ref}_to_Nb.pickle', 'rb') as f:
        mapping = pickle.load(f)

        if mapping[gene]:
            return ', '.join(mapping[gene])

        return NULL_PLACEHOLDER


# ========================
# Functions for lift-over
# ========================


def get_genes_in_Nb(nb_intervals):
    """
    Returns a data frame containing the genes in Nipponbare

    Parameters:
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Data frame containing the genes in Nipponbare
    """
    dfs = []

    for nb_interval in nb_intervals:
        # Load and search GFF_DB of Nipponbare
        db = gffutils.FeatureDB(
            f'{Constants.ANNOTATIONS}/Nb/IRGSPMSU.gff.db', keep_order=True)
        genes_in_interval = list(db.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                           completely_within=False, featuretype='gene'))

        # Map accessions to their respective OGIs
        ogi_mapping_path = f'{Constants.OGI_MAPPING}/Nb_to_ogi.pickle'
        ogi_list = []
        with open(ogi_mapping_path, 'rb') as f:
            ogi_mapping = pickle.load(f)
            ogi_list = get_ogi_list([sanitize_gene_id(gene.id)
                                     for gene in genes_in_interval], ogi_mapping)

        # Get QTARO annotations
        with open(Constants.QTARO_DICTIONARY, 'rb') as f:
            qtaro_dict = pickle.load(f)
            qtaro_list = get_qtaro_entries(
                qtaro_dict, [gene.id for gene in genes_in_interval])

        pubmed_ids = [get_pubmed_entry(gene.id) for gene in genes_in_interval]

        # Construct the data frame
        df = pd.DataFrame({
            'OGI': ogi_list,
            'Name': [gene.id for gene in genes_in_interval],
            'Chromosome': [gene.chrom for gene in genes_in_interval],
            'Start': [gene.start for gene in genes_in_interval],
            'End': [gene.end for gene in genes_in_interval],
            'Strand': [gene.strand for gene in genes_in_interval],
            'QTL Analyses': qtaro_list,
            'PubMed Article IDs': pubmed_ids
        })

        dfs.append(df)

    try:
        table_gene_ids = pd.concat(dfs, ignore_index=True)
        # Read in dataframe containing gene descriptions
        gene_description_df = pd.read_csv(
            f'{Constants.GENE_DESCRIPTIONS}/Nb/Nb_gene_descriptions.csv')
        # Right merge because some genes do not have descriptions or UniProtKB/Swiss-Prot IDs
        table = pd.merge(gene_description_df, table_gene_ids,
                         left_on='Gene_ID', right_on='Name', how='right')

        # Reorder columns
        table = table[NB_COLUMNS]

        table['UniProtKB/Swiss-Prot'] = get_uniprot_link(
            table, 'UniProtKB/Swiss-Prot')

        table = table.fillna(NULL_PLACEHOLDER)

        if table.shape[0] == 0:
            return create_empty_df_with_cols(NB_COLUMNS)(), table['Name'].values.tolist()

        return table, table['Name'].values.tolist()

    except ValueError:      # No results to concatenate
        return create_empty_df_with_cols(NB_COLUMNS)(), table['Name'].values.tolist()


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

    # Get intervals from other refs that align to (parts) of the input loci
    db_align = gffutils.FeatureDB(
        f'{Constants.ALIGNMENTS}/{"Nb_"+str(ref)}/{"Nb_"+str(ref)}.gff.db')

    # Get corresponding intervals on ref
    db_annotation = gffutils.FeatureDB(
        f"{Constants.ANNOTATIONS}/{ref}/{ref}.gff.db")

    dfs = []

    for nb_interval in nb_intervals:
        gff_intersections = list(db_align.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                                 completely_within=False))
        for intersection in gff_intersections:
            ref_interval = to_genomic_interval(
                intersection.attributes['Name'][0])
            genes_in_interval = list(db_annotation.region(region=(ref_interval.chrom, ref_interval.start, ref_interval.stop),
                                                          completely_within=False, featuretype='gene'))

            # Map accessions to their respective OGIs
            ogi_mapping_path = f'{Constants.OGI_MAPPING}/{ref}_to_ogi.pickle'
            ogi_list = []
            with open(ogi_mapping_path, 'rb') as f:
                ogi_mapping = pickle.load(f)
                ogi_list = get_ogi_list([sanitize_gene_id(gene.id)
                                         for gene in genes_in_interval], ogi_mapping)

            # Construct the data frame
            df = pd.DataFrame({
                'OGI': ogi_list,
                'Name': [sanitize_gene_id(gene.id) for gene in genes_in_interval],
                'Chromosome': [gene.chrom for gene in genes_in_interval],
                'Start': [gene.start for gene in genes_in_interval],
                'End': [gene.end for gene in genes_in_interval],
                'Strand': [gene.strand for gene in genes_in_interval]
            })
            dfs.append(df)

    try:
        table = pd.concat(dfs, ignore_index=True)
        if table.shape[0] == 0:
            return create_empty_df_with_cols(OTHER_REF_COLUMNS)()

        return table

    except ValueError:      # No results to concatenate
        return create_empty_df_with_cols(OTHER_REF_COLUMNS)()


def get_common_genes(refs, nb_intervals):
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
        return create_empty_df_with_cols(NO_REFS_COLUMNS)()

    common_genes = None
    for ref in refs:
        if ref != 'Nipponbare':
            genes_in_ref = get_genes_in_other_ref(ref, nb_intervals)
        else:
            genes_in_ref = get_genes_in_Nb(nb_intervals)[0]

        genes_in_ref = genes_in_ref[['OGI', 'Name']]

        try:
            common_genes = pd.merge(
                common_genes, genes_in_ref, on='OGI')
        # First instance of merging (that is, common_genes is still None)
        except TypeError:
            common_genes = genes_in_ref

        common_genes = common_genes.rename(
            columns={'Name_x': 'Nipponbare', 'Name_y': ref, 'Name': ref})

    common_genes = common_genes.rename(
        columns={'Name': 'Nipponbare'}).dropna().drop_duplicates()

    return common_genes


def get_all_genes(refs, nb_intervals):
    """
    Returns a data frame containing all the genes (i.e., the set-theoretic union of all the genes)
    in Nipponbare, as well as orthologous genes in the given references

    Parameters:
    - ref: References (other than Nipponbare)
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Data frame containing all the genes
    """
    genes_in_nb = get_genes_in_Nb(nb_intervals)[0]
    genes_in_nb = genes_in_nb[['OGI', 'Name']]

    common_genes = genes_in_nb
    for ref in refs:
        if ref != 'Nipponbare':
            genes_in_other_ref = get_genes_in_other_ref(ref, nb_intervals)
            genes_in_other_ref = genes_in_other_ref[['OGI', 'Name']]
            common_genes = pd.merge(
                common_genes, genes_in_other_ref, on='OGI', how='outer')

            common_genes = common_genes.rename(
                columns={'Name_x': 'Nipponbare', 'Name_y': ref, 'Name': ref})

    common_genes = common_genes.rename(
        columns={'Name': 'Nipponbare'}).fillna(NULL_PLACEHOLDER).drop_duplicates()

    return common_genes


def get_unique_genes_in_other_ref(ref, nb_intervals):
    """
    Returns a data frame containing the genes in a reference that are not present in Nipponbare

    Parameters:
    - ref: References
    - nb_intervals: List of Genomic_interval tuples

    Returns:
    - Data frame containing the genes in a reference that are not present in Nipponbare
    """
    genes_in_nb = get_genes_in_Nb(nb_intervals)[0]
    genes_in_other_ref = get_genes_in_other_ref(ref, nb_intervals)

    genes_in_nb = genes_in_nb[['OGI']]

    # Get set difference
    unique_genes = pd.concat([genes_in_other_ref, genes_in_nb, genes_in_nb]).drop_duplicates(
        subset=['OGI'], keep=False)

    gene_description_df = pd.read_csv(
        f'{Constants.GENE_DESCRIPTIONS}/{ref}/{ref}_gene_descriptions.csv')
    # Right merge because some genes do not have descriptions or UniProtKB/Swiss-Prot IDs
    unique_genes = pd.merge(gene_description_df, unique_genes,
                            left_on='Gene_ID', right_on='Name', how='right')

    unique_genes['Ortholog in Nipponbare'] = unique_genes.apply(
        lambda x: get_nb_ortholog(x['Name'], ref), axis=1)

    unique_genes = unique_genes[FRONT_FACING_COLUMNS +
                                ['Ortholog in Nipponbare']]

    unique_genes['UniProtKB/Swiss-Prot'] = get_uniprot_link(
        unique_genes, 'UniProtKB/Swiss-Prot')

    unique_genes = unique_genes.fillna(NULL_PLACEHOLDER)

    if unique_genes.shape[0] == 0:
        return create_empty_df_with_cols(FRONT_FACING_COLUMNS + ['Ortholog in Nipponbare'])

    return unique_genes
