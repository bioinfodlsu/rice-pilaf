from dash import Input, Output, State, html, dcc, ctx
from dash.exceptions import PreventUpdate

from .util import *
from ..lift_over import util as lift_over_util
from ..coexpression import util as coexpression_util


def init_callback(app):
    @app.callback(
        Output("tfbs-genomic-intervals-input", "children"),
        State("homepage-submitted-genomic-intervals", "data"),
        Input("homepage-is-submitted", "data"),
        Input("tfbs-submit", "n_clicks"),
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        """
        Displays the genomic interval input in the tfbs page

        Parameters:
        - nb_intervals_str: Submitted genomic interval
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - *_: Other input that facilitates displaying of the submitted genomic interval

        Returns:
        - Submitted genomic interval text
        """

        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(
                lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)
            ):
                return [html.B("Your Input Intervals: "), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    # =================
    # Input-related
    # =================

    @app.callback(
        Output("tfbs-is-submitted", "data", allow_duplicate=True),
        Output("tfbs-submitted-addl-genes", "data", allow_duplicate=True),
        Output("tfbs-valid-addl-genes", "data", allow_duplicate=True),
        Output("tfbs-combined-genes", "data", allow_duplicate=True),
        Output("tfbs-submitted-set", "data", allow_duplicate=True),
        Output("tfbs-submitted-prediction-technique", "data", allow_duplicate=True),
        Output("tfbs-addl-genes-error", "style"),
        Output("tfbs-addl-genes-error", "children"),
        Input("tfbs-submit", "n_clicks"),
        State("homepage-is-submitted", "data"),
        State("homepage-submitted-genomic-intervals", "data"),
        State("tfbs-addl-genes", "value"),
        State("tfbs-set", "value"),
        State("tfbs-prediction-technique", "value"),
        prevent_initial_call=True,
    )
    def submit_tfbs_input(
        tfbs_submitted_n_clicks,
        homepage_is_submitted,
        genomic_intervals,
        submitted_addl_genes,
        submitted_tfbs_set,
        submitted_tfbs_prediction_technique,
    ):
        """
        Parses tfbs input, displays the tbfs result container
        - If user clicks on the tfbs submit button, the inputs will be parsed and either an error message or the tfbs results container will appear

        Parameters:
        - tfbs_submitted_n_clicks: Number of clicks pressed on the tfbs submit button
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - genomic_intervals: Saved genomic intervals found in the dcc.Store
        - submitted_addl_genes: Submitted tfbs additional genes
        - submitted_tfbs_set: Submitted tfbs set
        - submitted_tfbs_prediction_technique: Submitted tfbs prediction technique

        Returns:
        - ('tfbs-is-submitted', 'data'): [Tfbs] True for submitted valid input; otherwise False
        - ('tfbs-submitted-addl-genes', 'data'): Submitted tfbs additional genes
        - ('tfbs-valid-addl-genes', 'data'): Submitted tfbs valid additional genes
        - ('tfbs-combined-genes', 'data'): Combined genes
        - ('tfbs-submitted-set', 'data'): Submitted tfbs set
        - ('tfbs-submitted-prediction-technique', 'data'): Submitted tfbs prediction technique
        - ('tfbs-addl-genes-error', 'style'): {'display': 'block'} for displaying the error message; otherwise {'display': 'none'}
        - ('tfbs-addl-genes-error', 'children'): Error message
        """

        if homepage_is_submitted and tfbs_submitted_n_clicks >= 1:
            if submitted_addl_genes:
                submitted_addl_genes = submitted_addl_genes.strip()
            else:
                submitted_addl_genes = ""

            list_addl_genes = list(
                filter(None, [gene.strip() for gene in submitted_addl_genes.split(";")])
            )

            # Check which genes are valid MSU IDs
            list_addl_genes, invalid_genes = coexpression_util.check_if_valid_msu_ids(
                list_addl_genes
            )

            if not invalid_genes:
                error_display = {"display": "none"}
                error = None
            else:
                error_display = {"display": "block"}

                if len(invalid_genes) == 1:
                    error_msg = invalid_genes[0] + " is not a valid MSU accession ID."
                    error_msg_ignore = "It"
                else:
                    if len(invalid_genes) == 2:
                        error_msg = invalid_genes[0] + " and " + invalid_genes[1]
                    else:
                        error_msg = (
                            ", ".join(invalid_genes[:-1]) + ", and " + invalid_genes[-1]
                        )

                    error_msg += " are not valid MSU accession IDs."
                    error_msg_ignore = "They"

                error = [
                    html.Span(error_msg),
                    html.Br(),
                    html.Span(
                        f"{error_msg_ignore} will be ignored when running the analysis."
                    ),
                ]

            # Perform lift-over if it has not been performed.
            # Otherwise, just fetch the results from the file
            lift_over_nb_entire_table = lift_over_util.get_genes_in_Nb(
                genomic_intervals
            )[0].to_dict("records")

            combined_genes = lift_over_nb_entire_table + get_annotations_addl_gene(
                list_addl_genes
            )

            return (
                True,
                submitted_addl_genes,
                list_addl_genes,
                combined_genes,
                submitted_tfbs_set,
                submitted_tfbs_prediction_technique,
                error_display,
                error,
            )

        raise PreventUpdate

    @app.callback(
        Output("tfbs-results-container", "style"),
        Input("tfbs-is-submitted", "data"),
    )
    def display_tfbs_output(tfbs_is_submitted):
        """
        Displays the tfbs results container

        Parameters:
        - tfbs_is_submitted: [Tfbs] Saved boolean value of submitted valid input

        Returns:
        - ('tfbs-results-container', 'style'): {'display': 'block'} for displaying the tfbs results container; otherwise {'display': 'none'}
        """

        if tfbs_is_submitted:
            return {"display": "block"}

        else:
            return {"display": "none"}

    @app.callback(
        Output("tfbs-submit", "disabled"),
        Input("tfbs-submit", "n_clicks"),
        Input("tfbs-results-table", "data"),
    )
    def disable_tfbs_button_upon_run(n_clicks, *_):
        """
        Disables the submit button in the tfbs page until computation is done in the tfbs page

        Parameters:
        - n_clicks: Number of clicks pressed on the tfbs submit button
        - *_: Other input that facilitates the disabling of the tfbs submit button

        Returns:
        - ('tfbs-submit', 'disabled'): True for disabling the submit button; otherwise False
        """

        return ctx.triggered_id == "tfbs-submit" and n_clicks > 0

    @app.callback(
        Output("tfbs-prediction-technique-modal", "is_open"),
        Output("tfbs-set-modal", "is_open"),
        Output("tfbs-converter-modal", "is_open"),
        Input("tfbs-prediction-technique-tooltip", "n_clicks"),
        Input("tfbs-set-tooltip", "n_clicks"),
        Input("tfbs-converter-tooltip", "n_clicks"),
    )
    def open_modals(
        prediction_technique_tooltip_n_clicks,
        set_tooltip_n_clicks,
        converter_tooltip_n_clicks,
    ):
        """
        Displays the tooltip modals

        Parameters:
        - prediction_technique_tooltip_n_clicks: Number of clicks pressed for the tooltip button near the tfbs prediction technique input field
        - set_tooltip_n_clicks: Number of clicks pressed for the tooltip button near the tfbs set input field
        - converter_tooltip_n_clicks: Number of clicks pressed for the tooltip button near the tfbs additional genes input field

        Returns:
        - ('tfbs-prediction-technique-modal', 'is_open'): True for showing the tfbs prediction technique tooltip; otherwise False
        - ('tfbs-set-modal', 'is_open'): True for showing the tfbs set tooltip; otherwise False
        - ('tfbs-converter-modal', 'is_open'): True for showing the tfbs additional genes tooltip; otherwise False
        """

        if (
            ctx.triggered_id == "tfbs-prediction-technique-tooltip"
            and prediction_technique_tooltip_n_clicks > 0
        ):
            return True, False, False

        if ctx.triggered_id == "tfbs-set-tooltip" and set_tooltip_n_clicks > 0:
            return False, True, False

        if (
            ctx.triggered_id == "tfbs-converter-tooltip"
            and converter_tooltip_n_clicks > 0
        ):
            return False, False, True

        raise PreventUpdate

    @app.callback(
        Output("tfbs-input", "children"),
        Input("tfbs-is-submitted", "data"),
        State("tfbs-valid-addl-genes", "data"),
        State("tfbs-submitted-set", "data"),
        State("tfbs-submitted-prediction-technique", "data"),
    )
    def display_tfbs_submitted_input(
        tfbs_is_submitted, addl_genes, tfbs_set, tfbs_prediction_technique
    ):
        """
        Displays the tfbs submitted input

        Parameters:
        - tfbs_is_submitted: [Tfbs] Saved boolean value of submitted valid input
        - addl_genes: Saved tfbs additional genes found in the dcc.Store
        - tfbs_set: Saved tfbs set found in the dcc.Store
        - tfbs_prediction_technique: Saved tfbs prediction technique found in the dcc.Store

        Returns:
        - ('tfbs-input', 'children'): Submitted tfbs inputs text
        """

        if tfbs_is_submitted:
            if not addl_genes:
                addl_genes = "None"
            else:
                addl_genes = "; ".join(addl_genes)

            return [
                html.B("Additional Genes: "),
                addl_genes,
                html.Br(),
                html.B("Selected TF Binding Site Prediction Technique: "),
                tfbs_prediction_technique,
                html.Br(),
                html.B("Selected TF Binding Site Regions: "),
                tfbs_set.capitalize(),
                html.Br(),
            ]

        raise PreventUpdate

    # =================
    # Table-related
    # =================

    @app.callback(
        Output("tfbs-results-table", "data"),
        Output("tfbs-results-table", "columns"),
        Output("tfbs-table-stats", "children"),
        Output("tfbs-results-table", "filter_query", allow_duplicate=True),
        Output("tfbs-results-table", "page_current", allow_duplicate=True),
        State("homepage-submitted-genomic-intervals", "data"),
        Input("tfbs-combined-genes", "data"),
        Input("tfbs-valid-addl-genes", "data"),
        State("homepage-is-submitted", "data"),
        State("tfbs-submitted-set", "data"),
        State("tfbs-submitted-prediction-technique", "data"),
        State("tfbs-is-submitted", "data"),
        prevent_initial_call=True,
    )
    def display_enrichment_results(
        genomic_intervals,
        combined_genes,
        valid_addl_genes,
        homepage_is_submitted,
        tfbs_set,
        tfbs_prediction_technique,
        tfbs_is_submitted,
    ):
        """
        Displays the tfbs results table

        Parameters:
        - genomic_intervals: Saved genomic intervals found in the dcc.Sotre
        - combined_genes: Saved tfbs combined genes found in the dcc.Store
        - valid_addl_genes: Saved tfbs additional genes found in the dcc.Store
        - homepage_submitted:[Homepage] Saved boolean value of submitted valid input
        - tfbs_set: Saved tfbs set found in the dcc.Store
        - tfbs_prediction_technique: Saved tfbs prediction technique found in the dcc.Store
        - tfbs_is_submitted: [Tfbs] Saved boolean value of submitted valid input

        Returns:
        - ('text-mining-results-table', 'data'): Data for the text mining table
        - ('text-mining-results-table', 'columns'): List of columns for the text mining table
        - ('text-mining-results-stats', 'children'): Stats of the publications found for the query
        """

        if homepage_is_submitted and tfbs_is_submitted:
            enrichment_results_df, num_tf = perform_enrichment_all_tf(
                combined_genes,
                valid_addl_genes,
                tfbs_set,
                tfbs_prediction_technique,
                genomic_intervals,
            )

            mask = enrichment_results_df["Transcription Factor"] != NULL_PLACEHOLDER
            enrichment_results_df.loc[mask, "Transcription Factor"] = (
                get_msu_browser_link(enrichment_results_df, "Transcription Factor")
            )

            columns = [
                {"id": x, "name": x, "presentation": "markdown"}
                for x in enrichment_results_df.columns
            ]

            num_nonzero_overlap = get_num_unique_entries(
                enrichment_results_df, "Transcription Factor"
            )

            stats = f"{num_nonzero_overlap} out of {num_tf} transcription "
            if num_nonzero_overlap == 1:
                stats += " factor has "
            else:
                stats += " factors have "

            stats += (
                "predicted binding sites that overlap with your GWAS/QTL intervals."
            )

            return enrichment_results_df.to_dict("records"), columns, stats, "", 0

        raise PreventUpdate

    @app.callback(
        Output("tfbs-results-table", "filter_query", allow_duplicate=True),
        Output("tfbs-results-table", "page_current", allow_duplicate=True),
        Input("tfbs-reset-table", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_table_filter_page(*_):
        """
        Resets the tfbs table and the current page to its original state

        Parameters:
        - *_: Other input that facilitates the resetting of the tfbs table

        Returns:
        - ('tfbs-results-table', 'filter_query'): '' for removing the filter query
        - ('tfbs-results-table', 'page_current'): 0
        """

        return "", 0

    @app.callback(
        Output("tfbs-download-df-to-csv", "data"),
        Input("tfbs-export-table", "n_clicks"),
        State("tfbs-results-table", "data"),
        State("homepage-submitted-genomic-intervals", "data"),
    )
    def download_tfbs_table_to_csv(download_n_clicks, tfbs_df, genomic_intervals):
        """
        Export the tfbs table in csv file format

        Parameters:
        - download_n_clicks: Number of clicks pressed on the export tfbs table button
        - tfbs_df: Tfbs table data in dataframe format
        - genomic_intervals: Saved genomic intervals found in the dcc.Store

        Returns:
        - ('tfbs-download-df-to-csv', 'data'): Tfbs table in csv file format data
        """

        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(tfbs_df))
            return dcc.send_data_frame(
                df.to_csv,
                f"[{genomic_intervals}] Regulatory Feature Enrichment.csv",
                index=False,
            )

        raise PreventUpdate

    # =================
    # Session-related
    # =================

    @app.callback(
        Output("tfbs-addl-genes", "value"),
        Output("tfbs-prediction-technique", "value"),
        Output("tfbs-set", "value"),
        State("tfbs-submitted-addl-genes", "data"),
        State("tfbs-submitted-prediction-technique", "data"),
        State("tfbs-submitted-set", "data"),
        Input("tfbs-is-submitted", "data"),
    )
    def get_input_tfbs_session_state(
        addl_genes, tfbs_prediction_technique, tfbs_set, *_
    ):
        """
        Gets the tfbs related dcc.Store variables data in the tfbs input container and displays them

        Parameters:
        - addl_genes: Saved tfbs additional genes found in the dcc.Store
        - tfbs_prediction_technique: Saved tfbs prediction technique found in the dcc.Store
        - tfbs_set: Saved tfbs set found in the dcc.Store
        - *_: Other inputs in facilitating the saved state of the tfbs input

        Returns:
        - ('tfbs-addl-genes', 'value'): Saved tfbs additional genes found in the dcc.Store
        - ('tfbs-prediction-technique', 'value'): Saved tfbs prediction technique found in the dcc.Store; otherwise 'FunTFBS' for default value
        - ('tfbs-set', 'value'): Saved tfbs set found in the dcc.Store; otherwise 'promoters' for default value
        """

        if not tfbs_prediction_technique:
            tfbs_prediction_technique = "FunTFBS"

        if not tfbs_set:
            tfbs_set = "promoters"

        return addl_genes, tfbs_prediction_technique, tfbs_set
