from collections import defaultdict
import os
import pickle


def map_genes_to_modules(module_file):
    genes_to_modules_mapping = defaultdict(set)

    with open(module_file) as f:
        for idx, line in enumerate(f):
            genes = line.strip().split("\t")
            for gene in genes:
                gene = gene.strip()
                # Add 1 since modules are indexed by 1
                genes_to_modules_mapping[gene].add(idx + 1)

    return genes_to_modules_mapping


def export_mapping(mapping, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/genes_to_modules.pickle", "wb") as handle:
        pickle.dump(mapping, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Generated {output_dir}/genes_to_modules.pickle")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "module_file", help="text file storing the genes in each module"
    )
    parser.add_argument(
        "output_dir",
        help="output directory for the pickled dictionary mapping genes to the modules where they belong",
    )

    args = parser.parse_args()

    export_mapping(map_genes_to_modules(args.module_file), args.output_dir)
