import dash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dash_table, dcc, html

dash.register_page(__name__, name='Co-expression Network Analysis')


layout = dbc.Row(dbc.Col(id='coexpression-container', children=[
    html.P(id='coexpression-genomic-intervals-input'),

    dbc.Label(['Select a module detection algorithm ',
               html.I(
                   className='bi bi-info-circle mx-2',
                   id='coexpression-clustering-algo-tooltip',
                   n_clicks=0
               )]),

    dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle('Module Detection Algorithms')
        ),
        dbc.ModalBody([
            html.P(
                'The available algorithms allow for overlapping modules (that is, genes may belong to more than one module):'),
            html.Ul(
                html.Li(
                    [html.B('COACH'),
                     html.Span(
                         ' detects highly connected gene subnetworks and expands them by including closely associated genes'),
                     html.Br(),
                     html.B('Reference: '),
                     html.Span(
                         'Wu, M., Li, X., Kwoh, C. K., & Ng, S. K. (2009). A core-attachment based method to detect protein complexes in PPI networks. '),
                     html.I('BMC Bioinformatics, 10'),
                     html.Span('(169). '),
                     html.A('https://doi.org/10.1186/1471-2105-10-169',
                            href='https://doi.org/10.1186/1471-2105-10-169',
                            target='_blank')]
                )
            )
        ])],
        id='coexpression-clustering-algo-modal',
        is_open=False,
        size='xl',
    ),

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
               html.Span('parameter', id='coexpression-parameter-name'),
               html.I(
                   className='bi bi-info-circle mx-2', id='coexpression-parameter-tooltip')],
              className='mb-4'),

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

    html.Div(id='coexpression-results-container',
             style={'display': 'none'},
             children=[
                 dcc.Loading(id='coexpression-loading',
                             children=[
                                 dbc.Label('Select an enriched module'),

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

                                 html.P(
                                     html.Div([
                                         dbc.Button([html.I(
                                             className='bi bi-download me-2'),
                                             'Export to CSV'],
                                             id='lift-over-export-table',
                                             color='light', size='sm', className='table-button'),
                                         dbc.Button([html.I(
                                             className='bi bi-arrow-clockwise me-2'),
                                             'Reset Table'],
                                             id='lift-over-reset-table',
                                             color='light', size='sm', className='ms-3 table-button')
                                     ], style={'textAlign': 'right'})
                                 ),

                                 dash_table.DataTable(
                                     id='coexpression-pathways',
                                     persistence=True,
                                     persistence_type='memory',
                                     style_cell={
                                         'whiteSpace': 'pre-line',
                                         'font-family': 'sans-serif'
                                     },
                                     markdown_options={'html': True},
                                     sort_action='native',
                                     filter_action='native',
                                     filter_options={'case': 'insensitive',
                                                     'placeholder_text': 'Search column'},
                                     page_action='native',
                                     page_size=15
                                 ),

                                 html.Br(),

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
                             ], parent_style={'height': '5em'})
             ])
]
))
