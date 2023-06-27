import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

dash.register_page(__name__, name="Regulatory feature enrichment")


layout = html.Div(
    [
        html.Div(id='TF-enrichment-input-genomic-intervals'),

        html.Br(),
        dcc.Markdown("Consider TF binding sites in the following regions:"),
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
        dcc.Markdown("Choose TF binding site prediction technique:"),
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
