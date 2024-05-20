import pandas as pd
from dash import Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate

from ..coexpression.util import (
    get_user_facing_algo,
    get_user_facing_network,
    get_user_facing_parameter,
)
from ..general_util import NULL_PLACEHOLDER, purge_html_export_table
from ..lift_over.util import get_genes_in_Nb, get_genomic_intervals_from_input, is_error
from ..links_util import get_msu_browser_link
from .util import make_summary_table


def init_callback(app):
    @app.callback(
        Output(
            "summary-genomic-intervals-input", "children"
        ),  # Genomic interval for display
        State("homepage-submitted-genomic-intervals", "data"),  # Saved genomic interval
        Input(
            "homepage-is-submitted", "data"
        ),  # Saved Boolean indicating whether a valid genomic interval was submitted
        Input("summary-submit", "n_clicks"),
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        """
        Displays the genomic interval input in the summary page
        """

        if homepage_is_submitted:
            if nb_intervals_str and not is_error(
                get_genomic_intervals_from_input(nb_intervals_str)
            ):
                return [html.B("Your Input Intervals: "), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output(
            "summary-is-submitted", "data", allow_duplicate=True
        ),  # True if submitted values are valid; False, otherwise
        Input(
            "summary-submit", "n_clicks"
        ),  # Number of times submit button was clicked
        State(
            "homepage-is-submitted", "data"
        ),  # Saved Boolean indicating whether a valid genomic interval was submitted
        prevent_initial_call=True,
    )
    def submit_summary_input(summary_submitted_n_clicks, homepage_is_submitted):
        """
        Submits the summary input
        """

        if homepage_is_submitted and summary_submitted_n_clicks >= 1:
            return True

        raise PreventUpdate

    @app.callback(
        Output("summary-results-container", "style"),
        Input("summary-is-submitted", "data"),
        Input("coexpression-is-submitted", "data"),
    )
    def display_summary_output(*_):
        if ctx.triggered_id != "summary-is-submitted":
            return {"display": "none"}

        return {"display": "block"}

    @app.callback(
        Output("summary-submit", "disabled", allow_duplicate=True),
        Input("summary-submit", "n_clicks"),
        prevent_initial_call=True,
    )
    def disable_summary_button_upon_run(n_clicks):
        """
        Disables the submit button in the summary page until computation is done in the summary page

        Parameters:
        - n_clicks: Number of clicks pressed on the summary submit button
        - *_: Other input that facilitates the disabling of the summary submit button

        Returns:
        - ('summary-submit', 'disabled'): True for disabling the submit button; otherwise False
        """

        return n_clicks > 0

    @app.callback(
        Output("summary-submit", "disabled", allow_duplicate=True),
        Input("summary-results-table", "data"),
        prevent_initial_call=True,
    )
    def enable_summary_button_once_finished(*_):
        return False

    @app.callback(
        Output("summary-input", "children"),
        Input("summary-is-submitted", "data"),
        State("coexpression-is-submitted", "data"),
        State("coexpression-valid-addl-genes", "data"),
        State("coexpression-submitted-network", "data"),
        State("coexpression-submitted-clustering-algo", "data"),
        State("coexpression-submitted-parameter-slider", "data"),
    )
    def display_summary_submitted_input(
        summary_submitted,
        coexpression_submitted,
        genes,
        network,
        algo,
        submitted_parameter_slider,
    ):
        """
        Displays the submitted inputs

        Parameters:
        - summary_submitted: [Summary] Saved boolean value of submitted valid input
        - coexpression_submitted: [Coexpression] Saved boolean value of submitted valid input
        - genes: [Coexpression] Saved valid additional genes in the dcc.Store
        - network: [Coexpression] Saved network found in the dcc.Store
        - algo: [Coexpression] Saved clustering algorithm found in the dcc.Store
        - submitted_parameter_slider: [Coexpression] Saved parameter slider tuple found in the dcc.Store

        Returns:
        - ('summary-input', 'children'): Submitted inputs text
        """

        if coexpression_submitted:
            parameters = 0
            if submitted_parameter_slider and algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[algo]["value"]

            if not genes:
                genes = "None"
            else:
                genes = "; ".join(genes)

        else:
            # Assume default coexpression network parameters
            algo = "clusterone"
            network = "OS-CX"
            parameters = 30
            genes = "None"

        if summary_submitted:
            return [
                html.B("Co-Expression Network Analysis"),
                html.Br(),
                html.Ul(
                    [
                        html.Li([html.B("Additional Genes: "), genes]),
                        html.Li(
                            [
                                html.B("Selected Co-Expression Network: "),
                                get_user_facing_network(network),
                            ]
                        ),
                        html.Li(
                            [
                                html.B("Selected Module Detection Algorithm: "),
                                get_user_facing_algo(algo),
                            ]
                        ),
                        html.Li(
                            [
                                html.B("Selected Algorithm Parameter: "),
                                get_user_facing_parameter(algo, parameters),
                            ]
                        ),
                    ],
                    className="pb-0 mb-1",
                ),
            ]

        raise PreventUpdate

    # =================
    # Table-related
    # =================

    @app.callback(
        Output("summary-results-table", "data"),
        Output("summary-results-table", "columns"),
        Output("summary-results-table", "filter_query", allow_duplicate=True),
        Output("summary-results-table", "page_current", allow_duplicate=True),
        State("homepage-submitted-genomic-intervals", "data"),
        State("coexpression-combined-genes", "data"),
        State("coexpression-valid-addl-genes", "data"),
        State("coexpression-submitted-network", "data"),
        State("coexpression-submitted-clustering-algo", "data"),
        State("coexpression-submitted-parameter-slider", "data"),
        State("homepage-is-submitted", "data"),
        Input("summary-is-submitted", "data"),
        State("coexpression-is-submitted", "data"),
        prevent_initial_call=True,
    )
    def display_summary_results(
        genomic_intervals,
        combined_gene_ids,
        valid_addl_genes,
        submitted_network,
        submitted_algo,
        submitted_parameter_slider,
        homepage_submitted,
        summary_submitted,
        coexpression_submitted,
    ):
        """
        Displays the summary results

        Parameters:
        - genomic_intervals: Saved genomic intervals found in the dcc.Store
        - combined_gene_ids: [Coexpression] Saved combined gene ids found in the dcc.Store
        - valid_addl_genes: [Coexpression] Saved valid additional genes found in the dcc.Store
        - submitted_network: [Coexpression] Saved network found in the dcc.Store
        - submitted_algo: [Coexpression] Saved clustering algorithm found in the dcc.Store
        - submitted_parameter_slider: [Coexpression] Saved parameter slider tuple found in the dcc.Store
        - homepage_submitted: [Homepage] Saved boolean value of submitted valid input
        - summary_submitted: [Summary] Saved boolean value of submitted valid input
        - coexpression_submitted: [Coexpression] Saved boolean value of submitted valid input

        Returns:
        - ('summary-results-table', 'data'): Data for the summary table
        - ('summary-results-table', 'columns'): List of columns for the summary table
        - ('summary-results-table', 'filter_query'): '' for default value
        - ('summary-results-table', 'page_current'): 0 for default value
        """

        if coexpression_submitted:
            parameters = 0
            if (
                submitted_parameter_slider
                and submitted_algo in submitted_parameter_slider
            ):
                parameters = submitted_parameter_slider[submitted_algo]["value"]

        else:
            # Assume default coexpression network parameters
            submitted_algo = "clusterone"
            submitted_network = "OS-CX"
            parameters = 30

            # Will throw exception when cache is cleared and display is reset while summary page is open
            try:
                combined_gene_ids = get_genes_in_Nb(genomic_intervals)[1]
            except:
                pass
            valid_addl_genes = []

        if homepage_submitted and summary_submitted:
            summary_results_df = make_summary_table(
                genomic_intervals,
                combined_gene_ids,
                valid_addl_genes,
                submitted_network,
                submitted_algo,
                parameters,
            )

            # Changing null values should be done here after loading the summary table
            # in order to avoid having .0 in the columns with null values
            summary_results_df = summary_results_df.fillna(NULL_PLACEHOLDER)

            mask = summary_results_df["Gene"] != NULL_PLACEHOLDER
            summary_results_df.loc[mask, "Gene"] = get_msu_browser_link(
                summary_results_df, "Gene"
            )

            columns = [
                {"id": x, "name": x, "presentation": "markdown"}
                for x in summary_results_df.columns
            ]

            return summary_results_df.to_dict("records"), columns, "", 0

        raise PreventUpdate

    @app.callback(
        Output("summary-results-table", "filter_query", allow_duplicate=True),
        Output("summary-results-table", "page_current", allow_duplicate=True),
        Input("summary-reset-table", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_table_filter_page(*_):
        """
        Resets the summary table and the current page to its original state

        Parameters:
        - *_: Other input that facilitates the resetting of the summary table

        Returns:
        - ('summary-results-table', 'filter_query'): '' for removing the filter query
        - ('summary-results-table', 'page_current'): 0
        """

        return "", 0

    @app.callback(
        Output("summary-download-df-to-csv", "data"),
        Input("summary-export-table", "n_clicks"),
        State("summary-results-table", "data"),
        State("homepage-submitted-genomic-intervals", "data"),
    )
    def download_tfbs_table_to_csv(download_n_clicks, summary_df, genomic_intervals):
        """
        Export the summary table in csv file format

        Parameters:
        - download_n_clicks: Number of clicks pressed on the export gene table button
        - summary_df: Summary table data in dataframe format
        - genomic_intervals: Saved genomic intervals found in the dcc.Store

        Returns:
        - ('summary-download-df-to-csv', 'data'): Summary table in csv file format data
        """

        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(summary_df))
            return dcc.send_data_frame(
                df.to_csv, f"[{genomic_intervals}] Summary.csv", index=False
            )

        raise PreventUpdate
