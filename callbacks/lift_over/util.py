import pickle
from collections import defaultdict, namedtuple

import gffutils
import pandas as pd

Genomic_interval = namedtuple('Genomic_interval', ['chrom', 'start', 'stop'])

# Error codes for genomic interval input
NO_CHROM_INTERVAL_SEP = 1
NO_START_STOP_SEP = 2
START_STOP_NOT_INT = 3
START_GREATER_THAN_STOP = 4

error_messages = {
    NO_CHROM_INTERVAL_SEP: 'A genomic interval should be entered as chrom:start-end. Use a semicolon (;) to separate multiple intervals',
    NO_START_STOP_SEP: 'Specify a valid start and end for the genomic interval',
    START_STOP_NOT_INT: 'The start and end of a genomic interval should be integers',
    START_GREATER_THAN_STOP: 'The start of a genomic interval should not be past the end'
}


def has_user_submitted(is_submitted):
    return is_submitted


def get_user_genomic_intervals_str_input(n_clicks, nb_intervals_str, orig_nb_intervals_str):
    if n_clicks == 0 and orig_nb_intervals_str and orig_nb_intervals_str != nb_intervals_str:
        return orig_nb_intervals_str
    else:
        return nb_intervals_str


def get_user_other_refs_input(n_clicks, other_refs, orig_other_refs):
    if n_clicks == 0 and orig_other_refs and orig_other_refs != other_refs:
        return orig_other_refs
    else:
        return other_refs


def create_empty_df():
    return pd.DataFrame({
        'name': ['-'],
        'chrom': ['-'],
        'start': ['-'],
        'end': ['-']
    })

# The first element is the error code and the second element is the malformed interval


def is_error(intervals):
    return isinstance(intervals[0], int)


def get_error_message(error_code):
    return error_messages[error_code]


def sanitize_other_refs(other_refs):
    if other_refs:
        print(type(other_refs))

    return other_refs


def sanitize_nb_intervals_str(nb_intervals_str):
    # Remove spaces
    nb_intervals_str = nb_intervals_str.replace(' ', '')

    # Remove trailing semicolons
    nb_intervals_str = nb_intervals_str.rstrip(';')

    return nb_intervals_str

# convert 'Chr01:10000-25000' to a Genomic_Interval named tuple


def to_genomic_interval(interval_str):
    try:
        chrom, interval = interval_str.split(":")
    except ValueError:
        return NO_CHROM_INTERVAL_SEP, interval_str

    try:
        start, stop = interval.split("-")
    except ValueError:
        return NO_START_STOP_SEP, interval_str

    try:
        start = int(start)
        stop = int(stop)
    except ValueError:
        return START_STOP_NOT_INT, interval_str

    if start > stop:
        return START_GREATER_THAN_STOP, interval_str

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


def get_ogi_nb(Nb_intervals):
    if is_error(Nb_intervals):
        Nb_intervals = []

    final_ogi_set = set()
    final_ogi_dict = defaultdict(set)

    for Nb_interval in Nb_intervals:
        # load and search GFF_DB of Nipponbare
        db = gffutils.FeatureDB(
            'data/annotations/Nb/IRGSPMSU.gff.db', keep_order=True)
        genes_in_interval = list(db.region(region=(Nb_interval.chrom, Nb_interval.start, Nb_interval.stop),
                                           completely_within=False, featuretype='gene'))

        ogi_mapping_path = f'data/ogi_mapping/Nb_to_ogi.pickle'
        with open(ogi_mapping_path, 'rb') as f:
            ogi_mapping = pickle.load(f)
            for gene in genes_in_interval:
                gene_id = sanitize_gene_id(gene.id)
                ogi = ogi_mapping[gene_id]

                final_ogi_set.add(ogi)
                final_ogi_dict[ogi].add(gene_id)

    return final_ogi_set, final_ogi_dict


