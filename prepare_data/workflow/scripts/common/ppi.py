def search_genes(protein, gene_desc_file) -> int:
    """
    Iterate over the gene_desc_file and find all the genes related to the protein.

    Parameters:
    protein (string): The protein to be checked
    gene_desc_file (string): The path to the gene_description file

    Return:
    The list of genes related to the protein
    """
    result = []
    with open(gene_desc_file) as genes:
        next(genes)  # skip header

        for gene in genes:
            gene = gene.rstrip()
            cols = gene.split(",")

            gene_id, gene_prot = cols[0], cols[-1]

            if protein == gene_prot:
                result.append(gene_id)

    return result
