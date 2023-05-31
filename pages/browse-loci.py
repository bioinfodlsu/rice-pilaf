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
    dcc.Dropdown(
        id='igv-genomic-intervals'
    ),

    html.Br(),

    html.Div(id='igv-track-intro', children=''),

    dbc.Checklist(id='igv-track-filter',
                  inline=True,
                  options=[],
                  style={}),

    html.Br(),

    dcc.Loading(id='igv-display')
]
)
