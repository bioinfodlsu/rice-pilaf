import os
import pickle
from collections import defaultdict


def map_genes_to_ontology(ontology_files):
    genes_to_ontology_mapping = defaultdict(set)

    for ontology_file in ontology_files:
        with open(ontology_file) as f:
            for line in f:
                ontology, gene = line.strip().split('\t')
                genes_to_ontology_mapping[gene].add(ontology)

    return genes_to_ontology_mapping


def export_mapping(mapping, output_dir, option):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/genes_to_{option}.pickle', 'wb') as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(f'Generated {output_dir}/genes_to_{option}.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'output_dir', help='output directory for the pickled dictionary mapping genes to their ontology terms'
    )
    parser.add_argument(
        'option', help='can be "go" (for gene ontology), "po" (for plant ontology), "to" (for term ontology), or "pathway"'
    )
    parser.add_argument(
        'ontology_files', help='text files containing the GO annotations', nargs='+')

    args = parser.parse_args()

    export_mapping(map_genes_to_ontology(args.ontology_files),
                   args.output_dir, args.option)
