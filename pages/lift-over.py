import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


dash.register_page(__name__, path="/", name="Lift-over")

layout = html.Div(id='lift-over-container', children=[
    html.P(id='lift-over-results-genomic-intervals-input',
           children=''),

    html.P(id='lift-over-results-other-refs-input',
           children=''),

    html.Div(id='lift-over-results-intro', children=''),

    html.Br(),

    dbc.Tabs(id='lift-over-results-tabs', active_tab='', children=[]),

    html.Br(),

    dcc.Loading([
        dbc.Label(id='lift-over-results-gene-intro', children=''),

        dbc.Checklist(id='lift-over-overlap-table-filter',
                      inline=True),

        html.P(
            html.Div([
                dbc.Button([html.I(
                    className="bi bi-download me-2", id="coexpression-clustering-algo-tooltip"),
                    'Export to CSV'],
                    id='lift-over-export-table',
                    color='light', size='sm', className='table-button'),
                dbc.Button([html.I(
                    className="bi bi-arrow-clockwise me-2", id="coexpression-clustering-algo-tooltip"),
                    'Reset Table'],
                    id='lift-over-reset-table',
                    color='light', size='sm', className='ms-3 table-button')
            ], style={'textAlign': 'right'})
        ),

        dash_table.DataTable(
            id='lift-over-results-table',
            persistence=True,
            persistence_type='memory',
            style_cell={
                'whiteSpace': 'pre-line',
                'font-family': 'sans-serif'
            },
            sort_action='native',
            filter_action='native',
            filter_options={'case': 'insensitive',
                            'placeholder_text': 'Search column'},
            page_action='native',
            page_size=15
        )]),

    html.Br()
]
)
