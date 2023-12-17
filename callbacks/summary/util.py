from ..lift_over.util import *
from ..general_util import *

from collections import defaultdict


def get_liftover_summary(genomic_interval):
    all_genes = get_all_genes(other_ref_genomes.keys(),
                              genomic_interval).values.tolist()

    NB_IDX = 1
    NB_PREFIX = 'LOC_Os'

    gene_to_orthologs_map = defaultdict(set)
    for row in all_genes:
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
        gene_to_count, columns=['Gene', '# Orthologs'])
    return gene_to_count_df


def make_summary_table(genomic_interval, implicated_genes):
    return get_liftover_summary(genomic_interval)
