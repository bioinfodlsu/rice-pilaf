from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from collections import namedtuple
from .util import *

Parameter_module = namedtuple('Parameter_module', [
                              'param_slider_marks', 'param_slider_value', 'param_module'])


def init_callback(app):
    @app.callback(
        Output('coexpression-parameter-slider', 'marks'),
        Output('coexpression-parameter-slider', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-module-saved-input', 'data')
    )
    def set_parameter_slider(algo, parameter_module):
        if parameter_module and algo in parameter_module:
            return parameter_module[algo]['param_slider_marks'], parameter_module[algo]['param_slider_value']

        return get_parameters_for_algo(algo), ALGOS_DEFAULT_PARAM[algo] * ALGOS_MULT[algo]

    @app.callback(
        Output('coexpression-modules', 'style'),
        Output('coexpression-modules', 'options'),
        Output('coexpression-modules', 'value'),
        Input('lift-over-nb-table', 'data'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-parameter-module-saved-input', 'data')
    )
    def perform_module_enrichment(implicated_gene_ids, genomic_intervals, algo, parameters, is_submitted, parameter_module):
        if is_submitted:
            enriched_modules = do_module_enrichment_analysis(
                implicated_gene_ids, genomic_intervals, algo, parameters)

            first_module = 'No enriched modules found'

            if parameter_module and algo in parameter_module:
                if parameter_module[algo]['param_module']:
                    first_module = parameter_module[algo]['param_module']

            else:
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
        Input('lift-over-nb-table', 'data'),
        Input('coexpression-modules', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value')
    )
    def display_module_graph(implicated_gene_ids, module, algo, parameters):
        return load_module_graph(
            implicated_gene_ids, module, algo, parameters)

    @app.callback(
        Output('coexpression-clustering-algo-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-parameter-module-saved-input',
               'data', allow_duplicate=True),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value'),
        Input('coexpression-modules', 'value'),
        State('coexpression-parameter-slider', 'marks'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-parameter-module-saved-input', 'data'),
        prevent_initial_call=True
    )
    def set_coexpression_session_state(algo, parameter_value, module, parameter_mark, is_submitted, parameter_module):
        if is_submitted:
            paramater_module_value = Parameter_module(
                parameter_mark, parameter_value, module)._asdict()

            if parameter_module:
                parameter_module[algo] = paramater_module_value

            else:
                parameter_module = {algo: paramater_module_value}

            return algo, parameter_module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-clustering-algo', 'value'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-clustering-algo-saved-input', 'data')
    )
    def display_selected_clustering_algo(nb_intervals_str, is_submitted, algo):
        if is_submitted:
            if not algo:
                return 'clusterone'

            return algo

        raise PreventUpdate
