from ..lift_over.util import *
from ..general_util import *

from collections import defaultdict


def get_liftover_summary(implicated_genes):
    NB_IDX = 1
    NB_PREFIX = 'LOC_Os'

    gene_to_orthologs_map = defaultdict(set)
    for row in implicated_genes:
        if row[NB_IDX].startswith(NB_PREFIX):
            # Subtract 2 (i.e., subtract OGI)
            for gene in row:
                if gene != NULL_PLACEHOLDER:
                    gene_to_orthologs_map[row[NB_IDX]].add(gene)

    gene_to_count = []
    for gene, orthologs in gene_to_orthologs_map.items():
        # Subtract 2 to remove OGI and Nipponbare
        gene_to_count.append([gene, len(orthologs) - 2])

    gene_to_count_df = pd.DataFrame(
        gene_to_count, columns=['Name', '# Orthologs'])

    return gene_to_count_df


def get_num_qtl_pubs(qtl_str):
    # Each QTL study has an associated DOI
    return qtl_str.count('doi.org')


def get_num_pubmed_pubs(pubmed_str):
    # Each PubMed study has an associated PubMed link
    return pubmed_str.count('pubmed')


def get_qtl_summary(genomic_interval):
    genes = get_genes_in_Nb(genomic_interval)[0]
    genes['# QTL Analyses'] = genes.apply(
        lambda x: get_num_qtl_pubs(x['QTL Analyses']), axis=1)

    return genes[['Name', '# QTL Analyses']]


def get_pubmed_summary(genomic_interval):
    genes = get_genes_in_Nb(genomic_interval)[0]
    genes['# PubMed Article IDs'] = genes.apply(
        lambda x: get_num_pubmed_pubs(x['PubMed Article IDs']), axis=1)

    return genes[['Name', '# PubMed Article IDs']]


def make_summary_table(genomic_interval):
    implicated_genes = get_all_genes(other_ref_genomes.keys(),
                                     genomic_interval).values.tolist()

    liftover_summary = get_liftover_summary(implicated_genes)
    qtl_summary = get_qtl_summary(genomic_interval)
    pubmed_summary = get_pubmed_summary(genomic_interval)

    summary = liftover_summary.merge(
        qtl_summary, on='Name', how='left', validate='one_to_one')
    summary = summary.merge(pubmed_summary, on='Name',
                            how='left', validate='one_to_one')

    summary = summary.rename(columns={'Name': 'Gene'})

    return summary
