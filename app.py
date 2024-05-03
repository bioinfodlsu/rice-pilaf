import logging
import sqlite3
from logging.config import dictConfig

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from flask import Flask

import callbacks.coexpression.callbacks
import callbacks.epigenome.callbacks
import callbacks.homepage.callbacks
import callbacks.homepage.util
import callbacks.lift_over.callbacks
import callbacks.summary.callbacks
import callbacks.template.callbacks
import callbacks.text_mining.callbacks
import callbacks.tf_enrich.callbacks
import pages.navigation.main_nav as main_nav
from callbacks.config import *
from callbacks.constants import *
from callbacks.file_util import *
from generate_config import *

# Create .env file if it does not exist
if not path_exists(".env"):
    generate_config(debug=True, deployed=False, logging=False)

make_dir("logs")

if is_logging_mode():
    # Suppress writing GET requests to the log
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    GB_TO_BYTES = 1e9


    class UTCFormatter(logging.Formatter):
        converter = time.gmtime


    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "()": UTCFormatter,
                    "format": "%(asctime)s%(msecs)03d|%(message)s",
                    "datefmt": "%Y%m%d%H%M%S",
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "backupCount": 1,
                    "maxBytes": get_max_logging_gb() * GB_TO_BYTES,
                    "filename": f"logs/usage.log",
                    "formatter": "default",
                },
            },
            "root": {"level": "DEBUG", "handlers": ["file"]},
        }
    )

server = Flask(__name__, static_folder="static")
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
    ],
    server=server,
    title="RicePilaf",
    update_title="Loading...",
    meta_tags=[{"name": "viewport", "content": "width=1024"}],
)


# ============
# Main Layout
# ============


