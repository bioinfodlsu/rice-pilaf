import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

other_ref_genomes = ['N22','MH63']
genomic_interval = 'Chr01:10000-20000;Chr01:22000-25000'

dash.register_page(__name__, path ="/", name="Input and Lift-over")

layout = html.Div(
    [
        dcc.ConfirmDialog(
            id='input-error',
            message='',
        ),

        dcc.Markdown('Provide genomic interval(s) from your GWAS:'),
        dbc.Input(
            id='lift-over-genomic-intervals',
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

        html.Div(id='lift-over-results-intro', children=''),

        html.Br(),

        dbc.Tabs(id='lift-over-results-tabs', active_tab='', children=[]),

        html.Br(),

        html.Div(id='lift-over-results-gene-intro', children=''),

        html.Br(),

        dash_table.DataTable(id='lift-over-results-table'),

        html.Br()
    ]
)




