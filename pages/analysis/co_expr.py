import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dash_table, dcc, html
from callbacks.constants import Constants
const = Constants()

coach = html.Li(
    [html.B('COACH'),
     html.Span(
        ' Detects highly connected gene subnetworks (referred to as "cores") and expands them by including closely associated genes',
        className='algo-desc'),
     html.Div([
         html.Span(
             'Wu, M., Li, X., Kwoh, C. K., & Ng, S. K. (2009). A core-attachment based method to detect protein complexes in PPI networks. '),
         html.I('BMC Bioinformatics, 10'),
         html.Span('(169). '),
         html.A('https://doi.org/10.1186/1471-2105-10-169',
                href='https://doi.org/10.1186/1471-2105-10-169',
                target='_blank')],
        className='reference'
    )]
)

demon = html.Li(
    [html.B('DEMON'),
     html.Span(
        ' Adopts a bottom-up approach where genes "vote" to determine the subnetwork to which connected genes belong',
        className='algo-desc'),
     html.Div([
         html.Span(
             'Coscia, M., Rossetti, G., Giannotti, F., & Pedreschi, D. (2012). DEMON: A local-first discovery method for overlapping communities. In '),
         html.I('KDD\'12: Proceedings of the 18th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining '),
         html.Span('(pp. 615–623). Association for Computing Machinery. '),
         html.A('https://doi.org/10.1145/2339530.2339630',
                href='https://doi.org/10.1145/2339530.2339630',
                target='_blank')],
        className='reference'
    )]
)

clusterone = html.Li(
    [html.B('ClusterONE'),
     html.Span(
        ' Forms cohesive gene subnetworks from an initial set of seed genes. Among the module detection algorithms supported by this app, this is the only algorithm that takes into account the weights associated with the coexpression',
        className='algo-desc'),
     html.Div([
         html.Span(
             'Nepusz, T., Yu, H., & Paccanaro, A. (2012). Detecting overlapping protein complexes in protein-protein interaction networks. '),
         html.I('Nature Methods, 9, '),
         html.Span('471–472. '),
         html.A('https://doi.org/10.1038/nmeth.1938',
                href='https://doi.org/10.1038/nmeth.1938',
                target='_blank')],
        className='reference'
    )],
)

fox = html.Li(
    [html.B('FOX'),
     html.Span(
        ' Determines the membership of a gene to a subnetwork by counting the number of triangles formed by the gene with other genes in the subnetwork',
        className='algo-desc'),
     html.Div([
         html.Span(
             'Lyu, T., Bing, L., Zhang, Z., & Zhang, Y. (2020). FOX: Fast overlapping community detection algorithm in big weighted networks. '),
         html.I('ACM Transactions on Social Computing, 3'),
         html.Span('(3), 1–23. '),
         html.A('https://doi.org/10.1145/3404970',
                href='https://doi.org/10.1145/3404970',
                target='_blank')],
        className='reference'
    )],
)

module_detection_algo_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle('Module Detection Algorithms')
    ),
    dbc.ModalBody([
        html.P(
            'Since genes can possibly be involved in multiple biological functions or processes, the algorithms supported by RicePilaf allow for overlapping modules (that is, a given gene may belong to multiple modules):'),
        html.Ul([
            clusterone, html.Br(), coach, html.Br(), demon, html.Br(), fox
        ])
    ])],
    id='coexpression-clustering-algo-modal',
    is_open=False,
    size='xl'
)