def get_ogi_other_ref(ref, Nb_intervals):
    db_align = gffutils.FeatureDB(
        "data/alignments/{0}/{0}.gff.db".format("Nb_"+str(ref)))
    db_annotation = gffutils.FeatureDB(
        "data/annotations/{0}/{0}.gff.db".format(ref))
    # get corresponding intervals on ref
    if is_error(Nb_intervals):
        Nb_intervals = []

    final_ogi_set = set()
    final_ogi_dict = defaultdict(set)

    for Nb_interval in Nb_intervals:
        gff_intersections = list(db_align.region(region=(Nb_interval.chrom, Nb_interval.start, Nb_interval.stop),
                                                 completely_within=False))
        for intersection in gff_intersections:
            ref_interval = to_genomic_interval(
                intersection.attributes['Name'][0])
            genes_in_interval = list(db_annotation.region(region=(ref_interval.chrom, ref_interval.start, ref_interval.stop),
                                                          completely_within=False, featuretype='gene'))

            ogi_mapping_path = f'data/ogi_mapping/{ref}_to_ogi.pickle'
            with open(ogi_mapping_path, 'rb') as f:
                ogi_mapping = pickle.load(f)
                for gene in genes_in_interval:
                    gene_id = sanitize_gene_id(gene.id)
                    ogi = ogi_mapping[gene_id]

                    final_ogi_set.add(ogi)
                    final_ogi_dict[ogi].add(gene_id)

    return final_ogi_set, final_ogi_dict


def get_overlapping_ogi(refs, Nb_intervals):
    ogi_list = []
    accession_list = []

    ogi_nb = get_ogi_nb(Nb_intervals)
    ogi_other_refs = []

    if 'Nb' in refs:
        ogi_list.append(ogi_nb[0])
        accession_list.append(ogi_nb[1])

    idx = 0
    for ref in refs:
        if ref != 'Nb':
            ogi_other_refs.append(get_ogi_other_ref(ref, Nb_intervals))
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


# getting genes from Nipponbare


def get_genes_from_Nb(Nb_intervals):
    dfs = []
    if is_error(Nb_intervals):
        Nb_intervals = []

    for Nb_interval in Nb_intervals:
        # load and search GFF_DB of Nipponbare
        db = gffutils.FeatureDB(
            'data/annotations/Nb/IRGSPMSU.gff.db', keep_order=True)
        genes_in_interval = list(db.region(region=(Nb_interval.chrom, Nb_interval.start, Nb_interval.stop),
                                           completely_within=False, featuretype='gene'))

        ogi_mapping_path = f'data/ogi_mapping/Nb_to_ogi.pickle'
        ogi_list = []
        with open(ogi_mapping_path, 'rb') as f:
            ogi_mapping = pickle.load(f)
            ogi_list = get_ogi([sanitize_gene_id(gene.id)
                                for gene in genes_in_interval], ogi_mapping)

        # TODO should be a better way to do this?
        df = pd.DataFrame({
            'ogi': ogi_list,
            'name': [gene.id for gene in genes_in_interval],
            'chrom': [gene.chrom for gene in genes_in_interval],
            'start': [gene.start for gene in genes_in_interval],
            'end': [gene.end for gene in genes_in_interval]
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


# Remove 'gene' prefix from gene IDs (e.g., from N22)
def sanitize_gene_id(gene_id):
    if gene_id[:len('gene:')] == 'gene:':
        return gene_id[len('gene:'):]

    return gene_id

# get intervals from other refs that align to (parts) of the input loci


def get_genes_from_other_ref(ref, Nb_intervals):
    db_align = gffutils.FeatureDB(
        "data/alignments/{0}/{0}.gff.db".format("Nb_"+str(ref)))
    db_annotation = gffutils.FeatureDB(
        "data/annotations/{0}/{0}.gff.db".format(ref))
    # get corresponding intervals on ref
    dfs = []
    if is_error(Nb_intervals):
        Nb_intervals = []

    for Nb_interval in Nb_intervals:
        gff_intersections = list(db_align.region(region=(Nb_interval.chrom, Nb_interval.start, Nb_interval.stop),
                                                 completely_within=False))
        for intersection in gff_intersections:
            ref_interval = to_genomic_interval(
                intersection.attributes['Name'][0])
            genes_in_interval = list(db_annotation.region(region=(ref_interval.chrom, ref_interval.start, ref_interval.stop),
                                                          completely_within=False, featuretype='gene'))

            ogi_mapping_path = f'data/ogi_mapping/{ref}_to_ogi.pickle'
            ogi_list = []
            with open(ogi_mapping_path, 'rb') as f:
                ogi_mapping = pickle.load(f)
                ogi_list = get_ogi([sanitize_gene_id(gene.id)
                                    for gene in genes_in_interval], ogi_mapping)

            df = pd.DataFrame({
                'ogi': ogi_list,
                'name': [gene.id for gene in genes_in_interval],
                'chrom': [gene.chrom for gene in genes_in_interval],
                'start': [gene.start for gene in genes_in_interval],
                'end': [gene.end for gene in genes_in_interval]
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
