import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

layout = html.Div(id='text-mining-container', children=[
    html.Div([
        html.Span('In this page, you can retrieve gene names associated with traits, diseases, chemicals, etc. from text-mined PubMed abstracts. '
                  'Conversely, you can retrieve literature that associates your gene of interest to some phenotype.'),
    ], className='analysis-intro p-3'),

    html.Div([
        html.Br(),
        html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
        html.Span(id='text-mining-genomic-intervals-input'),

        html.Br(),
        html.Br(),

        dbc.Label('Enter your query trait or gene:', className='mb-2'),
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
                            className='sample-genomic-interval ms-3'),
                  html.Span(',', className='sample-genomic-interval'),
                  html.Span('LOC_xxxxxx',
                            id={'type': 'example-text-mining',
                                'description': 'LOC_xxxxxx'},
                            className='sample-genomic-interval ms-3')
                  ],
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
                            dcc.Download(id='text-mining-download-df-to-csv')
                        ], style={'textAlign': 'right'})
                    ),

                    dash_table.DataTable(
                        id='text_mining_result_table',
                        persistence=True,
                        persistence_type='memory'
                    )
                ])
            ], className='p-3 mt-2')

    ])
], className='p-3 mt-2')