# ============
# Main Layout
# ============

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': const.COEXPRESSION
    },
    hidden=True,

    children=[

        html.Div([
            html.P('In this page, you can search for modules (a.k.a. communities, clusters) in rice co-expression networks, which are significantly enriched in the genes implicated by your GWAS. '
                   'Likely functions of the modules are inferred by enrichment analysis against several ontologies and pathway databases.')
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='coexpression-genomic-intervals-input'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            dbc.Label(
                'Include additional genes from the pan-genome lift-over or the text mining results'),
            html.Br(),
            dbc.Label(
                'Enter their MSU accession IDs, separated by a semicolon (e.g., LOC_Os01g03680;LOC_Os01g03690;LOC_Os01g04110)'),

            dbc.Textarea(id='coexpression-addl-genes'),

            html.Br(),

            dbc.Label(['Select the co-expression network',
                       html.I(
                           className='bi bi-info-circle', id='coexpression-network-tooltip')]),

            dbc.RadioItems(
                id='coexpression-network',
                options=[
                    {'value': 'OS-CX', 'label': 'RiceNet v2', 'label_id': 'os-cx'},
                    {'value': 'RCRN',
                     'label': 'Rice Combined Mutual Ranked Network (RCRN)', 'label_id': 'rcrn'},
                ],
                value='OS-CX',
                inline=True,
                className='ms-3 mt-1'
            ),

            html.Br(),

            dbc.Label(['Select a module detection algorithm ',
                       html.I(
                           className='bi bi-info-circle',
                           id='coexpression-clustering-algo-tooltip',
                           n_clicks=0
                       )]),

            module_detection_algo_modal,

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
                inline=True,
                className='ms-3 mt-1'
            ),

            html.Br(),

            dbc.Label(['Select the ',
                       html.Span('parameter for running the algorithm',
                                 id='coexpression-parameter-name'),
                       html.I(
                           className='bi bi-info-circle', id='coexpression-parameter-tooltip')],
                      className='mb-4'),

            # Should also be changed if parameter space is changed
            html.Div([dcc.Slider(id='coexpression-parameter-slider', step=None,
                                 marks={0: '1 (Loose Modules)', 30: '2', 60: '3',
                                        90: '4 (Dense Modules)'},
                                 value=30)],
                     id='coexpression-parameter-slider-container'),

            html.Br(),

            dbc.Button('Run Analysis',
                       id='coexpression-submit',
                       className='page-button',
                       n_clicks=0),
        ], className='analysis-intro p-3'),


        html.Br(),

        html.Div(
            id='coexpression-results-container',
            style={'display': 'none'},
            children=[
                dcc.Loading(
                    id='coexpression-loading',
                    children=[
                        html.Hr(className='mt-3 mb-4'),
                        html.Div([
                            html.I(
                                className='bi bi-bar-chart me-2 non-clickable'),
                            html.Span(id='coexpression-module-stats')
                        ], className='mb-3 stats ps-1'),

                        html.Div(
                            id='coexpression-results-module-tabs-container',
                            children=[
                                dbc.Label('Select an enriched module'),
                                dcc.Dropdown(id='coexpression-modules'),
                            ]
                        )
                    ]
                ),

                html.Div(
                    id='coexpression-graph-container',
                    children=[
                        html.Div(
                            id='coexpression-table-container',
                            children=[
                                html.Br(),

                                html.Div([
                                    html.I(
                                        className='bi bi-bar-chart me-2 non-clickable'),
                                    html.Span(id='coexpression-graph-stats')
                                ], className='mb-3 stats ps-1'),

                                html.Br(),

                                dbc.Tabs(
                                    id='coexpression-modules-pathway',
                                    active_tab='tab-0',
                                    children=[
                                        dcc.Tab(label='Gene Ontology',
                                                value='Gene Ontology'),
                                        dcc.Tab(label='Trait Ontology',
                                                value='Trait Ontology'),
                                        dcc.Tab(label='Plant Ontology',
                                                value='Plant Ontology'),
                                        dcc.Tab(label='Pathways (Over-Representation)',
                                                value='Pathways (Over-Representation)'),
                                        dcc.Tab(label='Pathway-Express',
                                                value='Pathway-Express'),
                                        dcc.Tab(label='SPIA',
                                                value='SPIA')
                                    ]
                                ),

                                html.Br(),

                                dcc.Loading([
                                    html.P(
                                        html.Div([
                                            html.Div([
                                                html.I(
                                                    className='bi bi-bar-chart me-2 non-clickable'),
                                                html.Span(
                                                    id='coexpression-table-stats')
                                            ], className='mb-3 stats ps-1'),
                                            dbc.Button([html.I(
                                                className='bi bi-download me-2'),
                                                'Export to CSV'],
                                                id='coexpression-export-table',
                                                n_clicks=0,
                                                color='light', size='sm', className='table-button'),
                                            dcc.Download(
                                                id='coexpression-download-df-to-csv'),
                                            dbc.Button([html.I(
                                                className='bi bi-arrow-clockwise me-2'),
                                                'Reset Table'],
                                                id='coexpression-reset-table',
                                                color='light', size='sm', className='ms-3 table-button')
                                        ], style={'textAlign': 'right'})
                                    ),

                                    dash_table.DataTable(
                                        id='coexpression-pathways',
                                        style_cell={
                                            'whiteSpace': 'pre-line'
                                        },
                                        markdown_options={'html': True},
                                        sort_action='native',
                                        filter_action='native',
                                        filter_options={'case': 'insensitive',
                                                        'placeholder_text': 'Search column'},
                                        page_action='native',
                                        page_size=15,
                                        cell_selectable=False
                                    )
                                ]),

                                html.Br(),
                                html.Br(),

                                html.P(
                                    'The connections indicate that the genes are co-expressed. The shaded nodes refer to the genes implicated by your GWAS/QTL, including those that you manually added.'),

                                dbc.Label('Select the module display layout'),

                                dbc.RadioItems(
                                    id='coexpression-graph-layout',
                                    options=[
                                        {'value': 'circle', 'label': 'Circle',
                                         'label_id': 'circle'},
                                        {'value': 'grid', 'label': 'Grid',
                                         'label_id': 'grid'}
                                    ],
                                    value='circle',
                                    inline=True,
                                    className='ms-3'
                                ),

                                html.P(
                                    html.Div([
                                        dbc.Button([html.I(
                                            className='bi bi-download me-2'),
                                            'Export Edge List'],
                                            id='coexpression-export-graph',
                                            color='light', size='sm',
                                            n_clicks=0,
                                            className='table-button'),
                                        dcc.Download(
                                            id='coexpression-download-graph-to-json'),
                                        dbc.Button([html.I(
                                            className='bi bi-arrow-clockwise me-2'),
                                            'Reset Graph'],
                                            id='coexpression-reset-graph',
                                            n_clicks=0,
                                            color='light', size='sm',
                                            className='ms-3 table-button')
                                    ], style={'textAlign': 'right'})
                                )
                            ]
                        ),

                        dcc.Loading(
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
                        )
                    ]
                )
            ]
        )
    ], className='mt-2')
