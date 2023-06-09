from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from .util import *
gwas_loci = None


def init_callback(app):
    @app.callback(
        Output('tf_enrichment_result_table', 'data'),
        Input('lift_over_nb_entire_table', 'data'),
        Input('tfbs_set', 'value'),
        Input('tfbs_prediction_technique', 'value'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        Input('tfbs-submit', 'n_clicks'),
        State('lift-over-is-submitted', 'data')
    )
    def display_enrichment_results(lift_over_nb_entire_table, tfbs_set, tfbs_prediction_technique,
                                   nb_interval_str, tfbs_submit_n_clicks, lift_over_submitted):
        if lift_over_submitted and tfbs_submit_n_clicks >= 1:
            nb_interval_str_fname = nb_interval_str.replace(
                ":", "_").replace(";", "__").replace("-", "_")
            # TODO this should be moved to lift_over/callbacks.py
            write_promoter_intervals_to_file(
                lift_over_nb_entire_table, nb_interval_str_fname)
            enrichment_results_df = perform_enrichment_all_tf(
                tfbs_set, tfbs_prediction_technique, nb_interval_str_fname)
            return enrichment_results_df.to_dict('records')

        raise PreventUpdate
