import pickle
from collections import defaultdict, namedtuple

import gffutils
import pandas as pd

from ..constants import Constants
from ..general_util import *

const = Constants()
Genomic_interval = namedtuple('Genomic_interval', ['chrom', 'start', 'stop'])
Error_message = namedtuple('Error_message', ['code', 'message'])

errors = {
    'NO_CHROM_INTERVAL_SEP': Error_message(1, 'A genomic interval should be entered as chrom:start-end. Use a semicolon (;) to separate multiple intervals'),
    'NO_START_STOP_SEP': Error_message(2, 'Specify a valid start and end for the genomic interval'),
    'START_STOP_NOT_INT': Error_message(3, 'The start and end of a genomic interval should be integers'),
    'START_GREATER_THAN_STOP': Error_message(4, 'The start of a genomic interval should not be past the end')
}


def create_empty_df():
    """
    Returns an empty data frame if there are no results

    Returns:
    - Empty data frame
    """
    return create_empty_df_with_cols(['OGI', 'Name', 'Chromosome', 'Start', 'End', 'Strand'])

# =====================================================
# Utility functions for parsing input genomic interval
# =====================================================


def is_error(intervals):
    """
    Returns True if the genomic interval entered by the user 
    """
    # The first element is the error code and the second element is the malformed interval
    return isinstance(intervals[0], int)


def get_error_message(error_code):
    return errors[error_code].message


def sanitize_other_refs(other_refs):
    if other_refs:
        if isinstance(other_refs, str):
            return [other_refs]
        else:
            return other_refs

    return []


def sanitize_nb_intervals_str(nb_intervals_str):
    # Remove spaces
    nb_intervals_str = nb_intervals_str.replace(' ', '')

    # Remove trailing semicolons
    nb_intervals_str = nb_intervals_str.rstrip(';')

    return nb_intervals_str

# convert 'Chr01:10000-25000' to a Genomic_Interval named tuple


def is_one_digit_chromosome(chromosome):
    # Examples: Chr1, Chr2
    return len(chromosome) == len('Chr') + 1


def pad_one_digit_chromosome(chromosome):
    # Convert 'Chr1' to 'Chr01'
    return chromosome[:-1] + '0' + chromosome[-1]


def to_genomic_interval(interval_str):
    try:
        chrom, interval = interval_str.split(":")
        if is_one_digit_chromosome(chrom):
            chrom = pad_one_digit_chromosome(chrom)

    except ValueError:
        return errors['NO_CHROM_INTERVAL_SEP'].code, interval_str

    try:
        start, stop = interval.split("-")
    except ValueError:
        return errors['NO_START_STOP_SEP'].code, interval_str

    try:
        start = int(start)
        stop = int(stop)
    except ValueError:
        return errors['START_STOP_NOT_INT'].code, interval_str

    if start > stop:
        return errors['START_GREATER_THAN_STOP'].code, interval_str

    return Genomic_interval(chrom, start, stop)

# Split 'Chr01:10000-25000;;Chr01:22000-25000'


def get_genomic_intervals_from_input(nb_intervals_str):
    nb_intervals_str = sanitize_nb_intervals_str(nb_intervals_str)
    nb_intervals = []

    nb_intervals_split = nb_intervals_str.split(";")

    for interval_str in nb_intervals_split:
        interval = to_genomic_interval(interval_str)

        # Check if interval is malformed
        if is_error(interval):
            return interval
        else:
            nb_intervals.append(interval)

    return nb_intervals

# ================================
# Utility functions for lift-over
# ================================


def sanitize_gene_id(gene_id):
    # Remove 'gene' prefix from gene IDs (e.g., from N22)
    if gene_id[:len('gene:')] == 'gene:':
        return gene_id[len('gene:'):]

    return gene_id


def get_ogi_nb(nb_intervals):
    if is_error(nb_intervals):
        nb_intervals = []

    final_ogi_set = set()
    final_ogi_dict = defaultdict(set)

    for nb_interval in nb_intervals:
        # load and search GFF_DB of Nipponbare
        db = gffutils.FeatureDB(
            f'{const.ANNOTATIONS}/Nb/IRGSPMSU.gff.db', keep_order=True)
        genes_in_interval = list(db.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                           completely_within=False, featuretype='gene'))

        ogi_mapping_path = f'{const.OGI_MAPPING}/Nb_to_ogi.pickle'
        with open(ogi_mapping_path, 'rb') as f:
            ogi_mapping = pickle.load(f)
            for gene in genes_in_interval:
                gene_id = sanitize_gene_id(gene.id)
                ogi = ogi_mapping[gene_id]

                final_ogi_set.add(ogi)
                final_ogi_dict[ogi].add(gene_id)

    return final_ogi_set, final_ogi_dict


def get_ogi_other_ref(ref, nb_intervals):
    db_align = gffutils.FeatureDB(
        f'{const.ALIGNMENTS}/{"Nb_"+str(ref)}/{"Nb_"+str(ref)}.gff.db')
    db_annotation = gffutils.FeatureDB(
        f"{const.ANNOTATIONS}/{ref}/{ref}.gff.db".format(ref))
    # get corresponding intervals on ref
    if is_error(nb_intervals):
        nb_intervals = []

    final_ogi_set = set()
    final_ogi_dict = defaultdict(set)

    for nb_interval in nb_intervals:
        gff_intersections = list(db_align.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                                 completely_within=False))
        for intersection in gff_intersections:
            ref_interval = to_genomic_interval(
                intersection.attributes['Name'][0])
            genes_in_interval = list(db_annotation.region(region=(ref_interval.chrom, ref_interval.start, ref_interval.stop),
                                                          completely_within=False, featuretype='gene'))

            ogi_mapping_path = f'{const.OGI_MAPPING}/{ref}_to_ogi.pickle'
            with open(ogi_mapping_path, 'rb') as f:
                ogi_mapping = pickle.load(f)
                for gene in genes_in_interval:
                    gene_id = sanitize_gene_id(gene.id)
                    ogi = ogi_mapping[gene_id]

                    final_ogi_set.add(ogi)
                    final_ogi_dict[ogi].add(gene_id)

    return final_ogi_set, final_ogi_dict


