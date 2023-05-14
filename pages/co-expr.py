import dash
import dash_cytoscape as cyto
import networkx as nx
from dash import dcc, html

dash.register_page(__name__, name="Co-expression Network Analysis")

# path needs to be relative to top-level folder
coexpress_nw = "static/networks_display/clusterone/module-3.tsv"
G = nx.read_edgelist(coexpress_nw, data=(("coexpress", float),))
cyto_G = nx.cytoscape_data(G)

# Set the node label (user-facing)
for node in cyto_G['elements']['nodes']:
    node['data']['label'] = node['data']['name']

layout = html.Div(
    [
        dcc.Markdown("Co-expression action happens here"),
        cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout={'name': 'cose'},
            style={'width': '100%', 'height': '400px'},
            elements=cyto_G['elements']
        )
    ]
)
