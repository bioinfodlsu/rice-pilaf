import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dash_table, dcc, html

dash.register_page(__name__, name="Co-expression Network Analysis")


layout = dbc.Row(dbc.Col(id='coexpression-container', children=[
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
            {'value': 'fox', 'label': 'FOX', 'label_id': 'fox'}
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

    dcc.Slider(id='coexpression-parameter-slider', step=None,
               marks={0: '0.0', 10: '0.1', 20: '0.2', 30: '0.3', 40: '0.4',
                      50: '0.5', 60: '0.6', 70: '0.7', 80: '0.8', 90: '0.9', 100: '1.0'},
               value=30),

    html.Br(),

    dbc.Button('Run Analysis',
               id='coexpression-submit',
               className='page-button',
               n_clicks=0),

    html.Br(),
    html.Br(),

    html.Div(id="coexpression-results-container", style={'display': 'none'}, children=[
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
            export_format='csv',
            style_cell={
                'whiteSpace': 'pre-line',
                'font-family': 'sans-serif'
            },
            markdown_options={"html": True},
            sort_action='native',
            filter_action='native',
            filter_options={'case': 'insensitive',
                            'placeholder_text': 'Search column'},
            page_action='native',
            page_size=15
        ),

        html.Br(),

        dcc.Markdown("Module"),

        dbc.RadioItems(
            id='coexpression-graph-layout',
            options=[
                {'value': 'circle', 'label': 'Circle', 'label_id': 'circle'},
                {'value': 'grid', 'label': 'Grid', 'label_id': 'grid'}
            ],
            value='circle',
            inline=True
        ),

        html.Br(),

        cyto.Cytoscape(
            id='coexpression-module-graph',
            layout={'name': 'circle'},
            style={'width': '100%',
                   'height': '100vh'},          # Should be here (otherwise, initial loading does not consume entire width and height)
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
                },
                {
                    'selector': '.shaded',
                    'style': {
                        'background-color': '#254b5d',
                        'line-color': '#254b5d',
                        'height': '20px',
                        'width': '20px'
                    }
                }
            ]
        )
    ])
]
))
