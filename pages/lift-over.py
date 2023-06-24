import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


dash.register_page(__name__, path='/', name='Lift-over')

other_ref_genomes = [{'value': 'N22', 'label': 'N22   (aus Nagina-22)'},
                     {'value': 'MH63', 'label': 'MH63   (indica Minghui-63)'},
                     {'value': 'Azu', 'label': 'Azu   (japonica Azucena)'},
                     {'value': 'ARC', 'label': 'ARC   (basmati ARC)'},
                     {'value': 'IR64', 'label': 'IR64   (indica IR64)'},
                     {'value': 'CMeo', 'label': 'CMeo   (japonica CHAO MEO)'}]

layout = html.Div(id='lift-over-container', children=[
    dbc.Label(
        'Select a genome to search for homologous regions'),
    dcc.Dropdown(
        other_ref_genomes,
        id='lift-over-other-refs',
        multi=False,
        persistence=True,
        persistence_type='memory',
        className='dash-bootstrap'
    ),

    html.Br(),

    dbc.Button('Run Analysis',
               id='lift-over-submit',
               className='page-button',
               n_clicks=0),

    html.Br(),
    html.Br(),

    html.Div(
        id='lift-over-results-container',
        style={'display': 'none'},
        children=[
            html.P(id='lift-over-results-genomic-intervals-input'),

            html.P(id='lift-over-results-other-refs-input'),

            html.Div(id='lift-over-results-intro'),

            html.Br(),

            dbc.Tabs(id='lift-over-results-tabs', active_tab='tab-0'),

            html.Br(),

            dbc.Label(id='lift-over-results-gene-intro'),

            dbc.Checklist(id='lift-over-overlap-table-filter',
                          inline=True,
                          className='ms-3'),


            dcc.Loading([
                html.P(
                    html.Div([
                             dbc.Button([html.I(
                                 className='bi bi-download me-2'),
                                 'Export to CSV'],
                                 id='lift-over-export-table',
                                 color='light', size='sm', className='table-button'),
                             dbc.Button([html.I(
                                 className='bi bi-arrow-clockwise me-2'),
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
                )])
        ])

]
)
