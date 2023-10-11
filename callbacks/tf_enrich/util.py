import pandas as pd
import os
import shutil
import subprocess
from scipy.stats import false_discovery_control
import pickle
from ..file_util import *
from ..constants import Constants
from ..general_util import *
from ..links_util import *

import gffutils
import pybedtools


COLUMNS = ['Transcription Factor', 'Family',
           'p-value', 'Adj. p-value']  # , 'Significant?']


def create_empty_df():
    return create_empty_df_with_cols(['Transcription Factor', 'p-value', 'adj. p-value'])


def get_annotations_addl_gene(addl_genes):
    db = gffutils.FeatureDB(
        f'{Constants.ANNOTATIONS}/Nb/IRGSPMSU.gff.db', keep_order=True)

    return [{'ogi': None,
             'name': addl_gene,
             'Chromosome': db[addl_gene].chrom,
             'Start': db[addl_gene].start,
             'End': db[addl_gene].end,
             'Strand': db[addl_gene].strand} for addl_gene in addl_genes]

# gene_table is a list of dictionaries, each dictionary of this kind: {'ogi': 'OGI:01005230', 'name': 'LOC_Os01g03710', 'chrom': 'Chr01', 'start': 1534135, 'end': 1539627, 'strand': '+'}


def write_query_promoter_intervals_to_file(gene_table, nb_interval_str, addl_genes, upstream_win_len=500, downstream_win_len=100):
    make_dir(get_path_to_temp(nb_interval_str, Constants.TEMP_TFBS))

    # addl_genes has already been shortened by the time this function is called
    filepath_without_timestamp = get_path_to_temp(
        nb_interval_str, Constants.TEMP_TFBS, addl_genes, Constants.PROMOTER_BED)
    filepath = append_timestamp_to_filename(filepath_without_timestamp)

    with open(filepath, "w") as f:
        for gene in gene_table:
            if gene['Strand'] == '+':
                promoter_start = gene['Start'] - upstream_win_len
                assert promoter_start >= 0
                promoter_end = gene['Start'] + downstream_win_len - 1
                f.write("{}\t{}\t{}\n".format(
                    gene['Chromosome'], promoter_start, promoter_end))
            elif gene['Strand'] == '-':
                promoter_start = gene['End'] + upstream_win_len
                promoter_end = gene['End'] + 1 - downstream_win_len
                assert promoter_end >= 0
                f.write("{}\t{}\t{}\n".format(
                    gene['Chromosome'], promoter_end, promoter_start))

    # Renaming will be done once TF enrichment has finished

    return filepath, filepath_without_timestamp


def write_query_genome_intervals_to_file(nb_interval_str, addl_genes):
    make_dir(get_path_to_temp(nb_interval_str, Constants.TEMP_TFBS))

    # addl_genes has already been shortened by the time this function is called
    filepath_without_timestamp = get_path_to_temp(
        nb_interval_str, Constants.TEMP_TFBS, addl_genes, Constants.GENOME_WIDE_BED)
    filepath = append_timestamp_to_filename(filepath_without_timestamp)

    with open(filepath, "w") as f:
        for interval in nb_interval_str.split(";"):
            chrom, range = interval.split(":")
            beg, end = range.split("-")
            f.write("{}\t{}\t{}\n".format(chrom, beg, end))

    # Renaming will be done once TF enrichment has finished

    return filepath, filepath_without_timestamp


