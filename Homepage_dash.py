
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

import callbacks.lift_over.callbacks
import callbacks.browse_loci.callbacks
import callbacks.coexpression.callbacks
import callbacks.tf_enrich.callbacks
import callbacks.homepage_dash.callbacks

from flask import Flask

server = Flask(__name__, static_folder='static')
app = dash.Dash(__name__, use_pages=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                                      dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME],
                server=server,
                title='Rice Pilaf',
                update_title='Loading...')

welcome = dcc.Markdown(
    """
    Welcome ! Rice Pilaf is short for Rice Post-GWAS Dashboard.
    Ok, we are not good at abbreviations, but like a good pilaf, this dashboard combines many ingredients.
    With this tool, you can do amazing things like ... (write me)
    """
)

other_ref_genomes = ['N22', 'MH63', 'Azu', 'ARC', 'IR64', 'CMeo']
genomic_interval = 'Chr01:1523625-1770814;Chr04:4662701-4670717'


# ===================
# Top Navigation Bar
# ===================

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink('Home', href='/', active='exact')),
        dbc.NavItem(dbc.NavLink(
                    'About', href='/about', active='exact')),
        dbc.NavItem(dbc.NavLink(
                    'People', href='/people', active='exact'))
    ],
    id='navbar',
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
                html.Div(page["name"], className="ms-2"),
            ],
            href=page["path"],
            active="exact",
        )
        for page in dash.page_registry.values()
    ],
    vertical=True,
    pills=True,
    className="bg-light",
    id='homepage-dash-nav'
)


# ======
# Input
# ======

submit_clear_buttons = [dbc.Button('Submit',
                                   id='lift-over-submit',
                                   n_clicks=0,
                                   className='home-button'),
                        dbc.Button('Clear All Display',
                                   color='danger',
                                   outline=True,
                                   id='lift-over-reset',
                                   n_clicks=0,
                                   className='home-button')]

genome_ref_input = dbc.Col([
    html.H5('Genomic interval(s) from GWAS'),
    dbc.Alert(
        id='input-error',
        children='',
        color='danger',
        style={'display': 'none'}
    ),
    dbc.Input(
        id='lift-over-genomic-intervals',
        type='text',
        value=genomic_interval,
        persistence=True,
        persistence_type='memory'
    ),

    html.Br(),

    dbc.Label(
        'Select a genome to search for homologous regions'),
    dcc.Dropdown(
        other_ref_genomes,
        id='lift-over-other-refs',
        multi=False,
        persistence=True,
        persistence_type='memory',
        className='dash-bootstrap'
    ),

    html.Br(),

    html.Div(submit_clear_buttons)
])


# ============
# Main Layout
# ============

app.layout = dbc.Container(
    [
        dbc.Row(navbar),
        html.Br(),

        dbc.Row(
            genome_ref_input,
            className='px-5'
        ),

        html.Br(),

        html.Hr(),

        dbc.Row([
            dbc.Col([sidebar], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
            dbc.Col([dash.page_container], xs=8,
                    sm=8, md=10, lg=10, xl=10, xxl=10)
        ], className='p-3'),

        # Session storage
        dcc.Store(
            id='lift-over-is-submitted',
            storage_type='session',
        ),

        dcc.Store(
            id='lift-over-active-tab',
            storage_type='session'
        ),

        dcc.Store(
            id='lift-over-genomic-intervals-saved-input',
            storage_type='session',
        ),

        dcc.Store(
            id='lift-over-other-refs-saved-input',
            storage_type='session',
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
            id='coexpression-parameter-module-saved-input',
            storage_type='session'
        )
    ],
    fluid=True,
)

callbacks.lift_over.callbacks.init_callback(app)
callbacks.browse_loci.callbacks.init_callback(app)
callbacks.coexpression.callbacks.init_callback(app)
callbacks.tf_enrich.callbacks.init_callback(app)
callbacks.homepage_dash.callbacks.init_callback(app)

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port="8050", debug=True)
