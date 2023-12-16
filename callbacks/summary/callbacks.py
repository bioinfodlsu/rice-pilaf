from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate

from ..lift_over import util as lift_over_util


def init_callback(app):
    @app.callback(
        Output('summary-genomic-intervals-input', 'children'),
        State('homepage-submitted-genomic-intervals', 'data'),
        Input('homepage-is-submitted', 'data'),
    )
    def display_input(nb_intervals_str, homepage_is_submitted):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate
