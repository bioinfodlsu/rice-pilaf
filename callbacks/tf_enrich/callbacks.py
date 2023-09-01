from dash import Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util

Tfbs_input = namedtuple(
    'Tfbs_input', ['tfbs_set', 'tfbs_prediction_technique', 'tfbs_fdr'])


def init_callback(app):
    @app.callback(
        Output('tf-enrichment-genomic-intervals-input', 'children'),
        State('homepage-genomic-intervals-submitted-input', 'data'),
        Input('homepage-is-submitted', 'data'),
        Input('tfbs-submit', 'n_clicks')
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('tfbs-is-submitted', 'data', allow_duplicate=True),
        Output('tfbs-submitted-input', 'data', allow_duplicate=True),

        Input('tfbs-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),

        State('tfbs-addl-genes', 'value'),
        State('tfbs-set', 'value'),
        State('tfbs-prediction-technique', 'value'),
        State('tfbs-fdr', 'value'),
        prevent_initial_call=True
    )
    def submit_tfbs_input(tfbs_submitted_n_clicks, homepage_is_submitted, addl_genes, tfbs_set, tfbs_prediction_technique, tfbs_fdr):
        if homepage_is_submitted and tfbs_submitted_n_clicks >= 1:
            submitted_input = Tfbs_input(
                tfbs_set, tfbs_prediction_technique, tfbs_fdr)._asdict()

            return True, submitted_input

        raise PreventUpdate

    @app.callback(
        Output('tfbs-results-container', 'style'),
        Input('tfbs-is-submitted', 'data'),
    )
    def display_tfbs_output(tfbs_is_submitted):
        if tfbs_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    @app.callback(
        Output('tf-enrichment-result-table', 'data'),
        Output('tf-enrichment-result-table', 'columns'),

        Input('tfbs-is-submitted', 'data'),
        State('lift-over-nb-entire-table', 'data'),
        State('tfbs-addl-genes', 'value'),

        State('homepage-genomic-intervals-submitted-input', 'data'),

        State('homepage-is-submitted', 'data'),
        State('tfbs-submitted-input', 'data')
    )
    def display_enrichment_results(tfbs_is_submitted, lift_over_nb_entire_table, submitted_addl_genes,
                                   nb_interval_str, homepage_submitted, tfbs_submitted_input):
        if homepage_submitted and tfbs_is_submitted:
            tfbs_set = tfbs_submitted_input['tfbs_set']
            tfbs_prediction_technique = tfbs_submitted_input['tfbs_prediction_technique']
            tfbs_fdr = tfbs_submitted_input['tfbs_fdr']

            if submitted_addl_genes:
                submitted_addl_genes = submitted_addl_genes.strip()
            else:
                submitted_addl_genes = ''

            list_addl_genes = list(
                filter(None, [gene.strip() for gene in submitted_addl_genes.split(';')]))

            combined_genes = lift_over_nb_entire_table + \
                get_annotations_addl_gene(list_addl_genes)

            enrichment_results_df = perform_enrichment_all_tf(combined_genes, submitted_addl_genes,
                                                              tfbs_set, tfbs_prediction_technique, float(tfbs_fdr), nb_interval_str)

            columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
                       for x in enrichment_results_df.columns]

            return enrichment_results_df.to_dict('records'), columns

        raise PreventUpdate

    @app.callback(
        Output('tfbs-saved-input', 'data', allow_duplicate=True),
        Input('tfbs-set', 'value'),
        Input('tfbs-prediction-technique', 'value'),
        Input('tfbs-fdr', 'value'),
        State('homepage-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def set_input_tfbs_session_state(tfbs_set, tfbs_prediction_technique, tfbs_fdr, homepage_is_submitted):
        if homepage_is_submitted:
            tfbs_saved_input = Tfbs_input(
                tfbs_set, tfbs_prediction_technique, tfbs_fdr)._asdict()

            return tfbs_saved_input

        raise PreventUpdate

    @app.callback(
        Output('tfbs-set', 'value'),
        Output('tfbs-prediction-technique', 'value'),
        State('homepage-is-submitted', 'data'),
        State('tfbs-saved-input', 'data'),
        Input('homepage-genomic-intervals-submitted-input', 'data')
    )
    def get_input_tfbs_session_state(homepage_is_submitted, tfbs_saved_input, *_):
        if homepage_is_submitted:
            if not tfbs_saved_input:
                return 'promoters', 'FunTFBS'

            return tfbs_saved_input['tfbs-set'], tfbs_saved_input['tfbs-prediction-technique']

        raise PreventUpdate

    @app.callback(
        Output('tf-enrichment-result-table', 'filter_query'),
        Input('tfbs-reset-table', 'n_clicks')
    )
    def reset_table_filters(*_):
        return ''

    @app.callback(
        Output('tfbs-download-df-to-csv', 'data'),
        Input('tfbs-export-table', 'n_clicks'),
        State('tf-enrichment-result-table', 'data'),
        State('homepage-genomic-intervals-submitted-input', 'data')
    )
    def download_tfbs_table_to_csv(download_n_clicks, tfbs_df, genomic_intervals):
        if download_n_clicks >= 1:
            df = pd.DataFrame(tfbs_df)
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Regulatory Feature Enrichment.csv', index=False)

        raise PreventUpdate
