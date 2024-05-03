import dash_bootstrap_components as dbc
from dash import dcc, html

from callbacks.constants import Constants

# ============
# Main Layout
# ============


layout = html.Div(
    id={
        "type": "analysis-layout",
        "label": Constants.LABEL_TEMPLATE,  # Replace the Constants.LABEL_TEMPLATE with the constant variable you have defined in the Constants.py for consistency
    },
    hidden=True,
    children=[
        # Place the necessary UI here
        html.Div(
            [
                html.P(
                    [
                        Constants.INTRO_TEMPLATE,
                        " Click ",
                        dcc.Link(
                            [
                                "here ",
                                html.I(
                                    id="demo-link",
                                    className="fa-solid fa-up-right-from-square fa-2xs",
                                ),
                            ],
                            href="https://github.com/bioinfodlsu/rice-pilaf/wiki/3.5.-Adding-a-Feature",
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
                html.Span(id="template-genomic-intervals-input"),
            ],
            className="analysis-intro p-3",
        ),
        html.Br(),
        html.Div(
            [
                dbc.Label(["Additional Genes"]),
                html.Br(),
                dbc.Alert(
                    id="template-addl-genes-error",
                    color="danger",
                    style={"display": "none"},
                ),
                dbc.Textarea(id="template-addl-genes"),
                html.Br(),
                dbc.RadioItems(
                    id="template-radio-buttons",
                    options=["Option 1", "Option 2"],
                    value="Option 1",
                    inline=True,
                    className="ms-3 mt-1",
                ),
                html.Br(),
                dbc.Checklist(
                    id="template-checkbox-buttons",
                    options=["Checkbox 1", "Checkbox 2"],
                    value=["Checkbox 1", "Checkbox 2"],
                    inline=True,
                    className="ms-3",
                ),
                html.Br(),
                # Should also be changed if parameter space is changed
                html.Div(
                    [
                        dcc.Slider(
                            id="template-parameter-slider",
                            step=None,
                            marks={
                                0: "1 (Loose Modules)",
                                30: "2",
                                60: "3",
                                90: "4 (Dense Modules)",
                            },
                            value=30,
                        )
                    ],
                    id="template-parameter-slider-container",
                ),
                html.Br(),
                dbc.Button(
                    "Run Analysis",
                    id="template-submit",
                    className="page-button",
                    n_clicks=0,
                ),
            ],
            className="analysis-intro p-3",
        ),
        html.Br(),
        html.Div(
            id="template-results-container",
            style={"display": "none"},
            children=[
                html.Hr(className="mt-3 mb-4"),
                dcc.Loading(
                    [
                        html.Div(id="template-input", className="analysis-intro p-3"),
                    ]
                ),
            ],
        ),
    ],
    className="mt-2 mb-4",
)
