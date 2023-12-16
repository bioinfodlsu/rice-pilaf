from dash import Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate

from ..lift_over import util as lift_over_util


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
        Output('summary-converter-modal', 'is_open'),
        Input('summary-converter-tooltip', 'n_clicks'),
    )
    def open_modals(summary_converter_tooltip_n_clicks):
        if ctx.triggered_id == 'summary-converter-tooltip' and summary_converter_tooltip_n_clicks > 0:
            return True

        raise PreventUpdate
