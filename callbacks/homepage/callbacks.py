
from dash import Input, Output, State, html, ctx, ALL
from dash.exceptions import PreventUpdate
from .util import *
from ..lift_over import util as lift_over_util
from ..epigenome import util as epigenome_util

from ..style_util import *


def init_callback(app):
    # =================
    # Layout-related
    # =================
    @app.callback(
        Output({'type': 'analysis-nav', 'label': ALL}, 'className'),
        Output({'type': 'analysis-layout', 'label': ALL}, 'hidden'),
        State({'type': 'analysis-nav', 'label': ALL}, 'className'),
        State({'type': 'analysis-nav', 'label': ALL}, 'id'),
        State({'type': 'analysis-layout', 'label': ALL}, 'id'),
        Input('current-analysis-page-nav', 'data'),
        Input('homepage-submit', 'n_clicks'),
        State({'type': 'analysis-layout', 'label': ALL}, 'hidden'),
    )
    def display_specific_analysis_page(nav_className, analysis_nav_id, analysis_layout_id, current_page, *_):
        """
        Displays the selected analyis page and hides the unselected analysis pages

        Parameters:
        - nav_className: All of the analysis pages' classnames found in the side bar
        - analysis_nav_id: All of the analysis page's id found in the side bar  
        - analysis_layout_id: All of the analysis page's id found in the analysis folder
        - current_page: selected analysis 
        - *_: other inputs in facilitating the saved state of the selected analysis page 

        Returns:
        - List of updated classname and hidden attributes of the analysis page buttons in the side bar and analysis pages in the analysis folder respectively
        """
        if current_page:
            update_nav_class_name = []
            update_layout_hidden = []

            # add active classname attribute to the selected analysis button in the side bar; and remove the active attribute to the unselected ones
            for i in range(len(analysis_nav_id)):
                if analysis_nav_id[i]['label'] == current_page:
                    nav_classes = add_class_name('active', nav_className[i])
                else:
                    nav_classes = remove_class_name('active', nav_className[i])

                update_nav_class_name.append(nav_classes)

            # change the hidden attribute of the selected layout to True and the unselected ones to False
            for i in range(len(analysis_layout_id)):
                if analysis_layout_id[i]['label'] == current_page:
                    hide_layout = False
                else:
                    hide_layout = True

                update_layout_hidden.append(hide_layout)

            return update_nav_class_name, update_layout_hidden

        raise PreventUpdate

    # =================
    # Input-related
    # =================

    @app.callback(
        Output('session-container', 'children'),
        Output('input-error', 'children'),
        Output('input-error', 'style'),
        Output('homepage-is-submitted', 'data'),
        Output('homepage-submitted-genomic-intervals', 'data'),
        Output('homepage-is-resetted', 'data'),

        State('homepage-genomic-intervals', 'value'),

        Input('homepage-submit', 'n_clicks'),
        Input('homepage-genomic-intervals', 'n_submit'),
        State('session-container', 'children'),

        Input('homepage-reset', 'n_clicks'),
        Input('homepage-clear-cache', 'n_clicks'),

        prevent_initial_call=True
    )
    def parse_input(nb_intervals_str, n_clicks, n_submit, dccStore_children, *_):
        """
        Parses input and outputs depending on the input
        - if user clicks the "Clear Cache" button, all the data in the cache (temp) folder will be cleared
        - if user clicks the "Reset All Analyses" button, all the saved data in the dcc.Store variables will be cleared
        - if user clicks the "Proceed to Analysis Menu" button, the genomic interval will be parsed and an error message or the analysis menu will appear

        Parameters:
        - nb_intervals_str: Submitted genomic interval input
        - n_clicks: Number of clicks pressed on the submit button ("Proceed to Analysis Menu" button)  
        - n_submit: Number of times Enter was pressed while the input (genomic interval input field) had focus
        - dccStore_children: All of the dcc.Store variables 
        - *_: Other inputs in facilitating the saved state of the homepage 

        Returns:
        - Updated dcc.Store variables values
        - Error Message
        - Display of Error Message 
        - Boolean value of True / False of whether the genomic interval input is valid or not 
        - Submitted genomic interval 
        - Boolean value of True / False of whether the saved data in the dcc.Store variables should be cleared or not 
        """

        # Clears the cache folder
        if 'homepage-clear-cache' == ctx.triggered_id:
            clear_cache_folder()

        # Clears all the data 
        if 'homepage-reset' == ctx.triggered_id:
            # clear data for items in dcc.Store found in session-container
            dccStore_children = get_cleared_dccStore_data_excluding_some_data(
                dccStore_children)

            return dccStore_children, None, {'display': 'none'}, False, '', True

        # Parses the genomic interval input 
        if n_submit >= 1 or ('homepage-submit' == ctx.triggered_id and n_clicks >= 1):
            if nb_intervals_str:
                intervals = lift_over_util.get_genomic_intervals_from_input(
                    nb_intervals_str)

                if lift_over_util.is_error(intervals):
                    return dccStore_children, [f'Error encountered while parsing genomic interval {intervals[1]}', html.Br(), lift_over_util.get_error_message(intervals[0])], \
                        {'display': 'block'}, False, nb_intervals_str, True
                else:
                    # clear data for items in dcc.Store found in session-container
                    dccStore_children = get_cleared_dccStore_data_excluding_some_data(
                        dccStore_children)

                    epigenome_util.write_igv_tracks_to_file(nb_intervals_str)

                    return dccStore_children, None, {'display': 'none'}, True, nb_intervals_str, True
            else:
                return dccStore_children, [f'Error: Input for genomic interval should not be empty.'], \
                    {'display': 'block'}, False, nb_intervals_str, True

        raise PreventUpdate

    @app.callback(
        Output('homepage-genomic-intervals',
               'value', allow_duplicate=True),
        Input({'type': 'example-genomic-interval',
              'description': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def set_input_fields_with_preset_input(example_genomic_interval_n_clicks):
        """
        Displays the preset genomic interval depending on the selected description choice

        Parameters:
        - example_genomic_interval_n_clicks: List of number of clicks pressed for each description choice

        Returns:
        - The preset genomic interval depending on the seelcted description choice
        """
        if ctx.triggered_id and not all(val == 0 for val in example_genomic_interval_n_clicks):
            return get_example_genomic_interval(ctx.triggered_id['description'])

        raise PreventUpdate

    @app.callback(
        Output('homepage-results-container', 'style'),
        Output('about-the-app', 'style'),
        Input('homepage-is-submitted', 'data'),
        Input('homepage-submit', 'n_clicks'),
    )
    def display_homepage_output(homepage_is_submitted, *_):
        """
        Displays the homepage output 

        Parameters:
        - homepage_is_submitted: Saved boolean value of True / False of whether a valid input was submitted or not 
        - *_: other inputs in facilitating the saved state of the homepage 

        Returns:
        - Either the display of analysis pages or about the app page 
        """
        if homepage_is_submitted:
            return {'display': 'block'}, {'display': 'none'}

        else:
            return {'display': 'none'}, {'display': 'block'}

    @app.callback(
        Output('genomic-interval-modal', 'is_open'),
        Input('genomic-interval-tooltip', 'n_clicks')
    )
    def open_modals(tooltip_n_clicks):
        """
        Displays the genomic interval input tooltip

        Parameters:
        - tooltip_n_clicks: Number of clicks pressed for the tooltip button near the genomic interval input field

        Returns:
        - Boolean value of True / False in showing the tooltip
        """
        if tooltip_n_clicks > 0:
            return True

        raise PreventUpdate

    # =================
    # Session-related
    # =================

    @app.callback(
        Output('current-analysis-page-nav', 'data'),
        Input({'type': 'analysis-nav', 'label': ALL}, 'n_clicks')
    )
    def set_input_homepage_session_state(analysis_nav_items_n_clicks):
        """
        Sets the homepage-related dcc.Store variables data

        Parameters:
        - analysis_nav_items_n_clicks: List of number of clicks pressed for each analysis page button found in the side bar 

        Returns:
        - Saved analysis page button found in the side bar id 
        """

        if ctx.triggered_id:
            if not all(val == 0 for val in analysis_nav_items_n_clicks):
                analysis_page_id = ctx.triggered_id.label
                return analysis_page_id

        raise PreventUpdate

    @app.callback(
        Output('homepage-genomic-intervals', 'value'),
        State('homepage-submitted-genomic-intervals', 'data'),
        State('homepage-is-submitted', 'data'),
        Input('homepage-submit', 'value'),
    )
    def get_input_homepage_session_state(genomic_intervals, homepage_is_submitted, *_):
        """
        Gets the homepage-related dcc.Store variables data in the homepage input container and displays them 

        Parameters:
        - genomic_intervals: Saved genomic interval value found in the dcc.Store
        - homepage_is_submitted: Saved boolean value of True / False of whether a valid input was submitted or not 
        - *_: Other inputs in facilitating the saved state of the homepage 

        Returns:
        - Saved genomic interval value found in the dcc.Store
        """
        if homepage_is_submitted:
            return genomic_intervals

        raise PreventUpdate
