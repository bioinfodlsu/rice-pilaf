import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dash_table, dcc, html

dash.register_page(__name__, name="Co-expression Network Analysis")

layout = html.Div(
    [
        html.Div(id='coexpression-loading',
                 children='Finding enriched modules...', hidden=False),

        dcc.Dropdown(
            id='coexpression-modules',
            style={'display': 'none'}
        ),

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