def get_overlapping_ogi(refs, nb_intervals):
    ogi_list = []
    accession_list = []

    ogi_nb_set, ogi_nb_dict = get_ogi_nb(nb_intervals)
    ogi_other_refs = []

    if 'Nb' in refs:
        ogi_list.append(ogi_nb_set)
        accession_list.append(ogi_nb_dict)

    idx = 0
    for ref in refs:
        if ref != 'Nb':
            ogi_other_refs.append(get_ogi_other_ref(ref, nb_intervals))
            ogi_list.append(ogi_other_refs[idx][0])
            accession_list.append(ogi_other_refs[idx][1])

            idx += 1

    overlapping_ogi = []
    if ogi_list:
        overlapping_ogi = list(set.intersection(*ogi_list))

    df_matrix = []
    for ogi in overlapping_ogi:
        ogi_row = [ogi]
        idx = 0
        for ref in refs:
            ogi_row.append(', '.join(accession_list[idx][ogi]))
            idx += 1

        df_matrix.append(ogi_row)

    if not df_matrix:
        df_matrix.append(['-' for _ in range(len(refs) + 1)])

    df = pd.DataFrame(df_matrix, columns=['OGI'] + refs)

    return df


def get_genes_from_Nb(nb_intervals):
    dfs = []
    if is_error(nb_intervals):
        nb_intervals = []

    for nb_interval in nb_intervals:
        # load and search GFF_DB of Nipponbare
        db = gffutils.FeatureDB(
            f'{const.ANNOTATIONS}/Nb/IRGSPMSU.gff.db', keep_order=True)
        genes_in_interval = list(db.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                           completely_within=False, featuretype='gene'))

        ogi_mapping_path = f'{const.OGI_MAPPING}/Nb_to_ogi.pickle'
        ogi_list = []
        with open(ogi_mapping_path, 'rb') as f:
            ogi_mapping = pickle.load(f)
            ogi_list = get_ogi([sanitize_gene_id(gene.id)
                                for gene in genes_in_interval], ogi_mapping)

        # TODO should be a better way to do this?
        df = pd.DataFrame({
            'OGI': ogi_list,
            'Name': [gene.id for gene in genes_in_interval],
            'Chromosome': [gene.chrom for gene in genes_in_interval],
            'Start': [gene.start for gene in genes_in_interval],
            'End': [gene.end for gene in genes_in_interval],
            'Strand': [gene.strand for gene in genes_in_interval]
        })
        dfs.append(df)

    # Return empty dataframe if there are no results to concatenate
    try:
        table_gene_ids = pd.concat(dfs, ignore_index=True)
        # read in dataframe containing gene descriptions
        gene_description_df = pd.read_csv(
            f'{const.GENE_DESCRIPTIONS}/Nb/Nb_gene_descriptions.csv')
        table = pd.merge(gene_description_df, table_gene_ids,
                         left_on='Gene_ID', right_on='Name')

        if table.shape[0] == 0:
            return create_empty_df(), table['Name'].values.tolist()

        return table, table['Name'].values.tolist()

    except ValueError:
        return create_empty_df(), table['Name'].values.tolist()


def get_genes_from_other_ref(ref, nb_intervals):
    # get intervals from other refs that align to (parts) of the input loci
    db_align = gffutils.FeatureDB(
        f'{const.ALIGNMENTS}/{"Nb_"+str(ref)}/{"Nb_"+str(ref)}.gff.db')
    db_annotation = gffutils.FeatureDB(
        f"{const.ANNOTATIONS}/{ref}/{ref}.gff.db")
    # get corresponding intervals on ref
    dfs = []
    if is_error(nb_intervals):
        nb_intervals = []

    for nb_interval in nb_intervals:
        gff_intersections = list(db_align.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                                 completely_within=False))
        for intersection in gff_intersections:
            ref_interval = to_genomic_interval(
                intersection.attributes['Name'][0])
            genes_in_interval = list(db_annotation.region(region=(ref_interval.chrom, ref_interval.start, ref_interval.stop),
                                                          completely_within=False, featuretype='gene'))

            ogi_mapping_path = f'{const.OGI_MAPPING}/{ref}_to_ogi.pickle'
            ogi_list = []
            with open(ogi_mapping_path, 'rb') as f:
                ogi_mapping = pickle.load(f)
                ogi_list = get_ogi([sanitize_gene_id(gene.id)
                                    for gene in genes_in_interval], ogi_mapping)

            df = pd.DataFrame({
                'OGI': ogi_list,
                'Name': [gene.id for gene in genes_in_interval],
                'Chromosome': [gene.chrom for gene in genes_in_interval],
                'Start': [gene.start for gene in genes_in_interval],
                'End': [gene.end for gene in genes_in_interval],
                'Strand': [gene.strand for gene in genes_in_interval]
            })
            dfs.append(df)

    # Return empty dataframe if there are no results to concatenate
    try:
        table = pd.concat(dfs, ignore_index=True)
        if table.shape[0] == 0:
            return create_empty_df()

        return table

    except ValueError:
        return create_empty_df()


def get_ogi(accession_ids, ogi_mapping):
    ogi_list = []
    for accession_id in accession_ids:
        ogi_list.append(ogi_mapping[accession_id])

    return ogi_list
