import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dash_table, dcc, html
from callbacks.constants import Constants
from callbacks.coexpression.util import *

# ============================
# Module Detection Algorithms
# ============================


coach = html.Li([
    html.B('COACH'),
    html.Span(
        ' Detects highly connected gene subnetworks (referred to as "cores") and expands them by including closely associated genes',
        className='algo-desc'),
    html.Div([
        html.Span(
             'Wu, M., Li, X., Kwoh, C. K., & Ng, S. K. (2009). A core-attachment based method to detect protein complexes in PPI networks. '),
        html.I('BMC Bioinformatics, 10'),
        html.Span('(169). '),
        html.A(
            'https://doi.org/10.1186/1471-2105-10-169',
            href='https://doi.org/10.1186/1471-2105-10-169',
            target='_blank')
    ], className='reference')
])

demon = html.Li([
    html.B('DEMON'),
    html.Span(
        ' Adopts a bottom-up approach where genes "vote" to determine the subnetwork to which connected genes belong',
        className='algo-desc'),
    html.Div([
        html.Span(
             'Coscia, M., Rossetti, G., Giannotti, F., & Pedreschi, D. (2012). DEMON: A local-first discovery method for overlapping communities. In '),
        html.I('KDD\'12: Proceedings of the 18th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining '),
        html.Span('(pp. 615–623). Association for Computing Machinery. '),
        html.A(
            'https://doi.org/10.1145/2339530.2339630',
            href='https://doi.org/10.1145/2339530.2339630',
            target='_blank')
    ], className='reference')
])

clusterone = html.Li([
    html.B('ClusterONE'),
    html.Span(
        ' Forms cohesive gene subnetworks from an initial set of seed genes. ',
        className='algo-desc'),
    html.Div([
        html.Span(
             'Nepusz, T., Yu, H., & Paccanaro, A. (2012). Detecting overlapping protein complexes in protein-protein interaction networks. '),
        html.I('Nature Methods, 9, '),
        html.Span('471–472. '),
        html.A(
            'https://doi.org/10.1038/nmeth.1938',
            href='https://doi.org/10.1038/nmeth.1938',
            target='_blank')
    ], className='reference')
])

fox = html.Li([
    html.B('FOX'),
    html.Span(
        ' Determines the membership of a gene to a subnetwork by counting the number of triangles formed by the gene with other genes in the subnetwork',
        className='algo-desc'),
    html.Div([
        html.Span(
            'Lyu, T., Bing, L., Zhang, Z., & Zhang, Y. (2020). FOX: Fast overlapping community detection algorithm in big weighted networks. '),
        html.I('ACM Transactions on Social Computing, 3'),
        html.Span('(3), 1–23. '),
        html.A(
            'https://doi.org/10.1145/3404970',
            href='https://doi.org/10.1145/3404970',
            target='_blank')
    ], className='reference mb-3'),
    html.Span(
        'RicePilaf uses LazyFox for a parallelized implementation of FOX. LazyFox is run with the queue size and thread count set to 20.',
        className='algo-desc'),
    html.Div([
        html.Span(
            'Garrels, T., Khodabakhsh, A., Renard, B. Y., & Baum, K. (2023). LazyFox: Fast and parallelized overlapping community detection in large graphs. '),
        html.I('PeerJ Computer Science, 9, '),
        html.Span('e1291. '),
        html.A(
            'https://doi.org/10.7717/peerj-cs.1291',
            href='https://doi.org/10.7717/peerj-cs.1291',
            target='_blank')
    ], className='reference mb-3')
])

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
    size='xl',
    scrollable=True
)

# ======================
# Coexpression Networks
# ======================

ricenet = html.Li([
    html.B('RiceNet v2'),
    html.Br(),
    html.Div([html.Span(
        'RicePilaf uses the component network derived from the co-expression of '),
        html.I('Oryza sativa '),
        html.Span(
        'genes across microarray experiments.',
    )], className='algo-desc'),
    html.Div([
        html.Span(
             'Lee, T., Oh, T., Yang, S., Shin, J., Hwang, S., Kim, C. Y., Kim, H., Shim, H., Shim, J. E., Ronald, P. C., & Lee, I. (2015). RiceNet v2: An improved network prioritization server for rice genes. '),
        html.I('Nucleic Acids Research, 43'),
        html.Span('(W1), W122–W127 '),
        html.A(
            'https://doi.org/10.1093/nar/gkv253',
            href='https://doi.org/10.1093/nar/gkv253',
            target='_blank')
    ], className='reference')
])

