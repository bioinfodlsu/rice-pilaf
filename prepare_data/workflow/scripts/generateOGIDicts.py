import os
import csv


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


def generate_dict(ogi_file, mapping_dict):
    with open(ogi_file) as f:
        csv_reader = csv.reader(f, delimiter='\t')

        for row in csv_reader:
            mapping_dict


if __name__ == '__main__':
    path = 'data/gene_ID_mapping_fromRGI'
    mapping_dict = {}

    rice_variants = get_rice_variants(path)
    print(rice_variants)

    # for file in os.listdir(path):
    #     generate_dict(f'{path}/{file}', mapping_dict)
