import os
import pickle
from collections import defaultdict


def map_genes_to_ontology(ontology_file):
    genes_to_ontology_mapping = defaultdict(set)

    with open(ontology_file) as f:
        for line in f:
            ontology, gene = line.strip().split('\t')
            genes_to_ontology_mapping[gene].add(ontology)

    return genes_to_ontology_mapping


def export_mapping(mapping, output_dir, option):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.exists(f'{output_dir}/genes_to_{option}.pickle'):
        with open(f'{output_dir}/genes_to_{option}.pickle', 'rb') as handle:
            curr_mapping = pickle.load(handle)
            for gene, ontology in curr_mapping.items():
                mapping[gene] = mapping[gene].union(ontology)

        print(f'Merged existing mapping with newly constructed one')

    with open(f'{output_dir}/genes_to_{option}.pickle', 'wb') as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print(f'Generated {output_dir}/genes_to_{option}.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'ontology_file', help='text file containing the GO annotations')
    parser.add_argument(
        'output_dir', help='output directory for the pickled dictionary mapping genes to their ontology terms'
    )
    parser.add_argument(
        'option', help='can be "go" (for gene ontology), "po" (for plant ontology), "to" (for term ontology), or "pathway"'
    )

    args = parser.parse_args()

    export_mapping(map_genes_to_ontology(args.ontology_file),
                   args.output_dir, args.option)
