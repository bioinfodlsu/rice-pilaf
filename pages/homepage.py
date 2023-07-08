import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

import callbacks.homepage.util
from pages import lift_over, co_expr, tf_enrich, browse_loci

dash.register_page(__name__, path='/', name='Home')


genomic_interval = callbacks.homepage.util.example_genomic_intervals[
    'example-preharvest']


# ====================
# Side Navigation Bar
# ====================

sidebar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink(
                    'Lift-Over', id='lift-over-link', className='ms-2', active='exact')),
        dbc.NavItem(dbc.NavLink(
            'Co-Expression Network Analysis', id='coexpression-link', className='ms-2', active='exact')),
        dbc.NavItem(dbc.NavLink(
            'Regulatory Feature Enrichment', id='tf-enrichment-link', className='ms-2', active='exact')),
        dbc.NavItem(dbc.NavLink(
            'Browse Loci', id='igv-link', className='ms-2', active='exact'))
    ],
    vertical=True,
    pills=True,
    className='bg-light',
    id='homepage-dash-nav'
)


# ======
# Input
# ======

submit_clear_buttons = dbc.Row([dbc.Col(dbc.Button('Start Post-GWAS Analysis',
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
    html.H5('Enter genomic intervals from GWAS', id='genomic-interval-hdr'),
    dbc.Alert(
        id='input-error',
        children='',
        color='danger',
        style={'display': 'none'}
    ),
    dbc.Input(
        id='homepage-genomic-intervals',
        type='text',
        value='',  # genomic_interval,
        persistence=True,
        persistence_type='memory'
    ),

    html.Div([html.Span('Or select from these examples: ', className='pe-2'),
              html.Span('Pre-Harvest Sprouting (Lee et al., 2021)', id='example-preharvest', className='sample-genomic-interval')],
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
                                sidebar],
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
