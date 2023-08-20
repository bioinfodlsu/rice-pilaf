from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks.constants import Constants
const = Constants()

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': const.IGV
    },
    hidden=True,
    children=[
        html.Div([
            html.P('WRITE ME')
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='igv-genomic-intervals-input'),

            html.Br(),
            html.Br(),

            dbc.Label('Select an interval: ',
                      className='mb-2'),

            dcc.Dropdown(
                id='igv-genomic-intervals',
            ),

            html.Br(),

            dbc.Button('Submit',
                       id='igv-submit',
                       n_clicks=0,
                       className='page-button'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div(
            id='igv-results-container',
            style={'display': 'none'},
            children=[
                html.Hr(className='mt-3 mb-4'),
                dbc.Label(id='igv-track-intro'),

                dcc.Loading(dbc.Checklist(id='igv-track-filter',
                                          inline=True,
                                          className='ms-3')),

                html.Br(),

                dcc.Loading(id='igv-display')
            ]
        )
    ], className='mt-2'
)
