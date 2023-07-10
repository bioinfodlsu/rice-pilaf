import json
from timeit import default_timer as timer
import pandas as pd
import os
import subprocess
import statsmodels.stats.multitest as sm

from ..constants import Constants
const = Constants()


def create_empty_df():
    return pd.DataFrame({
        'Transcription Factor': ['-'],
        'p-value': ['-'],
        'adj. p-value': ['-']
    })


# gene_table is a list of dictionaries, each dictionary of this kind: {'ogi': 'OGI:01005230', 'name': 'LOC_Os01g03710', 'chrom': 'Chr01', 'start': 1534135, 'end': 1539627, 'strand': '+'}
def write_promoter_intervals_to_file(gene_table, nb_interval_str_fname, upstream_win_len=500, downstream_win_len=100):
    # if not os.path.exists(const.TEMP_TFBS):
    #    os.makedirs(const.TEMP_TFBS)
    if not os.path.exists(os.path.join(const.TEMP_TFBS, nb_interval_str_fname)):
        os.makedirs(os.path.join(const.TEMP_TFBS,
                    nb_interval_str_fname))

    with open(f'{const.TEMP_TFBS}/{nb_interval_str_fname}/query', "w") as f:
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


def perform_enrichment_all_tf(tfbs_set, tfbs_prediction_technique, tfbs_fdr, nb_interval_str_fname):

    out_dir = f'{const.TEMP_TFBS}/{nb_interval_str_fname}/{tfbs_set}/{tfbs_prediction_technique}'

    #already computed everything include adjusted p-value, just display
    if os.path.exists(f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv'):
        return pd.read_csv(f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv')



    #single-TF p-values already computed, but not BH_corrected, possibly FDR value changed
    elif os.path.exists(f'{out_dir}/results_before_multiple_corrections.csv'):
        results_df =  multiple_testing_correction(pd.read_csv(f'{out_dir}/results_before_multiple_corrections.csv'),
                                                  float(tfbs_fdr))
        results_df.to_csv(f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv', index=False) # should this be inside multiple_testing_correction?
        return results_df

    #if everything needs to be computed afresh
    elif not os.path.exists(out_dir):
        os.makedirs(out_dir)

    query_bed = f'{const.TEMP_TFBS}/{nb_interval_str_fname}/query'
    sizes = f'{const.TFBS_BEDS}/sizes/{tfbs_set}'

    TF_list = []
    pvalue_list = [] #keep together using a dict? but BH correction needs a separate list of p_values

    # perform annotation overlap statistical significance tests
    for tf in os.listdir(os.path.join(const.TFBS_BEDS, tfbs_set, tfbs_prediction_technique, "intervals")):
        ref_bed = f'{const.TFBS_BEDS}/{tfbs_set}/{tfbs_prediction_technique}/intervals/{tf}'

        out_dir_tf = f'{out_dir}/{tf}'
        if not os.path.exists(out_dir_tf):
            os.makedirs(out_dir_tf)

        p_value = perform_enrichment_specific_tf(
                  ref_bed, query_bed, sizes, out_dir_tf)

        TF_list.append(tf)
        pvalue_list.append(p_value)

    results_no_adj_df = pd.DataFrame(list((zip(TF_list,pvalue_list))),columns = ["Transcription factor","p-value"])
    results_no_adj_df.to_csv(f'{out_dir}/results_before_multiple_corrections.csv',index=False)

    results_df = multiple_testing_correction(results_no_adj_df,tfbs_fdr)
    #significant,adj_pvalue = multiple_testing_correction(pvalue_list, 0.25)
    #results = sorted(list(zip(TF_list,pvalue_list, adj_pvalue,significant)),key=lambda x:(x[3],x[1]))
    #results_df = pd.DataFrame(results,columns=["Transcription factor","p_value","Benjamini-Hochberg corrected pvalue","significant?"])
    results_df.to_csv(f'{out_dir}/BH_corrected_fdr_{tfbs_fdr}.csv',index=False)
    return results_df


def perform_enrichment_specific_tf(ref_bed, query_bed, sizes, out_dir):
    # COMMAND = f'mcdp2 single {ref_bed} {query_bed} {sizes} -o {out_dir}'
    # os.system(COMMAND)

    summary_file = f'{out_dir}/summary.txt'

    if not os.path.exists(summary_file):
        subprocess.run(["mcdp2", "single", ref_bed, query_bed, sizes, "-o", out_dir],
                       shell=False, capture_output=True, text=True)  # TODO exception handling

    with open(f'{out_dir}/summary.txt') as f:
        content = f.readlines()
        p_value = float(content[3].rstrip().split(":")[1])
    return p_value

def multiple_testing_correction(single_tf_results,fdr):
    pvalues = single_tf_results['p-value'].tolist()
    sig, adj_pvalue, _, _ = sm.multipletests(pvalues, alpha=fdr, method='fdr_bh', is_sorted=False, returnsorted=False)
    sig = sig.tolist()
    adj_pvalue = adj_pvalue.tolist()
    single_tf_results['Benjamini-Hochberg corrected pvalue'] = adj_pvalue
    single_tf_results['significant?'] = sig
    single_tf_results.sort_values(by=['p-value'],inplace=True)
    return single_tf_results
    #
