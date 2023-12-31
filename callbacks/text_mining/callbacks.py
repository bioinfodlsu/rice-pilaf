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
        """
        Displays the genomic interval input in the text mining page

        Parameters:
        - nb_intervals_str: Saved genomic interval value found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input 
        - *_: Other input that facilitates displaying of the submitted genomic interval

        Returns:
        - ('lift-over-genomic-intervals-input', 'children'): Genomic interval text
        """

        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    # =================
    # Input-related
    # =================
    @app.callback(
        Output('text-mining-query', 'value', allow_duplicate=True),
        Input({'type': 'example-text-mining',
               'description': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def set_input_fields_with_preset_input(example_text_mining_n_clicks):
        """
        Displays the preset text mining input depending on the selected description choice

        Parameters:
        - example_text_mining_n_clicks: List of number of clicks pressed for each description choice

        Returns:
        - ('text-mining-query', 'value'): Preset text mining input depending on the selected description choice
        """

        if ctx.triggered_id and not all(val == 0 for val in example_text_mining_n_clicks):
            return ctx.triggered_id['description']

        raise PreventUpdate

    @app.callback(
        Output('text-mining-input-error', 'style', allow_duplicate=True),
        Output('text-mining-input-error', 'children', allow_duplicate=True),

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
        """
        Parses text mining input and displays the text mining result container
        - If user clicks on the text mining submit button, the inputs will be parsed and either an error message or the text mining results container will appear

        Parameters:
        - text_mining_submitted_n_clicks: Number of clicks pressed on the text mining submit button 
        - text_mining_query_n_submit: Number of times "Enter" was pressed while the text mining query input field had focus
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input 
        - text_mining_query: Text mining query input

        Returns:
        - ('text-mining-input-error', 'style'): {'display': 'block'} for displaying the error message; otherwise {'display': 'none'}
        - ('text-mining-input-error', 'children'): Error message
        - ('text-mining-is-submitted', 'data'): [Text mining] True for submitted valid input; otherwise False
        - ('text-mining-submitted-query', 'data'): Submitted text mining query
        """

        if homepage_is_submitted and (text_mining_submitted_n_clicks >= 1 or text_mining_query_n_submit >= 1):
            is_there_error, message = is_error(text_mining_query)

            if not is_there_error:
                return {'display': 'none'}, message, True, text_mining_query
            else:
                return {'display': 'block'}, message, False, text_mining_query

        raise PreventUpdate

    @app.callback(
        Output('text-mining-results-container', 'style'),
        Input('text-mining-is-submitted', 'data')
    )
    def display_text_mining_output(text_mining_is_submitted):
        """
        Displays the text mining results container

        Parameters:
        - text_mining_is_submitted: [Text mining] Saved boolean value of submitted valid input 

        Returns:
        - ('text-mining-results-container', 'style'): {'display': 'block'} for displaying the text mining results container; otherwise {'display': 'none'}
        """

        if text_mining_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    @app.callback(
        Output('text-mining-input-error', 'style'),
        Output('text-mining-input-error', 'children'),
        Input('homepage-is-resetted', 'data')
    )
    def clear_text_mining_error_messages(homepage_is_resetted):
        """
        Clears text mining input error 

        Parameters:
        - homepage_is_resetted: Saved boolean value of resetted analysis 

        Returns:
        - ('text-mining-input-error', 'style'): {'display': 'block'} for displaying the text mining error container; otherwise {'display': 'none'}
        - ('text-mining-input-error', 'children'): None for no error message
        """

        if homepage_is_resetted:
            return {'display': 'none'}, None

        raise PreventUpdate

    @app.callback(
        Output('text-mining-submit', 'disabled'),

        Input('text-mining-submit', 'n_clicks'),
        State('text-mining-query', 'value'),
        Input('text-mining-results-table', 'data'),
    )
    def disable_text_mining_button_upon_run(n_clicks, text_mining_query, *_):
        """
        Disables the submit button in the text mining page until computation is done in the text mining page

        Parameters:
        - n_clicks: Number of clicks pressed on the text mining submit button
        - text_mining_query: Text mining query input
        - *_: Other input that facilitates the disabling of the text mining submit button

        Returns:
        - ('text-mining-submit', 'disabled'): True for disabling the submit button; otherwise False 
        """

        is_there_error, _ = is_error(text_mining_query)

        if is_there_error:
            return False

        return ctx.triggered_id == 'text-mining-submit' and n_clicks > 0

    # =================
    # Table-related
    # =================

    @app.callback(
        Output('text-mining-results-table', 'data'),
        Output('text-mining-results-table', 'columns'),
        Output('text-mining-results-stats', 'children'),

        Input('text-mining-is-submitted', 'data'),
        State('homepage-is-submitted', 'data'),
        State('text-mining-submitted-query', 'data')
    )
    def display_text_mining_results(text_mining_is_submitted, homepage_is_submitted, text_mining_query_submitted_input):
        """
        Displays the text mining results table 

        Parameters:
        - text_mining_is_submitted: [Text mining] Saved boolean value of submitted valid input 
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input 
        - text_mining_query_submitted_input: Saved text mining query found in the dcc.Store

        Returns:
        - ('text-mining-results-table', 'data'): Data for the text mining table
        - ('text-mining-results-table', 'columns'): List of columns for the text mining table
        - ('text-mining-results-stats', 'children'): Stats of the publications found for the query
        """

        if homepage_is_submitted and text_mining_is_submitted:
            query_string = text_mining_query_submitted_input

            is_there_error, _ = is_error(query_string)
            if not is_there_error:
                text_mining_results_df = text_mining_query_search(query_string)

                columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
                           for x in text_mining_results_df.columns]

                num_unique_entries = get_num_unique_entries(
                    text_mining_results_df, "PMID")

                stats = f'"{text_mining_query_submitted_input}" has found matches across '
                if num_unique_entries == 1:
                    stats += f'{num_unique_entries} publication'
                elif num_unique_entries == MAX_NUM_RESULTS:
                    stats += f'over {num_unique_entries} publications. Consider making your search query more specific'
                else:
                    stats += f'{num_unique_entries} publications'

                return text_mining_results_df.to_dict('records'), columns, stats

        raise PreventUpdate

    @app.callback(
        Output('text-mining-results-table', 'filter_query'),
        Output('text-mining-results-table', 'page_current'),

        Input('text-mining-reset-table', 'n_clicks'),
        Input('text-mining-submit', 'n_clicks'),
        Input('text-mining-query', 'n_submit')
    )
    def reset_table_filter_page(*_):
        """
        Resets the text mining table and the current page to its original state

        Parameters:
        - *_: Other input that facilitates the resetting of the text mining table 

        Returns:
        - ('text-mining-results-table', 'filter_query'): '' for removing the filter query
        - ('text-mining-results-table', 'page_current'): 0
        """

        return '', 0

    @app.callback(
        Output('text-mining-download-df-to-csv', 'data'),
        Input('text-mining-export-table', 'n_clicks'),
        State('text-mining-results-table', 'data'),
        State('text-mining-submitted-query', 'data')
    )
    def download_text_mining_table_to_csv(download_n_clicks, text_mining_df, submitted_query):
        """
        Export the text mining table in csv file format 

        Parameters:
        - download_n_clicks: Number of clicks pressed on the export gene table button
        - text_mining_df: Text mining table data in dataframe format
        - submitted_query: Saved text mining query found in the dcc.Store
   
        Returns:
        - ('text-mining-download-df-to-csv', 'data'): Text mining table in csv file format data
        """

        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(text_mining_df))
            return dcc.send_data_frame(df.to_csv, f'[{submitted_query}] Text Mining Analysis Table.csv', index=False)

        raise PreventUpdate

    # =================
    # Session-related
    # =================
    @app.callback(
        Output('text-mining-query', 'value'),
        State('text-mining-submitted-query', 'data'),

        Input('text-mining-is-submitted', 'data'),
    )
    def get_input_homepage_session_state(query,  *_):
        """
        Gets the [Input container] text mining related dcc.Store data and displays them 

        Parameters:
        - query: Saved text mining query found in the dcc.Store
        - *_: Other inputs in facilitating the saved state of the text mining input

        Returns:
        - ('text-mining-query', 'value'): Saved text mining query
        """

        return query
