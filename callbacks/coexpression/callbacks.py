from dash import Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util

Parameter_module = namedtuple('Parameter_module', [
                              'param_slider_marks', 'param_slider_value', 'param_module'])


def init_callback(app):
    @app.callback(
        Output('coexpression-genomic-intervals-input', 'children'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        State('lift-over-is-submitted', 'data'),
    )
    def display_input(nb_intervals_str, is_submitted):
        if is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Genomic Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('coexpression-results-container', 'style'),
        Output('coexpression-is-submitted', 'data', allow_duplicate=True),
        Output('coexpression-submitted-clustering-algo',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-parameter-module',
               'data', allow_duplicate=True),
        Input('coexpression-submit', 'n_clicks'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-slider', 'marks'),
        State('coexpression-parameter-slider', 'value'),
        prevent_initial_call=True
    )
    def display_coexpression_results(coexpression_submit_n_clicks, is_submitted, submitted_algo, submitted_slider_marks, submitted_slider_value):
        if is_submitted and coexpression_submit_n_clicks >= 1:
            paramater_module_value = Parameter_module(
                submitted_slider_marks, submitted_slider_value, '')._asdict()

            coexpression_submitted_parameter_module = {
                submitted_algo: paramater_module_value}

            return {'display': 'block'}, True, submitted_algo, coexpression_submitted_parameter_module

        else:
            return {'display': 'none'}, False, None, None

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
        Input('coexpression-submit', 'n_clicks'),
        State('lift-over-nb-table', 'data'),
        State('lift-over-genomic-intervals-saved-input', 'data'),
        State('coexpression-clustering-algo', 'value'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-parameter-slider', 'value'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-parameter-module-saved-input', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def perform_module_enrichment(coexpression_n_clicks, implicated_gene_ids, genomic_intervals, algo, submitted_algo, parameters, is_submitted, parameter_module, submitted_parameter_module, coexpression_is_submitted):
        if is_submitted:
            if coexpression_n_clicks >= 1:
                enriched_modules = do_module_enrichment_analysis(
                    implicated_gene_ids, genomic_intervals, algo, parameters)

                if enriched_modules:
                    first_module = enriched_modules[0]
                else:
                    first_module = 'hello'

                return {'display': 'block'}, enriched_modules, first_module

            elif coexpression_is_submitted:
                # TODO: maybe theres a way to improve lines 67-73
                # (Potential bug: submitted algo or submitted parameter module is missing)
                # --> if any one of them are missing, it will use the latest clicked clustering algo or saved parameter module
                # if coexpression_is_submitted:
                #    if submitted_algo:
                #        algo = submitted_algo

                #    if submitted_parameter_module:
                #        parameter_module = submitted_parameter_module

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
        Input('coexpression-submit', 'n_clicks'),
        Input('coexpression-modules-pathway', 'active_tab'),
        Input('coexpression-modules', 'value'),
        State('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-slider', 'value'),
    )
    def display_pathways(coexpression_n_clicks, active_tab, module, algo, parameters):
        if coexpression_n_clicks >= 1:
            try:
                module_idx = module.split(' ')[1]
                table, empty = convert_to_df(
                    active_tab, module_idx, algo, parameters)
            except:
                table, empty = convert_to_df(
                    active_tab, None, algo, parameters)

            if not empty:
                columns = [{'id': x, 'name': x, 'presentation': 'markdown'} if x ==
                           'View on KEGG' else {'id': x, 'name': x} for x in table.columns]
            else:
                columns = [{'id': x, 'name': x}
                           for x in table.columns]

            return table.to_dict('records'), columns

        raise PreventUpdate

    @app.callback(
        Output('coexpression-module-graph', 'elements'),
        Output('coexpression-module-graph', 'layout'),
        Output('coexpression-module-graph', 'style'),
        State('lift-over-nb-table', 'data'),
        State('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-slider', 'value'),
        State('coexpression-graph-layout', 'value'),
        Input('coexpression-submit', 'n_clicks'),
        prevent_initial_call='initial_duplicate'
    )
    def hide_module_graph(implicated_gene_ids, algo, parameters, layout, coexpression_n_clicks):
        if coexpression_n_clicks >= 1:
            return load_module_graph(
                implicated_gene_ids, None, algo, parameters, layout)

        raise PreventUpdate

    @app.callback(
        Output('coexpression-module-graph', 'elements', allow_duplicate=True),
        Output('coexpression-module-graph', 'layout', allow_duplicate=True),
        Output('coexpression-module-graph', 'style', allow_duplicate=True),
        State('lift-over-nb-table', 'data'),
        Input('coexpression-modules', 'value'),
        State('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-slider', 'value'),
        Input('coexpression-graph-layout', 'value'),
        Input('coexpression-reset-graph', 'n_clicks'),
        prevent_initial_call='initial_duplicate'
    )
    def display_module_graph(implicated_gene_ids, module, algo, parameters, layout, reset_graph_n_clicks):
        if 'coexpression-reset-graph' == ctx.triggered_id:
            if reset_graph_n_clicks > 0:
                return load_module_graph(
                    implicated_gene_ids, module, algo, parameters, layout)

        return load_module_graph(
            implicated_gene_ids, module, algo, parameters, layout)

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
    def set_input_coexpression_session_state(algo, parameter_value, module, parameter_mark, is_submitted, parameter_module):
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
        Output('coexpression-submitted-parameter-module',
               'data', allow_duplicate=True),
        Input('coexpression-submit', 'n_clicks'),
        Input('coexpression-modules', 'value'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
        prevent_initial_call=True
    )
    def set_submitted_coexpression_session_state_module(coexpression_n_clicks, module, algo, is_submitted, parameter_module):
        if is_submitted and coexpression_n_clicks >= 1:
            if parameter_module and algo in parameter_module:
                parameter_module[algo]['param_module'] = module

                return parameter_module

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
    """
    @app.callback(
        Output('coexpression-submit', 'n_clicks'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def display_submitted_results(nb_intervals_str, coexpression_is_submitted):
        if coexpression_is_submitted:
            return 1

        else:
            return 0
    """

    @app.callback(
        Output('coexpression-clustering-algo-modal', 'is_open'),
        Input('coexpression-clustering-algo-tooltip', 'n_clicks')
    )
    def open_modals(tooltip_n_clicks):
        if tooltip_n_clicks > 0:
            return True

    @app.callback(
        Output('coexpression-pathways', 'filter_query'),
        Input('coexpression-modules-pathway', 'active_tab'),
        Input('coexpression-reset-table', 'n_clicks')
    )
    def reset_table_filters(active_tab, reset_n_clicks):
        if 'coexpression-reset-table' == ctx.triggered_id:
            if reset_n_clicks > 0:
                return ''
        else:
            return ''