app.layout = lambda: dbc.Container(
    [
        dbc.Row(
            html.Div(
                children=[
                    html.P(
                        [
                            "This is a demo version. Click ",
                            dcc.Link(
                                [
                                    "here ",
                                    html.I(
                                        id="demo-link",
                                        className="fa-solid fa-up-right-from-square fa-2xs",
                                    ),
                                ],
                                href="https://github.com/bioinfodlsu/rice-pilaf/wiki/1.-Installation",
                                target="_blank",
                                className="top-navbar-item",
                            ),
                            " to install.",
                        ],
                        className="my-auto",
                    )
                ],
                className="banner d-flex justify-content-center py-1 text-white",
                id="demo-banner",
            ),
            style=show_if_deployed(),
        ),
        dbc.Row(main_nav.navbar()),
        dash.page_container,
        dbc.Row(
            [
                dbc.Col(
                    dcc.Link(
                        html.Img(src="assets/bioinfo_lab_logo.png", height="45px"),
                        href="https://bioinfodlsu.com/",
                        target="_blank",
                    ),
                    className="col-auto text-center",
                ),
                dbc.Col(
                    [
                        html.Span(f"RicePilaf {get_release_version()}"),
                        html.Span("© 2023", className="ps-3"),
                        html.Span("|", className="px-3"),
                        html.Span(
                            "Bioinformatics Lab, De La Salle University (DLSU), Manila, Philippines"
                        ),
                        html.Br(),
                        html.Span(
                            "Rural Development Administration (RDA), South Korea – International Rice Research Institute (IRRI) Cooperative Project"
                        ),
                    ],
                    className="col-sm-11",
                ),
            ],
            className="ps-5 pb-4 pt-4 text-white",
            id="footer",
        ),
        # Session storage
        # Insert your session variables inside the session-container div
        html.Div(
            id="session-container",
            children=[
                # =========
                # Template
                # =========
                dcc.Store(id="template-is-submitted", storage_type="session"),
                dcc.Store(id="template-submitted-addl-genes", storage_type="session"),
                dcc.Store(
                    id="template-submitted-radio-buttons", storage_type="session"
                ),
                dcc.Store(
                    id="template-submitted-checkbox-buttons", storage_type="session"
                ),
                dcc.Store(
                    id="template-submitted-parameter-slider", storage_type="session"
                ),
                # =========
                # Homepage
                # =========
                dcc.Store(id="homepage-is-submitted", storage_type="session"),
                dcc.Store(
                    id="homepage-submitted-genomic-intervals", storage_type="session"
                ),
                dcc.Store(id="current-analysis-page-nav", storage_type="session"),
                dcc.Store(id="homepage-is-resetted", storage_type="session"),
                # ==========
                # Lift-over
                # ==========
                dcc.Store(id="lift-over-is-submitted", storage_type="session"),
                dcc.Store(id="lift-over-active-tab", storage_type="session"),
                dcc.Store(id="lift-over-submitted-other-refs", storage_type="session"),
                dcc.Store(id="lift-over-active-filter", storage_type="session"),
                # ============
                # IGV Browser
                # ============
                dcc.Store(
                    id="epigenome-submitted-genomic-intervals", storage_type="session"
                ),
                dcc.Store(id="epigenome-submitted-tissue", storage_type="session"),
                dcc.Store(id="epigenome-submitted-tracks", storage_type="session"),
                dcc.Store(id="epigenome-is-submitted", storage_type="session"),
                # ==============
                # Co-expression
                # ==============
                dcc.Store(
                    id="coexpression-submitted-parameter-slider", storage_type="session"
                ),
                dcc.Store(id="coexpression-submitted-module", storage_type="session"),
                dcc.Store(id="coexpression-pathway-active-tab", storage_type="session"),
                dcc.Store(
                    id="coexpression-graph-active-layout", storage_type="session"
                ),
                dcc.Store(
                    id="coexpression-submitted-addl-genes", storage_type="session"
                ),
                dcc.Store(id="coexpression-valid-addl-genes", storage_type="session"),
                dcc.Store(id="coexpression-combined-genes", storage_type="session"),
                dcc.Store(id="coexpression-submitted-network", storage_type="session"),
                dcc.Store(
                    id="coexpression-submitted-clustering-algo", storage_type="session"
                ),
                dcc.Store(id="coexpression-is-submitted", storage_type="session"),
                # ==============================
                # Regulatory Feature Enrichment
                # ==============================
                dcc.Store(id="tfbs-is-submitted", storage_type="session"),
                dcc.Store(id="tfbs-submitted-addl-genes", storage_type="session"),
                dcc.Store(id="tfbs-valid-addl-genes", storage_type="session"),
                dcc.Store(id="tfbs-combined-genes", storage_type="session"),
                dcc.Store(
                    id="tfbs-submitted-prediction-technique", storage_type="session"
                ),
                dcc.Store(id="tfbs-submitted-set", storage_type="session"),
                # ============
                # Text Mining
                # ============
                dcc.Store(id="text-mining-submitted-query", storage_type="session"),
                dcc.Store(id="text-mining-is-submitted", storage_type="session"),
                dcc.Store(id="text-mining-filter-query", storage_type="session"),
                dcc.Store(id="text-mining-submitted-filter", storage_type="session"),
                # ========
                # Summary
                # ========
                dcc.Store(id="summary-is-submitted", storage_type="session"),
            ],
        ),
    ],
    fluid=True,
)

callbacks.homepage.callbacks.init_callback(app)

# callbacks.template.callbacks.init_callback(app)

callbacks.lift_over.callbacks.init_callback(app)
callbacks.epigenome.callbacks.init_callback(app)
callbacks.coexpression.callbacks.init_callback(app)
callbacks.tf_enrich.callbacks.init_callback(app)
callbacks.text_mining.callbacks.init_callback(app)
callbacks.summary.callbacks.init_callback(app)

# Create database table

make_dir(Constants.TEMP)

try:
    connection = sqlite3.connect(Constants.FILE_STATUS_DB)
    cursor = connection.cursor()

    query = f"CREATE TABLE IF NOT EXISTS {Constants.FILE_STATUS_TABLE} (name TEXT, UNIQUE(name));"

    cursor.execute(query)
    connection.commit()

    cursor.close()
    connection.close()
except sqlite3.Error as error:
    pass

if __name__ == "__main__":
    if is_deployed_version():
        app.run_server(port="8050", debug=is_debug_mode())
    else:
        app.run_server(host="0.0.0.0", port="8050", debug=is_debug_mode())
