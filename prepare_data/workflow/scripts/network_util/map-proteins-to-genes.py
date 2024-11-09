import os

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
            
            gene_count = search_genes(protein, gene_desc_file, file)
            total_genes += gene_count
    
    file.close()
    
    print(f"Wrote {total_genes} genes to {output_dir}/all-genes.txt")
            
def search_genes(protein, gene_desc_file, output_file) -> int:
    """
    Iterate over the gene_desc_file and write the genes of the protein to
    the output_file.
    
    Parameters:
    protein (string): The protein to be checked
    gene_desc_file (string): The path to the gene_description file
    output_file (file): an open file for writing
    
    Return:
    number of genes of the protein written to the file
    """
    gene_count = 0
    with open(gene_desc_file) as genes:
        next(genes) #skip header
        
        for gene in genes:
            gene = gene.rstrip()
            cols = gene.split(",")
            
            gene_id, gene_prot = cols[0], cols[-1]
            
            if protein == gene_prot:
                output_file.write(f"{gene_id}\n")
                gene_count += 1
    
    return gene_count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("all_proteins_file", help="text file corresponding to the list of proteins in the network")
    parser.add_argument("gene_desc_file", help="the csv file containing the gene descriptions and its protein")
    parser.add_argument("output_dir", help="output directory for the list of genes")
    args = parser.parse_args()
    
    get_genes(args.all_proteins_file, args.gene_desc_file, args.output_dir)