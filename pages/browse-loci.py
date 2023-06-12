import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

dash.register_page(__name__, name="Browse Loci")

layout = html.Div(id='igv-container', children=[
    # dashbio.Igv(
    #      id='igv-Nipponbare',
    #      genome="GCF_001433935.1",
    #      minimumBases=100,
    # )
    html.P(id='igv-genomic-intervals-input'),

    dbc.Label('Select a genomic interval of interest',
              className='mb-2'),

    dcc.Dropdown(
        id='igv-genomic-intervals',
    ),

    html.Br(),

    dbc.Label(id='igv-track-intro'),

    dbc.Checklist(id='igv-track-filter',
                  inline=True,
                  className='ms-3'),

    html.Br(),

    dcc.Loading(id='igv-display')
]
)
