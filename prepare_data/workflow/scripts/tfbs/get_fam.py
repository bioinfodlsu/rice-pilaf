from collections import defaultdict
import os
import pickle


def get_family_df(family_file):
    family_mapping = defaultdict(set)
    with open(family_file) as f:
        next(f)     # Skip header
        for line in f:
            _, gene_id, family = line.strip().split('\t')
            family_mapping[gene_id].add(family)

    family_str_mapping = {}
    for gene_id, family in family_mapping.items():
        family_str_mapping[gene_id] = ', '.join(family_mapping[gene_id])

    print("Generated gene-to-family mapping dictionary")

    return family_str_mapping


def export_mapping(mapping, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/family_mapping.pickle', 'wb') as f:
        pickle.dump(mapping, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/family_mapping.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'family_file', help='raw file containing the families of the transcription factors')
    parser.add_argument(
        'output_dir', help='output directory for the parsed file containing the families of the transcription factors')

    args = parser.parse_args()
    family_mapping = get_family_df(args.family_file)
    export_mapping(family_mapping, args.output_dir)
