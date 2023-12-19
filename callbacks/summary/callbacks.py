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
        if ctx.triggered_id == 'coexpression-submit':
            return {'display': 'none'}

        if summary_is_submitted:
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output('summary-input', 'children'),

        Input('summary-is-submitted', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-slider', 'data'),
    )
    def display_summary_submitted_input(summary_is_submitted,
                                        coexpression_is_submitted, network, algo, submitted_parameter_slider):
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
            return [html.B('Additional Genes: '), 'hello',
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

        Output('summary-results-table', 'filter_query', allow_duplicate=True),
        Output('summary-results-table', 'page_current', allow_duplicate=True),

        State('homepage-submitted-genomic-intervals', 'data'),
        State('homepage-is-submitted', 'data'),
        Input('summary-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def display_summary_results(genomic_intervals, homepage_submitted, summary_submitted):
        print(homepage_submitted)
        print(summary_submitted)
        if homepage_submitted and summary_submitted:
            summary_results_df = make_summary_table(
                genomic_intervals)

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
