import csv
import os
import pickle


def initialize_dict(gene_desc_file):
    mapping_dict = {}

    with open(gene_desc_file) as file:
        reader = csv.reader(file)
        next(reader)
        for line in reader:
            mapping_dict[line[2].strip()] = []

    return mapping_dict


def map_genes_to_proteins(dict, gene_desc_file):
    with open(gene_desc_file) as file:
        reader = csv.reader(file)
        next(reader)
        for line in reader:
            gene = line[0].strip()
            protein = line[2].strip()

            dict[protein].append(gene)


def export_mapping(mapping, output_dir, filename):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/{filename}.pickle", "wb") as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Generated {output_dir}/{filename}.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "gene_desc_file",
        help="text file containing both the genes and it's related proteins",
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the pickled gene description dictionary",
    )
    parser.add_argument("output_name", help="filename of the output file")

    args = parser.parse_args()

    dict = initialize_dict(args.gene_desc_file)
    map_genes_to_proteins(dict, args.gene_desc_file)
    export_mapping(dict, args.output_dir, args.output_name)
