import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

# dash.register_page(__name__, path='/tf-enrichment',
#                   name="Regulatory Feature Enrichment")


layout = html.Div(id='tf-enrichment-over-container', children=[
    html.P(id='tf-enrichment-genomic-intervals-input'),
    dcc.Markdown('''
        Perhaps your intervals contains variants that influence regulatory elements, for example by affecting binding affinity.
        
        In this page, you can search for transcription factors whose binding sites overlap significantly with your intervals.
        '''),
    html.Div(id='TF-enrichment-input-genomic-intervals'),

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
            {'value': 'motif conservation', 'label': 'motif conservation',
             'label_id': 'motif conservation'},
            {'value': 'motif scan', 'label': 'motif scan',
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
            {'value': 'genome-wide', 'label': 'genome-wide',
             'label_id': 'genome-wide'}

        ],
        value='promoters',
        inline=True
    ),
    html.Br(),
    dcc.Markdown("Select threshold for False-Discovery Rate:"),
    dcc.Slider(id='coexpression-parameter-slider', step=None,
               marks={0: '0.01', 10: '0.025',  20: '0.05',
                      30: '0.1',  40: '0.25'},
               value=40),

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
]
)