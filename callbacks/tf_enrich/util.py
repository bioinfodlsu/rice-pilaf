import pandas as pd
import os
import subprocess
import statsmodels.stats.multitest as sm
from ..file_util import *
from ..constants import Constants
from ..general_util import *

const = Constants()


def create_empty_df():
    return create_empty_df_with_cols(['Transcription Factor', 'p-value', 'adj. p-value'])

# gene_table is a list of dictionaries, each dictionary of this kind: {'ogi': 'OGI:01005230', 'name': 'LOC_Os01g03710', 'chrom': 'Chr01', 'start': 1534135, 'end': 1539627, 'strand': '+'}


def write_query_promoter_intervals_to_file(gene_table, nb_interval_str, addl_genes, upstream_win_len=500, downstream_win_len=100):
    make_dir(get_path_to_temp(nb_interval_str, const.TEMP_TFBS))
    filepath = get_path_to_temp(
        nb_interval_str, const.TEMP_TFBS, addl_genes, const.PROMOTER_BED)
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
    return filepath


def write_query_genome_intervals_to_file(nb_interval_str, addl_genes):
    make_dir(get_path_to_temp(nb_interval_str, const.TEMP_TFBS, addl_genes))
    filepath = get_path_to_temp(
        nb_interval_str, const.TEMP_TFBS, const.GENOME_WIDE_BED)
    with open(filepath, "w") as f:
        for interval in nb_interval_str.split(";"):
            chrom, range = interval.split(":")
            beg, end = range.split("-")
            f.write("{}\t{}\t{}\n".format(chrom, beg, end))
    return filepath


def perform_enrichment_all_tf(lift_over_nb_entire_table, addl_genes, tfbs_set, tfbs_prediction_technique, tfbs_fdr, nb_interval_str):
    out_dir = get_path_to_temp(
        nb_interval_str, const.TEMP_TFBS, addl_genes, tfbs_set, tfbs_prediction_technique)
    # if previously computed
    if path_exists(f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv'):
        results_df = pd.read_csv(
            f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv', dtype=object)
        return results_df

    # single-TF p-values already computed, but not BH_corrected, possibly FDR value changed
    elif path_exists(f'{out_dir}/results_before_multiple_corrections.csv'):
        results_before_multiple_corrections = pd.read_csv(
            f'{out_dir}/results_before_multiple_corrections.csv')
        results_df = multiple_testing_correction(results_before_multiple_corrections,
                                                 float(tfbs_fdr))
        results_df.to_csv(
            f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv', index=False)
        return results_df

    make_dir(out_dir)

    # construct query BED file
    out_dir_tf_enrich = get_path_to_temp(
        nb_interval_str, const.TEMP_TFBS, addl_genes)
    if tfbs_set == 'promoters':
        query_bed = write_query_promoter_intervals_to_file(
            lift_over_nb_entire_table, nb_interval_str, addl_genes)
        sizes = f'{const.TFBS_BEDS}/sizes/{tfbs_set}'
    elif tfbs_set == 'genome':
        query_bed = write_query_genome_intervals_to_file(
            nb_interval_str, addl_genes)
        sizes = f'{const.TFBS_BEDS}/sizes/{tfbs_set}'

    TF_list = []
    # keep together using a dict? but BH correction needs a separate list of p_values
    pvalue_list = []

    # perform annotation overlap statistical significance tests
    for tf in os.listdir(os.path.join(const.TFBS_BEDS, tfbs_set, tfbs_prediction_technique, "intervals")):
        # print("computing overlaps for: {}".format(tf))
        ref_bed = f'{const.TFBS_BEDS}/{tfbs_set}/{tfbs_prediction_technique}/intervals/{tf}'
        out_dir_tf = f'{out_dir}/{tf}'
        make_dir(out_dir_tf)

        p_value = perform_enrichment_specific_tf(
            ref_bed, query_bed, sizes, out_dir_tf)

        TF_list.append(tf)
        pvalue_list.append(p_value)

    results_no_adj_df = pd.DataFrame(list((zip(TF_list, pvalue_list))), columns=[
                                     "Transcription Factor", "p-value"])
    results_no_adj_df.to_csv(
        f'{out_dir}/results_before_multiple_corrections.csv', index=False)

    results_df = multiple_testing_correction(results_no_adj_df, tfbs_fdr)
    display_cols_in_sci_notation(results_df, ['p-value', 'Adj. p-value'])

    results_df.to_csv(
        f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv', index=False)

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


def multiple_testing_correction(single_tf_results, fdr):
    pvalues = single_tf_results['p-value'].tolist()
    sig, adj_pvalue, _, _ = sm.multipletests(
        pvalues, alpha=fdr, method='fdr_bh', is_sorted=False, returnsorted=False)
    sig = sig.tolist()
    sig = list(map(str, sig))
    adj_pvalue = adj_pvalue.tolist()
    single_tf_results['Adj. p-value'] = adj_pvalue
    single_tf_results['Significant?'] = sig
    single_tf_results.sort_values(by=['p-value'], inplace=True)
    return single_tf_results
