import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


dash.register_page(__name__, path="/", name="Input and Lift-over")

layout = html.Div(
    [
        html.Div(id='lift-over-results-genomic-intervals-input',
                 children=''),

        html.Div(id='lift-over-results-other-refs-input',
                 children=''),

        html.Div(id='lift-over-results-intro', children=''),

        html.Br(),

        dbc.Tabs(id='lift-over-results-tabs', active_tab='', children=[]),

        html.Br(),

        html.Div(id='lift-over-results-gene-intro', children=''),

        html.Br(),

        dbc.Checklist(id='lift-over-overlap-table-filter',
                      inline=True,
                      options=[],
                      style={}),

        html.Br(),

        dcc.Loading(dash_table.DataTable(
            id='lift-over-results-table',
            persistence=True,
            persistence_type='memory',
            export_format='csv',
            style_cell={
                'whiteSpace': 'pre-line',
                'font-family': 'sans-serif'
            }
        )),

        html.Br()
    ]
)
