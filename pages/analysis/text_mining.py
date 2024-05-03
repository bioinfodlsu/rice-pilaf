import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from callbacks.constants import Constants

layout = html.Div(
    id={"type": "analysis-layout", "label": Constants.LABEL_TEXT_MINING},
    hidden=True,
    children=[
        html.Div(
            [
                html.P(
                    [
                        Constants.INTRO_TEXT_MINING,
                        " Click ",
                        dcc.Link(
                            [
                                "here ",
                                html.I(
                                    id="demo-link",
                                    className="fa-solid fa-up-right-from-square fa-2xs",
                                ),
                            ],
                            href="https://github.com/bioinfodlsu/rice-pilaf/wiki/2.2-Gene-retrieval-by-text-mining",
                            target="_blank",
                            className="top-navbar-item",
                        ),
                        " for the user guide.",
                    ]
                ),
            ],
            className="analysis-intro p-3",
        ),
        html.Br(),
        html.Div(
            [
                html.I(className="bi bi-chevron-bar-right me-2 non-clickable"),
                html.Span(id="text-mining-genomic-intervals-input"),
            ],
            className="analysis-intro p-3",
        ),
        html.Br(),
        html.Div(
            [
                dbc.Label("Enter your query trait/phenotype", className="mb-2"),
                dbc.Alert(
                    id="text-mining-input-error",
                    color="danger",
                    style={"display": "none"},
                ),
                dbc.Input(
                    id="text-mining-query",
                    type="text",
                    value="",
                    debounce=True,
                    n_submit=0,
                ),
                html.Div(
                    [
                        html.Span("Examples:", className="pe-3"),
                        html.Span(
                            "pre-harvest sprouting",
                            id={
                                "type": "example-text-mining",
                                "description": "pre-harvest sprouting",
                            },
                            className="sample-genomic-interval",
                            n_clicks=0,
                        ),
                        html.Span(",", className="sample-genomic-interval"),
                        html.Span(
                            "anaerobic germination",
                            id={
                                "type": "example-text-mining",
                                "description": "anaerobic germination",
                            },
                            className="sample-genomic-interval ms-3",
                            n_clicks=0,
                        ),
                    ],
                    className="pt-3",
                ),
                html.Br(),
                dbc.Label(
                    "Do you want to filter the results to display only genes overlapping your input intervals?",
                ),
                dbc.RadioItems(
                    id="text-mining-filter",
                    options=["Yes", "No"],
                    value="No",
                    inline=True,
                    className="ms-3 mt-1",
                ),
                html.Br(),
                dbc.Button(
                    "Search",
                    id="text-mining-submit",
                    className="page-button",
                    n_clicks=0,
                ),
            ],
            className="analysis-intro p-3",
        ),
        html.Br(),
        html.Div(
            id="text-mining-results-container",
            style={"display": "none"},
            children=[
                html.Hr(className="mt-3 mb-4"),
                dcc.Loading(
                    [
                        html.Div(
                            [html.Span(id="text-mining-results-stats")],
                            className="mb-3 stats",
                        ),
                        html.P(
                            html.Div(
                                [
                                    dbc.Button(
                                        [
                                            html.I(className="bi bi-download me-2"),
                                            "Export to CSV",
                                        ],
                                        id="text-mining-export-table",
                                        n_clicks=0,
                                        color="light",
                                        size="sm",
                                        className="table-button",
                                    ),
                                    dcc.Download(id="text-mining-download-df-to-csv"),
                                    dbc.Button(
                                        [
                                            html.I(
                                                className="bi bi-arrow-clockwise me-2"
                                            ),
                                            "Reset Table",
                                        ],
                                        id="text-mining-reset-table",
                                        color="light",
                                        size="sm",
                                        className="ms-3 table-button",
                                    ),
                                ],
                                style={"textAlign": "right"},
                            )
                        ),
                        dash_table.DataTable(
                            id="text-mining-results-table",
                            style_data={
                                "whiteSpace": "normal",
                                "height": "auto",
                                "textAlign": "left",
                            },
                            markdown_options={"html": True},
                            sort_action="native",
                            filter_action="native",
                            filter_options={
                                "case": "insensitive",
                                "placeholder_text": "🔎︎ Search Column",
                            },
                            page_action="native",
                            page_size=10,
                            cell_selectable=False,
                            style_table={"overflowX": "auto"},
                        ),
                    ]
                ),
            ],
            className="mt-2",
        ),
        # Do not remove; for log purposes
        html.Div(id="text-mining-log"),
    ],
    className="mt-2 mb-4",
)
