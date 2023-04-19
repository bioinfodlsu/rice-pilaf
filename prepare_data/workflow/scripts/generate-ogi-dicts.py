import os
import csv
import pickle
from pathlib import Path


def get_rice_variants(path):
    rice_variants = []

    with open(f'{path}/core.ogi') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        for row in csv_reader:
            rice_variants = row
            break

    for i in range(len(rice_variants)):
        # Remove OS prefix
        if rice_variants[i][:len('Os')] == 'Os':
            rice_variants[i] = rice_variants[i][len('OS'):]

        # Nipponbare is abbreviated as 'NB' in the app but 'Nip' in RGI
        if rice_variants[i] == 'Nip':
            rice_variants[i] = 'NB'

        # Remove LOC
        if rice_variants[i] == 'LOC':
            rice_variants[i] = ''

    rice_variants = [
        rice_variant for rice_variant in rice_variants if rice_variant != '']

    return rice_variants


def make_mapping_dicts(rice_variants):
    mapping_dicts = []
    for rice_variant in rice_variants:
        mapping_dicts.append({})

    return mapping_dicts


def separate_paralogs(genes):
    if ',' in genes:
        paralogs = genes.split(',')
        return paralogs

    return [genes]


def generate_dict(ogi_file, mapping_dicts):
    with open(ogi_file) as f:
        csv_reader = csv.reader(f, delimiter='\t')

        # Skip header row
        next(csv_reader, None)

        for row in csv_reader:
            NB_ACCESSION = 3
            for idx in range(NB_ACCESSION, len(row)):
                try:
                    gene_str = row[idx].strip()

                    if gene_str != '.':
                        genes = separate_paralogs(row[idx].strip())
                        for gene in genes:
                            if gene != '':
                                mapping_dicts[idx -
                                              NB_ACCESSION][gene] = row[0].strip()

                except IndexError:
                    break


def pickle_mapping_dicts(path, mapping_dicts):
    path_mapping_dicts = f'{path}/mapping_dicts'
    if not os.path.exists(path_mapping_dicts):
        os.makedirs(path_mapping_dicts)

    for rice_variant, mapping_dict in zip(rice_variants, mapping_dicts):
        pickle_path = f'{path_mapping_dicts}/{rice_variant}_to_ogi.pickle'
        with open(pickle_path, 'wb') as f:
            pickle.dump(mapping_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
            print(f'Generated {path}/{rice_variant}_to_ogi.pickle')


if __name__ == '__main__':
    path = 'data/gene_ID_mapping_fromRGI'

    rice_variants = get_rice_variants(path)
    mapping_dicts = make_mapping_dicts(rice_variants)

    for file in os.listdir(path):
        generate_dict(f'{path}/{file}', mapping_dicts)
        print(f'Generated dictionary for {path}/{file}')

    pickle_mapping_dicts(path, mapping_dicts)
