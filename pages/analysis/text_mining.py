import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from callbacks.constants import Constants
const = Constants()

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': const.TEXT_MINING
    },
    hidden=True,
    children=[
        html.Div([
            html.P('In this page, you can retrieve gene names associated with traits, diseases, chemicals, etc. from a database constructed from text-mined PubMed abstracts. '
                   # 'Conversely, you can retrieve literature that associates your gene of interest to some phenotype.'
                   ),
        ], className='analysis-intro p-3'),

        html.Div([
            html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='text-mining-genomic-intervals-input'),

            html.Br(),
            html.Br(),

            dbc.Label('Enter your query trait/phenotype:', className='mb-2'),

            dbc.Alert(
                id='text-mining-input-error',
                color='danger',
                style={'display': 'none'}
            ),
            dbc.Input(
                id='text-mining-query',
                type='text',
                value=''
            ),

            html.Div([html.Span('Examples:', className='pe-3'),
                      html.Span('pre-harvest sprouting',
                                id={'type': 'example-text-mining',
                                    'description': 'pre-harvest sprouting'},
                                className='sample-genomic-interval'),
                      html.Span(',', className='sample-genomic-interval'),
                      html.Span('anaerobic germination',
                                id={'type': 'example-text-mining',
                                    'description': 'anaerobic germination'},
                                className='sample-genomic-interval ms-3')],
                     className='pt-3'),
            html.Br(),

            dbc.Button('Search',
                       id='text-mining-submit',
                       className='page-button',
                       n_clicks=0),

            html.Br(),
            html.Br(),

            html.Div(
                id='text-mining-results-container',
                style={'display': 'none'},
                children=[
                    dcc.Loading([
                        html.P(
                            html.Div([
                                dbc.Button([html.I(
                                    className='bi bi-download me-2'),
                                    'Export to CSV'],
                                    id='text-mining-export-table',
                                    n_clicks=0,
                                    color='light', size='sm', className='table-button'),
                                dcc.Download(
                                    id='text-mining-download-df-to-csv'),
                                dbc.Button([html.I(
                                    className='bi bi-arrow-clockwise me-2'),
                                    'Reset Table'],
                                    id='text-mining-reset-table',
                                    color='light', size='sm', className='ms-3 table-button')
                            ], style={'textAlign': 'right'})
                        ),

                        dash_table.DataTable(
                            id='text-mining-result-table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'textAlign': 'left'
                            },
                            markdown_options={'html': True},
                            sort_action='native',
                            filter_action='native',
                            filter_options={'case': 'insensitive',
                                            'placeholder_text': 'Search column'},
                            page_action='native',
                            page_size=10,
                            cell_selectable=False
                        )
                    ])
                ], className='mt-2')
        ], className='p-3 mt-2')
    ])
