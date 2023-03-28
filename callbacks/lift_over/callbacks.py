from dash import dcc, Input, Output
from dash.exceptions import PreventUpdate

from .util import to_genomic_interval, get_genes_from_Nb, get_genes_from_other_ref

def init_callback(app):
    @app.callback(
        Output('lift-over-results-intro', 'children'),
        Output('lift-over-results-tabs', 'children'),
        Input('lift-over-submit', 'n_clicks'),
        Input('lift-over-other-refs', 'value')
    )
    def display_gene_tabs(n_clicks, other_refs):
        if n_clicks >= 1:
            tabs = ['NB']
            if other_refs:
                tabs = tabs + other_refs

            tabs_children = [dcc.Tab(label=tab, value=tab) for tab in tabs]

            return 'The tabs below show a list of genes in Nipponbare and in homologous regions of the other references you chose', \
                tabs_children
        
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
        Input('lift-over-results-tabs', 'children'),
        Input('lift-over-genomic-intervals', 'value')
    )
    def display_gene_tables(n_clicks, active_tab, children, nb_intervals_str):
        if n_clicks >= 1:
            nb_intervals = []
            for interval_str in nb_intervals_str.split(";"):
                nb_intervals.append(to_genomic_interval(interval_str))

            if active_tab == 'tab-0':
                df_nb = get_genes_from_Nb(nb_intervals).to_dict('records')
                return 'Genes overlapping the site in the Nipponbare reference', df_nb
            
            else:
                Nb_intervals = []
                for interval_str in nb_intervals_str.split(";"):
                    Nb_intervals.append(to_genomic_interval(interval_str))

                tab_number = int(active_tab[len('tab-'):])
                other_ref = children[tab_number]["props"]["value"]
                df_nb = get_genes_from_other_ref(other_ref, Nb_intervals).to_dict('records')

                return f'Genes from homologous regions in {other_ref}', df_nb
            
        raise PreventUpdate

