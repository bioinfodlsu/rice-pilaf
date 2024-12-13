import os
import pickle


def convert_to_genes(all_proteins_file, data, output_dir):
    """
    Given an all_proteins_file and a mapped dict of proteins to genes,
    convert the all_proteins_file to an all-genes.txt file
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_genes = 0
    file = open(f"{output_dir}/all-genes.txt", "w")

    with open(all_proteins_file) as proteins:
        for protein in proteins:
            protein = protein.rstrip()

            if protein in data:
                genes = data[protein]

                # Write Genes to the Output File
                for gene in genes:
                    file.write(f"{gene}\n")

                total_genes += len(genes)

    file.close()

    print(f"Wrote {total_genes} genes to {output_dir}/all-genes.txt")


def get_protein_to_gene_map(mapping_file):
    with open(mapping_file, "rb") as f:
        data = pickle.load(f)

    return data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "all_proteins_file",
        help="text file corresponding to the list of proteins in the network",
    )
    parser.add_argument(
        "protein_to_gene_mapping",
        help="the pickled dictionary containing protein to gene mapping",
    )
    parser.add_argument("output_dir", help="output directory for the list of genes")
    args = parser.parse_args()

    data = get_protein_to_gene_map(args.protein_to_gene_mapping)
    convert_to_genes(args.all_proteins_file, data, args.output_dir)
