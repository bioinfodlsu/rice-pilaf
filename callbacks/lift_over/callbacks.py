from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from .util import *
from ..constants import Constants
const = Constants()


def init_callback(app):
    @app.callback(
        Output('lift-over-genomic-intervals-input', 'children'),
        Input('homepage-genomic-intervals-saved-input', 'data'),
        State('homepage-is-submitted', 'data'),
    )
    def display_input(nb_intervals_str, homepage_is_submitted):
        if homepage_is_submitted:
            if nb_intervals_str and not is_error(
                    get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('lift-over-is-submitted', 'data', allow_duplicate=True),
        Output('lift-over-other-refs-submitted-input',
               'data', allow_duplicate=True),
        Output('lift-over-active-tab', 'data', allow_duplicate=True),
        Output('lift-over-active-filter', 'data', allow_duplicate=True),
        Input('lift-over-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),
        State('lift-over-other-refs', 'value'),
        prevent_initial_call=True
    )
    def display_lift_over_results(lift_over_submit_n_clicks, homepage_is_submitted, other_refs):
        if homepage_is_submitted and lift_over_submit_n_clicks >= 1:
            other_refs = sanitize_other_refs(other_refs)

            return True, other_refs, None, None

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-container', 'style'),
        Input('lift-over-is-submitted', 'data'),
    )
    def display_submitted_lift_over_results(lift_over_is_submitted):
        if lift_over_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    @app.callback(
        Output('lift-over-results-intro', 'children'),
        Output('lift-over-results-tabs', 'children'),

        Output('lift-over-overlap-table-filter', 'options'),
        Output('lift-over-overlap-table-filter', 'value'),

        State('homepage-genomic-intervals-saved-input', 'data'),
        Input('lift-over-other-refs-submitted-input', 'data'),

        State('homepage-is-submitted', 'data'),

        State('lift-over-active-filter', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_gene_tabs(nb_intervals_str, other_refs, homepage_is_submitted, active_filter, lift_over_is_submitted):
        if homepage_is_submitted and lift_over_is_submitted:
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

                return gene_list_msg, tabs_children, tabs[1:], active_filter
            else:
                return None, None, [], None

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-tabs', 'active_tab'),
        State('homepage-is-submitted', 'data'),
        State('lift-over-active-tab', 'data'),
        State('lift-over-is-submitted', 'data'),
        Input('lift-over-other-refs-submitted-input', 'data')
    )
    def display_active_tab(homepage_is_submitted, saved_active_tab, lift_over_is_submitted, *_):
        if homepage_is_submitted and lift_over_is_submitted:
            if not saved_active_tab:
                return 'tab-0'

            return saved_active_tab

        raise PreventUpdate

    @app.callback(
        Output('lift-over-other-refs-saved-input',
               'data', allow_duplicate=True),
        Input('lift-over-other-refs', 'value'),
        State('homepage-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def set_input_lift_over_session_state(other_refs, homepage_is_submitted):
        if homepage_is_submitted:
            return other_refs

        raise PreventUpdate

    @app.callback(
        Output('lift-over-active-tab', 'data', allow_duplicate=True),
        Output('lift-over-active-filter', 'data', allow_duplicate=True),

        Input('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-overlap-table-filter', 'value'),

        State('homepage-is-submitted', 'data'),
        State('lift-over-is-submitted', 'data'),
        prevent_initial_call=True,
    )
    def set_submitted_lift_over_session_state(active_tab, filter_rice_variants, homepage_is_submitted, lift_over_is_submitted):
        if homepage_is_submitted and lift_over_is_submitted:
            return active_tab, filter_rice_variants

        raise PreventUpdate

    @app.callback(
        Output('lift-over-other-refs', 'value'),
        State('lift-over-other-refs', 'multi'),
        State('homepage-is-submitted', 'data'),
        State('lift-over-other-refs-saved-input', 'data'),
        Input('homepage-genomic-intervals-saved-input', 'data')
    )
    def get_input_lift_over_session_state(is_multi_other_refs, homepage_is_submitted, other_refs, *_):
        if homepage_is_submitted:
            if not is_multi_other_refs and other_refs:
                other_refs = other_refs[0]

            return other_refs

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
        State('homepage-is-submitted', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_gene_tables(nb_intervals_str, active_tab, filter_rice_variants, children, homepage_is_submitted, lift_over_is_submitted):
        if homepage_is_submitted and lift_over_is_submitted:
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

        Input('lift-over-reset-table', 'n_clicks'),
        Input('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-overlap-table-filter', 'value')
    )
    def reset_table_filters(*_):
        return ''


    @app.callback(
        Output('lift-over-download-df-to-csv', 'data'),
        Input('lift-over-export-table', 'n_clicks'),
        State('lift-over-results-table', 'data'),
        State('homepage-genomic-intervals-saved-input', 'data')
    )
    def download_lift_over_table_to_csv(download_n_clicks, lift_over_df, genomic_intervals):
        if download_n_clicks >= 1:
            df = pd.DataFrame(lift_over_df)
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Gene List and Lift-Over.csv', index=False)