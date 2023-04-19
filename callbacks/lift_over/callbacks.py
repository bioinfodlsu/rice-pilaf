from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from .util import *


def init_callback(app):
    @app.callback(
        Output('input-error', 'children'),
        Output('input-error', 'style'),
        Output('lift-over-is-submitted', 'data'),

        Output('lift-over-genomic-intervals-saved-input', 'data'),
        Output('lift-over-other-refs-saved-input', 'data'),

        Input('lift-over-submit', 'n_clicks'),
        State('lift-over-genomic-intervals', 'value'),
        
        State('lift-over-other-refs', 'value')
    )
    def parse_input(n_clicks, nb_intervals_str, other_refs):
        if n_clicks >= 1:
            intervals = get_genomic_intervals_from_input(nb_intervals_str)
            if is_error(intervals):
                return [f'Error encountered while parsing genomic interval {intervals[1]}', html.Br(), get_error_message(intervals[0])], \
                    {'display': 'block'}, str(True), nb_intervals_str, other_refs
            else:
                return None, {'display': 'none'}, str(True), nb_intervals_str, other_refs

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-intro', 'children'),
        Output('lift-over-results-tabs', 'children'),
        Input('lift-over-submit', 'n_clicks'),
        State('lift-over-is-submitted', 'data'),
        State('lift-over-other-refs', 'value'),
        State('lift-over-genomic-intervals', 'value'),

        State('lift-over-other-refs-saved-input', 'data'),
        State('lift-over-genomic-intervals-saved-input', 'data')
    )
    def display_gene_tabs(n_clicks, is_submitted, other_refs, nb_intervals_str, orig_other_refs, orig_nb_intervals_str):
        if n_clicks >= 1 or has_user_submitted(is_submitted):

            if n_clicks == 0 and orig_nb_intervals_str != nb_intervals_str:
                nb_intervals_str = orig_nb_intervals_str
            
            if not is_error(get_genomic_intervals_from_input(nb_intervals_str)):
                tabs = ['NB']
                    
                if orig_other_refs or other_refs:
                    if n_clicks == 0 and orig_other_refs != other_refs:
                        tabs = tabs + orig_other_refs
                    else:
                        tabs = tabs + other_refs
                #if other_refs:
                #    tabs = tabs + other_refs

                tabs_children = [dcc.Tab(label=tab, value=tab) for tab in tabs]

                return 'The tabs below show a list of genes in Nipponbare and in homologous regions of the other references you chose', \
                    tabs_children

            else:
                return None, None

        raise PreventUpdate

    # Chain callback for active tab
    @app.callback(
        Output('lift-over-results-tabs', 'active_tab'),
        Input('lift-over-submit', 'n_clicks'),
        State('lift-over-is-submitted', 'data'),
        State('lift-over-genomic-intervals', 'value'),
        State('lift-over-active-tab', 'data')
    )
    def switch_active_tab(n_clicks, is_submitted, nb_intervals_str, active_tab):
        if n_clicks >= 1 or has_user_submitted(is_submitted):
            if not active_tab or n_clicks >= 1:
                return 'tab-0'

            return active_tab

        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-gene-intro', 'children'),
        Output('lift-over-results-table', 'data'),
        Output('lift-over-active-tab', 'data'),
        Input('lift-over-submit', 'n_clicks'),
        Input('lift-over-results-tabs', 'active_tab'),
        State('lift-over-results-tabs', 'children'),
        State('lift-over-is-submitted', 'data'),
        State('lift-over-genomic-intervals', 'value'),

        State('lift-over-genomic-intervals-saved-input', 'data')
    )
    def display_gene_tables(n_clicks, active_tab, children, is_submitted, nb_intervals_str, orig_nb_intervals_str):
        if n_clicks >= 1 or has_user_submitted(is_submitted):
            
            if n_clicks == 0 and orig_nb_intervals_str != nb_intervals_str:
               nb_intervals = get_genomic_intervals_from_input(orig_nb_intervals_str)

            else:
               nb_intervals = get_genomic_intervals_from_input(nb_intervals_str)
               
            if not is_error(nb_intervals):
                if active_tab == 'tab-0':
                    df_nb = get_genes_from_Nb(nb_intervals).to_dict('records')

                    return 'Genes overlapping the site in the Nipponbare reference', df_nb, active_tab

                else:
                    tab_number = int(active_tab[len('tab-'):])
                    other_ref = children[tab_number]["props"]["value"]
                    df_nb = get_genes_from_other_ref(
                        other_ref, nb_intervals).to_dict('records')

                    return f'Genes from homologous regions in {other_ref}', df_nb, active_tab

            else:
                return None, None, None

        raise PreventUpdate
    
    @app.callback(
        Output('lift-over-results-table', 'css'),
        Input('lift-over-results-table', 'derived_virtual_data')
    )
    def display_export_button(data):
        if data == []:
            return [{"selector": ".export", "rule": "display:none"}]
        else:
            return [{"selector": ".export", "rule": "display:block"}]
