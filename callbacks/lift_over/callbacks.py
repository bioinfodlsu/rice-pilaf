from dash import dcc, Input, Output, State, html
from dash.exceptions import PreventUpdate

from .util import *

def init_callback(app):
    @app.callback(
        Output('input-error', 'children'),
        Output('input-error', 'style'),
        Input('lift-over-submit', 'n_clicks'),
        State('lift-over-genomic-intervals', 'value')
    )
    def parse_input(n_clicks, nb_intervals_str):
        if n_clicks >= 1:
            intervals = get_genomic_intervals_from_input(nb_intervals_str)
            if is_error(intervals):    
                return [f'Error encountered while parsing genomic interval {intervals[1]}', html.Br(), get_error_message(intervals[0])], \
                    {'display': 'block'}
            else:
                return None, {'display': 'none'}
            
        raise PreventUpdate

    @app.callback(
        Output('lift-over-results-intro', 'children'),
        Output('lift-over-results-tabs', 'children'),
        Input('lift-over-submit', 'n_clicks'),
        State('lift-over-other-refs', 'value'),
        State('lift-over-genomic-intervals', 'value')
    )
    def display_gene_tabs(n_clicks, other_refs, nb_intervals_str):
        if n_clicks >= 1:
            if not is_error(get_genomic_intervals_from_input(nb_intervals_str)):
                tabs = ['NB']
                if other_refs:
                    tabs = tabs + other_refs
                
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
    )
    def switch_active_tab(n_clicks):
        if n_clicks >= 1:
            return 'tab-0'
        
        raise PreventUpdate
    
    @app.callback(
        Output('lift-over-results-gene-intro', 'children'),
        Output('lift-over-results-table', 'data'),
        Input('lift-over-submit', 'n_clicks'),
        Input('lift-over-results-tabs', 'active_tab'),
        State('lift-over-results-tabs', 'children'),
        State('lift-over-genomic-intervals', 'value')
    )
    def display_gene_tables(n_clicks, active_tab, children, nb_intervals_str):
        if n_clicks >= 1:
            nb_intervals = get_genomic_intervals_from_input(nb_intervals_str)

            if not is_error(nb_intervals):
                if active_tab == 'tab-0':
                    df_nb = get_genes_from_Nb(nb_intervals).to_dict('records')

                    return 'Genes overlapping the site in the Nipponbare reference', df_nb
                
                else:
                    tab_number = int(active_tab[len('tab-'):])
                    other_ref = children[tab_number]["props"]["value"]
                    df_nb = get_genes_from_other_ref(other_ref, nb_intervals).to_dict('records')

                    return f'Genes from homologous regions in {other_ref}', df_nb
                
            else:
                return None, None
            
        raise PreventUpdate

        
    
    
        

