import dash
import dash_cytoscape as cyto
from dash import dcc, html

dash.register_page(__name__, name="Co-expression Network Analysis")

layout = html.Div(
    [
        html.Div(id='coexpression-input-genomic-intervals'),
        html.Br(),
        html.Div(id='coexpression-loading',
                 children='Finding enriched modules...', hidden=False),

        dcc.Dropdown(
            id='coexpression-modules',
            style={'display': 'none'}
        ),

        cyto.Cytoscape(
            id='coexpression-module-graph',
            layout={'name': 'circle'},
            style={'visibility': 'hidden', 'width': '100%', 'height': '100vh'},
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {
                        'content': 'data(id)',
                        'height': '5px',
                        'width': '5px',
                        'font-size': '10px'
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'width': '1px',
                    }
                }
            ]
        )
    ]
)