rcrn = html.Li([
    html.B('Rice Combined Mutual Ranked Network (RCRN)'),
    html.Br(),
    html.Span(
        'RicePilaf uses the integrated RCRN network.',
        className='algo-desc'),
    html.Div([
        html.Span(
             'Zhao, K., Lin, F., Romero-Gamboa, S. P., Saha, P., Goh, H. J., An, G., Jung, K. H., Hazen, S. P., & Bartley, L. E. (2019). Rice genome-scale network integration reveals transcriptional regulators of grass cell wall synthesis. '),
        html.I('Frontiers in Plant Science, 10, '),
        html.Span('1275. '),
        html.A(
            'https://doi.org/10.3389/fpls.2019.01275',
            href='https://doi.org/10.3389/fpls.2019.01275',
            target='_blank')
    ], className='reference')
])

coexpression_network_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle('Coexpression Networks')
    ),
    dbc.ModalBody([
        html.P(
            'RicePilaf provides the option to choose between two co-expression networks:'),
        html.Ul([
            ricenet, html.Br(), rcrn
        ])
    ])],
    id='coexpression-network-modal',
    is_open=False,
    size='xl',
    scrollable=True
)

# ===========
# Parameters
# ===========

parameter_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle('Coexpression Networks')
    ),
    dbc.ModalBody([
        html.P(
            'RicePilaf provides the option to configure selected parameters when running the module detection algorithms:'),
        html.Ul([
            html.Li([
                html.Span('For '),
                html.A(
                    'ClusterOne', href='https://doi.org/10.1038/nmeth.1938', target='_blank'),
                html.Span(
                    ', the parameter pertains to the minimum cluster density.')
            ]),
            html.Li([
                html.Span('For '),
                html.A(
                    'COACH', href='https://doi.org/10.1186/1471-2105-10-169', target='_blank'),
                html.Span(
                    ', the parameter pertains to the maximum core affinity.')
            ]),
            html.Li([
                html.Span('For '),
                html.A(
                    'DEMON', href='https://doi.org/10.1145/2339530.2339630', target='_blank'),
                html.Span(', the parameter pertains to the merging threshold.')
            ]),
            html.Li([
                html.Span('For '),
                html.A('FOX', href='https://doi.org/10.1145/3404970',
                       target='_blank'),
                html.Span(
                    ', the parameter pertains to the weighted community clustering metric.')
            ])
        ])
    ])],
    id='coexpression-parameter-modal',
    is_open=False,
    size='xl',
    scrollable=True
)

