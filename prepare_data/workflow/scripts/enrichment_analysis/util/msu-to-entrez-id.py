import csv
import os
import pickle
from collections import defaultdict


def load_msu_to_entrez(msu_to_entrez_dict, id_file):
    with open(id_file) as f:
        csv_reader = csv.reader(f, delimiter=',')
        next(csv_reader)            # Skip header
        for line in csv_reader:
            msu = line[-1]
            entrez = line[1]

            if msu != '-':
                msu_to_entrez_dict[msu].add(entrez)

        print("Finished mapping MSU accessions to Entrez IDs")


def save_msu_entrez_mapping(msu_to_entrez_dict, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/msu-to-entrez-id.pickle', 'wb') as handle:
        pickle.dump(msu_to_entrez_dict, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/msu-to-entrez-id.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'msu_to_entrez_file', help='text file mapping MSU accessions to Entrez IDs')
    parser.add_argument(
        'output_dir', help='output directory for the pickled dictionary mapping MSU accessions to their respective Entrez IDs')

    args = parser.parse_args()

    msu_to_entrez_dict = defaultdict(set)
    load_msu_to_entrez(msu_to_entrez_dict, args.msu_to_entrez_file)
    save_msu_entrez_mapping(msu_to_entrez_dict, args.output_dir)
