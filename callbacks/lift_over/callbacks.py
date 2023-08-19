from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from .util import *
from ..constants import Constants
const = Constants()


def init_callback(app):
    @app.callback(
        Output('lift-over-genomic-intervals-input', 'children'),
        Input('homepage-genomic-intervals-submitted-input', 'data'),
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
    def submit_lift_over_input(lift_over_submit_n_clicks, homepage_is_submitted, other_refs):
        if homepage_is_submitted and lift_over_submit_n_clicks >= 1:
            other_refs = sanitize_other_refs(other_refs)

            return True, other_refs, None, None

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-container', 'style'),
        Input('lift-over-is-submitted', 'data'),
    )
    def display_lift_over_output(lift_over_is_submitted):
        if lift_over_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    @app.callback(
        Output('lift-over-results-intro', 'children'),
        Output('lift-over-results-tabs', 'children'),

        Output('lift-over-overlap-table-filter', 'options'),
        Output('lift-over-overlap-table-filter', 'value'),

        State('homepage-genomic-intervals-submitted-input', 'data'),
        Input('lift-over-other-refs-submitted-input', 'data'),

        State('homepage-is-submitted', 'data'),

        State('lift-over-active-filter', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_gene_tabs(nb_intervals_str, other_refs, homepage_is_submitted, active_filter, lift_over_is_submitted):
        if homepage_is_submitted and lift_over_is_submitted:
            if nb_intervals_str and not is_error(get_genomic_intervals_from_input(nb_intervals_str)):
                tabs = get_tabs()

                other_refs = sanitize_other_refs(other_refs)

                if other_refs:
                    tabs = tabs + other_refs

                tabs_children = [dcc.Tab(label=tab, value=tab) if idx < len(get_tabs())
                                 else dcc.Tab(label=f'Unique to {tab}', value=tab)
                                 for idx, tab in enumerate(tabs)]

                if not active_filter:
                    active_filter = tabs[len(get_tabs()) - 1:]

                gene_list_msg = [html.Span(
                    'The tabs below show the implicated genes in '), html.B('Nipponbare (Nb)')]

                if other_refs:
                    other_refs_str = other_refs[0]
                    if len(other_refs) == 2:
                        other_refs_str += f' and {other_refs[1]}'
                    elif len(other_refs) > 2:
                        for idx, other_ref in enumerate(other_refs[1:]):
                            if idx != len(other_refs) - 2:
                                other_refs_str += f', '
                            else:
                                other_refs_str += f', and '

                            other_refs_str += f'{other_ref}'

                    gene_list_msg += [html.Span(' and in orthologous regions of '),
                                      html.B(other_refs_str)]

                gene_list_msg += [html.Span(':')]

                return gene_list_msg, tabs_children, tabs[len(get_tabs()) - 1:], active_filter
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
    def get_submitted_lift_over_session_state(active_tab, filter_rice_variants, homepage_is_submitted, lift_over_is_submitted):
        if homepage_is_submitted and lift_over_is_submitted:
            return active_tab, filter_rice_variants

        raise PreventUpdate

    @app.callback(
        Output('lift-over-other-refs', 'value'),
        State('lift-over-other-refs', 'multi'),
        State('homepage-is-submitted', 'data'),
        State('lift-over-other-refs-saved-input', 'data'),
        Input('homepage-genomic-intervals-submitted-input', 'data')
    )
    def get_input_lift_over_session_state(is_multi_other_refs, homepage_is_submitted, other_refs, *_):
        if homepage_is_submitted:
            if not is_multi_other_refs and other_refs:
                other_refs = other_refs[0]

            return other_refs

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-gene-intro', 'children'),
        Output('lift-over-overlap-table-filter', 'style'),

        Input('lift-over-results-tabs', 'active_tab'),
        State('lift-over-results-tabs', 'children'),
        State('homepage-is-submitted', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_gene_intro(active_tab, children, homepage_is_submitted, lift_over_is_submitted):
        if homepage_is_submitted and lift_over_is_submitted:
            if active_tab == get_tab_id('All Genes'):
                return 'The table below lists all the implicated genes.', {'display': 'none'}

            elif active_tab == get_tab_id('Common Genes'):
                return 'The table below lists the implicated genes that are common to:', {'display': 'block'}

            elif active_tab == get_tab_id('Nipponbare'):
                return 'The table below lists the genes overlapping the site in the Nipponbare reference.', {'display': 'none'}

            else:
                tab_number = get_tab_index(active_tab)
                other_ref = children[tab_number]['props']['value']

                return f'The table below lists the genes from homologous regions in {other_ref} that are not in Nipponbare.', {'display': 'none'}

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-statistics', 'children'),

        Input('homepage-genomic-intervals-submitted-input', 'data'),
        Input('lift-over-other-refs-submitted-input', 'data'),

        State('homepage-is-submitted', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_gene_statistics(nb_intervals_str, other_refs, homepage_is_submitted, lift_over_is_submitted):
        if homepage_is_submitted and lift_over_is_submitted:
            nb_intervals = get_genomic_intervals_from_input(
                nb_intervals_str)

            genes_from_Nb_raw = get_genes_in_Nb(nb_intervals)[0]

            gene_statistics_nb = f'{genes_from_Nb_raw["OGI"].nunique()} genes were found in Nipponbare'
            for idx, other_ref in enumerate(other_refs):
                common_genes_raw = get_common_genes([other_ref], nb_intervals)
                if idx == len(other_refs) - 1:
                    gene_statistics_nb += f', and {common_genes_raw["OGI"].nunique()} genes in {other_ref}'
                else:
                    gene_statistics_nb += f', {common_genes_raw["OGI"].nunique()} genes in {other_ref}'

            gene_statistics_nb += '. '
            gene_statistics_items = [html.Li(gene_statistics_nb)]

            if other_refs:
                other_refs.append('Nipponbare')
                genes_common = get_common_genes(other_refs, nb_intervals)
                gene_statistics_common = f'Among these, {genes_common["OGI"].nunique()} genes are common to all cultivars.'
                gene_statistics_items.append(
                    html.Li(gene_statistics_common))

                gene_statistics_other_ref = f''
                other_refs.pop()            # Remove added Nipponbare
                for idx, other_ref in enumerate(other_refs):
                    genes_from_other_ref_raw = get_unique_genes_in_other_ref(
                        other_ref, nb_intervals)

                    if len(other_refs) > 1 and idx == len(other_refs) - 1:
                        gene_statistics_other_ref += f', and '
                    elif idx != 0:
                        gene_statistics_other_ref += f', '

                    gene_statistics_other_ref += f'{genes_from_other_ref_raw["OGI"].nunique()} genes are unique to {other_ref}'

                gene_statistics_other_ref += '.'
                gene_statistics_items.append(
                    html.Li(gene_statistics_other_ref))

            return gene_statistics_items

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-table', 'columns'),
        Output('lift-over-results-table', 'data'),

        Input('homepage-genomic-intervals-submitted-input', 'data'),
        Input('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-overlap-table-filter', 'value'),
        Input('lift-over-other-refs-submitted-input', 'data'),

        State('lift-over-results-tabs', 'children'),
        State('homepage-is-submitted', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_gene_tables(nb_intervals_str, active_tab, filter_rice_variants, other_refs, children, homepage_is_submitted, lift_over_is_submitted):
        if homepage_is_submitted and lift_over_is_submitted:
            nb_intervals = get_genomic_intervals_from_input(
                nb_intervals_str)

            if active_tab == get_tab_id('All Genes'):
                all_genes_raw = get_all_genes(other_refs, nb_intervals)
                all_genes = all_genes_raw.to_dict('records')

                columns = [{'id': key, 'name': key}
                           for key in all_genes_raw.columns]

                return columns, all_genes

            elif active_tab == get_tab_id('Common Genes'):
                common_genes_raw = get_common_genes(
                    filter_rice_variants, nb_intervals)
                common_genes = common_genes_raw.to_dict('records')

                columns = [{'id': key, 'name': key}
                           for key in common_genes_raw.columns]

                return columns, common_genes

            elif active_tab == get_tab_id('Nipponbare'):
                genes_from_Nb_raw = get_genes_in_Nb(
                    nb_intervals)[0].drop(
                    ['Chromosome', 'Start', 'End', 'Strand'], axis=1)
                genes_from_Nb = genes_from_Nb_raw.to_dict('records')

                columns = [{'id': x, 'name': x, 'presentation': 'markdown'} if x == 'UniProtKB/Swiss-Prot'
                           else {'id': x, 'name': x} for x in genes_from_Nb_raw.columns]

                return columns, genes_from_Nb

            else:
                tab_number = get_tab_index(active_tab)
                other_ref = children[tab_number]['props']['value']

                genes_from_other_ref_raw = get_unique_genes_in_other_ref(
                    other_ref, nb_intervals).drop(
                    ['Chromosome', 'Start', 'End', 'Strand'], axis=1)
                genes_from_other_ref = genes_from_other_ref_raw.to_dict(
                    'records')

                columns = [{'id': key, 'name': key}
                           for key in genes_from_other_ref_raw.columns]

                return columns, genes_from_other_ref

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
        State('homepage-genomic-intervals-submitted-input', 'data')
    )
    def download_lift_over_table_to_csv(download_n_clicks, lift_over_df, genomic_intervals):
        if download_n_clicks >= 1:
            df = pd.DataFrame(lift_over_df)
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Gene List and Lift-Over.csv', index=False)

        raise PreventUpdate
