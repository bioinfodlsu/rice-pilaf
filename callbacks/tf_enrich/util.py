import json
from timeit import default_timer as timer
import pandas as pd
import os
import subprocess
import statsmodels.stats.multitest as sm
from ..file_util import *
from ..constants import Constants
const = Constants()


def create_empty_df():
    return pd.DataFrame({
        'Transcription Factor': ['-'],
        'p-value': ['-'],
        'adj. p-value': ['-']
    })


# gene_table is a list of dictionaries, each dictionary of this kind: {'ogi': 'OGI:01005230', 'name': 'LOC_Os01g03710', 'chrom': 'Chr01', 'start': 1534135, 'end': 1539627, 'strand': '+'}
def write_promoter_intervals_to_file(gene_table, nb_interval_str, upstream_win_len=500, downstream_win_len=100):
    temp_output_folder_dir = get_temp_output_folder_dir(
        nb_interval_str, const.TEMP_TFBS, '')

    create_dir(temp_output_folder_dir)

    with open(f'{temp_output_folder_dir}/query', "w") as f:
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
    return f


def perform_enrichment_all_tf(tfbs_set, tfbs_prediction_technique, nb_interval_str):

    out_dir_all = get_temp_output_folder_dir(
        nb_interval_str, const.TEMP_TFBS, 'significance_outdir')

    # already computed, just display
    if dir_exist(f'{out_dir_all}/BH_corrected.csv'):
        results_df = load_csv_from_dir(
            f'{out_dir_all}/BH_corrected.csv')
        return results_df

    create_dir(out_dir_all)
    query_bed = get_temp_output_folder_dir(
        nb_interval_str, const.TEMP_TFBS, 'query')
    sizes = f'{const.TFBS_BEDS}/sizes/{tfbs_set}'

    TF_list = []
    # keep together using a dict? but BH correction needs a separate list of p_values
    pvalue_list = []

    # perform annotation overlap statistical significance tests
    for tf in os.listdir(os.path.join(const.TFBS_BEDS, tfbs_set, tfbs_prediction_technique, "intervals")):
        ref_bed = f'{const.TFBS_BEDS}/{tfbs_set}/{tfbs_prediction_technique}/intervals/{tf}'

        out_dir_tf = f'{out_dir_all}/{tf}'
        create_dir(out_dir_tf)

        p_value = perform_enrichment_specific_tf(
            ref_bed, query_bed, sizes, out_dir_tf)

        TF_list.append(tf)
        pvalue_list.append(p_value)

    significant, adj_pvalue = multiple_testing_correction(pvalue_list, 0.25)
    results = sorted(list(zip(TF_list, pvalue_list, adj_pvalue,
                     significant)), key=lambda x: (x[3], x[1]))
    results_df = pd.DataFrame(results, columns=[
                              "Transcription factor", "p_value", "Benjamini-Hochberg corrected pvalue", "significant?"])
    results_df.to_csv(f'{out_dir_all}/BH_corrected.csv', index=False)
    return results_df


def perform_enrichment_specific_tf(ref_bed, query_bed, sizes, out_dir):
    # COMMAND = f'mcdp2 single {ref_bed} {query_bed} {sizes} -o {out_dir}'
    # os.system(COMMAND)

    summary_file = f'{out_dir}/summary.txt'

    if not dir_exist(summary_file):
        subprocess.run(["mcdp2", "single", ref_bed, query_bed, sizes, "-o", out_dir],
                       shell=False, capture_output=True, text=True)  # TODO exception handling

    with open(f'{out_dir}/summary.txt') as f:
        content = f.readlines()
        p_value = float(content[3].rstrip().split(":")[1])
    return p_value


def multiple_testing_correction(pvalues, fdr):
    sig, adj_pvalue, _, _ = sm.multipletests(
        pvalues, alpha=fdr, method='fdr_bh', is_sorted=False, returnsorted=False)
    sig = sig.tolist()
    adj_pvalue = adj_pvalue.tolist()
    return sig, adj_pvalue
