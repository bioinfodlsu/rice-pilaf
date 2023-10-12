from dash import Input, Output, State, ctx, ALL, html, no_update, dcc
from dash.exceptions import PreventUpdate

from .util import *
from ..lift_over import util as lift_over_util


def init_callback(app):

    # to display user input interval in the top nav
    @app.callback(
        Output('text-mining-genomic-intervals-input', 'children'),
        State('homepage-submitted-genomic-intervals', 'data'),
        Input('homepage-is-submitted', 'data'),
        Input('text-mining-submit', 'n_clicks')
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('text-mining-query', 'value', allow_duplicate=True),
        Input({'type': 'example-text-mining',
               'description': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def set_input_fields_with_preset_input(example_text_mining_n_clicks):
        if ctx.triggered_id and not all(val == 0 for val in example_text_mining_n_clicks):
            return ctx.triggered_id['description']

        raise PreventUpdate

    @app.callback(
        Output('text-mining-query', 'value'),
        State('text-mining-submitted-query', 'data'),
        Input('text-mining-is-submitted', 'data')
    )
    def get_input_homepage_session_state(query, *_):
        return query

    @app.callback(
        Output('text-mining-input-error', 'style'),
        Output('text-mining-input-error', 'children'),

        Output('text-mining-is-submitted', 'data', allow_duplicate=True),
        Output('text-mining-submitted-query',
               'data', allow_duplicate=True),
        Input('text-mining-submit', 'n_clicks'),
        Input('text-mining-query', 'n_submit'),
        State('homepage-is-submitted', 'data'),
        State('text-mining-query', 'value'),
        prevent_initial_call=True
    )
    def submit_text_mining_input(text_mining_submitted_n_clicks, text_mining_query_n_submit, homepage_is_submitted, text_mining_query):
        if homepage_is_submitted and (text_mining_submitted_n_clicks >= 1 or text_mining_query_n_submit >= 1):
            is_there_error, message = is_error(text_mining_query)

            if not is_there_error:
                return {'display': 'none'}, message, True, text_mining_query
            else:
                return {'display': 'block'}, message, False, no_update

        raise PreventUpdate

    @app.callback(
        Output('text-mining-results-container', 'style'),
        Input('text-mining-is-submitted', 'data')
    )
    def display_coexpression_output(text_mining_is_submitted):
        if text_mining_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    @app.callback(
        Output('text-mining-submit', 'disabled'),

        Input('text-mining-submit', 'n_clicks'),
        State('text-mining-query', 'value'),
        Input('text-mining-result-table', 'data'),
    )
    def disable_text_mining_button_upon_run(n_clicks, text_mining_query, *_):
        is_there_error, _ = is_error(text_mining_query)

        if is_there_error:
            return False

        return ctx.triggered_id == 'text-mining-submit' and n_clicks > 0

    @app.callback(
        Output('text-mining-result-table', 'data'),
        Output('text-mining-result-table', 'columns'),
        Output('text-mining-results-stats', 'children'),

        Input('text-mining-is-submitted', 'data'),
        State('homepage-is-submitted', 'data'),
        State('text-mining-submitted-query', 'data')
    )
    def display_text_mining_results(text_mining_is_submitted, homepage_submitted, text_mining_query_submitted_input):
        if homepage_submitted and text_mining_is_submitted:
            query_string = text_mining_query_submitted_input

            is_there_error, _ = is_error(query_string)
            if not is_there_error:
                text_mining_results_df = text_mining_query_search(query_string)

                columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
                           for x in text_mining_results_df.columns]

                num_unique_entries = get_num_unique_entries(
                    text_mining_results_df, "PMID")

                stats = 'Found matches across '
                if num_unique_entries == 1:
                    stats += f'{num_unique_entries} publication'
                elif num_unique_entries == MAX_NUM_RESULTS:
                    stats += f'over {num_unique_entries} publications. Consider making your search query more specific'
                else:
                    stats += f'{num_unique_entries} publications'

                return text_mining_results_df.to_dict('records'), columns, stats

        raise PreventUpdate

    @app.callback(
        Output('text-mining-result-table', 'filter_query'),
        Input('text-mining-reset-table', 'n_clicks')
    )
    def reset_table_filters(*_):
        return ''

    @app.callback(
        Output('text-mining-download-df-to-csv', 'data'),
        Input('text-mining-export-table', 'n_clicks'),
        State('text-mining-result-table', 'data'),
    )
    def download_text_mining_table_to_csv(download_n_clicks, text_mining_df, ):
        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(text_mining_df))
            return dcc.send_data_frame(df.to_csv, f'Text Mining Analysis Table.csv', index=False)

        raise PreventUpdate
