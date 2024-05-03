from dash import ALL, Input, Output, State, ctx, html
from dash.exceptions import PreventUpdate
from flask import request

from ..lift_over import util as lift_over_util
from ..style_util import *
from .util import *


def init_callback(app):
    # =================
    # Layout-related
    # =================
    @app.callback(
        Output({"type": "analysis-nav", "label": ALL}, "className"),
        Output({"type": "analysis-layout", "label": ALL}, "hidden"),
        State({"type": "analysis-nav", "label": ALL}, "className"),
        State({"type": "analysis-nav", "label": ALL}, "id"),
        State({"type": "analysis-layout", "label": ALL}, "id"),
        Input("current-analysis-page-nav", "data"),
        Input("homepage-submit", "n_clicks"),
        State({"type": "analysis-layout", "label": ALL}, "hidden"),
    )
    def display_specific_analysis_page(
        nav_className, analysis_nav_id, analysis_layout_id, current_page, *_
    ):
        """
        Displays the selected analyis page and hides the unselected analysis pages

        Parameters:
        - nav_className: List of analysis navbar buttons' classnames
        - analysis_nav_id: List of analysis navbar buttons' ids
        - analysis_layout_id: List of analysis page layouts' ids
        - current_page: Saved selected analysis navbar button
        - *_: Other inputs that facilitates the saved state of the selected analysis navbar button and layout page

        Returns:
        - ({'type': 'analysis-nav', 'label': ALL}, 'className'): List of updated classnames for the analysis navbar buttons
        - ({'type': 'analysis-layout', 'label': ALL}, 'hidden'): List of updated hidden attributes for the analysis page layouts
        """

        if current_page:
            update_nav_class_name = []
            update_layout_hidden = []

            # This is to facilitate the feedback state of the navbar buttons depending on the selected navbar button
            for i in range(len(analysis_nav_id)):

                # Add active classname attribute to the selected navbar button
                if analysis_nav_id[i]["label"] == current_page:
                    nav_classes = add_class_name("active", nav_className[i])

                # Remove active classname attribute to the unselected navbar buttons
                else:
                    nav_classes = remove_class_name("active", nav_className[i])

                update_nav_class_name.append(nav_classes)

            # This is to facilitate the displaying and hiding of analysis page layouts depending on the selected navbar button
            for i in range(len(analysis_layout_id)):

                # Display the selected analysis page layout depending on the selected navbar button
                if analysis_layout_id[i]["label"] == current_page:
                    hide_layout = False

                # Hide the unselected analysis page layouts
                else:
                    hide_layout = True

                update_layout_hidden.append(hide_layout)

            return update_nav_class_name, update_layout_hidden

        raise PreventUpdate

    # =================
    # Input-related
    # =================

    @app.callback(
        Output("session-container", "children", allow_duplicate=True),
        Output("input-error", "children"),
        Output("input-error", "style"),
        Output("homepage-is-submitted", "data"),
        Output("homepage-submitted-genomic-intervals", "data"),
        Output("homepage-is-resetted", "data"),
        State("homepage-genomic-intervals", "value"),
        Input("homepage-submit", "n_clicks"),
        Input("homepage-genomic-intervals", "n_submit"),
        State("session-container", "children"),
        Input("homepage-reset", "n_clicks"),
        Input("homepage-clear-cache", "n_clicks"),
        prevent_initial_call=True,
    )
    def parse_input(nb_intervals_str, n_clicks, n_submit, dccStore_children, *_):
        """
        Parses homepage input and outputs depending on the input
        - If user clicks the "Clear Cache" button, all the data in the cache (temp) folder will be cleared
        - If user clicks the "Reset All Analyses" button, all the saved data in the dcc.Store variables will be cleared
        - If user clicks the "Proceed to Analysis Menu" button, the genomic interval will be parsed and an error message or the homepage results container will appear

        Parameters:
        - nb_intervals_str: Submitted genomic interval input
        - n_clicks: Number of clicks pressed on the homepage submit button
        - n_submit: Number of times "Enter" was pressed while the genomic interval input field had focus
        - dccStore_children: List of dcc.Store data
        - *_: Other inputs in facilitating the saved state of the homepage

        Returns:
        - ('session-container', 'children'): Updated dcc.Store data
        - ('input-error', 'children'): Error message
        - ('input-error', 'style'): {'display': 'block'} for displaying the error message; otherwise {'display': 'none'}
        - ('homepage-is-submitted', 'data'): [Homepage] True for submitted valid input; otherwise False
        - ('homepage-submitted-genomic-intervals', 'data'): Submitted genomic interval
        - ('homepage-is-resetted', 'data'): True for clearing data in the dcc.Store variables; otherwise False
        """

        # Clears the cache folder
        if "homepage-clear-cache" == ctx.triggered_id:
            clear_cache_folder()

        # Clears all the data
        if "homepage-reset" == ctx.triggered_id:
            # clear data for items in dcc.Store found in session-container
            dccStore_children = clear_specific_dccStore_data(dccStore_children, "")

            return dccStore_children, None, {"display": "none"}, False, "", True

        # Parses the genomic interval input
        if n_submit >= 1 or ("homepage-submit" == ctx.triggered_id and n_clicks >= 1):
            if nb_intervals_str:
                intervals = lift_over_util.get_genomic_intervals_from_input(
                    nb_intervals_str
                )

                if lift_over_util.is_error(intervals):
                    return (
                        dccStore_children,
                        [
                            f"Error encountered while parsing genomic interval {intervals[1]}",
                            html.Br(),
                            lift_over_util.get_error_message(intervals[0]),
                        ],
                        {"display": "block"},
                        False,
                        nb_intervals_str,
                        True,
                    )
                else:
                    # clear data for items in dcc.Store found in session-container
                    dccStore_children = clear_specific_dccStore_data(
                        dccStore_children, ""
                    )

                    return (
                        dccStore_children,
                        None,
                        {"display": "none"},
                        True,
                        nb_intervals_str,
                        True,
                    )
            else:
                return (
                    dccStore_children,
                    [f"Error: Input for genomic interval should not be empty."],
                    {"display": "block"},
                    False,
                    nb_intervals_str,
                    True,
                )

        raise PreventUpdate

    @app.callback(
        Output("homepage-genomic-intervals", "value", allow_duplicate=True),
        Input({"type": "example-genomic-interval", "description": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def set_input_fields_with_preset_input(example_genomic_interval_n_clicks):
        """
        Displays the preset genomic interval depending on the selected description choice

        Parameters:
        - example_genomic_interval_n_clicks: List of number of clicks pressed for each description choice

        Returns:
        - ('homepage-genomic-intervals', 'value'): Preset genomic interval depending on the selected description choice
        """

        if ctx.triggered_id and not all(
            val == 0 for val in example_genomic_interval_n_clicks
        ):
            return get_example_genomic_interval(ctx.triggered_id["description"])

        raise PreventUpdate

    @app.callback(
        Output("homepage-results-container", "style"),
        Output("about-the-app", "style"),
        Input("homepage-is-submitted", "data"),
        Input("homepage-submit", "n_clicks"),
    )
    def display_homepage_output(homepage_is_submitted, *_):
        """
        Displays either the homepage results container or about the page container

        Parameters:
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - *_: Other inputs in facilitating the saved state of the homepage

        Returns:
        - ('homepage-results-container', 'style'): {'display': 'block'} for displaying the homepage results container; otherwise {'display': 'none'}
        - ('about-the-app', 'style'): {'display': 'block'} for displaying the about the page container; otherwise {'display': 'none'}
        """

        if homepage_is_submitted:
            return {"display": "block"}, {"display": "none"}

        else:
            return {"display": "none"}, {"display": "block"}

    @app.callback(
        Output("genomic-interval-modal", "is_open"),
        Input("genomic-interval-tooltip", "n_clicks"),
    )
    def open_modals(tooltip_n_clicks):
        """
        Displays the tooltip modals

        Parameters:
        - tooltip_n_clicks: Number of clicks pressed for the tooltip button near the genomic interval input field

        Returns:
        - ('genomic-interval-modal', 'is_open'): True for showing the genomic interval tooltip; otherwise False
        """

        if tooltip_n_clicks > 0:
            return True

        raise PreventUpdate

    # =================
    # Session-related
    # =================

    @app.callback(
        Output("current-analysis-page-nav", "data"),
        Input({"type": "analysis-nav", "label": ALL}, "n_clicks"),
    )
    def set_input_homepage_session_state(analysis_nav_items_n_clicks):
        """
        Sets the [Input container] homepage related input dcc.Store data

        Parameters:
        - analysis_nav_items_n_clicks: List of number of clicks pressed for each analysis navbar button

        Returns:
        - ('current-analysis-page-nav', 'data'): Selected analysis navbar button's id label
        """

        if ctx.triggered_id:
            if not all(val == 0 for val in analysis_nav_items_n_clicks):
                analysis_page_id = ctx.triggered_id.label
                return analysis_page_id

        raise PreventUpdate

    @app.callback(
        Output("homepage-genomic-intervals", "value"),
        State("homepage-submitted-genomic-intervals", "data"),
        State("homepage-is-submitted", "data"),
        Input("homepage-submit", "value"),
    )
    def get_input_homepage_session_state(genomic_intervals, homepage_is_submitted, *_):
        """
        Gets the [Input container] homepage related dcc.Store data and displays them

        Parameters:
        - genomic_intervals: Saved genomic interval value found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - *_: Other inputs in facilitating the saved state of the homepage

        Returns:
        - ('homepage-genomic-intervals', 'value'): Saved genomic interval value found in the dcc.Store
        """

        if homepage_is_submitted:
            return genomic_intervals

        raise PreventUpdate

    # =================
    # Logging-related
    # =================

    @app.callback(
        Output("homepage-log", "children"),
        State("homepage-genomic-intervals", "value"),
        Input("homepage-submit", "n_clicks"),
        Input("homepage-genomic-intervals", "n_submit"),
        Input({"type": "analysis-nav", "label": ALL}, "n_clicks"),
    )
    def get_homepage_logs(
        genomic_intervals, n_clicks, n_submit, analysis_nav_items_n_clicks
    ):
        if n_submit >= 1 or ("homepage-submit" == ctx.triggered_id and n_clicks >= 1):
            app.logger.info("%s|home %s", request.remote_addr, genomic_intervals)

        if ctx.triggered_id and not all(
            val == 0 for val in analysis_nav_items_n_clicks
        ):
            try:
                analysis_page_id = ctx.triggered_id.label
                app.logger.info("%s|%s", request.remote_addr, analysis_page_id)
            except:
                raise PreventUpdate

        raise PreventUpdate
