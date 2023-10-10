from dash import Input, Output, State, html, dcc, ctx
from dash.exceptions import PreventUpdate

from .util import *
from ..lift_over import util as lift_over_util


def init_callback(app):
    @app.callback(
        Output('tf-enrichment-genomic-intervals-input', 'children'),
        State('homepage-submitted-genomic-intervals', 'data'),
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
        Output('tfbs-submitted-addl-genes',
               'data', allow_duplicate=True),
        Output('tfbs-submitted-set', 'data', allow_duplicate=True),
        Output('tfbs-submitted-prediction-technique',
               'data', allow_duplicate=True),

        Input('tfbs-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),

        State('tfbs-addl-genes', 'value'),
        State('tfbs-set', 'value'),
        State('tfbs-prediction-technique', 'value'),
        prevent_initial_call=True
    )
    def submit_tfbs_input(tfbs_submitted_n_clicks, homepage_is_submitted, addl_genes, tfbs_set, tfbs_prediction_technique):
        if homepage_is_submitted and tfbs_submitted_n_clicks >= 1:
            return True, addl_genes, tfbs_set, tfbs_prediction_technique

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
        Output('tfbs-submit', 'disabled'),

        Input('tfbs-submit', 'n_clicks'),
        Input('tf-enrichment-result-table', 'data')
    )
    def disable_tfbs_button_upon_run(n_clicks,  *_):
        return ctx.triggered_id == 'tfbs-submit' and n_clicks > 0

    @app.callback(
        Output('tf-enrichment-result-table', 'data'),
        Output('tf-enrichment-result-table', 'columns'),
        Input('tfbs-is-submitted', 'data'),
        State('tfbs-submitted-addl-genes', 'data'),
        State('homepage-submitted-genomic-intervals', 'data'),
        State('homepage-is-submitted', 'data'),
        State('tfbs-submitted-set', 'data'),
        State('tfbs-submitted-prediction-technique', 'data'),
    )
    def display_enrichment_results(tfbs_is_submitted, submitted_addl_genes,
                                   nb_interval_str, homepage_submitted, tfbs_set, tfbs_prediction_technique):
        if homepage_submitted and tfbs_is_submitted:
            if submitted_addl_genes:
                submitted_addl_genes = submitted_addl_genes.strip()
            else:
                submitted_addl_genes = ''

            list_addl_genes = list(
                filter(None, [gene.strip() for gene in submitted_addl_genes.split(';')]))

            # Perform lift-over if it has not been performed.
            # Otherwise, just fetch the results from the file
            lift_over_nb_entire_table = lift_over_util.get_genes_in_Nb(nb_interval_str)[
                0].to_dict('records')

            combined_genes = lift_over_nb_entire_table + \
                get_annotations_addl_gene(list_addl_genes)

            enrichment_results_df = perform_enrichment_all_tf(combined_genes, submitted_addl_genes,
                                                              tfbs_set, tfbs_prediction_technique, nb_interval_str)

            mask = (
                enrichment_results_df['Transcription Factor'] != NULL_PLACEHOLDER)
            enrichment_results_df.loc[mask, 'Transcription Factor'] = get_msu_browser_link(
                enrichment_results_df, 'Transcription Factor')

            columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
                       for x in enrichment_results_df.columns]

            return enrichment_results_df.to_dict('records'), columns

        raise PreventUpdate

    @app.callback(
        Output('tfbs-input', 'children'),
        Input('tfbs-is-submitted', 'data'),
        State('tfbs-submitted-addl-genes', 'data'),
        State('tfbs-submitted-set', 'data'),
        State('tfbs-submitted-prediction-technique', 'data')
    )
    def display_tfbs_submitted_input(tfbs_is_submitted, genes, tfbs_set, tfbs_prediction_technique):
        if tfbs_is_submitted:
            if not genes:
                genes = 'None'
            else:
                genes = '; '.join(
                    list(filter(None, [gene.strip() for gene in genes.split(';')])))

            return [html.B('Additional Genes: '), genes,
                    html.Br(),
                    html.B(
                        'Selected TF Binding Site Prediction Technique: '), tfbs_prediction_technique,
                    html.Br(),
                    html.B('Selected TF Binding Site Regions: '), tfbs_set,
                    html.Br()]

        raise PreventUpdate

    @app.callback(
        Output('tfbs-saved-addl-genes', 'data', allow_duplicate=True),
        Output('tfbs-saved-set', 'data', allow_duplicate=True),
        Output('tfbs-saved-prediction-technique',
               'data', allow_duplicate=True),
        Input('tfbs-addl-genes', 'value'),
        Input('tfbs-set', 'value'),
        Input('tfbs-prediction-technique', 'value'),
        State('homepage-is-submitted', 'data'),
        Input('tfbs-submit', 'n_clicks'),
        prevent_initial_call=True
    )
    def set_input_tfbs_session_state(genes, tfbs_set, tfbs_prediction_technique, homepage_is_submitted, *_):
        if homepage_is_submitted:
            return genes, tfbs_set, tfbs_prediction_technique

        raise PreventUpdate

    @app.callback(
        Output('tfbs-addl-genes', 'value'),
        Output('tfbs-prediction-technique', 'value'),
        Output('tfbs-set', 'value'),

        State('homepage-is-submitted', 'data'),

        State('tfbs-saved-addl-genes', 'data'),
        State('tfbs-saved-prediction-technique', 'data'),
        State('tfbs-saved-set', 'data'),
        Input('tfbs-submit', 'n_clicks')
    )
    def get_input_tfbs_session_state(homepage_is_submitted, genes, tfbs_prediction_technique, tfbs_set, *_):
        if homepage_is_submitted:
            if not tfbs_prediction_technique:
                tfbs_prediction_technique = 'FunTFBS'

            if not tfbs_set:
                tfbs_set = 'promoters'

            return genes, tfbs_prediction_technique, tfbs_set

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
        State('homepage-submitted-genomic-intervals', 'data')
    )
    def download_tfbs_table_to_csv(download_n_clicks, tfbs_df, genomic_intervals):
        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(tfbs_df))
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Regulatory Feature Enrichment.csv', index=False)

        raise PreventUpdate
