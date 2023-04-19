import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

other_ref_genomes = ['N22', 'MH63']
genomic_interval = ''  # 'Chr01:10000-20000;Chr01:22000-25000'

dash.register_page(__name__, path="/", name="Input and Lift-over")

layout = html.Div(
    [
        dcc.ConfirmDialog(
            id='input-error',
            message='',
        ),

        dcc.Markdown('Provide genomic interval(s) from your GWAS:'),
        dbc.Alert(
            id='input-error',
            children='',
            color='danger',
            style={'display': 'none'}
        ),
        dbc.Input(
            id='lift-over-genomic-intervals',
            type='text',
            style={'width': '100%'},
            value=genomic_interval,
            persistence=True,
            persistence_type='memory'
        ),

        html.Br(),

        dcc.Markdown('Search homologous regions of the following genomes:'),
        dcc.Dropdown(other_ref_genomes,
                     id='lift-over-other-refs',
                     multi=True,
                     persistence=True,
                     persistence_type='memory'
                     ),

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

        dash_table.DataTable(
            id='lift-over-results-table',
            persistence=True,
            persistence_type='memory'
        ),

        html.Br(),

        # Session storage
        dcc.Store(
            id='lift-over-is-submitted',
            storage_type='session',
        ),

        dcc.Store(
            id='lift-over-active-tab',
            storage_type='session'
        )
    ]
)
