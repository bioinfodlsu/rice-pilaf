import csv
import os
import pickle


def generate_dict(gene_description_file):
    mapping_dict = {}

    with open(gene_description_file) as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for line in csv_reader:
            id = line[0].strip()
            description = line[1].strip()
            uniprot = line[2].strip()

            mapping_dict[id] = (description, uniprot)

    return mapping_dict


def export_mapping(mapping, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/Nb_gene_descriptions.pickle', 'wb') as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/Nb_gene_descriptions.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('gene_description_file', help='gene description file')
    parser.add_argument(
        'output_dir', help='output directory for the pickled gene description dictionary')

    args = parser.parse_args()
    mapping_dict = generate_dict(args.gene_description_file)
    export_mapping(mapping_dict, args.output_dir)