# ============
# Main Layout
# ============

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_COEXPRESSION
    },
    hidden=True,

    children=[

        html.Div([
            html.P(
                [
                    'In this page, you can search for modules (a.k.a. communities, clusters) in rice co-expression networks, '
                    'which are significantly enriched in the genes implicated by your GWAS. '
                    'Likely functions of the modules are inferred by enrichment analysis against several ontologies and pathway databases. Click ',
                    dcc.Link(
                        ['here ', html.I(
                            id='demo-link',
                            className='fa-solid fa-up-right-from-square fa-2xs'
                        )],
                        href='https://github.com/bioinfodlsu/rice-pilaf/wiki/2.3-Co%E2%80%90expression-Network-Analysis',
                        target='_blank',
                        className='top-navbar-item'
                    ),
                    ' for user guide.'

                ]
            )
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
                'Enter their MSU accession IDs, separated by a semicolon (e.g., LOC_Os01g03680;LOC_Os01g03690;LOC_Os01g04110)',
                className='small text-muted'),

            dbc.Textarea(id='coexpression-addl-genes'),

            html.Br(),

            dbc.Label(['Select the co-expression network',
                       html.I(
                           className='bi bi-info-circle', id='coexpression-network-tooltip', n_clicks=0)]),

            html.Br(),

            dbc.RadioItems(
                id='coexpression-network',
                options=COEXPRESSION_NETWORKS_VALUE_LABEL,
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
            html.Br(),

            dbc.RadioItems(
                id='coexpression-clustering-algo',
                options=MODULE_DETECTION_ALGOS_VALUE_LABEL,
                value='clusterone',
                inline=True,
                className='ms-3 mt-1'
            ),

            coexpression_network_modal,
            html.Br(),

            dbc.Label(['Select the ',
                       html.Span('parameter for running the algorithm',
                                 id='coexpression-parameter-name'),
                       html.I(
                           className='bi bi-info-circle', id='coexpression-parameter-tooltip', n_clicks=0)],
                      className='mb-4'),

            # Should also be changed if parameter space is changed
            html.Div([dcc.Slider(id='coexpression-parameter-slider', step=None,
                                 marks={0: '1 (Loose Modules)', 30: '2', 60: '3',
                                        90: '4 (Dense Modules)'},
                                 value=30)],
                     id='coexpression-parameter-slider-container'),

            parameter_modal,
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
                        html.Hr(className='mt-3 mb-3'),

                        html.Br(),

                        html.Div(
                            id='coexpression-input',
                            className='analysis-intro p-3'
                        ),

                        html.Br(),

                        html.Div([
                            html.Div([
                                html.Span(id='coexpression-module-stats')
                            ], className='stats'),

                            html.Div(
                                id='coexpression-results-module-tabs-container',
                                children=[
                                    dbc.Label('Select an enriched module'),
                                    dcc.Dropdown(id='coexpression-modules'),
                                ],
                                className='pt-3 pb-2'
                            )
                        ], className='analysis-intro p-3')
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
                                    html.Span(id='coexpression-graph-stats')
                                ], className='mb-3 stats'),

                                html.P(
                                    'Click on the tabs below to see the ontology terms and pathways in which the module is enriched.',
                                    className='mb-4'),

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
                                                html.Span(
                                                    id='coexpression-table-stats')
                                            ], className='mb-3 stats'),
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
                                                        'placeholder_text': '🔎︎ Search Column'},
                                        page_action='native',
                                        page_size=15,
                                        cell_selectable=False
                                    )
                                ]),

                                html.Br(),
                                html.Br(),

                                html.Div([
                                    html.P(
                                        'The graph below shows the selected module. The connections indicate that the genes are co-expressed. The shaded nodes refer to the genes implicated by your GWAS/QTL, including those that you manually added.'),

                                    dbc.Label(
                                        'Select the graph display layout'),

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
                                        className='ms-3 mb-3',
                                    ),

                                    html.P(
                                        'Click "Reset Graph Display" to position the graph at the center and restore default zoom settings.')
                                ], className='analysis-intro p-3'),

                                html.Br(),

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
                                            'Reset Graph Display'],
                                            id='coexpression-reset-graph',
                                            n_clicks=0,
                                            color='light', size='sm',
                                            className='ms-3 table-button')
                                    ], style={'textAlign': 'right'})
                                ),
                            ]
                        ),

                        html.Div([
                            html.Div([
                                dcc.Loading([
                                    cyto.Cytoscape(
                                        id='coexpression-module-graph',
                                        className='mb-3',
                                        layout={'name': 'circle'},
                                        style={'width': '75%',
                                            'height': '100vh'},          # Should be here (otherwise, initial loading does not consume entire width and height)
                                        stylesheet=[
                                            {
                                                'selector': 'node',
                                                'style': {
                                                    'content': 'data(id)',
                                                    'height': '10px',
                                                    'width': '10px',
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
                                    ),
                                ])
                            ], className='w-75'),

                            html.Div(
                                dcc.Loading(
                                    html.Div(
                                        children='Click on a node to display information about the gene.',
                                        id='coexpression-module-graph-node-data',
                                        className='p-3'
                                    )
                                ),
                                className='w-25',
                                id='coexpression-module-graph-node-data-container'
                            ),
                        ], className='d-flex flex-row'),

                        # This is for adding padding at the bottom of the graph
                        html.Div(id='coexpression-extra-bottom-div',
                                 className='mb-4')
                    ]
                )
            ]
        )
    ], className='mt-2')
