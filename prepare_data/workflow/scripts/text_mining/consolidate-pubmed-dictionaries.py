import os
import pickle


def consolidate_pubmed_dictionaries(pubmed_dictionary_dir, output_dir):
    mapping = {}
    for dictionary in os.listdir(pubmed_dictionary_dir):
        with open(f'{pubmed_dictionary_dir}/{dictionary}', 'rb') as f:
            gene = dictionary[:-len('.pickle')]
            mapping[gene] = pickle.load(f)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/pubmed_per_gene.pickle', 'wb') as f:
        pickle.dump(mapping, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/pubmed_per_gene.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'pubmed_dictionary_dir', help='directory containing the dictionaries with the PubMed IDs of related articles')
    parser.add_argument(
        'output_dir', help='output directory for the dictionary consolidating the PubMed IDs of related articles')

    args = parser.parse_args()

    consolidate_pubmed_dictionaries(
        args.pubmed_dictionary_dir, args.output_dir)
