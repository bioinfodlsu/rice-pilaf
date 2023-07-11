import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

import pages.navigation.main_nav as main_nav

import callbacks.homepage.callbacks
import callbacks.homepage.util
import callbacks.lift_over.callbacks
import callbacks.browse_loci.callbacks
import callbacks.coexpression.callbacks
import callbacks.tf_enrich.callbacks


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


# ============
# Main Layout
# ============

app.layout = dbc.Container(
    [
        dbc.Row(main_nav.navbar),

        dash.page_container,


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
            id='igv-selected-genomic-intervals-submitted-input',
            storage_type='session'
        ),

        dcc.Store(
            id='igv-selected-tracks-submitted-input',
            storage_type='session'
        ),

        dcc.Store(
            id='igv-is-submitted',
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

callbacks.homepage.callbacks.init_callback(app)

callbacks.lift_over.callbacks.init_callback(app)
callbacks.browse_loci.callbacks.init_callback(app)
callbacks.coexpression.callbacks.init_callback(app)
callbacks.tf_enrich.callbacks.init_callback(app)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port='8050', debug=True)
