from dash import Input, Output, State, dcc, html, ctx
from dash.exceptions import PreventUpdate

from .util import *
from ..general_util import *
from ..homepage import util as homepage_util


def init_callback(app):
    @app.callback(
        Output("lift-over-genomic-intervals-input", "children"),
        State("homepage-submitted-genomic-intervals", "data"),
        Input("homepage-is-submitted", "data"),
        Input("lift-over-submit", "n_clicks"),
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        """
        Displays the genomic interval input in the lift-over page

        Parameters:
        - nb_intervals_str: Saved genomic interval value found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - *_: Other input that facilitates displaying of the submitted genomic interval

        Returns:
        - ('lift-over-genomic-intervals-input', 'children'): Genomic interval text
        """

        if homepage_is_submitted:
            if nb_intervals_str and not is_error(
                get_genomic_intervals_from_input(nb_intervals_str)
            ):
                return [html.B("Your Input Intervals: "), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    # =================
    # Input-related
    # =================

    @app.callback(
        Output("session-container", "children", allow_duplicate=True),
        Output("lift-over-is-submitted", "data", allow_duplicate=True),
        Output("lift-over-submitted-other-refs", "data", allow_duplicate=True),
        Input("lift-over-submit", "n_clicks"),
        State("homepage-is-submitted", "data"),
        State("session-container", "children"),
        State("lift-over-other-refs", "value"),
        prevent_initial_call=True,
    )
    def submit_lift_over_input(
        lift_over_submit_n_clicks, homepage_is_submitted, dccStore_children, other_refs
    ):
        """
        Parses lift-over input, displays the lift-over result container, and resets the lift-over active data in the dcc.Store
        - If user clicks on the lift-over submit button, the inputs will be parsed and the lift-over results container will appear

        Parameters:
        - lift_over_submit_n_clicks: Number of clicks pressed on the lift-over submit button
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - dccStore_children: List of dcc.Store data
        - other_refs: Submitted other references of genome(s)

        Returns:
        - ('session-container', 'children'): Updated dcc.Store data
        - ('lift-over-is-submitted', 'data'): [Lift-over] True for submitted valid input; otherwise False
        - ('lift-over-submitted-other-refs', 'data'): Submitted other references of genome(s)
        - ('lift-over-active-tab', 'data'): None for clearing data for the saved active tab for the lift-over gene table; otherwise 'tab-#' where # pertains to specific tab number
        - ('lift-over-active-filter', 'data'): None for clearing data for the saved active filter for the lift-over gene table's common gene tab; otherwise specific values for the filter checklist
        """

        if homepage_is_submitted and lift_over_submit_n_clicks >= 1:
            other_refs = sanitize_other_refs(other_refs)

            dccStore_children = homepage_util.clear_specific_dccStore_data(
                dccStore_children, "lift-over-active"
            )

            return dccStore_children, True, other_refs

        raise PreventUpdate

    @app.callback(
        Output("lift-over-results-container", "style"),
        Input("lift-over-is-submitted", "data"),
    )
    def display_lift_over_output(lift_over_is_submitted):
        """
        Displays the lift-over results container

        Parameters:
        - lift_over_is_submitted: [Lift-over] Saved boolean value of submitted valid input

        Returns:
        - ('lift-over-results-container', 'style'): {'display': 'block'} for displaying the lift-over results container; otherwise {'display': 'none'}
        """

        if lift_over_is_submitted:
            return {"display": "block"}

        else:
            return {"display": "none"}

    @app.callback(
        Output("lift-over-submit", "disabled"),
        Input("lift-over-submit", "n_clicks"),
        Input("lift-over-results-table", "data"),
        Input("lift-over-results-statistics", "children"),
    )
    def disable_lift_over_button_upon_run(n_clicks, *_):
        """
        Disables the submit button in the lift-over page until computation is done in the lift-over page

        Parameters:
        - n_clicks: Number of clicks pressed on the lift-over submit button
        - *_: Other input that facilitates the disabling of the lift-over submit button

        Returns:
        - ('lift-over-submit', 'disabled'): True for disabling the submit button; otherwise False
        """

        return ctx.triggered_id == "lift-over-submit" and n_clicks > 0

    # =================
    # Table-related
    # =================

    @app.callback(
        Output("lift-over-results-gene-intro", "children"),
        Output("lift-over-overlap-table-filter", "style"),
        Input("lift-over-results-tabs", "active_tab"),
        State("lift-over-results-tabs", "children"),
        State("homepage-is-submitted", "data"),
        State("lift-over-is-submitted", "data"),
    )
    def display_gene_intro(
        active_tab, children, homepage_is_submitted, lift_over_is_submitted
    ):
        """
        Displays a short introduction of the genes

        Parameters:
        - active_tab: Selected tab for a specific gene table
        - children: List of columns (tabs) for various gene tables
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - lift_over_is_submitted: [Lift-over] Saved boolean value of submitted valid input

        Returns:
        - ('lift-over-results-gene-intro', 'children'): The introduction of the genes
        - ('lift-over-overlap-table-filter', 'style'): {'display': 'block'} for displaying the short introduction of the genes; otherwise {'display': 'none'}
        """

        if homepage_is_submitted and lift_over_is_submitted:
            if active_tab == get_tab_id("All Genes"):
                return "The table below lists all the implicated genes.", {
                    "display": "none"
                }

            elif active_tab == get_tab_id("Common Genes"):
                return (
                    "The table below lists the implicated genes that are common to:",
                    {"display": "block"},
                )

            elif active_tab == get_tab_id("Nipponbare"):
                return (
                    "The table below lists the genes overlapping the site in the Nipponbare reference.",
                    {"display": "none"},
                )

            else:
                tab_number = get_tab_index(active_tab)
                other_ref = children[tab_number]["props"]["value"]

                return (
                    f"The table below lists the genes from homologous regions in {other_ref} that are not in Nipponbare.",
                    {"display": "none"},
                )

        raise PreventUpdate

    @app.callback(
        Output("lift-over-results-statistics", "children"),
        Output("lift-over-results-tabs", "className"),
        Input("homepage-submitted-genomic-intervals", "data"),
        Input("lift-over-submitted-other-refs", "data"),
        State("homepage-is-submitted", "data"),
        State("lift-over-is-submitted", "data"),
    )
    def display_gene_statistics(
        nb_intervals_str, other_refs, homepage_is_submitted, lift_over_is_submitted
    ):
        """
        Displays the gene statistics

        Parameters:
        - nb_intervals_str: Saved genomic interval value found in the dcc.Store
        - other_refs: Saved other references of genome(s) found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - lift_over_is_submitted: [Lift-over] Saved boolean value of submitted valid input

        Returns:
        - ('lift-over-results-statistics', 'children'): Gene statistics text
        - ('lift-over-results-tabs', 'className'): None for removing the top margin during loading
        """

        if homepage_is_submitted and lift_over_is_submitted:
            genes_from_Nb_raw = get_genes_in_Nb(nb_intervals_str)[0]

            # Number of genes in Nipponbare
            num_unique_genes = get_num_unique_entries(genes_from_Nb_raw, "Name")
            if num_unique_genes == 1:
                gene_statistics_nb = f"{num_unique_genes} gene was found in Nipponbare"
            else:
                gene_statistics_nb = (
                    f"{num_unique_genes} genes were found in Nipponbare"
                )

            # Number of genes in other reference
            for idx, other_ref in enumerate(other_refs):
                common_genes_raw = get_common_genes([other_ref], nb_intervals_str)
                num_unique_genes = get_num_unique_entries(common_genes_raw, other_ref)
                if idx == len(other_refs) - 1:
                    if num_unique_genes == 1:
                        gene_statistics_nb += (
                            f", and {num_unique_genes} gene in {other_ref}"
                        )
                    else:
                        gene_statistics_nb += (
                            f", and {num_unique_genes} genes in {other_ref}"
                        )
                else:
                    if num_unique_genes == 1:
                        gene_statistics_nb += (
                            f", {num_unique_genes} gene in {other_ref}"
                        )
                    else:
                        gene_statistics_nb += (
                            f", {num_unique_genes} genes in {other_ref}"
                        )

            gene_statistics_nb += ". "
            gene_statistics_items = [html.Li(gene_statistics_nb)]

            if other_refs:
                # Number of orthogroups with genes common across all cultivars
                other_refs.append("Nipponbare")
                genes_common = get_common_genes(other_refs, nb_intervals_str)
                num_unique_genes = get_num_unique_entries(genes_common, "OGI")

                if num_unique_genes == 1:
                    gene_statistics_common = f"{num_unique_genes} orthogroup has genes across all selected cultivars."
                else:
                    gene_statistics_common = f"{num_unique_genes} orthogroups have genes across all selected cultivars."

                gene_statistics_items.append(html.Li(gene_statistics_common))

                # Number of unique genes
                gene_statistics_other_ref = f""
                other_refs.pop()  # Remove added Nipponbare
                for idx, other_ref in enumerate(other_refs):
                    genes_from_other_ref_raw = get_unique_genes_in_other_ref(
                        other_refs, other_ref, nb_intervals_str
                    )

                    if len(other_refs) > 1 and idx == len(other_refs) - 1:
                        gene_statistics_other_ref += f", and "
                    elif idx != 0:
                        gene_statistics_other_ref += f", "

                    num_unique_genes = get_num_unique_entries(
                        genes_from_other_ref_raw, "Name"
                    )

                    if num_unique_genes == 1:
                        gene_statistics_other_ref += (
                            f"{num_unique_genes} gene is unique to {other_ref}"
                        )
                    else:
                        gene_statistics_other_ref += (
                            f"{num_unique_genes} genes are unique to {other_ref}"
                        )

                gene_statistics_other_ref += "."
                gene_statistics_items.append(html.Li(gene_statistics_other_ref))

            # Setting the class name of lift-over-results-tabs to None is for removing the top margin during loading
            return gene_statistics_items, None

        raise PreventUpdate

    @app.callback(
        Output("lift-over-results-intro", "children"),
        Output("lift-over-results-tabs", "children"),
        Output("lift-over-overlap-table-filter", "options"),
        Output("lift-over-overlap-table-filter", "value"),
        State("homepage-submitted-genomic-intervals", "data"),
        Input("lift-over-submitted-other-refs", "data"),
        State("homepage-is-submitted", "data"),
        State("lift-over-active-filter", "data"),
        State("lift-over-is-submitted", "data"),
    )
    def display_gene_tabs(
        nb_intervals_str,
        other_refs,
        homepage_is_submitted,
        active_filter,
        lift_over_is_submitted,
    ):
        """
        Displays the following:
        - a short introduction on the selected lift-over input;
        - list of tabs available for the gene table; and
        - available filters for the common genes

        Parameters:
        - nb_intervals_str: Saved genomic interval value found in the dcc.Store
        - other_refs: Saved other references of genome(s) found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - active_filter: Saved list of selected rice variants found in the common genes table
        - lift_over_is_submitted: [Lift-over] Saved boolean value of submitted valid input

        Returns:
        - ('lift-over-results-intro', 'children'): Introduction about the selected lift-over input
        - ('lift-over-results-tabs', 'children'): List of tabs available for the gene table
        - ('lift-over-overlap-table-filter', 'options'): List of available filters (genes + other refs)
        - ('lift-over-overlap-table-filter', 'value'): Selected filters
        """

        if homepage_is_submitted and lift_over_is_submitted:
            if nb_intervals_str and not is_error(
                get_genomic_intervals_from_input(nb_intervals_str)
            ):
                tabs = get_tabs()

                other_refs = sanitize_other_refs(other_refs)

                if other_refs:
                    tabs = tabs + other_refs

                tabs_children = [
                    (
                        dcc.Tab(label=tab, value=tab)
                        if idx < len(get_tabs())
                        else dcc.Tab(label=f"Unique to {tab}", value=tab)
                    )
                    for idx, tab in enumerate(tabs)
                ]

                if not active_filter:
                    active_filter = tabs[len(get_tabs()) - 1 :]

                gene_list_msg = [
                    html.Span("The tabs below show the implicated genes in "),
                    html.B("Nipponbare"),
                ]

                if other_refs:
                    other_refs_str = other_refs[0]
                    if len(other_refs) == 2:
                        other_refs_str += f" and {other_refs[1]}"
                    elif len(other_refs) > 2:
                        for idx, other_ref in enumerate(other_refs[1:]):
                            if idx != len(other_refs) - 2:
                                other_refs_str += f", "
                            else:
                                other_refs_str += f", and "

                            other_refs_str += (
                                f"{other_ref} ({other_ref_genomes[other_ref]})"
                            )

                    gene_list_msg += [
                        html.Span(" and in orthologous regions of "),
                        html.B(other_refs_str),
                    ]

                gene_list_msg += [html.Span(":")]

                return (
                    gene_list_msg,
                    tabs_children,
                    tabs[len(get_tabs()) - 1 :],
                    active_filter,
                )
            else:
                return None, None, [], None

        raise PreventUpdate

    @app.callback(
        Output("lift-over-results-tabs", "active_tab"),
        State("homepage-is-submitted", "data"),
        State("lift-over-active-tab", "data"),
        State("lift-over-is-submitted", "data"),
        Input("lift-over-submitted-other-refs", "data"),
    )
    def display_active_tab(
        homepage_is_submitted, saved_active_tab, lift_over_is_submitted, *_
    ):
        """
        Displays the active tab for a specific gene table

        Parameters:
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - saved_active_tab: Saved active tab for a specific gene table
        - lift_over_is_submitted: [Lift-over] Saved boolean value of submitted valid input
        - *_: Other input that facilitates displaying of the saved active tab for a specific gene table

        Returns:
        - ('lift-over-results-tabs', 'active_tab'): Selected tab for a specific gene table
        """

        if homepage_is_submitted and lift_over_is_submitted:
            if not saved_active_tab:
                return "tab-0"

            return saved_active_tab

        raise PreventUpdate

    @app.callback(
        Output("lift-over-results-table", "columns"),
        Output("lift-over-results-table", "data"),
        Input("homepage-submitted-genomic-intervals", "data"),
        Input("lift-over-results-tabs", "active_tab"),
        Input("lift-over-overlap-table-filter", "value"),
        Input("lift-over-submitted-other-refs", "data"),
        State("lift-over-results-tabs", "children"),
        State("homepage-is-submitted", "data"),
        State("lift-over-is-submitted", "data"),
    )
    def display_gene_tables(
        nb_intervals_str,
        active_tab,
        filter_rice_variants,
        other_refs,
        children,
        homepage_is_submitted,
        lift_over_is_submitted,
    ):
        """
        Displays the gene table depending on the selected active tab and filters, if present

        Parameters:
        - nb_intervals_str: Saved genomic interval value found in the dcc.Store
        - active_tab: Selected tab for a specific gene table
        - filter_rice_variants: List of selected rice variants found in the common genes table
        - other_refs: Other references of genome(s)
        - children: List of columns (tabs) for various gene tables
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - lift_over_is_submitted: [Lift-over] Saved boolean value of submitted valid input

        Returns:
        - ('lift-over-results-table', 'columns'): List of columns for a specific gene table
        - ('lift-over-results-table', 'data'): Data for a specific gene table
        """

        if homepage_is_submitted and lift_over_is_submitted:
            # The RGI links are added here instead of the util.py file so that the IDs
            # in the dataframe stored in dcc.Store are not polluted with the hyperlinks.

            if active_tab == get_tab_id("All Genes"):
                all_genes_raw = get_all_genes(other_refs, nb_intervals_str)

                mask = all_genes_raw["OGI"] != NULL_PLACEHOLDER
                all_genes_raw.loc[mask, "OGI"] = get_rgi_orthogroup_link(
                    all_genes_raw, "OGI"
                )
                if "Nipponbare" in all_genes_raw.columns:
                    mask = all_genes_raw["Nipponbare"] != NULL_PLACEHOLDER
                    all_genes_raw.loc[mask, "Nipponbare"] = get_msu_browser_link(
                        all_genes_raw, "Nipponbare"
                    )

                for cultivar in other_ref_genomes:
                    if cultivar in all_genes_raw.columns:
                        mask = all_genes_raw[cultivar] != NULL_PLACEHOLDER
                        all_genes_raw.loc[mask, cultivar] = get_rgi_genecard_link(
                            all_genes_raw, cultivar
                        )

                all_genes = all_genes_raw.to_dict("records")

                columns = [
                    {"id": x, "name": x, "presentation": "markdown"}
                    for x in all_genes_raw.columns
                ]

                return columns, all_genes

            elif active_tab == get_tab_id("Common Genes"):
                common_genes_raw = get_common_genes(
                    filter_rice_variants, nb_intervals_str
                )

                # Mask will be triggered if no cultivar is selected
                mask = common_genes_raw["OGI"] != NULL_PLACEHOLDER
                common_genes_raw.loc[mask, "OGI"] = get_rgi_orthogroup_link(
                    common_genes_raw, "OGI"
                )

                if "Nipponbare" in common_genes_raw.columns:
                    mask = common_genes_raw["Nipponbare"] != NULL_PLACEHOLDER
                    common_genes_raw.loc[mask, "Nipponbare"] = get_msu_browser_link(
                        common_genes_raw, "Nipponbare"
                    )

                for cultivar in other_ref_genomes:
                    if cultivar in common_genes_raw.columns:
                        mask = common_genes_raw[cultivar] != NULL_PLACEHOLDER
                        common_genes_raw.loc[mask, cultivar] = get_rgi_genecard_link(
                            common_genes_raw, cultivar
                        )

                common_genes = common_genes_raw.to_dict("records")

                columns = [
                    {"id": x, "name": x, "presentation": "markdown"}
                    for x in common_genes_raw.columns
                ]

                return columns, common_genes

            elif active_tab == get_tab_id("Nipponbare"):
                genes_from_Nb_raw = get_genes_in_Nb(nb_intervals_str)[0].drop(
                    ["Chromosome", "Start", "End", "Strand"], axis=1
                )

                mask = genes_from_Nb_raw["OGI"] != NULL_PLACEHOLDER
                genes_from_Nb_raw.loc[mask, "OGI"] = get_rgi_orthogroup_link(
                    genes_from_Nb_raw, "OGI"
                )

                mask = genes_from_Nb_raw["Name"] != NULL_PLACEHOLDER
                genes_from_Nb_raw.loc[mask, "Name"] = get_msu_browser_link(
                    genes_from_Nb_raw, "Name"
                )

                genes_from_Nb = genes_from_Nb_raw.to_dict("records")

                columns = [
                    {"id": x, "name": x, "presentation": "markdown"}
                    for x in genes_from_Nb_raw.columns
                ]

                return columns, genes_from_Nb

            else:
                tab_number = get_tab_index(active_tab)
                other_ref = children[tab_number]["props"]["value"]

                genes_from_other_ref_raw = get_unique_genes_in_other_ref(
                    other_refs, other_ref, nb_intervals_str
                )

                mask = genes_from_other_ref_raw["OGI"] != NULL_PLACEHOLDER
                genes_from_other_ref_raw.loc[mask, "OGI"] = get_rgi_orthogroup_link(
                    genes_from_other_ref_raw, "OGI"
                )

                mask = genes_from_other_ref_raw["Name"] != NULL_PLACEHOLDER
                genes_from_other_ref_raw.loc[mask, "Name"] = get_rgi_genecard_link(
                    genes_from_other_ref_raw, "Name"
                )

                genes_from_other_ref = genes_from_other_ref_raw.to_dict("records")

                columns = [
                    {"id": x, "name": x, "presentation": "markdown"}
                    for x in genes_from_other_ref_raw.columns
                ]

                return columns, genes_from_other_ref

        raise PreventUpdate

    @app.callback(
        Output("lift-over-results-table", "filter_query"),
        Output("lift-over-results-table", "page_current"),
        Input("lift-over-reset-table", "n_clicks"),
        Input("lift-over-submit", "n_clicks"),
        Input("lift-over-results-tabs", "active_tab"),
        Input("lift-over-overlap-table-filter", "value"),
    )
    def reset_table_filter_page(*_):
        """
        Resets the lift-over gene table and the current page to its original state

        Parameters:
        - *_: Other input that facilitates the resetting of the lift-over gene table

        Returns:
        - ('lift-over-results-table', 'filter_query'): '' for removing the filter query
        - ('lift-over-results-table', 'page_current'): 0
        """

        return "", 0

    @app.callback(
        Output("lift-over-download-df-to-csv", "data"),
        Input("lift-over-export-table", "n_clicks"),
        State("lift-over-results-table", "data"),
        State("homepage-submitted-genomic-intervals", "data"),
    )
    def download_lift_over_table_to_csv(
        download_n_clicks, lift_over_df, genomic_intervals
    ):
        """
        Export the gene table in csv file format

        Parameters:
        - download_n_clicks: Number of clicks pressed on the export gene table button
        - lift_over_df: Gene table data in dataframe format
        - genomic_intervals: Saved genomic interval value found in the dcc.Store

        Returns:
        - ('lift-over-download-df-to-csv', 'data'): Gene table in csv file format data
        """

        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(lift_over_df))
            return dcc.send_data_frame(
                df.to_csv,
                f"[{genomic_intervals}] Gene List and Lift-Over.csv",
                index=False,
            )

        raise PreventUpdate

    # =================
    # Session-related
    # =================

    @app.callback(
        Output("lift-over-active-tab", "data", allow_duplicate=True),
        Output("lift-over-active-filter", "data", allow_duplicate=True),
        Input("lift-over-results-tabs", "active_tab"),
        Input("lift-over-overlap-table-filter", "value"),
        State("homepage-is-submitted", "data"),
        State("lift-over-is-submitted", "data"),
        prevent_initial_call=True,
    )
    def set_submitted_lift_over_session_state(
        active_tab, filter_rice_variants, homepage_is_submitted, lift_over_is_submitted
    ):
        """
        Sets the submitted lift-over related dcc.Store variables data

        Parameters:
        - active_tab: Selected tab for a specific gene table
        - filter_rice_variants: List of selected rice variants found in the common genes table
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - lift_over_is_submitted: [Lift-over] Saved boolean value of submitted valid input

        Returns:
        - ('lift-over-active-tab', 'data'): Active tab input
        - ('lift-over-active-filter', 'data'): Filtered rice variants input
        """

        if homepage_is_submitted and lift_over_is_submitted:
            return active_tab, filter_rice_variants

        raise PreventUpdate

    @app.callback(
        Output("lift-over-other-refs", "value"),
        State("lift-over-other-refs", "multi"),
        State("lift-over-submitted-other-refs", "data"),
        Input("lift-over-is-submitted", "data"),
    )
    def get_input_lift_over_session_state(is_multi_other_refs, other_refs, *_):
        """
        Gets the [Input container] lift-over related dcc.Store data and displays them

        Parameters:
        - is_multi_other_refs: True for multiple values being accepted; otherwise False
        - other_refs: Saved value of other references of genome(s) input found in the dcc.Store
        - *_: Other inputs in facilitating the saved state of the lift-over input

        Returns:
        - ('lift-over-other-refs', 'value'): Saved other references of genome(s)
        """

        # if the other ref input field only accepts single value
        if not is_multi_other_refs and other_refs:
            other_refs = other_refs[0]

        return other_refs
