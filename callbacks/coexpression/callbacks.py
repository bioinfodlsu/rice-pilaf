from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from .util import *


def init_callback(app):
    @app.callback(
        Output('coexpression-parameter-slider', 'marks'),
        Output('coexpression-parameter-slider', 'value'),
        Input('coexpression-clustering-algo', 'value')
    )
    def set_parameter_slider(algo):
        return get_parameters_for_algo(algo), ALGOS_DEFAULT_PARAM[algo] * ALGOS_MULT[algo]

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
                gene_ids, genomic_intervals, algo, parameters)

            first_module = 'No enriched modules found'
            if enriched_modules:
                first_module = enriched_modules[0]

            return {'display': 'block'}, enriched_modules, first_module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-pathways', 'data'),
        Output('coexpression-pathways', 'columns'),
        Input('coexpression-modules-pathway', 'active_tab'),
        Input('coexpression-modules', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value'),
    )
    def display_pathways(active_tab, module, algo, parameters):
        module_idx = module.split(' ')[1]
        table, empty = convert_to_df(active_tab, module_idx, algo, parameters)

        if not empty:
            columns = [{'id': x, 'name': x, 'presentation': 'markdown'} if x ==
                       'View on KEGG' else {'id': x, 'name': x} for x in table.columns]
        else:
            columns = [{'id': x, 'name': x}
                       for x in table.columns]

        return table.to_dict('records'), columns

    @app.callback(
        Output('coexpression-module-graph', 'elements'),
        Output('coexpression-module-graph', 'style'),
        Input('coexpression-modules', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value')
    )
    def display_module_graph(module, algo, parameters):
        return load_module_graph(module, algo, parameters)
