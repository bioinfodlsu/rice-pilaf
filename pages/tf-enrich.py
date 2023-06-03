import dash
from dash import dash_table, dcc, html

dash.register_page(__name__, name="Regulatory feature enrichment")


layout = html.Div(
    [
        html.Div(id='TF-enrichment-input-genomic-intervals'),

        html.Br(),
        dcc.Markdown("Consider TF binding sites in the following regions:"),
        dcc.Dropdown(["genome-wide","promoters"],
                     'promoters',
                     id='tfbs_set',
                     placeholder='Select a TFBS set',
                     multi=False,
                     persistence=True,
                     persistence_type='memory'
        ),
       html.Br(),
       dcc.Markdown("Choose TF binding site prediction technique:"),
       dcc.Dropdown(["motif scan","motif conservation","FunTFBS"],
                    "FunTFBS",
                     id='tfbs_prediction_technique',
                     placeholder='Select a TF binding site prediction technique',
                     multi=False,
                     persistence=True,
                     persistence_type='memory'
        ),

        dash_table.DataTable(
            id='tf_enrichment_result_table',
            persistence=True,
            persistence_type='memory'
        )

    ]
)
