import os
from common.ppi import search_genes


def map_protein_modules(modules_file, gene_desc_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = f"{output_dir}/{os.path.basename(modules_file)}"
    file = open(output_path, "w")

    total_modules = 0
    with open(modules_file) as modules:
        for module in modules:
            mod = module.strip("\n").split("\t")

            genes = get_genes_of_module(mod, gene_desc_file)
            write_genes_to_file(genes, file)

            total_modules += 1

    print(f"Converted protein {total_modules} modules to genes in {output_path}")


def get_genes_of_module(module, gene_desc_file):
    result = []
    for protein in module:
        genes = search_genes(protein, gene_desc_file)
        result.extend(genes)
    return result


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
        "gene_desc_file",
        help="the csv file containing the gene descriptions and its protein",
    )
    parser.add_argument(
        "output_dir", help="output directory for the converted module list"
    )
    args = parser.parse_args()

    map_protein_modules(args.modules_file, args.gene_desc_file, args.output_dir)
