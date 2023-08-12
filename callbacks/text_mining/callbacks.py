from dash import Input, Output,State,ctx,ALL, html
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util



Text_mining_input = namedtuple(
    'Text_mining_input', ['text_mining_query'])


def init_callback(app):

    #to display user input interval in the top nav
    @app.callback(
        Output('text-mining-genomic-intervals-input', 'children'),
        Input('homepage-genomic-intervals-submitted-input', 'data'),
        State('homepage-is-submitted', 'data')
    )
    def display_input(nb_intervals_str, homepage_is_submitted):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate


    @app.callback(
        Output('text-mining-query-saved-input', 'data', allow_duplicate=True),
        Input('text-mining-query', 'value'),
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
        Output('text-mining-query-submitted-input', 'data', allow_duplicate=True),
        Input('text-mining-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),
        State('text-mining-query', 'value'),
        prevent_initial_call=True
    )
    def submit_text_mining_input(text_mining_submitted_n_clicks, homepage_is_submitted,text_mining_query):
        if homepage_is_submitted and text_mining_submitted_n_clicks >= 1:
            submitted_input = Text_mining_input(
                text_mining_query)._asdict()

            return True, submitted_input

        raise PreventUpdate

    @app.callback(
        Output('text-mining-results-container', 'style'),
        Input('text-mining-is-submitted', 'data'),
    )
    def display_text_mining_output(text_mining_is_submitted):
        if text_mining_is_submitted:
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output('text_mining_result_table', 'data'),
        Input('text-mining-is-submitted', 'data'),
        State('homepage-is-submitted', 'data'),
        State('text-mining-query-submitted-input', 'data')
    )
    def display_text_mining_results(text_mining_is_submitted, homepage_submitted,
                                   text_mining_query_submitted_input):
        if homepage_submitted and text_mining_is_submitted:
            query_string = text_mining_query_submitted_input['text_mining_query']
            text_mining_results_df = text_mining_query_search(query_string)

            return text_mining_results_df.to_dict('records')

        raise PreventUpdate