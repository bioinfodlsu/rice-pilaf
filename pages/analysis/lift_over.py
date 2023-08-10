import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from callbacks.constants import Constants
const = Constants()

other_ref_genomes = [{'value': 'N22', 'label': 'N22   (aus Nagina-22)'},
                     {'value': 'MH63', 'label': 'MH63   (indica Minghui-63)'},
                     {'value': 'Azu', 'label': 'Azu   (japonica Azucena)'},
                     {'value': 'ARC', 'label': 'ARC   (basmati ARC)'},
                     {'value': 'IR64', 'label': 'IR64   (indica IR64)'},
                     {'value': 'CMeo', 'label': 'CMeo   (japonica CHAO MEO)'}]

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': const.LIFT_OVER
    },  
    hidden=True,
    children=[
        html.Div([
            html.Span(
                'In this page, you can obtain the list of genes overlapping your input intervals.'),
            html.P(
                'Optionally, you can choose genomes to lift-over your Nipponbare coordinates to.'),

        ], className='analysis-intro p-3'),

        html.Div([
            html.I(
                className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='lift-over-genomic-intervals-input'),

            html.Br(),
            html.Br(),

            dbc.Label('Select genome(s) for lift-over (ignore if lift-over is not needed):', className='mb-2'),

            dcc.Dropdown(
                other_ref_genomes,
                id='lift-over-other-refs',
                multi=True,
                persistence=True,
                persistence_type='memory',
                className='dash-bootstrap'
            ),

            html.Br(),

            dbc.Button('Show gene list',
                    id='lift-over-submit',
                    className='page-button',
                    n_clicks=0),

            html.Br(),
            html.Br(),

            html.Div(
                id='lift-over-results-container',
                style={'display': 'none'},
                children=[
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
                                    n_clicks = 0,
                                    color='light', size='sm', className='table-button'),
                                dcc.Download(id='lift-over-download-df-to-csv'),
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
        ], className='p-3 mt-2')
])
