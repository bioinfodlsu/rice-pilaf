import dash
from dash import dcc, html

import dash_cytoscape as cyto

dash.register_page(__name__, name="Co-expression Network Analysis")

layout = html.Div(
    [
        dcc.Markdown("Co-expression action happens here"),
        cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '400px'},
        elements=[
            {'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 75, 'y': 75}},
            {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
            {'data': {'source': 'one', 'target': 'two'}}
        ]
    )
    ]
)
