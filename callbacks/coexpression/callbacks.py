import networkx as nx
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from .util import *


def init_callback(app):
    @app.callback(
        Output('coexpression-modules', 'style'),
        Output('coexpression-modules', 'options'),
        Output('coexpression-modules', 'value'),
        Input('lift-over-nb-table', 'data'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value'),
        State('lift-over-is-submitted', 'data')
    )
    def perform_module_enrichment(gene_ids, genomic_intervals, algo, parameters, is_submitted):
        if is_submitted:
            enriched_modules = do_module_enrichment_analysis(
                gene_ids, genomic_intervals, algo, int(float(parameters) * 100))

            first_module = 'No enriched modules found'
            if enriched_modules:
                first_module = enriched_modules[0]

            return {'display': 'block'}, enriched_modules, first_module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-pathways', 'data'),
        Input('coexpression-modules-pathway', 'active_tab'),
        Input('coexpression-modules', 'value')
    )
    def display_pathways(active_tab, module):
        module_idx = module.split(' ')[1]
        return convert_to_df(active_tab, module_idx).to_dict('records')

    @app.callback(
        Output('coexpression-module-graph', 'elements'),
        Output('coexpression-module-graph', 'style'),
        Input('coexpression-modules', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value')
    )
    def display_module_graph(module, algo, parameters):
        module_idx = module.split(' ')[1]
        coexpress_nw = f'{const.NETWORKS_DISPLAY_OS_CX}/{algo}/modules/{int(float(parameters) * 100)}/module-{module_idx}.tsv'
        G = nx.read_edgelist(coexpress_nw, data=(("coexpress", float),))

        return nx.cytoscape_data(G)['elements'], {'visibility': 'visible', 'width': '100%', 'height': '100vh'},
