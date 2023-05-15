import dash
import dash_cytoscape as cyto
import networkx as nx
from dash import dcc, html

dash.register_page(__name__, name="Co-expression Network Analysis")

# path needs to be relative to top-level folder
coexpress_nw = "static/networks_display/clusterone/module-25.tsv"
G = nx.read_edgelist(coexpress_nw, data=(("coexpress", float),))
cyto_G = nx.cytoscape_data(G)

layout = html.Div(
    [
        dcc.Markdown("Co-expression action happens here"),
        cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout={'name': 'circle'},
            style={'width': '100%', 'height': '200vh'},
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
            ],
            elements=cyto_G['elements']
        ),

        html.Div(id='test', children='')
    ]
)
