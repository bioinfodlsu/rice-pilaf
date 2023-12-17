from dash import Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate

from .util import *
from ..lift_over import util as lift_over_util
from ..coexpression import util as coexpression_util


def init_callback(app):
    @app.callback(
        Output('summary-genomic-intervals-input', 'children'),
        State('homepage-submitted-genomic-intervals', 'data'),
        Input('homepage-is-submitted', 'data'),
        Input('summary-submit', 'n_clicks')
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('summary-is-submitted', 'data', allow_duplicate=True),
        Output('summary-submitted-addl-genes',
               'data', allow_duplicate=True),
        Output('summary-valid-addl-genes',
               'data', allow_duplicate=True),
        Output('summary-combined-genes',
               'data', allow_duplicate=True),

        Output('summary-addl-genes-error', 'style'),
        Output('summary-addl-genes-error', 'children'),

        Input('summary-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),

        State('homepage-submitted-genomic-intervals', 'data'),
        State('summary-addl-genes', 'value'),
        prevent_initial_call=True
    )
    def submit_summary_input(summary_submitted_n_clicks, homepage_is_submitted,
                             genomic_intervals, submitted_addl_genes):
        if homepage_is_submitted and summary_submitted_n_clicks >= 1:
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
            implicated_gene_ids = lift_over_util.get_genes_in_Nb(genomic_intervals)[
                1]

            gene_ids = list(set.union(
                set(implicated_gene_ids), set(list_addl_genes)))

            return True, submitted_addl_genes, list_addl_genes, gene_ids, error_display, error

        raise PreventUpdate

    @app.callback(
        Output('summary-results-container', 'style'),
        Input('summary-is-submitted', 'data'),
    )
    def display_summary_output(summary_is_submitted):
        if summary_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    # @app.callback(
    #     Output('summary-submit', 'disabled'),

    #     Input('summary-submit', 'n_clicks'),
    #     Input('summary-results-table', 'data')
    # )
    # def disable_summary_button_upon_run(n_clicks,  *_):
    #     return ctx.triggered_id == 'summary-submit' and n_clicks > 0

    @app.callback(
        Output('summary-converter-modal', 'is_open'),
        Input('summary-converter-tooltip', 'n_clicks'),
    )
    def open_modals(summary_converter_tooltip_n_clicks):
        if ctx.triggered_id == 'summary-converter-tooltip' and summary_converter_tooltip_n_clicks > 0:
            return True

        raise PreventUpdate

    @app.callback(
        Output('summary-input', 'children'),

        Input('summary-is-submitted', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('summary-valid-addl-genes', 'data'),
        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-slider', 'data')
    )
    def display_summary_submitted_input(summary_is_submitted, coexpression_is_submitted, addl_genes, network, algo, submitted_parameter_slider):
        if coexpression_is_submitted:
            parameters = 0
            if submitted_parameter_slider and algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[algo]['value']

        else:
            # Assume default coexpression network parameters
            algo = 'clusterone'
            network = 'OS-CX'
            parameters = 30

        if summary_is_submitted:
            if not addl_genes:
                addl_genes = 'None'
            else:
                addl_genes = '; '.join(set(addl_genes))

            return [html.B('Additional Genes: '), addl_genes,
                    html.Br(),
                    html.B('Selected Co-Expression Network: '), coexpression_util.get_user_facing_network(
                        network),
                    html.Br(),
                    html.B('Selected Module Detection Algorithm: '), coexpression_util.get_user_facing_algo(
                        algo),
                    html.Br(),
                    html.B('Selected Algorithm Parameter: '), coexpression_util.get_user_facing_parameter(algo, parameters)]

        raise PreventUpdate

    # =================
    # Table-related
    # =================

    @app.callback(
        Output('summary-results-table', 'data'),
        Output('summary-results-table', 'columns'),

        State('homepage-submitted-genomic-intervals', 'data'),

        Input('summary-combined-genes', 'data'),
        Input('summary-submitted-addl-genes', 'data'),

        State('homepage-is-submitted', 'data'),
        State('summary-is-submitted', 'data')
    )
    def display_summary_results(genomic_intervals, combined_genes, submitted_addl_genes,
                                homepage_submitted, summary_is_submitted):
        if homepage_submitted and summary_is_submitted:
            summary_results_df = make_summary_table(
                genomic_intervals, combined_genes)

            columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
                       for x in summary_results_df.columns]

            return summary_results_df.to_dict('records'), columns

        raise PreventUpdate

    @app.callback(
        Output('summary-results-table', 'filter_query', allow_duplicate=True),
        Output('summary-results-table', 'page_current', allow_duplicate=True),

        Input('summary-reset-table', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_table_filter_page(*_):
        return '', 0

    # @app.callback(
    #     Output('tfbs-download-df-to-csv', 'data'),
    #     Input('tfbs-export-table', 'n_clicks'),
    #     State('tfbs-results-table', 'data'),
    #     State('homepage-submitted-genomic-intervals', 'data')
    # )
    # def download_tfbs_table_to_csv(download_n_clicks, tfbs_df, genomic_intervals):
    #     if download_n_clicks >= 1:
    #         df = pd.DataFrame(purge_html_export_table(tfbs_df))
    #         return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Regulatory Feature Enrichment.csv', index=False)

    #     raise PreventUpdate

    # =================
    # Session-related
    # =================

    # @app.callback(
    #     Output('summary-addl-genes', 'value'),

    #     State('tfbs-submitted-addl-genes', 'data')
    # )
    # def get_input_tfbs_session_state(addl_genes):
    #     return addl_genes
