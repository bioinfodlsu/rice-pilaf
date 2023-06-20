import json
from timeit import default_timer as timer
import pandas as pd
import os
import subprocess

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


def perform_enrichment_all_tf(tfbs_set, tfbs_prediction_technique, nb_interval_str_fname):
    results_outdir = f'{const.TEMP_TFBS}/{tfbs_set}/{tfbs_prediction_technique}/{nb_interval_str_fname}'

    if not os.path.exists(results_outdir):
        os.makedirs(results_outdir)

        query_bed = f'{const.TEMP_TFBS}/{nb_interval_str_fname}/query'
        sizes = f'{const.TFBS_BEDS}/sizes/{tfbs_set}'
        results_dict = {}  # key=tf, values = results from overlap enrichment analysis

        # perform annotation overlap statistical significance tests
        for tf in os.listdir(os.path.join(const.TFBS_BEDS, tfbs_set, tfbs_prediction_technique, "intervals")):
            ref_bed = f'{const.TFBS_BEDS}/{tfbs_set}/{tfbs_prediction_technique}/intervals/{tf}'

            out_dir = f'{const.TEMP_TFBS}/{nb_interval_str_fname}/significance_outdir/{tf}'
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            results_dict[tf] = perform_enrichment_specific_tf(
                ref_bed, query_bed, sizes, out_dir)

        # TODO perform proper multi-test correction
        for k in results_dict.keys():
            results_dict[k]['adj_p'] = min(1, results_dict[k]['p_value']*32)

        with open(f'{results_outdir}/output.txt', 'w') as fp:
            json.dump(results_dict, fp)

        # get results
        # return create_empty_df()
        return pd.DataFrame.from_dict(results_dict, orient='index').rename_axis("Transcription factor").reset_index()

    else:
        with open(f'{results_outdir}/output.txt', 'r') as fp:
            results_dict = json.load(fp)

        # get results
        # return create_empty_df()
        return pd.DataFrame.from_dict(results_dict, orient='index').rename_axis("Transcription factor").reset_index()


def perform_enrichment_specific_tf(ref_bed, query_bed, sizes, out_dir):
    # COMMAND = f'mcdp2 single {ref_bed} {query_bed} {sizes} -o {out_dir}'
    # os.system(COMMAND)

    summary_file = f'{out_dir}/summary.txt'

    if not os.path.exists(summary_file):
        subprocess.run(["mcdp2", "single", ref_bed, query_bed, sizes, "-o", out_dir],
                       shell=False, capture_output=True, text=True)  # TODO exception handling
    results = {}
    with open(f'{out_dir}/summary.txt') as f:
        content = f.readlines()
        results['p_value'] = float(content[3].rstrip().split(":")[1])
    return results


def multiple_testing_correction():
    pass
