from dash import Input, Output, State, ctx, ALL, html
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util


Text_mining_input = namedtuple(
    'Text_mining_input', ['text_mining_query'])


def init_callback(app):

    # to display user input interval in the top nav
    @app.callback(
        Output('text-mining-genomic-intervals-input', 'children'),
        State('homepage-genomic-intervals-submitted-input', 'data'),
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
        Output('text-mining-query-saved-input', 'data', allow_duplicate=True),
        State('text-mining-query', 'value'),
        Input({'type': 'example-text-mining',
               'description': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def set_input_fields(query_string, *_):
        if ctx.triggered_id:
            if 'text-mining-query' == ctx.triggered_id:
                return query_string

            return ctx.triggered_id['description']

        raise PreventUpdate

    @app.callback(
        Output('text-mining-query', 'value'),
        Input('text-mining-query-saved-input', 'data'),
    )
    def get_input_homepage_session_state(query):
        return query

    @app.callback(
        Output('text-mining-is-submitted', 'data', allow_duplicate=True),
        Output('text-mining-query-submitted-input',
               'data', allow_duplicate=True),
        Input('text-mining-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),
        State('text-mining-query', 'value'),
        prevent_initial_call=True
    )
    def submit_text_mining_input(text_mining_submitted_n_clicks, homepage_is_submitted, text_mining_query):
        if homepage_is_submitted and text_mining_submitted_n_clicks >= 1:
            submitted_input = Text_mining_input(
                text_mining_query)._asdict()

            return True, submitted_input

        raise PreventUpdate

    @app.callback(
        Output('text-mining-results-container', 'style'),
        Output('text-mining-input-error', 'style'),
        Output('text-mining-input-error', 'children'),

        State('text-mining-query', 'value'),
        Input('text-mining-is-submitted', 'data')
    )
    def display_text_mining_output(text_mining_query, text_mining_is_submitted):
        is_there_error, message = is_error(text_mining_query)
        if text_mining_is_submitted:
            if not is_there_error:
                return {'display': 'block'}, {'display': 'none'}, message
            else:
                return {'display': 'none'}, {'display': 'block'}, message

        return {'display': 'none'}, {'display': 'none'}, message

    @app.callback(
        Output('text-mining-result-table', 'data'),
        Output('text-mining-result-table', 'columns'),
        Output('text-mining-results-stats', 'children'),

        Input('text-mining-is-submitted', 'data'),
        State('homepage-is-submitted', 'data'),
        State('text-mining-query-submitted-input', 'data')
    )
    def display_text_mining_results(text_mining_is_submitted, homepage_submitted, text_mining_query_submitted_input):
        if homepage_submitted and text_mining_is_submitted:
            query_string = text_mining_query_submitted_input['text_mining_query']

            is_there_error, _ = is_error(query_string)
            if not is_there_error:
                text_mining_results_df = text_mining_query_search(query_string)

                columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
                           for x in text_mining_results_df.columns]

                num_entries = get_num_entries(text_mining_results_df, "PMID")
                num_unique_entries = get_num_unique_entries(
                    text_mining_results_df, "PMID")

                if num_entries == 1:
                    stats = f'{num_entries} match '
                else:
                    stats = f'{num_entries} matches '

                if num_unique_entries == 1:
                    stats += f'across {num_unique_entries} publication found.'
                else:
                    stats += f'across {num_unique_entries} publications found.'

                return text_mining_results_df.to_dict('records'), columns, stats

        raise PreventUpdate

    @app.callback(
        Output('text-mining-result-table', 'filter_query'),
        Input('text-mining-reset-table', 'n_clicks')
    )
    def reset_table_filters(*_):
        return ''
