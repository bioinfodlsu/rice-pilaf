from dash import Input, Output, State, html, dcc, ctx
from dash.exceptions import PreventUpdate

from .util import *
from ..lift_over import util as lift_over_util
from ..coexpression import util as coexpression_util


def init_callback(app):
    @app.callback(
        Output('tfbs-genomic-intervals-input', 'children'),
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
        Output('tfbs-valid-addl-genes',
               'data', allow_duplicate=True),
        Output('tfbs-combined-genes',
               'data', allow_duplicate=True),

        Output('tfbs-submitted-set', 'data', allow_duplicate=True),
        Output('tfbs-submitted-prediction-technique',
               'data', allow_duplicate=True),

        Output('tfbs-addl-genes-error', 'style'),
        Output('tfbs-addl-genes-error', 'children'),

        Input('tfbs-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),

        State('homepage-submitted-genomic-intervals', 'data'),
        State('tfbs-addl-genes', 'value'),

        State('tfbs-set', 'value'),
        State('tfbs-prediction-technique', 'value'),
        prevent_initial_call=True
    )
    def submit_tfbs_input(tfbs_submitted_n_clicks, homepage_is_submitted,
                          genomic_intervals, submitted_addl_genes,
                          submitted_tfbs_set, submitted_tfbs_prediction_technique):
        if homepage_is_submitted and tfbs_submitted_n_clicks >= 1:
            if submitted_addl_genes:
                submitted_addl_genes = submitted_addl_genes.strip()
            else:
                submitted_addl_genes = ''

            list_addl_genes = list(
                filter(None, [gene.strip() for gene in submitted_addl_genes.split(';')]))

            # Check which genes are valid MSU IDs
            list_addl_genes, invalid_genes = coexpression_util.check_if_valid_msu_ids(
                list_addl_genes)

            if not invalid_genes:
                error_display = {'display': 'none'}
                error = None
            else:
                error_display = {'display': 'block'}

                if len(invalid_genes) == 1:
                    error_msg = invalid_genes[0] + \
                        ' is not a valid MSU accession ID.'
                    error_msg_ignore = 'It'
                else:
                    if len(invalid_genes) == 2:
                        error_msg = invalid_genes[0] + \
                            ' and ' + invalid_genes[1]
                    else:
                        error_msg = ', '.join(
                            invalid_genes[:-1]) + ', and ' + invalid_genes[-1]

                    error_msg += ' are not valid MSU accession IDs.'
                    error_msg_ignore = 'They'

                error = [html.Span(error_msg), html.Br(), html.Span(
                    f'{error_msg_ignore} will be ignored when running the analysis.')]

            # Perform lift-over if it has not been performed.
            # Otherwise, just fetch the results from the file
            lift_over_nb_entire_table = lift_over_util.get_genes_in_Nb(genomic_intervals)[
                0].to_dict('records')

            combined_genes = lift_over_nb_entire_table + \
                get_annotations_addl_gene(list_addl_genes)

            return True, submitted_addl_genes, list_addl_genes, combined_genes, submitted_tfbs_set, submitted_tfbs_prediction_technique, error_display, error

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
        Input('tfbs-results-table', 'data')
    )
    def disable_tfbs_button_upon_run(n_clicks,  *_):
        return ctx.triggered_id == 'tfbs-submit' and n_clicks > 0

    @app.callback(
        Output('tfbs-results-table', 'data'),
        Output('tfbs-results-table', 'columns'),

        State('homepage-submitted-genomic-intervals', 'data'),

        Input('tfbs-combined-genes', 'data'),
        Input('tfbs-submitted-addl-genes', 'data'),

        State('homepage-is-submitted', 'data'),
        State('tfbs-submitted-set', 'data'),
        State('tfbs-submitted-prediction-technique', 'data'),
        State('tfbs-is-submitted', 'data')
    )
    def display_enrichment_results(genomic_intervals, combined_genes, submitted_addl_genes,
                                   homepage_submitted, tfbs_set, tfbs_prediction_technique, tfbs_is_submitted):
        if homepage_submitted and tfbs_is_submitted:
            enrichment_results_df = perform_enrichment_all_tf(combined_genes, submitted_addl_genes,
                                                              tfbs_set, tfbs_prediction_technique, genomic_intervals)

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
        State('tfbs-valid-addl-genes', 'data'),
        State('tfbs-submitted-set', 'data'),
        State('tfbs-submitted-prediction-technique', 'data')
    )
    def display_tfbs_submitted_input(tfbs_is_submitted, addl_genes, tfbs_set, tfbs_prediction_technique):
        if tfbs_is_submitted:
            if not addl_genes:
                addl_genes = 'None'
            else:
                addl_genes = '; '.join(set(addl_genes))

            return [html.B('Additional Genes: '), addl_genes,
                    html.Br(),
                    html.B(
                        'Selected TF Binding Site Prediction Technique: '), tfbs_prediction_technique,
                    html.Br(),
                    html.B('Selected TF Binding Site Regions: '), tfbs_set,
                    html.Br()]

        raise PreventUpdate

    @app.callback(
        Output('tfbs-addl-genes', 'value'),
        Output('tfbs-prediction-technique', 'value'),
        Output('tfbs-set', 'value'),

        State('tfbs-submitted-addl-genes', 'data'),
        State('tfbs-submitted-prediction-technique', 'data'),
        State('tfbs-submitted-set', 'data'),
        Input('tfbs-is-submitted', 'data')
    )
    def get_input_tfbs_session_state(addl_genes, tfbs_prediction_technique, tfbs_set, *_):
        if not tfbs_prediction_technique:
            tfbs_prediction_technique = 'FunTFBS'

        if not tfbs_set:
            tfbs_set = 'promoters'

        return addl_genes, tfbs_prediction_technique, tfbs_set

    @app.callback(
        Output('tfbs-converter-modal', 'is_open'),

        Input('tfbs-converter-tooltip', 'n_clicks'),
    )
    def open_modals(converter_tooltip_n_clicks):
        if ctx.triggered_id == 'tfbs-converter-tooltip' and converter_tooltip_n_clicks > 0:
            return True

        raise PreventUpdate

    @app.callback(
        Output('tfbs-results-table', 'filter_query'),
        Output('tfbs-results-table', 'page_current'),

        Input('tfbs-reset-table', 'n_clicks'),
        Input('tfbs-submit', 'n_clicks')
    )
    def reset_table_filter_page(*_):
        return '', 0

    @app.callback(
        Output('tfbs-download-df-to-csv', 'data'),
        Input('tfbs-export-table', 'n_clicks'),
        State('tfbs-results-table', 'data'),
        State('homepage-submitted-genomic-intervals', 'data')
    )
    def download_tfbs_table_to_csv(download_n_clicks, tfbs_df, genomic_intervals):
        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(tfbs_df))
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Regulatory Feature Enrichment.csv', index=False)

        raise PreventUpdate
