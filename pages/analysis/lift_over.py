import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from callbacks.constants import Constants
from callbacks.lift_over.util import *

layout = html.Div(
    id={"type": "analysis-layout", "label": Constants.LABEL_LIFT_OVER},
    hidden=True,
    children=[
        html.Div(
            [
                html.P(
                    [
                        Constants.INTRO_LIFT_OVER,
                        " Click ",
                        dcc.Link(
                            [
                                "here ",
                                html.I(
                                    id="demo-link",
                                    className="fa-solid fa-up-right-from-square fa-2xs",
                                ),
                            ],
                            href="https://github.com/bioinfodlsu/rice-pilaf/wiki/2.1-Gene-List-and-Lift%E2%80%90over",
                            target="_blank",
                            className="top-navbar-item",
                        ),
                        " for the user guide.",
                    ]
                )
            ],
            className="analysis-intro p-3",
        ),
        html.Br(),
        html.Div(
            [
                html.I(className="bi bi-chevron-bar-right me-2 non-clickable"),
                html.Span(id="lift-over-genomic-intervals-input"),
            ],
            className="analysis-intro p-3",
        ),
        html.Br(),
        html.Div(
            [
                dbc.Label(
                    "Select genome(s) for lift-over (ignore if lift-over is not needed)",
                    className="mb-2",
                ),
                dcc.Dropdown(
                    construct_options_other_ref_genomes(),
                    id="lift-over-other-refs",
                    multi=True,
                    className="dash-bootstrap",
                ),
                html.Br(),
                dbc.Button(
                    "Show gene list",
                    id="lift-over-submit",
                    className="page-button",
                    n_clicks=0,
                ),
            ],
            className="analysis-intro p-3",
        ),
        html.Br(),
        html.Div(
            id="lift-over-results-container",
            style={"display": "none"},
            children=[
                html.Hr(className="mt-3 mb-4"),
                html.P(id="lift-over-results-intro"),
                dcc.Loading([html.Ul(id="lift-over-results-statistics"), html.Br()]),
                dbc.Tabs(
                    id="lift-over-results-tabs", active_tab="tab-0", className="mt-3"
                ),
                html.Br(),
                dbc.Label(id="lift-over-results-gene-intro"),
                dbc.Checklist(
                    id="lift-over-overlap-table-filter", inline=True, className="ms-3"
                ),
                html.Br(),
                dcc.Loading(
                    [
                        html.P(
                            html.Div(
                                [
                                    dbc.Button(
                                        [
                                            html.I(className="bi bi-download me-2"),
                                            "Export to CSV",
                                        ],
                                        id="lift-over-export-table",
                                        n_clicks=0,
                                        color="light",
                                        size="sm",
                                        className="table-button",
                                    ),
                                    dcc.Download(id="lift-over-download-df-to-csv"),
                                    dbc.Button(
                                        [
                                            html.I(
                                                className="bi bi-arrow-clockwise me-2"
                                            ),
                                            "Reset Table",
                                        ],
                                        id="lift-over-reset-table",
                                        color="light",
                                        size="sm",
                                        className="ms-3 table-button",
                                    ),
                                ],
                                style={"textAlign": "right"},
                            )
                        ),
                        dash_table.DataTable(
                            id="lift-over-results-table",
                            style_cell={"whiteSpace": "pre-line", "height": "auto"},
                            markdown_options={"html": True},
                            sort_action="native",
                            filter_action="native",
                            filter_options={
                                "case": "insensitive",
                                "placeholder_text": "🔎︎ Search Column",
                            },
                            page_action="native",
                            page_size=15,
                            cell_selectable=False,
                            style_table={"overflowX": "auto"},
                        ),
                    ]
                ),
            ],
        ),
    ],
    className="mt-2 mb-4",
)
