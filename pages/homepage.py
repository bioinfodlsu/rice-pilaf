import dash
import dash_bootstrap_components as dbc
from dash import html

import pages.navigation.analysis_nav as analysis_nav
import pages.analysis_layout as analysis_layout

dash.register_page(__name__, path='/', name='RicePilaf', location='app-topbar')


# ======
# Modal
# ======

genomic_interval_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle('Genomic Intervals from GWAS/QTL')
    ),
    dbc.ModalBody([
        html.Span('Enter genomic intervals like so: '), html.Span(
            'Chr01:100000-200000', className='text-muted'),
        html.Br(),
        html.P([
            html.Span(
                'Multiple intervals should be separated by a semicolon like so: '),
            html.Span('Chr01:100000-200000;Chr02:300000-400000',
                      className='text-muted')
        ]),
        html.P(
            'These intervals are obtained from LD-based clumping of significant GWAS SNPs or from QTL mapping studies.'),
        html.P(
            'We also provide some sample genomic intervals, taken from the following GWAS/QTL analyses:'),
        html.Ul([
            html.Li([
                html.Div([
                    html.Span(
                        'Lee, J. S., Chebotarov, D., McNally, K. L., Pede, V., Setiyono, T. D., Raquid, R., Hyun, W. J., Leung, J. U., Kohli, A., & Mo, Y. (2021). Novel sources of pre-harvest sprouting resistance for Japanoica rice improvement. '),
                    html.I(
                        'Plants, 10'),
                    html.Span(
                        '(8), 1709. '),
                    html.A('https://doi.org/10.3390/plants10081709',
                           href='https://doi.org/10.3390/plants10081709',
                           target='_blank')],
                )
            ])
        ]),
        html.Ul([
            html.Li([
                html.Div([
                    html.Span(
                        'Tnani, H., Chebotarov, D., Thapa, R., Ignacio, J. C. I., Israel, W. K.,  Quilloy, F. A., Dixit, S., & Septiningsih, E. M., & Kretzschmar, T. (2021). Enriched-GWAS and transcriptome analysis to refine and characterize a major QTL for anaerobic germination tolerance in rice. '),
                    html.I(
                        'International Journal of Molecular Sciences, 22'),
                    html.Span(
                        '(9), 4445. '),
                    html.A('https://doi.org/10.3390/ijms22094445',
                           href='https://doi.org/10.3390/ijms22094445',
                           target='_blank')],
                )
            ])
        ])
    ])],
    id='genomic-interval-modal',
    is_open=False,
    size='xl',
    scrollable=True
)

# ======
# Input
# ======

submit_clear_buttons = dbc.Row([
    dbc.Col(dbc.Button('Proceed to Analyses Menu',
                       id='homepage-submit',
                       n_clicks=0,
                       className='home-button'),
            xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
    dbc.Col(dbc.Button('Reset All Analyses',
                       color='danger',
                       outline=True,
                       id='homepage-reset',
                       n_clicks=0,
                       className='home-button'),
            xs=4, sm=4, md=2, lg=2, xl=2, xxl=2,
            id='reset-analyses-container'),
    dbc.Col(dbc.Button('Clear Cache',
                       id='homepage-clear-cache',
                       color='danger',
                       outline=True,
                       n_clicks=0,
                       className='home-button'),
            xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
], className='pt-2')

genome_ref_input = dbc.Col([
    html.Div([
        html.H5('Enter your GWAS/QTL intervals',
                id='genomic-interval-hdr'),
        html.I(className='bi bi-info-circle',
               id='genomic-interval-tooltip',
               n_clicks=0)
    ], id='genomic-interval-container'),

    genomic_interval_modal,

    dbc.Alert(
        id='input-error',
        color='danger',
        style={'display': 'none'}
    ),
    dbc.Input(
        id='homepage-genomic-intervals',
        type='text',
        value='',
        debounce=True,
        n_submit=0
    ),

    html.Div([
        html.Span('Or select from these examples:', className='pe-3'),
        html.Span('Pre-Harvest Sprouting (Lee et al., 2021)',
                  id={'type': 'example-genomic-interval',
                      'description': 'pre-harvest'},
                  className='sample-genomic-interval',
                  n_clicks=0),
        html.Span(',', className='sample-genomic-interval'),
        html.Span('Anaerobic Germination (Tnani et al., 2021)',
                  id={'type': 'example-genomic-interval',
                      'description': 'anaerobic-germination'},
                  className='sample-genomic-interval ms-3',
                  n_clicks=0)],
             className='pt-3'),
    html.Br(),

    submit_clear_buttons
])

# ============
# Main Layout
# ============

layout = html.Div([
    dbc.Row(
        genome_ref_input,
        className='px-5 pt-4 pb-5',
        id='genome-ref-input-container'
    ),

    html.Br(),

    html.Div(
        id='about-the-app',
        children=[
            dbc.Row([
                dbc.Col([
                    html.H5('RicePilaf: A Post-GWAS/QTL Dashboard'),
                    html.P('RicePilaf is  a web app for post-GWAS/QTL analysis that performs a slew of novel bioinformatics analyses to cross GWAS results and QTL mapping with a host of publicly available rice databases. ', className='pt-3'),
                    html.P('It integrates (1) pan-genomic information from high-quality genome builds of multiple rice varieties, (2) co-expression information from genome-scale co-expression networks, (3) ontology and pathway information, regulatory information from rice transcription factor databases, (4) epigenomic information from multiple high-throughput epigenetic experiments, and (5) text-mining information extracted from scientific abstracts linking genes and traits.')
                ], className='col-sm-9'),

                dbc.Col([
                    html.Div(
                        html.Img(src='assets/images/rice1.png',
                                 className='img-about-the-app py-auto'),
                        className='text-center'
                    )
                ], className='col-sm-3 d-flex flex-wrap align-items-center')
            ], className='ps-5 pt-3 pb-4'),

            dbc.Row([
                dbc.Col([
                    html.Div(
                        html.Img(src='assets/images/table1.png',
                                 className='img-about-the-app py-auto'),
                        className='text-center'
                    )
                ], className='col-sm-3 d-flex flex-wrap align-items-center'),

                dbc.Col([
                    html.H5('Lift-Over'),
                    html.P('Nipponbare serves as the gold-standard reference genome sequence and genomic coordinate system. However, for GWAS/QTL analysis on populations that are not derived from or include in Nipponbare, by relying only on its genome and its annotation, we likely will miss genes and regulatory features linked to the phenotype of interest.', className='pt-3'),
                    html.P(
                        'RicePilaf can lift over the intervals in the Nipponbare reference coordinates to several other recently published genomes, representing major rice populations. Using the Rice Gene Index database, it retrieves the genes overlapping the lifted-over intervals and their orthologs. This pan-genomic view of gene sets may be useful, for example if the GWAS/QTL mapping is on an accession that is closer to a genome other than Nipponbare.')
                ], className='col-sm-9 pe-6 alt-row')
            ], className='gray-container ps-3 pt-5 pb-3')
        ]
    ),

    html.Div(
        id='homepage-results-container',
        style={'display': 'none'},
        children=[
            html.Div(
                id='post-gwas-analysis-container',
                children=[dbc.Row([
                    dbc.Col(
                        [html.H5('Select an analysis', id='post-gwas-hdr'),
                         analysis_nav.navbar()],
                        xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
                    dbc.Col(
                        children=analysis_layout.layout,
                        xs=7, sm=7, md=9, lg=9, xl=9, xxl=9,
                        id='page',
                    )
                ], className='ps-5 py-2')]
            )
        ]
    )
])
