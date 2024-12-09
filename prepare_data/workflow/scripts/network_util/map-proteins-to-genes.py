import os
from common.ppi import search_genes


def get_genes(all_proteins_file, gene_desc_file, output_dir):
    """
    Iterate over the all_proteins_file and for each protein search
    the genes_description file and write the genes related to the protein
    in the output_dir.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_genes = 0
    file = open(f"{output_dir}/all-genes.txt", "w")

    with open(all_proteins_file) as proteins:
        for protein in proteins:
            protein = protein.rstrip()

            genes = search_genes(protein, gene_desc_file)

            # Write Genes to the Output File
            for gene in genes:
                file.write(f"{gene}\n")

            total_genes += len(genes)

    file.close()

    print(f"Wrote {total_genes} genes to {output_dir}/all-genes.txt")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "all_proteins_file",
        help="text file corresponding to the list of proteins in the network",
    )
    parser.add_argument(
        "gene_desc_file",
        help="the csv file containing the gene descriptions and its protein",
    )
    parser.add_argument("output_dir", help="output directory for the list of genes")
    args = parser.parse_args()

    get_genes(args.all_proteins_file, args.gene_desc_file, args.output_dir)
