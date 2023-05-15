from dash import Input, Output

from .util import *


def init_callback(app):
    @app.callback(
        Output('coexpression-input-genomic-intervals', 'children'),
        Input('lift-over-nb-table', 'data')
    )
    def display_implicated_genes(gene_ids):
        return 'Implicated genes: ' + ', '.join(gene_ids)

    @app.callback(
        Output('coexpression-loading', 'hidden'),
        Input('lift-over-nb-table', 'data')
    )
    def perform_module_enrichment(gene_ids):
        do_module_enrichment_analysis(gene_ids)
        return True
