import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

import pages.analysis.lift_over as lift_over
import pages.analysis.co_expr as co_expr
import pages.analysis.tf_enrich as tf_enrich
import pages.analysis.browse_loci as browse_loci
import pages.navigation.analysis_nav as analysis_nav

dash.register_page(__name__, path='/', name='Home')


# ======
# Modal
# ======

genomic_interval_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle('Genomic Intervals from GWAS')
    ),
    dbc.ModalBody([
        html.P('WRITE ME'),
        html.P(
            'We also provide some example genomic intervals, taken from the following papers:'),
        html.Ul([
            html.Li([
                html.Div([
                    html.Span(
                        'Coscia, M., Rossetti, G., Giannotti, F., & Pedreschi, D. (2012). DEMON: A local-first discovery method for overlapping communities. In '),
                    html.I(
                        'KDD\'12: Proceedings of the 18th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining '),
                    html.Span(
                        '(pp. 615–623). Association for Computing Machinery. '),
                    html.A('https://doi.org/10.1145/2339530.2339630',
                           href='https://doi.org/10.1145/2339530.2339630',
                           target='_blank')],
                )
            ])
        ])
    ])],
    id='genomic-interval-modal',
    is_open=False,
    size='xl'
)

# ======
# Input
# ======

submit_clear_buttons = dbc.Row([dbc.Col(dbc.Button('Start Analysis',
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
                                        style={'marginLeft': '3em'}),
                                dbc.Col(dbc.Button('Clear Cache',
                                                   id='homepage-clear-cache',
                                                   color='danger',
                                                   outline=True,
                                                   n_clicks=0,
                                                   className='home-button'),
                                        xs=4, sm=4, md=2, lg=2, xl=2, xxl=2,
                                        style={'marginLeft': '3em'}),
                                ], className='pt-2')

genome_ref_input = dbc.Col([
    html.Div([
        html.H5('Enter genomic intervals from GWAS',
                id='genomic-interval-hdr'),
        html.I(className='bi bi-info-circle',
               id='genomic-interval-tooltip',
               n_clicks=0)
    ], id='genomic-interval-container'),

    genomic_interval_modal,

    dbc.Alert(
        id='input-error',
        children='',
        color='danger',
        style={'display': 'none'}
    ),
    dbc.Input(
        id='homepage-genomic-intervals',
        type='text',
        value='',
        persistence=True,
        persistence_type='memory'
    ),

    html.Div([html.Span('Or select from these examples:', className='pe-3'),
              html.Span('Pre-Harvest Sprouting (Lee et al., 2021)',
                        id={'type': 'example-genomic-interval',
                            'description': 'pre-harvest'},
                        className='sample-genomic-interval pe-3'),
              html.Span('Anaerobic Germination Tolerance (Tnani et al., 2021)',
                        id={'type': 'example-genomic-interval',
                            'description': 'anaerobic-germination'},
                        className='sample-genomic-interval')],
             className='pt-3'),
    html.Br(),

    submit_clear_buttons
])

# ============
# Main Layout
# ============

layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.Row(
            genome_ref_input,
            className='px-5 pt-4 pb-5',
            id='genome-ref-input-container'
        ),

        html.Br(),

        html.Div(id='post-gwas-analysis-container', hidden=True,
                 children=[
                    dbc.Row([
                        dbc.Col([html.H5('Post-GWAS Analysis', id='post-gwas-hdr'),
                                analysis_nav.navbar],
                            xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
                        dbc.Col(children=[lift_over.layout, co_expr.layout, tf_enrich.layout, browse_loci.layout],
                            xs=7, sm=7, md=9, lg=9, xl=9, xxl=9,
                            id='page', style={'display': 'none'})
                    ], className='ps-5 py-2')]
                 ),

        html.Div(id='page-content', children=[])
    ],
    # fluid=True
)
