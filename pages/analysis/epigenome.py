from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks.constants import Constants

from callbacks.epigenome.util import *

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_EPIGENOME
    },
    hidden=True,
    children=[
        html.Div([
            html.P(Constants.INTRO_EPIGENOME)
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='epigenome-genomic-intervals-input'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            dbc.Label('Select an interval', className='mb-2'),

            dcc.Dropdown(
                id='epigenome-genomic-intervals',
            ),

            html.Br(),
            dbc.Label('Select a tissue'),

            dbc.RadioItems(
                id='epigenome-tissue',
                options=list(RICE_ENCODE_SAMPLES.keys()),
                value=list(RICE_ENCODE_SAMPLES.keys())[0],
                inline=True,
                className='ms-3 mt-1'
            ),

            html.Br(),
            dbc.Label('Select tracks to be displayed '),

            dbc.Checklist(id='epigenome-tracks', inline=True,
                          className='ms-3 mt-1', value=[]),

            html.Br(),

            dbc.Button('Submit',
                       id='epigenome-submit',
                       n_clicks=0,
                       className='page-button'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div(
            id='epigenome-results-container',
            style={'display': 'none'},
            children=[
                html.Hr(className='mt-3 mb-4'),

                dcc.Loading(id='epigenome-display')
            ]
        )
    ], className='mt-2'
)
