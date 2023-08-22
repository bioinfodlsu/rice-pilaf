import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from callbacks.constants import Constants
const = Constants()

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': const.TFBS
    },
    hidden=True,
    children=[
        html.Div([
            html.P(
                'Perhaps your intervals contains variants that influence regulatory elements, for example by affecting binding affinity.'),
            html.P(
                'In this page, you can search for transcription factors whose binding sites overlap significantly with your intervals.')
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='tf-enrichment-genomic-intervals-input'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            dbc.Label(['Choose TF binding site prediction technique:',
                       html.I(
                           className='bi bi-info-circle',
                           id='tf-enrichment-technique-tooltip',
                           n_clicks=0
                       )]),
            dbc.RadioItems(
                id='tfbs-prediction-technique',
                options=[
                    {'value': 'FunTFBS', 'label': 'FunTFBS', 'label_id': 'FunTFBS'},
                    {'value': 'CE', 'label': 'motif conservation',
                     'label_id': 'motif conservation'},
                    {'value': 'motif', 'label': 'motif scan',
                     'label_id': 'motif scan'}
                ],
                value='FunTFBS',
                inline=True
            ),

            html.Br(),
            dbc.Label(['Consider TF binding sites in the following regions:',
                       html.I(
                           className='bi bi-info-circle',
                           id='tf-enrichment-binding-site-tooltip',
                           n_clicks=0
                       )]),
            dbc.RadioItems(
                id='tfbs-set',
                options=[
                    {'value': 'promoters', 'label': 'promoters',
                        'label_id': 'promoters'},
                    {'value': 'genome', 'label': 'genome',
                     'label_id': 'genome'}

                ],
                value='promoters',
                inline=True
            ),
            html.Br(),
            dcc.Markdown("Input threshold for False-Discovery Rate:"),
            dbc.Input(id='tfbs-fdr', type='number',
                      value=0.25, min=0, max=1, step=0.05),
            html.Br(),

            dbc.Button('Run Analysis',
                       id='tfbs-submit',
                       n_clicks=0,
                       className='page-button'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div(
            id='tfbs-results-container',
            style={'display': 'none'},
            children=[
                html.Hr(className='mt-3 mb-4'),
                dcc.Loading([
                    html.P(
                        html.Div([
                            dbc.Button([html.I(
                                className='bi bi-download me-2'),
                                'Export to CSV'],
                                id='tfbs-export-table',
                                n_clicks=0,
                                color='light', size='sm', className='table-button'),
                            dcc.Download(id='tfbs-download-df-to-csv'),
                            dbc.Button([html.I(
                                className='bi bi-arrow-clockwise me-2'),
                                'Reset Table'],
                                id='tfbs-reset-table',
                                color='light', size='sm', className='ms-3 table-button')
                        ], style={'textAlign': 'right'})
                    ),

                    dash_table.DataTable(
                        id='tf-enrichment-result-table',
                        style_cell={
                            'whiteSpace': 'pre-line'
                        },
                        markdown_options={'html': True},
                        sort_action='native',
                        filter_action='native',
                        filter_options={'case': 'insensitive',
                                        'placeholder_text': 'Search column'},
                        page_action='native',
                        page_size=15,
                        cell_selectable=False
                    )
                ])
            ])
    ], className='mt-2'
)
