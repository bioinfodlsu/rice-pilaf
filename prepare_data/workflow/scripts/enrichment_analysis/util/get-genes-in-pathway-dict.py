import csv
import os
import pickle

from collections import defaultdict


def convert_geneset_to_dict(geneset_file):
    pathway_dict = defaultdict(set)

    with open(geneset_file) as f:
        csv_reader = csv.reader(f, delimiter='\t')
        for line in csv_reader:
            gene_components = line[0].split('.')
            gene = f'{gene_components[1]}-{gene_components[2]}'
            pathway = line[1][len('path:'):]

            pathway_dict[pathway].add(gene)

    return pathway_dict


def save_pathway_dict(pathway_dict, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/kegg_dosa_geneset.pickle', 'wb') as handle:
        pickle.dump(pathway_dict, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/kegg_dosa_geneset.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'geneset_file', help='text file mapping the genes to their respective KEGG pathways')
    parser.add_argument(
        'output_dir', help='output directory for the pickled dictionary mapping KEGG pathways to their genes')

    args = parser.parse_args()

    pathway_dict = convert_geneset_to_dict(args.geneset_file)
    save_pathway_dict(pathway_dict, args.output_dir)
