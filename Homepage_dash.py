
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

import callbacks.lift_over.callbacks
import callbacks.browse_loci.callbacks
import callbacks.coexpression.callbacks
import callbacks.tf_enrich.callbacks

from flask import Flask

server = Flask(__name__, static_folder='static')
app = dash.Dash(__name__, use_pages=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                server=server)

welcome = dcc.Markdown(
    """
    Welcome ! Rice Pilaf is short for Rice Post-GWAS Dashboard.
    Ok, we are not good at abbreviations, but like a good pilaf, this dashboard combines many ingredients.
    With this tool, you can do amazing things like ... (write me)
    """
)

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
    className="bg-light"
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("rice-pilaf",
                                 style={'fontSize': 50, 'textAlign': 'center'})),
                welcome
            ]
        ),

        html.Hr(),

        dbc.Row(
            [
                dbc.Col([sidebar], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
                dbc.Col([dash.page_container], xs=8,
                        sm=8, md=10, lg=10, xl=10, xxl=10)
            ]
        ),

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
        )
    ],
    fluid=True

)

callbacks.lift_over.callbacks.init_callback(app)
callbacks.browse_loci.callbacks.init_callback(app)
callbacks.coexpression.callbacks.init_callback(app)
callbacks.tf_enrich.callbacks.init_callback(app)

if __name__ == '__main__':
    app.run_server(debug=True)
