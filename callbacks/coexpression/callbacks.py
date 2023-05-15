from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from .util import *


def init_callback(app):
    @app.callback(
        Output('test', 'children'),
        Input('lift-over-nb-table', 'data')
    )
    def test(nb_table):
        # if active_tab == 'tab-1':
        print(nb_table)
        # return nb_table

        raise PreventUpdate
