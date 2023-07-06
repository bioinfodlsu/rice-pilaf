from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util

gwas_loci = None

Tfbs_input = namedtuple(
    'Tfbs_input', ['tfbs_set', 'tfbs_prediction_technique'])


def init_callback(app):
    @app.callback(
        Output('tf-enrichment-genomic-intervals-input', 'children'),
        Input('homepage-genomic-intervals-saved-input', 'data'),
        State('homepage-is-submitted', 'data'),
    )
    def display_input(nb_intervals_str, homepage_is_submitted):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your input intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('tfbs-results-container', 'style', allow_duplicate=True),
        Output('tfbs-is-submitted', 'data', allow_duplicate=True),
        Output('tfbs-submitted-input', 'data', allow_duplicate=True),
        Input('tfbs-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),
        State('tfbs_set', 'value'),
        State('tfbs_prediction_technique', 'value'),
        prevent_initial_call=True
    )
    def display_tfbs_results(tfbs_submitted_n_clicks, homepage_is_submitted, tfbs_set, tfbs_prediction_technique):
        if homepage_is_submitted and tfbs_submitted_n_clicks >= 1:
            submitted_input = Tfbs_input(
                tfbs_set, tfbs_prediction_technique)._asdict()

            return {'display': 'block'}, True, submitted_input

        raise PreventUpdate

    @app.callback(
        Output('tf_enrichment_result_table', 'data'),
        State('lift_over_nb_entire_table', 'data'),
        State('homepage-genomic-intervals-saved-input', 'data'),

        State('tfbs-is-submitted', 'data'),
        State('homepage-is-submitted', 'data'),
        Input('tfbs-submitted-input', 'data'),
        Input('tfbs_set', 'value'),
        prevent_initial_call=True
    )
    def display_enrichment_results(lift_over_nb_entire_table, nb_interval_str, tfbs_is_submitted, homepage_submitted, tfbs_submitted_input, tfbs_set):
        if homepage_submitted and tfbs_is_submitted:
            # TODO this should be moved to lift_over/callbacks.py
            write_promoter_intervals_to_file(
                lift_over_nb_entire_table, nb_interval_str)

            tfbs_set = tfbs_submitted_input['tfbs_set']
            tfbs_prediction_technique = tfbs_submitted_input['tfbs_prediction_technique']

            enrichment_results_df = perform_enrichment_all_tf(
                tfbs_set, tfbs_prediction_technique, nb_interval_str)

            return enrichment_results_df.to_dict('records')

        raise PreventUpdate

    @app.callback(
        Output('tfbs-saved-input',
               'data', allow_duplicate=True),
        Input('tfbs_set', 'value'),
        Input('tfbs_prediction_technique', 'value'),
        State('homepage-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def set_input_tfbs_session_state(tfbs_set, tfbs_prediction_technique, homepage_is_submitted):
        if homepage_is_submitted:
            tfbs_saved_input = Tfbs_input(
                tfbs_set, tfbs_prediction_technique)._asdict()

            return tfbs_saved_input

        raise PreventUpdate

    @app.callback(
        Output('tfbs-results-container', 'style', allow_duplicate=True),
        Input('tfbs-saved-input', 'data'),
        Input('tfbs-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def display_submitted_tfbs_results(tfbs_saved_input, tfbs_is_submitted):
        if tfbs_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    @app.callback(
        Output('tfbs_set', 'value'),
        Output('tfbs_prediction_technique', 'value'),
        Input('homepage-genomic-intervals-saved-input', 'data'),
        State('homepage-is-submitted', 'data'),
        State('tfbs-saved-input', 'data')
    )
    def display_submitted_tfbs_input(nb_intervals_str, homepage_is_submitted, tfbs_saved_input):
        if homepage_is_submitted:
            if not tfbs_saved_input:
                return 'promoters', 'FunTFBS'

            return tfbs_saved_input['tfbs_set'], tfbs_saved_input['tfbs_prediction_technique']

        raise PreventUpdate
