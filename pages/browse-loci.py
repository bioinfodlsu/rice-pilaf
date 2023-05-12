import dash
import dash_bio as dashbio
from dash.dependencies import Input, Output
from dash import html, dcc


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
    dcc.Loading(id='igv-container')
]
)
