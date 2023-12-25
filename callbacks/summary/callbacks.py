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
        Input('summary-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def submit_summary_input(summary_submitted_n_clicks, homepage_is_submitted):
        if homepage_is_submitted and summary_submitted_n_clicks >= 1:
            return True

        raise PreventUpdate

    @app.callback(
        Output('summary-results-container', 'style'),
        Input('summary-is-submitted', 'data'),
        Input('coexpression-submit', 'n_clicks'),
    )
    def display_summary_output(summary_is_submitted, *_):
        # Hide the summary table if a post-GWAS analysis submit button is clicked
        if ctx.triggered_id != 'summary-is-submitted':
            return {'display': 'none'}

        if summary_is_submitted:
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output('summary-submit', 'disabled'),

        Input('summary-submit', 'n_clicks'),
        Input('summary-results-table', 'data')
    )
    def disable_summary_button_upon_run(n_clicks,  *_):
        return ctx.triggered_id == 'summary-submit' and n_clicks > 0

    @app.callback(
        Output('summary-input', 'children'),

        Input('summary-is-submitted', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('coexpression-valid-addl-genes', 'data'),
        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-slider', 'data'),
    )
    def display_summary_submitted_input(summary_submitted,
                                        coexpression_submitted, genes, network, algo, submitted_parameter_slider):
        if coexpression_submitted:
            parameters = 0
            if submitted_parameter_slider and algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[algo]['value']

            if not genes:
                genes = 'None'
            else:
                # Preserve user-entered order while removing duplicates
                genes = '; '.join(list(dict.fromkeys(genes)))

        else:
            # Assume default coexpression network parameters
            algo = 'clusterone'
            network = 'OS-CX'
            parameters = 30
            genes = 'None'

        if summary_submitted:
            return [
                html.B('Co-Expression Network Analysis'),
                html.Br(),
                html.Ul([
                    html.Li([html.B('Additional Genes: '), genes]),
                    html.Li([html.B('Selected Co-Expression Network: '), coexpression_util.get_user_facing_network(
                        network)]),
                    html.Li([html.B('Selected Module Detection Algorithm: '), coexpression_util.get_user_facing_algo(
                        algo)]),
                    html.Li([html.B('Selected Algorithm Parameter: '), coexpression_util.get_user_facing_parameter(
                        algo, parameters)])
                ], className='pb-0 mb-1')
            ]

        raise PreventUpdate

    # =================
    # Table-related
    # =================

    @app.callback(
        Output('summary-results-table', 'data'),
        Output('summary-results-table', 'columns'),

        Output('summary-results-table', 'filter_query', allow_duplicate=True),
        Output('summary-results-table', 'page_current', allow_duplicate=True),

        State('homepage-submitted-genomic-intervals', 'data'),

        State('coexpression-combined-genes', 'data'),
        State('coexpression-valid-addl-genes', 'data'),
        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-slider', 'data'),

        State('homepage-is-submitted', 'data'),
        Input('summary-is-submitted', 'data'),
        State('coexpression-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def display_summary_results(genomic_intervals,
                                combined_gene_ids, valid_addl_genes, submitted_network, submitted_algo, submitted_parameter_slider,
                                homepage_submitted, summary_submitted, coexpression_submitted):
        if coexpression_submitted:
            parameters = 0
            if submitted_parameter_slider and submitted_algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[submitted_algo]['value']

        else:
            # Assume default coexpression network parameters
            submitted_algo = 'clusterone'
            submitted_network = 'OS-CX'
            parameters = 30

            # Will throw exception when cache is cleared and display is reset while summary page is open
            try:
                combined_gene_ids = lift_over_util.get_genes_in_Nb(genomic_intervals)[
                    1]
            except:
                pass
            valid_addl_genes = []

        if homepage_submitted and summary_submitted:
            summary_results_df = make_summary_table(
                genomic_intervals, combined_gene_ids, valid_addl_genes, submitted_network, submitted_algo, parameters)

            mask = (
                summary_results_df['Gene'] != NULL_PLACEHOLDER)
            summary_results_df.loc[mask, 'Gene'] = get_msu_browser_link(
                summary_results_df, 'Gene')

            columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
                       for x in summary_results_df.columns]

            return summary_results_df.to_dict('records'), columns, '', 0

        raise PreventUpdate

    @app.callback(
        Output('summary-results-table', 'filter_query', allow_duplicate=True),
        Output('summary-results-table', 'page_current', allow_duplicate=True),

        Input('summary-reset-table', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_table_filter_page(*_):
        return '', 0

    @app.callback(
        Output('summary-download-df-to-csv', 'data'),
        Input('summary-export-table', 'n_clicks'),
        State('summary-results-table', 'data'),
        State('homepage-submitted-genomic-intervals', 'data')
    )
    def download_tfbs_table_to_csv(download_n_clicks, summary_df, genomic_intervals):
        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(summary_df))
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Summary.csv', index=False)

        raise PreventUpdate
