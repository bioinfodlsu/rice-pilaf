import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import sqlite3

import pages.navigation.main_nav as main_nav

import callbacks.homepage.callbacks
import callbacks.homepage.util
import callbacks.lift_over.callbacks
import callbacks.browse_loci.callbacks
import callbacks.coexpression.callbacks
import callbacks.tf_enrich.callbacks
import callbacks.text_mining.callbacks

from callbacks.branch import *
from callbacks.constants import *
from callbacks.file_util import *

from flask import Flask

server = Flask(__name__, static_folder='static')
app = dash.Dash(__name__, use_pages=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                                      dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME],
                server=server,
                title='RicePilaf',
                update_title='Loading...',
                meta_tags=[{'name': 'viewport',
                            'content': 'width=1024'}])

welcome = dcc.Markdown(
    '''
    Welcome ! Rice Pilaf is short for Rice Post-GWAS/QTL Dashboard.
    Ok, we are not good at abbreviations, but like a good pilaf, this dashboard combines many ingredients.
    With this tool, you can do amazing things like ... (write me)
    '''
)


# ============
# Main Layout
# ============


app.layout = lambda: dbc.Container([
    dbc.Row(
        html.Div(
            children=[
                html.P([
                    'This is a demo version. Click ',
                    dcc.Link(
                        ['here ', html.I(
                            id='demo-link',
                            className='fa-solid fa-up-right-from-square fa-2xs'
                        )],
                        href='https://github.com/bioinfodlsu/rice-pilaf/wiki/1.-Installation',
                        target='_blank',
                        className='top-navbar-item'
                    ),
                    ' to install.'], className='my-auto'
                )
            ],
            className='banner d-flex justify-content-center py-1 text-white',
            id='demo-banner'
        ),
        style=show_if_in_demo_branch()
    ),

    dbc.Row(main_nav.navbar()),

    dash.page_container,

    # Session storage
    html.Div(
        id='session-container',
        children=[
            # =========
            # Homepage
            # =========
            dcc.Store(
                id='homepage-is-submitted',
                storage_type='session'
            ),

            dcc.Store(
                id='homepage-saved-genomic-intervals',
                storage_type='session'
            ),

            dcc.Store(
                id='homepage-submitted-genomic-intervals',
                storage_type='session'
            ),

            dcc.Store(
                id='current-analysis-page-nav',
                storage_type='session'
            ),



            # ==========
            # Lift-over
            # ==========
            dcc.Store(
                id='lift-over-is-submitted',
                storage_type='session'
            ),

            dcc.Store(
                id='lift-over-active-tab',
                storage_type='session'
            ),

            dcc.Store(
                id='lift-over-saved-other-refs',
                storage_type='session'
            ),

            dcc.Store(
                id='lift-over-submitted-other-refs',
                storage_type='session'
            ),

            dcc.Store(
                id='lift-over-active-filter',
                storage_type='session'
            ),

            # ============
            # IGV Browser
            # ============
            dcc.Store(
                id='igv-saved-genomic-intervals',
                storage_type='session'
            ),

            dcc.Store(
                id='igv-submitted-genomic-intervals',
                storage_type='session'
            ),

            dcc.Store(
                id='igv-saved-tracks',
                storage_type='session'
            ),

            dcc.Store(
                id='igv-submitted-tracks',
                storage_type='session'
            ),

            dcc.Store(
                id='igv-is-submitted',
                storage_type='session'
            ),

            # ==============
            # Co-expression
            # ==============
            dcc.Store(
                id='coexpression-submitted-parameter-slider',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-saved-parameter-slider',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-submitted-module',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-pathway-active-tab',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-submitted-layout',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-saved-addl-genes',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-submitted-addl-genes',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-combined-genes',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-saved-network',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-submitted-network',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-saved-clustering-algo',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-submitted-clustering-algo',
                storage_type='session'
            ),

            dcc.Store(
                id='coexpression-is-submitted',
                storage_type='session'
            ),

            # ==============================
            # Regulatory Feature Enrichment
            # ==============================

            dcc.Store(
                id='tfbs-is-submitted',
                storage_type='session'
            ),

            dcc.Store(
                id='tfbs-saved-addl-genes',
                storage_type='session'
            ),

            dcc.Store(
                id='tfbs-submitted-addl-genes',
                storage_type='session'
            ),

            dcc.Store(
                id='tfbs-saved-prediction-technique',
                storage_type='session'
            ),

            dcc.Store(
                id='tfbs-submitted-prediction-technique',
                storage_type='session'
            ),

            dcc.Store(
                id='tfbs-saved-set',
                storage_type='session'
            ),

            dcc.Store(
                id='tfbs-submitted-set',
                storage_type='session'
            ),

            # ============
            # Text Mining
            # ============

            dcc.Store(
                id='text-mining-saved-query',
                storage_type='session'
            ),

            dcc.Store(
                id='text-mining-submitted-query',
                storage_type='session'
            ),

            dcc.Store(
                id='text-mining-is-submitted',
                storage_type='session'
            )
        ])
], fluid=True, className='pb-4')

callbacks.homepage.callbacks.init_callback(app)

callbacks.lift_over.callbacks.init_callback(app)
callbacks.browse_loci.callbacks.init_callback(app)
callbacks.coexpression.callbacks.init_callback(app)
callbacks.tf_enrich.callbacks.init_callback(app)
callbacks.text_mining.callbacks.init_callback(app)

# Create database table

make_dir(Constants.TEMP)

try:
    connection = sqlite3.connect(Constants.FILE_STATUS_DB)
    cursor = connection.cursor()

    query = f'CREATE TABLE IF NOT EXISTS {Constants.FILE_STATUS_TABLE} (name TEXT, UNIQUE(name));'

    cursor.execute(query)
    connection.commit()

    cursor.close()
    connection.close()
except sqlite3.Error as error:
    pass

if __name__ == '__main__':
    app.run_server(port='8050', debug=True)
