import os

from ..constants import Constants

const = Constants()


def write_genes_to_file(genes):
    if not os.path.exists(const.IMPLICATED_GENES):
        os.makedirs(const.IMPLICATED_GENES)

    with open(f'{const.IMPLICATED_GENES}/genes.txt', 'w') as f:
        f.write('\t'.join(genes))
        f.write('\n')


def do_module_enrichment_analysis(gene_ids):
    genes = list(set(gene_ids))
    write_genes_to_file(genes)
