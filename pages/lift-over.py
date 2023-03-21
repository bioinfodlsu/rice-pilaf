import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

other_ref_genomes = ['N22','MH63']

genomic_interval = 'Chr01:10000-20000;Chr01:22000-25000'

dash.register_page(__name__, path ="/", name="Input and Lift-over")

layout = html.Div(
    [
        dcc.Markdown('Provide genomic interval(s) from your GWAS:'),
        dbc.Input(
            type = 'text',
            style = {'width': '100%'},
            value = genomic_interval
        ),

        html.Br(),

        dcc.Markdown('Search homologous regions of the following genomes:'),
        dcc.Dropdown(other_ref_genomes, id='lift-over-other-refs', multi=True),

        html.Br(),

        dbc.Button('Submit', id='lift-over-submit', n_clicks=0),

        html.Br(),
        html.Br(),

        html.Div(id='lift-over-results-intro', children = ''),
        dbc.Tabs(id="lift-over-results-tabs", children=[]),
    ]
)




