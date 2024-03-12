from dash import Input, Output, State, dcc, html, ctx
from dash.exceptions import PreventUpdate

from .util import *


def init_callback(app):
    @app.callback(
        Output("template-genomic-intervals-input", "children"),
        State("homepage-submitted-genomic-intervals", "data"),
        Input("homepage-is-submitted", "data"),
        Input("template-submit", "n_clicks"),
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        """
        Displays the genomic interval input in the template page

        Parameters:
        - nb_intervals_str: Saved genomic interval value found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - *_: Other input that facilitates displaying of the submitted genomic interval

        Returns:
        - ('template-genomic-intervals-input', 'children'): Genomic interval text
        """

        if homepage_is_submitted:
            if nb_intervals_str and not is_error(
                get_genomic_intervals_from_input(nb_intervals_str)
            ):
                return [html.B("Your Input Intervals: "), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output("template-is-submitted", "data"),
        Output("template-submitted-addl-genes", "data"),
        Output("template-submitted-radio-buttons", "data"),
        Output("template-submitted-checkbox-buttons", "data"),
        Output("template-submitted-parameter-slider", "data"),
        Input("template-submit", "n_clicks"),
        State("homepage-is-submitted", "data"),
        State("template-addl-genes", "value"),
        State("template-radio-buttons", "value"),
        State("template-checkbox-buttons", "value"),
        State("template-parameter-slider", "value"),
    )
    def submit_template_input(
        n_clicks,
        homepage_is_submitted,
        addl_genes,
        radio_buttons,
        checkbox_buttons,
        parameter_slider,
    ):
        if homepage_is_submitted and n_clicks >= 1:
            return True, addl_genes, radio_buttons, checkbox_buttons, parameter_slider

        raise PreventUpdate

    @app.callback(
        Output("template-results-container", "style"),
        Input("template-is-submitted", "data"),
    )
    def display_template_output(template_is_submitted):
        """
        Displays the template results container

        Parameters:
        - template_is_submitted: [Template] Saved boolean value of submitted valid input

        Returns:
        - ('template-results-container', 'style'): {'display': 'block'} for displaying the template results container; otherwise {'display': 'none'}
        """

        if template_is_submitted:
            return {"display": "block"}

        else:
            return {"display": "none"}

    @app.callback(
        Output("template-input", "children"),
        Input("template-is-submitted", "data"),
        State("template-submitted-addl-genes", "data"),
        State("template-submitted-radio-buttons", "data"),
        State("template-submitted-checkbox-buttons", "data"),
        State("template-submitted-parameter-slider", "data"),
    )
    def display_template_submitted_input(
        template_is_submitted,
        genes,
        radio_buttons,
        checkbox_buttons,
        submitted_parameter_slider,
    ):
        """
        Displays the template submitted input

        Parameters:
        - template_is_submitted: [Coexpression] Saved boolean value of submitted valid input
        - genes: Saved template additional genes found in the dcc.Store
        - radio_buttons: Saved template radio buttons value found in the dcc.Store
        - checkbox_buttons: Saved template checkbox buttons value found in the dcc.Store
        - submitted_parameter_slider: Saved checkbox parameter slider value found in the dcc.Store

        Returns:
        - ('template-input', 'children'): Submitted template inputs text
        """

        if template_is_submitted:
            checkbox_message = [html.Span("")]
            if checkbox_buttons:
                checkbox_buttons_str = checkbox_buttons[0]
                if len(checkbox_buttons) == 2:
                    checkbox_buttons_str += f" and {checkbox_buttons[1]}"
                elif len(checkbox_buttons) > 2:
                    for idx, checkbox_value in enumerate(checkbox_buttons[1:]):
                        if idx != len(checkbox_buttons) - 2:
                            checkbox_buttons_str += f", "
                        else:
                            checkbox_buttons_str += f", and "

                        checkbox_buttons_str += f"{checkbox_value}"

                checkbox_message += [html.Span(checkbox_buttons_str)]

            return [
                html.B("Additional Genes: "),
                genes,
                html.Br(),
                html.B("Selected Radio Buttons: "),
                radio_buttons,
                html.Br(),
                html.B("Selected Checkbox Buttons: "),
                html.Span(checkbox_message),
                html.Br(),
                html.B("Selected Parameter: "),
                submitted_parameter_slider,
            ]

        raise PreventUpdate
