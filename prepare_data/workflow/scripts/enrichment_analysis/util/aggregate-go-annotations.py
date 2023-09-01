import csv
import os
import pickle
import re
from collections import defaultdict

import pandas as pd


def from_agrigo(agrigo_file):
    annotations = []
    with open(agrigo_file) as agrigo:
        csv_reader = csv.reader(agrigo, delimiter='\t')
        for line in csv_reader:
            id = line[-2]
            go = line[-1]

            # Handle dirty data, like "LOC_ Os07g22494"
            id = id.replace(" ", "")
            annotations.append([go, id])

    return pd.DataFrame(annotations)


def from_oryzabase(oryzabase_file):
    annotations = []
    with open(oryzabase_file, encoding='utf-8') as oryzabase:
        csv_reader = csv.reader(oryzabase, delimiter='\t')
        next(csv_reader)

        for line in csv_reader:
            id = line[13]
            id_components = id.split('.')
            id = id_components[0].strip()

            go_terms = line[-3]
            go_components = go_terms.split(', ')
            for go in go_components:
                go = go.split(' - ')
                go = go[0].strip()

                # Handle dirty data, like "LOC_ Os07g22494"
                id = id.replace(" ", "")

                if id and go and re.compile('GO:\d+').match(go):
                    annotations.append([go, id])

    return pd.DataFrame(annotations)


def construct_rap_db_mapping(rap_db_file):
    rap_db_mapping = defaultdict(list)

    with open(rap_db_file) as rap_db:
        csv_reader = csv.reader(rap_db, delimiter='\t')
        next(csv_reader)

        for line in csv_reader:
            go_ids = re.findall(r'GO:\d+', line[9])
            rap_db_mapping[line[0].rstrip().replace(" ", "")] = go_ids

    return rap_db_mapping


def convert_transcript_to_msu(msu_to_transcript_mapping_file):
    with open(msu_to_transcript_mapping_file, 'rb') as mapping:
        mapping_dict = pickle.load(mapping)
        transcript_to_msu_mapping = defaultdict(set)

        for msu_id, transcript_ids in mapping_dict.items():
            for transcript_id in transcript_ids:
                transcript_to_msu_mapping[transcript_id].add(msu_id)

    return transcript_to_msu_mapping


def from_rap_db(rap_db_file, all_genes_file, msu_to_transcript_file):
    annotations = []
    rap_db_mapping = construct_rap_db_mapping(rap_db_file)
    transcript_to_msu_mapping = convert_transcript_to_msu(
        msu_to_transcript_file)

    with open(all_genes_file) as all_genes:
        csv_reader = csv.reader(all_genes, delimiter='\t')
        all_genes_list = []
        for line in csv_reader:
            all_genes_list += line

    for gene in all_genes_list:
        for go_id in rap_db_mapping[gene]:
            for msu_id in transcript_to_msu_mapping[gene]:
                msu_id = msu_id.replace(" ", "")
                annotations.append([go_id, msu_id])

    return pd.DataFrame(annotations)


def merge_annotations(*args):
    merged_df = pd.concat(args)
    merged_df.drop_duplicates(ignore_index=True, inplace=True)

    return merged_df


def save_to_csv(output_dir, merged_df):
    if not os.path.exists(f'{output_dir}'):
        os.makedirs(f'{output_dir}')

    merged_df.to_csv(f'{output_dir}/go-annotations.tsv',
                     sep='\t', index=False, header=False)
    print(f'Generated {output_dir}/go-annotations.tsv')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'agrigo_file', help='text file containing the GO annotations from agriGO v2.0')
    parser.add_argument(
        'oryzabase_file', help='text file containing the GO annotations from Oryzabase')
    parser.add_argument(
        'rap_db_file', help='text file containing the GO annotations from RAP-DB')
    parser.add_argument(
        'all_genes_file', help='text file containing the RAP-DB accessions of all the genes of interest')
    parser.add_argument(
        'msu_to_transcript_file', help='pickled dictionary mapping MSU accessions to KEGG transcript IDs')
    parser.add_argument(
        'output_dir', help='output directory for the TSV file mapping MSU accessions to GO term IDs')

    args = parser.parse_args()

    agrigo_df = from_agrigo(args.agrigo_file)
    oryzabase_df = from_oryzabase(args.oryzabase_file)
    rap_db_df = from_rap_db(
        args.rap_db_file, args.all_genes_file, args.msu_to_transcript_file)

    merged_df = merge_annotations(agrigo_df, oryzabase_df, rap_db_df)
    save_to_csv(args.output_dir, merged_df)
