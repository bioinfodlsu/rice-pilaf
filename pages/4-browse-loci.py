import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/browse-loci', name='Browse Loci')

layout = html.Div(id='igv-container', children=[
    # dashbio.Igv(
    #      id='igv-Nipponbare',
    #      genome='GCF_001433935.1',
    #      minimumBases=100,
    # )
    html.P(id='igv-genomic-intervals-input'),

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

    html.Br(),
    html.Br(),

    html.Div(
        id='igv-results-container',
        style={'display': 'none'},
        children=[
            dbc.Label(id='igv-track-intro'),

            dcc.Loading(dbc.Checklist(id='igv-track-filter',
                                      inline=True,
                                      className='ms-3')),

            html.Br(),

            dcc.Loading(id='igv-display')
        ]
    )
]
)
