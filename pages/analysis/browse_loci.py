from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks.constants import Constants

from callbacks.browse_loci.util import *

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_IGV
    },
    hidden=True,
    children=[
        html.Div([
            html.P('In this page, you can genome-browse your loci and overlay epigenomic information '
                   'such as chromatin accessibility and histone modification marks.')
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
            dbc.Label('Select a tissue: ',
                      className='mb-2'),

            dbc.RadioItems(
                id='epigenome-tissue',
                options= list(RICE_ENCODE_SAMPLES.keys()),
                value=list(RICE_ENCODE_SAMPLES.keys())[0],
                inline=True,
                className='ms-3 mt-1'
            ),

            html.Br(),

            dbc.Label(['Select tracks to be displayed:']),

            dbc.Checklist(id='epigenome-tracks',inline=True,className='ms-3'),

            html.Br(),

            dbc.Label(['(Old. Please remove.) Select tracks to be displayed']),
            dbc.Checklist(
                id='igv-tracks',
                options=construct_options_igv_tracks(),
                inline=True,
                className='ms-3'),

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
                
                dcc.Loading(id='igv-display')
            ]
        )
    ], className='mt-2'
)