def perform_enrichment_all_tf(lift_over_nb_entire_table, addl_genes,
                              tfbs_set, tfbs_prediction_technique,
                              nb_interval_str):
    out_dir_without_timestamp = get_path_to_temp(
        nb_interval_str, Constants.TEMP_TFBS, shorten_name(addl_genes), tfbs_set, tfbs_prediction_technique)

    # if previously computed
    if path_exists(f'{out_dir_without_timestamp}/BH_corrected.csv'):
        results_df = pd.read_csv(
            f'{out_dir_without_timestamp}/BH_corrected.csv', dtype=object)

        try:
            results_df['Family'] = results_df['Transcription Factor'].apply(
                get_family)

            results_df = results_df[COLUMNS]
        except KeyError:
            results_df = create_empty_df()

        return results_df

    '''
    # single-TF p-values already computed, but not BH_corrected, possibly FDR value changed
    elif path_exists(f'{out_dir}/results_before_multiple_corrections.csv'):
        results_before_multiple_corrections = pd.read_csv(
            f'{out_dir}/results_before_multiple_corrections.csv')
        results_df = multiple_testing_correction(results_before_multiple_corrections,
                                                 float(tfbs_fdr))
        results_df.to_csv(
            f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv', index=False)

        results_df['Family'] = results_df['Transcription Factor'].apply(
            get_family)

        results_df = results_df[COLUMNS]

        return results_df
    '''
    out_dir = append_timestamp_to_filename(out_dir_without_timestamp)
    make_dir(out_dir)

    # construct query BED file
    # out_dir_tf_enrich = get_path_to_temp(nb_interval_str, Constants.TEMP_TFBS, addl_genes)
    if tfbs_set == 'promoters':
        query_bed, query_bed_without_timestamp = write_query_promoter_intervals_to_file(
            lift_over_nb_entire_table, nb_interval_str, shorten_name(addl_genes))
        sizes = f'{Constants.TFBS_BEDS}/sizes/{tfbs_set}'
    elif tfbs_set == 'genome':
        query_bed, query_bed_without_timestamp = write_query_genome_intervals_to_file(
            nb_interval_str, shorten_name(addl_genes))
        sizes = f'{Constants.TFBS_BEDS}/sizes/{tfbs_set}'

    # construct a pybedtool object. we will use pybedtools to compute if there
    # is any overlap. If no, don't test for significance using mcdp2.
    query_pybed = pybedtools.BedTool(query_bed)

    TF_list = []
    # keep together using a dict? but BH correction needs a separate list of p_values
    pvalue_list = []

    # perform annotation overlap statistical significance tests
    for tf in os.listdir(os.path.join(Constants.TFBS_BEDS, tfbs_set, tfbs_prediction_technique, "intervals")):
        # print("computing overlaps for: {}".format(tf))
        ref_bed = f'{Constants.TFBS_BEDS}/{tfbs_set}/{tfbs_prediction_technique}/intervals/{tf}'
        ref_pybed = pybedtools.BedTool(ref_bed)

        out_dir_tf = f'{out_dir}/{tf}'
        make_dir(out_dir_tf)

        if query_pybed.intersect(ref_pybed, nonamecheck=True).count() != 0:

            p_value = perform_enrichment_specific_tf(ref_bed, query_bed,
                                                     sizes, out_dir_tf)

            TF_list.append(tf)
            pvalue_list.append(p_value)

    results_no_adj_df = pd.DataFrame(list((zip(TF_list, pvalue_list))), columns=[
                                     "Transcription Factor", "p-value"])
    results_no_adj_df.to_csv(
        f'{out_dir}/results_before_multiple_corrections.csv', index=False)

    results_df = multiple_testing_correction(results_no_adj_df)

    if results_df.empty:
        results_df = create_empty_df()
    else:
        display_cols_in_sci_notation(results_df, ['p-value', 'Adj. p-value'])

        results_df['Family'] = results_df['Transcription Factor'].apply(
            get_family)

        results_df = results_df[COLUMNS]

    results_df.to_csv(
        f'{out_dir}/BH_corrected.csv', index=False)

    try:
        os.replace(out_dir, out_dir_without_timestamp)
    except Exception as e:
        # Use shutil.rmtree to delete non-empty directory
        shutil.rmtree(out_dir, ignore_errors=True)
        pass

    try:
        os.replace(query_bed, query_bed_without_timestamp)
    except:
        pass

    return results_df


def perform_enrichment_specific_tf(ref_bed, query_bed, sizes, out_dir):
    summary_file = f'{out_dir}/summary.txt'

    if not path_exists(summary_file):
        subprocess.run(["mcdp2", "single", ref_bed, query_bed, sizes, "-o", out_dir],
                       shell=False, capture_output=True, text=True)  # TODO exception handling

    with open(f'{out_dir}/summary.txt') as f:
        content = f.readlines()
        p_value = float(content[3].rstrip().split(":")[1])
    return p_value


def multiple_testing_correction(single_tf_results):
    pvalues = single_tf_results['p-value'].tolist()
    adj_pvalue = false_discovery_control(pvalues, method='bh')
    single_tf_results['Adj. p-value'] = adj_pvalue
    single_tf_results.sort_values(by=['p-value'], inplace=True)
    return single_tf_results


def get_family(transcription_factor):
    with open(f'{Constants.TFBS_ANNOTATION}/family_mapping.pickle', 'rb') as f:
        mapping = pickle.load(f)

    return ', '.join(mapping[transcription_factor])
