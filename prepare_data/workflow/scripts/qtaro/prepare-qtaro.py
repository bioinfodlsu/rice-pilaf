import csv
import os
import pickle
from collections import defaultdict


def convert_default_to_vanilla_dict(d):
    """
    Lifted from https://stackoverflow.com/questions/26496831/how-to-convert-defaultdict-of-defaultdicts-of-defaultdicts-to-dict-of-dicts-o
    """
    if isinstance(d, defaultdict):
        d = {k: convert_default_to_vanilla_dict(v) for k, v in d.items()}
    return d


def prepare_qtaro_mapping(annotation_file):
    mapping = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    with open(annotation_file, encoding="utf8") as qtaro:
        csv_reader = csv.reader(qtaro, delimiter=",")
        for line in csv_reader:
            gene = line[-1]
            character_major = line[3]
            character_minor = line[4]
            pub = line[-2]

            mapping[gene][character_major][character_minor].add(pub)

    print("Generated dictionary from QTARO annotation file")

    return convert_default_to_vanilla_dict(mapping)


def export_mapping(mapping, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/qtaro.pickle", "wb") as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Generated {output_dir}/qtaro.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("annotation_file", help="annotation file from QTARO")
    parser.add_argument(
        "output_dir",
        help="output directory for the dictionary resulting from preprocessing the QTARO annotation file",
    )

    args = parser.parse_args()

    mapping = prepare_qtaro_mapping(args.annotation_file)
    export_mapping(mapping, args.output_dir)
