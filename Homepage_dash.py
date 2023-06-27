import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

import callbacks.lift_over.callbacks
import callbacks.browse_loci.callbacks
import callbacks.coexpression.callbacks
import callbacks.tf_enrich.callbacks
import callbacks.homepage_dash.callbacks
import callbacks.homepage_dash.util

from flask import Flask

server = Flask(__name__, static_folder='static')
app = dash.Dash(__name__, use_pages=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                                      dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME],
                server=server,
                title='Rice Pilaf',
                update_title='Loading...')

welcome = dcc.Markdown(
    '''
    Welcome ! Rice Pilaf is short for Rice Post-GWAS Dashboard.
    Ok, we are not good at abbreviations, but like a good pilaf, this dashboard combines many ingredients.
    With this tool, you can do amazing things like ... (write me)
    '''
)

genomic_interval = callbacks.homepage_dash.util.example_genomic_intervals[
    'example-preharvest']


# ===================
# Top Navigation Bar
# ===================

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink('Home', href='/', active='exact',
                    className='top-navbar-item')),
        dbc.NavItem(dbc.NavLink(
                    'About', href='/about', active='exact', className='top-navbar-item'))
    ],
    id='top-navbar',
    brand=['Rice Pilaf'],
    brand_href='/',
    color='#4d987d',
    dark=True
)


# ====================
# Side Navigation Bar
# ====================

sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [
                html.Div(page['name'], className='ms-2'),
            ],
            href=page['path'],
            active='exact',
        )
        for page in dash.page_registry.values()
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
                                dbc.Col(dbc.Button('Clear All Display',
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
        value=genomic_interval,
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

app.layout = dbc.Container(
    [
        dbc.Row(navbar),

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
                        dbc.Col([dash.page_container],
                            xs=7, sm=7, md=9, lg=9, xl=9, xxl=9,
                            id='page')
                    ], className='ps-5 py-2')]
                 ),

        # Session storage
        dcc.Store(
            id='homepage-is-submitted',
            storage_type='session'
        ),

        dcc.Store(
            id='lift-over-is-submitted',
            storage_type='session'
        ),

        dcc.Store(
            id='lift-over-active-tab',
            storage_type='session'
        ),

        dcc.Store(
            id='homepage-genomic-intervals-saved-input',
            storage_type='session'
        ),

        dcc.Store(
            id='lift-over-other-refs-saved-input',
            storage_type='session'
        ),

        dcc.Store(
            id='lift-over-other-refs-submitted-input',
            storage_type='session'
        ),

        dcc.Store(
            id='lift-over-active-filter',
            storage_type='session'
        ),

        dcc.Store(
            id='lift-over-nb-table',
            storage_type='session'
        ),

        dcc.Store(
            id='lift_over_nb_entire_table',
            storage_type='session'
        ),

        dcc.Store(
            id='igv-selected-genomic-intervals-saved-input',
            storage_type='session'
        ),

        dcc.Store(
            id='igv-active-filter',
            storage_type='session'
        ),

        dcc.Store(
            id='coexpression-clustering-algo-saved-input',
            storage_type='session'
        ),

        dcc.Store(
            id='coexpression-submitted-clustering-algo',
            storage_type='session'
        ),

        dcc.Store(
            id='coexpression-submitted-parameter-module',
            storage_type='session'
        ),

        dcc.Store(
            id='coexpression-parameter-module-saved-input',
            storage_type='session'
        ),

        dcc.Store(
            id='coexpression-is-submitted',
            storage_type='session'
        ),

        dcc.Store(
            id='tfbs-saved-input',
            storage_type='session'
        ),

        dcc.Store(
            id='tfbs-submitted-input',
            storage_type='session'
        ),

        dcc.Store(
            id='tfbs-is-submitted',
            storage_type='session'
        )

    ],
    fluid=True
)

callbacks.lift_over.callbacks.init_callback(app)
callbacks.browse_loci.callbacks.init_callback(app)
callbacks.coexpression.callbacks.init_callback(app)
callbacks.tf_enrich.callbacks.init_callback(app)
callbacks.homepage_dash.callbacks.init_callback(app)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port='8050', debug=True)
