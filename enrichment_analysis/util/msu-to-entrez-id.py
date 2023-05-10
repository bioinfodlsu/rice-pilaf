import os
import pickle
from collections import defaultdict


def save_msu_transcript_mapping(msu_to_transcript_dict, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/msu-to-transcript-id.pickle', 'wb') as handle:
        pickle.dump(msu_to_transcript_dict, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)

    print(f'Generated {output_dir}/msu-to-transcript-id.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'msu_genes', help='text file containing the input genes (MSU ID)')
    parser.add_argument(
        'msu_to_entrez_file', help='text file mapping RAP accessions to KEGG transcript IDs')
    parser.add_argument(
        'output_dir', help='output directory for the pickled dictionary mapping MSU accessions to their respective KEGG transcript IDs')

    args = parser.parse_args()
