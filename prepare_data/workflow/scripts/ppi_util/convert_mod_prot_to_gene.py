import os
import pickle


def map_protein_modules(modules_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = f"{output_dir}/{os.path.basename(modules_file)}"
    file = open(output_path, "w")

    total_modules = 0
    with open(modules_file) as modules:
        for module in modules:
            mod = module.strip("\n").split("\t")

            genes = get_genes_of_module(mod)
            write_genes_to_file(genes, file)

            total_modules += 1

    print(f"Converted protein {total_modules} modules to genes in {output_path}")


def get_genes_of_module(module):
    result, history = [], []
    for protein in module:
        if not protein in DATA:
            continue

        unique_genes = retrieve_unique_genes(DATA[protein], history)
        result.extend(unique_genes)
        history.extend(unique_genes)

    return result


def retrieve_unique_genes(genes, history):
    unique = []
    for gene in genes:
        if not gene in history:
            unique.append(gene)
    return unique


def get_protein_to_gene_map(mapping_file):
    with open(mapping_file, "rb") as f:
        data = pickle.load(f)

    return data


def write_genes_to_file(gene_list, file):
    for gene in gene_list:
        file.write(f"{gene}\t")
    file.write("\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "modules_file",
        help="the protein module list file generated after executing module detect algos",
    )
    parser.add_argument(
        "protein_to_gene_mapping",
        help="the pickled dictionary containing protein to gene mapping",
    )
    parser.add_argument(
        "output_dir", help="output directory for the converted module list"
    )
    args = parser.parse_args()

    DATA = get_protein_to_gene_map(args.protein_to_gene_mapping)

    map_protein_modules(args.modules_file, args.output_dir)
