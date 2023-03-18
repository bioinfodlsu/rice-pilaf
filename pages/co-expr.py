import dash
from dash import dcc, html

import dash_cytoscape as cyto
import networkx as nx

dash.register_page(__name__, name="Co-expression Network Analysis")

#G = nx.path_graph(3)
coexpress_nw  = "data/networks/OS-CX.txt.1000" #path needs to be relative to top-level folder
G = nx.read_edgelist(coexpress_nw, data=(("coexpress",float),))
print("converting to cytoscape JSON")
cyto_G = nx.cytoscape_data(G)

#print(cyto_G['elements']['nodes'])

layout = html.Div(
    [
        dcc.Markdown("Co-expression action happens here"),
        cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout={'name': 'cose'},
            style={'width': '100%', 'height': '400px'},
            elements = cyto_G['elements']
        )
    ]
)
