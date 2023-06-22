from dash import Input, Output, State, dcc, html, ctx
from dash.exceptions import PreventUpdate

from .util import *
from ..constants import Constants
const = Constants()


def init_callback(app):
    @app.callback(
        Output('lift-over-results-container', 'style', allow_duplicate=True),
        Output('lift-over-other-refs-saved-input',
               'data', allow_duplicate=True),
        Input('lift-over-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),
        State('lift-over-other-refs', 'value'),
        prevent_initial_call=True
    )
    def display_lift_over_results(lift_over_submit_n_clicks, homepage_is_submitted, other_refs):
        if homepage_is_submitted and lift_over_submit_n_clicks >= 1:
            other_refs = sanitize_other_refs(other_refs)

            return {'display': 'block'}, other_refs
        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-intro', 'children'),
        Output('lift-over-results-tabs', 'children'),

        Output('lift-over-results-genomic-intervals-input', 'children'),

        Output('lift-over-overlap-table-filter', 'options'),
        Output('lift-over-overlap-table-filter', 'value'),

        State('homepage-genomic-intervals-saved-input', 'data'),
        Input('lift-over-other-refs-saved-input', 'data'),

        State('homepage-is-submitted', 'data'),

        State('lift-over-active-filter', 'data')
    )
    def display_gene_tabs(nb_intervals_str, other_refs, homepage_is_submitted, active_filter):
        if homepage_is_submitted:
            if nb_intervals_str and not is_error(get_genomic_intervals_from_input(nb_intervals_str)):
                tabs = ['Summary', 'Nb']

                other_refs = sanitize_other_refs(other_refs)

                if other_refs:
                    tabs = tabs + other_refs

                tabs_children = [dcc.Tab(label=tab, value=tab)
                                 for tab in tabs]

                if not active_filter:
                    active_filter = tabs[1:]

                gene_list_msg = [html.Span(
                    'The tabs below show the implicated genes in '), html.B('Nipponbare (Nb)')]

                if other_refs:
                    gene_list_msg += [html.Span(' and in homologous regions of '),
                                      html.B(','.join(other_refs)), html.Span('.')]
                else:
                    gene_list_msg += [html.Span('.')]

                return gene_list_msg, tabs_children, [html.B('Genomic Intervals: '), html.Span(nb_intervals_str)], tabs[1:], active_filter
            else:
                return None, None, None, [], None

        raise PreventUpdate

    # Chain callback for active tab
    @app.callback(
        Output('lift-over-results-tabs', 'active_tab'),
        Input('homepage-genomic-intervals-saved-input', 'data'),
        State('homepage-is-submitted', 'data'),
        State('lift-over-active-tab', 'data')
    )
    def switch_active_tab(nb_intervals_str, homepage_is_submitted, active_tab):
        if homepage_is_submitted:
            if not active_tab:
                return 'tab-0'

            return active_tab

        raise PreventUpdate

    @app.callback(
        Output('lift-over-nb-table', 'data'),
        Output('lift_over_nb_entire_table', 'data'),
        Input('homepage-genomic-intervals-saved-input', 'data'),
        State('homepage-is-submitted', 'data')
    )
    def get_nipponbare_gene_ids(nb_intervals_str, homepage_is_submitted):
        if homepage_is_submitted:
            if nb_intervals_str:
                nb_intervals = get_genomic_intervals_from_input(
                    nb_intervals_str)

                if not is_error(nb_intervals):
                    genes_from_Nb = get_genes_from_Nb(
                        nb_intervals)

                    return genes_from_Nb[1], genes_from_Nb[0].to_dict('records')

        raise PreventUpdate

    @app.callback(
        Output('lift-over-active-tab', 'data', allow_duplicate=True),
        Output('lift-over-active-filter', 'data', allow_duplicate=True),

        Input('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-overlap-table-filter', 'value'),

        State('homepage-is-submitted', 'data'),
        prevent_initial_call=True,
    )
    def set_lift_over_session_state(active_tab, filter_rice_variants, homepage_is_submitted):
        if homepage_is_submitted:
            return active_tab, filter_rice_variants

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-gene-intro', 'children'),
        Output('lift-over-results-table', 'columns'),
        Output('lift-over-results-table', 'data'),
        Output('lift-over-overlap-table-filter', 'style'),

        Input('homepage-genomic-intervals-saved-input', 'data'),
        Input('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-overlap-table-filter', 'value'),

        State('lift-over-results-tabs', 'children'),
        State('homepage-is-submitted', 'data')
    )
    def display_gene_tables(nb_intervals_str, active_tab, filter_rice_variants, children, homepage_is_submitted):
        if homepage_is_submitted:
            if nb_intervals_str:
                nb_intervals = get_genomic_intervals_from_input(
                    nb_intervals_str)

                if not is_error(nb_intervals):
                    SUMMARY_TAB = 'tab-0'
                    NB_TAB = 'tab-1'
                    genes_from_Nb = get_genes_from_Nb(
                        nb_intervals)
                    df_nb_complete = genes_from_Nb[0].to_dict('records')

                    columns = [{'id': key, 'name': key}
                               for key in genes_from_Nb[0].columns]

                    if active_tab == SUMMARY_TAB:
                        df_nb_raw = get_overlapping_ogi(
                            filter_rice_variants, nb_intervals)
                        df_nb = df_nb_raw.to_dict('records')

                        columns = [{'id': key, 'name': key}
                                   for key in df_nb_raw.columns]

                        return 'The table below lists the implicated genes that are common to:', \
                            columns, df_nb, {'display': 'block'}

                    elif active_tab == NB_TAB:
                        return 'The table below lists the genes overlapping the site in the Nipponbare reference.', \
                            columns, df_nb_complete, {'display': 'none'}

                    else:
                        tab_number = int(active_tab[len('tab-'):])
                        other_ref = children[tab_number]["props"]["value"]

                        df_nb_raw = get_genes_from_other_ref(
                            other_ref, nb_intervals)
                        df_nb = df_nb_raw.to_dict('records')

                        columns = [{'id': key, 'name': key}
                                   for key in df_nb_raw.columns]

                        return f'The table below lists the genes from homologous regions in {other_ref}.', \
                            columns, df_nb, {'display': 'none'}

                else:
                    return None, None, None, {'display': 'none'}
            else:
                return None, None, None, {'display': 'none'}

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-table', 'filter_query'),
        Input('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-overlap-table-filter', 'value'),
        Input('lift-over-reset-table', 'n_clicks')
    )
    def reset_table_filters(active_tab, filter_rice_variants, reset_n_clicks):
        if 'lift-over-reset-table' == ctx.triggered_id:
            if reset_n_clicks > 0:
                return ''
        else:
            return ''
