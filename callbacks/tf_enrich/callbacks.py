from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from .util import *
gwas_loci = None

def init_callback(app):
    @app.callback(
        Output('TF-enrichment-input-genomic-intervals', 'children'),
        Input('lift-over-nb-table', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_implicated_genes(gene_ids, is_submitted):
        if is_submitted:
            return 'Implicated genes: ' + ', '.join(gene_ids)
        raise PreventUpdate

    @app.callback(
        Output('tf_enrichment_result_table', 'data'),
        Input('tfbs_set', 'value')
    )
    def display_enrichment_results(tfbs_set):
        enrichment_results_df = perform_enrichment_all_tf(tfbs_set,gwas_loci)
        return enrichment_results_df.to_dict('records')

