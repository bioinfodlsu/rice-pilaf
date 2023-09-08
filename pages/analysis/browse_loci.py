from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks.constants import Constants


layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_IGV
    },
    hidden=True,
    children=[
        html.Div([
            html.P('In this page, you can genome-browse your input intervals.')
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='igv-genomic-intervals-input'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
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
