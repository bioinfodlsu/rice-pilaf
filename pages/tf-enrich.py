import dash
from dash import dash_table, dcc, html

dash.register_page(__name__, name="Regulatory feature enrichment")


layout = html.Div(
    [
        html.Div(id='TF-enrichment-input-genomic-intervals'),

        html.Br(),

        dcc.Dropdown(["genome-wide","in promoter regions"],
                     id='tfbs_set',
                     placeholder='Select a TFBS set',
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
