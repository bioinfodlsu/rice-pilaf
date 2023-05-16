import csv
import os
import re

import pandas as pd


def get_annotations(oryzabase_file):
    annotations = []
    with open(oryzabase_file, encoding='utf-8') as oryzabase:
        csv_reader = csv.reader(oryzabase, delimiter='\t')
        next(csv_reader)

        for line in csv_reader:
            id = line[13]
            id_components = id.split('.')
            id = id_components[0].strip()

            to_terms = line[-2]
            to_components = to_terms.split(', ')
            for to in to_components:
                to = to.split(' - ')
                to = to[0].strip()

                # Handle dirty data, like "LOC_ Os07g22494"
                id = id.replace(" ", "")

                if id and to and re.compile('TO:\d+').match(to):
                    annotations.append([to, id])

    return pd.DataFrame(annotations)


def map_to_id_to_names(oryzabase_file):
    annotations = list()
    with open(oryzabase_file, encoding='utf-8') as oryzabase:
        csv_reader = csv.reader(oryzabase, delimiter='\t')
        next(csv_reader)

        for line in csv_reader:
            to_terms = line[-2]
            to_components = to_terms.split(', ')
            for to in to_components:
                to = to.split(' - ')

                try:
                    to_id = to[0].strip()
                    to_name = to[1].strip()
                except IndexError:
                    continue

                if to_id and re.compile('TO:\d+').match(to_id) and to_name:
                    annotations.append([to_id, to_name])

    return pd.DataFrame(annotations).drop_duplicates(ignore_index=True)


def save_annotations_to_csv(annotations_df, output_dir):
    if not os.path.exists(f'{output_dir}'):
        os.makedirs(f'{output_dir}')

    annotations_df.to_csv(f'{output_dir}/to-annotations.tsv',
                          sep='\t', index=False, header=False)
    print(f'Generated {output_dir}/to-annotations.tsv')


def save_id_to_names_to_csv(id_to_names_df, output_dir):
    id_to_names_df.to_csv(f'{output_dir}/to-id-to-name.tsv',
                          sep='\t', index=False, header=False)
    print(f'Generated {output_dir}/to-id-to-name.tsv')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'oryzabase_file', help='text file containing the TO annotations from Oryzabase')
    parser.add_argument(
        'output_dir', help='output directory for the TSV file mapping MSU accessions to TO term IDs')

    args = parser.parse_args()

    annotations_df = get_annotations(args.oryzabase_file)
    id_to_names_df = map_to_id_to_names(args.oryzabase_file)

    save_annotations_to_csv(annotations_df, args.output_dir)
    save_id_to_names_to_csv(id_to_names_df, args.output_dir)
