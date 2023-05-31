from dash import Input, Output, State, dcc
from dash.exceptions import PreventUpdate

from .util import *
from ..constants import Constants
const = Constants()


def init_callback(app):
    @app.callback(
        Output('lift-over-results-table', 'css'),
        Input('lift-over-results-table', 'derived_virtual_data')
    )
    def display_export_button(data):
        if data == []:
            return [{"selector": ".export", "rule": "display:none"}]
        else:
            return [{"selector": ".export", "rule": "display:block"}]

    @app.callback(
        Output('lift-over-results-intro', 'children'),
        Output('lift-over-results-tabs', 'children'),

        Output('lift-over-results-genomic-intervals-input', 'children'),
        Output('lift-over-results-other-refs-input', 'children'),

        Output('lift-over-overlap-table-filter', 'options'),
        Output('lift-over-overlap-table-filter', 'value'),

        Input('lift-over-genomic-intervals-saved-input', 'data'),
        Input('lift-over-other-refs-saved-input', 'data'),

        State('lift-over-is-submitted', 'data'),

        State('lift-over-active-filter', 'data')
    )
    def display_gene_tabs(nb_intervals_str, other_refs, is_submitted, active_filter):
        if is_submitted:
            if nb_intervals_str and not is_error(get_genomic_intervals_from_input(nb_intervals_str)):
                tabs = ['Summary', 'Nb']

                other_refs = sanitize_other_refs(other_refs)

                if other_refs:
                    tabs = tabs + other_refs

                tabs_children = [dcc.Tab(label=tab, value=tab)
                                 for tab in tabs]

                if not active_filter:
                    active_filter = tabs[1:]

                return 'The tabs below show a list of genes in Nipponbare and in homologous regions of the other references you chose', \
                    tabs_children, f'Genomic Interval: {nb_intervals_str}', f'Homologous regions: {str(other_refs)[1:-1]}', \
                    tabs[1:], active_filter
            else:
                return None, None, None, None, [], None

        raise PreventUpdate

    # Chain callback for active tab
    @app.callback(
        Output('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        State('lift-over-is-submitted', 'data'),
        State('lift-over-active-tab', 'data')
    )
    def switch_active_tab(nb_intervals_str, is_submitted, active_tab):
        if is_submitted:
            if not active_tab:
                return 'tab-0'

            return active_tab

        raise PreventUpdate

    @app.callback(
        Output('lift-over-nb-table', 'data'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def get_nipponbare_gene_ids(nb_intervals_str, is_submitted):
        if is_submitted:
            if nb_intervals_str:
                nb_intervals = get_genomic_intervals_from_input(
                    nb_intervals_str)

                if not is_error(nb_intervals):
                    genes_from_Nb = get_genes_from_Nb(
                        nb_intervals)

                    return genes_from_Nb[1]

        raise PreventUpdate

    @app.callback(
        Output('lift-over-active-tab', 'data', allow_duplicate=True),
        Output('lift-over-active-filter', 'data', allow_duplicate=True),

        Input('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-overlap-table-filter', 'value'),

        State('lift-over-is-submitted', 'data'),
        prevent_initial_call=True,
    )
    def set_lift_over_session_state(active_tab, filter_rice_variants, is_submitted):
        if is_submitted:
            return active_tab, filter_rice_variants

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-gene-intro', 'children'),
        Output('lift-over-results-table', 'data'),
        Output('lift-over-overlap-table-filter', 'style'),

        Input('lift-over-genomic-intervals-saved-input', 'data'),
        Input('lift-over-results-tabs', 'active_tab'),

        Input('lift-over-overlap-table-filter', 'value'),

        State('lift-over-results-tabs', 'children'),
        State('lift-over-is-submitted', 'data')
    )
    def display_gene_tables(nb_intervals_str, active_tab, filter_rice_variants, children, is_submitted):
        if is_submitted:
            if nb_intervals_str:
                nb_intervals = get_genomic_intervals_from_input(
                    nb_intervals_str)

                if not is_error(nb_intervals):
                    SUMMARY_TAB = 'tab-0'
                    NB_TAB = 'tab-1'
                    genes_from_Nb = get_genes_from_Nb(
                        nb_intervals)
                    df_nb_complete = genes_from_Nb[0].to_dict('records')

                    if active_tab == SUMMARY_TAB:
                        df_nb = get_overlapping_ogi(
                            filter_rice_variants, nb_intervals).to_dict('records')

                        return 'Genes present in the selected rice varieties. Use the checkbox below to filter rice varieties:', \
                            df_nb, {'display': 'block'}

                    elif active_tab == NB_TAB:
                        return 'Genes overlapping the site in the Nipponbare reference', df_nb_complete, {'display': 'none'}

                    else:
                        tab_number = int(active_tab[len('tab-'):])
                        other_ref = children[tab_number]["props"]["value"]
                        df_nb = get_genes_from_other_ref(
                            other_ref, nb_intervals).to_dict('records')

                        return f'Genes from homologous regions in {other_ref}', df_nb, {'display': 'none'}

                else:
                    return None, None, {'display': 'none'}
            else:
                return None, None, {'display': 'none'}

        raise PreventUpdate

    @app.callback(
        Output('lift-over-container', 'style'),
        Input('lift-over-is-submitted', 'data'),
    )
    def hide_lift_over_page(is_submitted):
        if is_submitted:
            return {'display': 'block'}
        else:
            return {'display': 'none'}
