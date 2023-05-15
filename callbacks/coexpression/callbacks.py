from dash import Input, Output
from dash.exceptions import PreventUpdate

from .util import *


def init_callback(app):
    @app.callback(
        Output('coexpression-input-genomic-intervals', 'children'),
        Input('lift-over-nb-table', 'data')
    )
    def test(gene_ids):
        do_module_enrichment_analysis(gene_ids)
        return 'Implicated genes: ' + ', '.join(gene_ids)

        raise PreventUpdate
