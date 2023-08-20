import csv
from collections import defaultdict
import os
import dill


def prepare_qtaro_mapping(annotation_file):
    mapping = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    with open(annotation_file, encoding='utf8') as qtaro:
        csv_reader = csv.reader(qtaro, delimiter=',')
        for line in csv_reader:
            gene = line[-1]
            character_major = line[3]
            character_minor = line[4]
            pub = line[-2]

            mapping[gene][character_major][character_minor].add(pub)

    print("Generated dictionary from QTARO annotation file")

    return mapping


def export_mapping(mapping, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f'{output_dir}/qtaro.pickle', 'wb') as handle:
        dill.dump(mapping, handle)

    print(f'Generated {output_dir}/qtaro.pickle')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('annotation_file', help='annotation file from QTARO')
    parser.add_argument(
        'output_dir', help='output directory for the dictionary resulting from preprocessing the QTARO annotation file')

    args = parser.parse_args()

    mapping = prepare_qtaro_mapping(args.annotation_file)
    export_mapping(mapping, args.output_dir)
