import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dash_table, dcc, html

dash.register_page(__name__, name="Co-expression Network Analysis")

layout = html.Div(
    [
        html.Div(["Module detection algorithm ", html.I(
            className="bi bi-info-circle-fill me-2", id="coexpression-clustering-algo-tooltip")]),

        html.Br(),

        dbc.RadioItems(
            id='coexpression-clustering-algo',
            options=[
                {'value': 'clusterone', 'label': 'ClusterONE',
                    'label_id': 'clusterone'},
                {'value': 'coach', 'label': 'COACH', 'label_id': 'coach'},
                {'value': 'demon', 'label': 'DEMON', 'label_id': 'demon'},
                {'value': 'fox', 'label': 'FOX', 'label_id': 'fox'},
            ],
            value='clusterone',
            inline=True
        ),

        dbc.Tooltip('The algorithms below allow for overlapping modules (that is, genes may belong to more than one module). Hover over each algorithm for more details',
                    target='coexpression-clustering-algo-tooltip'),

        dbc.Tooltip('Detects highly connected gene subnetworks and expands them by including closely associated genes. Reference: Wu, M., Li, X., Kwoh, C. K., & Ng, S. K. (2009). A core-attachment based method to detect protein complexes in PPI networks. BMC Bioinformatics, 10(169)',
                    target='coach'),

        html.Br(),

        html.Div(["Parameter ", html.I(
            className="bi bi-info-circle-fill me-2", id="coexpression-parameter-tooltip")]),

        html.Br(),

        dcc.Slider(id='coexpression-parameter-slider', step=None),

        dcc.Markdown("Enriched modules"),

        dcc.Loading(dcc.Dropdown(
            id='coexpression-modules',
            style={'display': 'none'}
        )),

        html.Br(),

        dbc.Tabs(id='coexpression-modules-pathway', active_tab='tab-0',
                 children=[dcc.Tab(label='Gene Ontology',
                                   value='Gene Ontology'),
                           dcc.Tab(label='Trait Ontology',
                                   value='Trait Ontology'),
                           dcc.Tab(label='Plant Ontology',
                                   value='Plant Ontology'),
                           dcc.Tab(label='Pathways (Overrepresentation)',
                                   value='Pathways (Overrepresentation)'),
                           dcc.Tab(label='Pathway-Express',
                                   value='Pathway-Express'),
                           dcc.Tab(label='SPIA', value='SPIA')]),

        html.Br(),

        dash_table.DataTable(
            id='coexpression-pathways',
            persistence=True,
            persistence_type='memory',
            export_format='csv'
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
