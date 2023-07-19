import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


layout = html.Div(id='tf-enrichment-over-container', children=[
    html.Div([
        html.P(
            'Perhaps your intervals contains variants that influence regulatory elements, for example by affecting binding affinity.'),
        html.Span(
            'In this page, you can search for transcription factors whose binding sites overlap significantly with your intervals.')
    ], className='analysis-intro p-3'),

    html.Div([
        html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
        html.Span(id='tf-enrichment-genomic-intervals-input'),

        html.Br(),
        html.Br(),

        dbc.Label(['Choose TF binding site prediction technique:',
                   html.I(
                       className='bi bi-info-circle mx-2',
                       id='tf-enrichment-technique-tooltip',
                       n_clicks=0
                   )]),
        dbc.RadioItems(
            id='tfbs_prediction_technique',
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
                       className='bi bi-info-circle mx-2',
                       id='tf-enrichment-binding-site-tooltip',
                       n_clicks=0
                   )]),
        dbc.RadioItems(
            id='tfbs_set',
            options=[
                {'value': 'promoters', 'label': 'promoters', 'label_id': 'promoters'},
                {'value': 'genome', 'label': 'genome',
                 'label_id': 'genome'}

            ],
            value='promoters',
            inline=True
        ),
        html.Br(),
        dcc.Markdown("Input threshold for False-Discovery Rate:"),
        # dcc.Slider(id='tfbs_fdr', step=None,
        #           marks={0:'0.01', 10: '0.025',  20: '0.05',
        #                  30: '0.1',  40: '0.25'},
        #           value=40),
        dbc.Input(id="tfbs_fdr", type="number", value=0.25),
        html.Br(),
        html.Br(),
        dbc.Button('Run Analysis',
                   id='tfbs-submit',
                   n_clicks=0,
                   className='page-button'),

        html.Br(),
        html.Br(),
        html.Div(id='tfbs-results-container', children=[
            dcc.Loading(
                dash_table.DataTable(
                    id='tf_enrichment_result_table',
                    persistence=True,
                    persistence_type='memory'
                )
            )

        ])
    ], className='p-3 mt-2')
])
