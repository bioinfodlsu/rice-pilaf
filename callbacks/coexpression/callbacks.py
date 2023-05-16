from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from .util import *


def init_callback(app):
    @app.callback(
        Output('coexpression-input-genomic-intervals', 'children'),
        Input('lift-over-nb-table', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_implicated_genes(gene_ids, is_submitted):
        if is_submitted:
            return 'Implicated genes: ' + ', '.join(gene_ids)

        raise PreventUpdate

    @app.callback(
        Output('coexpression-loading', 'hidden'),
        Input('lift-over-nb-table', 'data'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def perform_module_enrichment(gene_ids, genomic_intervals, is_submitted):
        if is_submitted:
            do_module_enrichment_analysis(gene_ids, genomic_intervals)
            return True

        raise PreventUpdate
