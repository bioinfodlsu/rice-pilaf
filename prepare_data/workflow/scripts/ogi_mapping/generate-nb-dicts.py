import pickle
from collections import defaultdict
import os


def convert_default_to_vanilla_dict(d):
    """
    Lifted from https://stackoverflow.com/questions/26496831/how-to-convert-defaultdict-of-defaultdicts-of-defaultdicts-to-dict-of-dicts-o
    """
    if isinstance(d, defaultdict):
        d = {k: convert_default_to_vanilla_dict(v) for k, v in d.items()}
    return d


def create_mapping_dict(input_dir, cultivar):
    # Load the cultivar-to-OGI dictionary
    with open(f'{input_dir}/{cultivar}_to_ogi.pickle', 'rb') as f:
        cultivar_to_ogi = pickle.load(f)

    # Load the Nb-to-OGI dictionary
    with open(f'{input_dir}/Nb_to_ogi.pickle', 'rb') as f:
        nb_to_ogi = pickle.load(f)

    # Construct ogi-to-nb dictionary
    ogi_to_nb = defaultdict(set)
    for nb, ogi in nb_to_ogi.items():
        ogi_to_nb[ogi].add(nb)

    # Construct cultivar-to-nb dictionary
    cultivar_to_nb = defaultdict(set)
    for cultivar in cultivar_to_ogi:
        cultivar_to_nb[cultivar] = ogi_to_nb[cultivar_to_ogi[cultivar]]

    return convert_default_to_vanilla_dict(cultivar_to_nb)


def create_mapping_dicts_for_cultivars(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        cultivar = file.split('_')[0]
        if cultivar != 'Nb':
            mapping = create_mapping_dict(input_dir, cultivar)

            with open(f'{output_dir}/{cultivar}_to_Nb.pickle', 'wb') as f:
                pickle.dump(mapping, f, protocol=pickle.HIGHEST_PROTOCOL)

            print(f'Generated {output_dir}/{cultivar}_to_Nb.pickle')

    print(f'Finished generating accession-to-Nb mapping dictionaries')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_dir', help='directory containing the pickled accesstion-to-OGI mapping dictionaries')
    parser.add_argument(
        'output_dir', help='directory containing the pickled accesstion-to-Nipponbare mapping dictionaries')

    args = parser.parse_args()

    create_mapping_dicts_for_cultivars(args.input_dir, args.output_dir)
