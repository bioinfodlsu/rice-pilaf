from dash import Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util

Input_parameter_module = namedtuple('Input_parameter_module', [
    'param_slider_marks', 'param_slider_value'])

Submitted_parameter_module = namedtuple('Submitted_parameter_module', [
    'param_slider_marks', 'param_slider_value', 'param_module', 'layout'])


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
        Output('coexpression-results-container',
               'style',  allow_duplicate=True),
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
            paramater_module_value = Submitted_parameter_module(
                submitted_slider_marks, submitted_slider_value, '', 'circle')._asdict()

            submitted_parameter_module = {
                submitted_algo: paramater_module_value}

            return {'display': 'block'}, True, submitted_algo, submitted_parameter_module

        raise PreventUpdate

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

    """
    @app.callback(
        Output('coexpression-module-graph', 'elements'),
        Output('coexpression-module-graph', 'layout'),
        Output('coexpression-module-graph', 'style'),
        Output('coexpression-graph-container', 'style'),

        State('lift-over-nb-table', 'data'),
        # State('coexpression-graph-layout', 'value'),

        Input('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data')
    )
    def hide_table_graph(implicated_gene_ids, submitted_algo, coexpression_is_submitted, submitted_parameter_module):
        if coexpression_is_submitted:
            parameters = submitted_parameter_module[submitted_algo]['param_slider_value']
            layout = submitted_parameter_module[submitted_algo]['layout']

            return load_module_graph(
                implicated_gene_ids, None, submitted_algo, parameters, layout) + ({'visibility': 'hidden'}, )

        raise PreventUpdate
    """
    @app.callback(
        Output('coexpression-modules', 'style'),
        Output('coexpression-modules', 'options'),
        Output('coexpression-modules', 'value'),
        State('lift-over-nb-table', 'data'),
        State('lift-over-genomic-intervals-saved-input', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def perform_module_enrichment(implicated_gene_ids, genomic_intervals, submitted_algo, is_submitted, submitted_parameter_module, coexpression_is_submitted):
        if is_submitted:
            if coexpression_is_submitted:
                parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

                enriched_modules = do_module_enrichment_analysis(
                    implicated_gene_ids, genomic_intervals, submitted_algo, parameters)

                first_module = 'No enriched modules found'

                if enriched_modules:
                    first_module = enriched_modules[0]

                if submitted_parameter_module and submitted_algo in submitted_parameter_module:
                    if submitted_parameter_module[submitted_algo]['param_module']:
                        first_module = submitted_parameter_module[submitted_algo]['param_module']

                return {'display': 'block'}, enriched_modules, first_module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-pathways', 'data'),
        Output('coexpression-pathways', 'columns'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        Input('coexpression-modules-pathway', 'active_tab'),
        Input('coexpression-modules', 'value'),
        State('coexpression-submitted-parameter-module', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def display_pathways(submitted_algo, active_tab, module, submitted_parameter_module, coexpression_is_submitted):
        if coexpression_is_submitted:
            parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

            try:
                module_idx = module.split(' ')[1]
                table, empty = convert_to_df(
                    active_tab, module_idx, submitted_algo, parameters)
            except:
                table, empty = convert_to_df(
                    active_tab, None, submitted_algo, parameters)

            if not empty:
                columns = [{'id': x, 'name': x, 'presentation': 'markdown'} if x ==
                           'View on KEGG' else {'id': x, 'name': x} for x in table.columns]
            else:
                columns = [{'id': x, 'name': x}
                           for x in table.columns]

            return table.to_dict('records'), columns

        raise PreventUpdate

    @app.callback(
        Output('coexpression-module-graph', 'elements', allow_duplicate=True),
        Output('coexpression-module-graph', 'layout', allow_duplicate=True),
        Output('coexpression-module-graph', 'style', allow_duplicate=True),
        Output('coexpression-graph-container', 'style', allow_duplicate=True),

        State('lift-over-nb-table', 'data'),
        Input('coexpression-modules', 'value'),

        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),

        Input('coexpression-graph-layout', 'value'),
        Input('coexpression-reset-graph', 'n_clicks'),
        State('coexpression-is-submitted', 'data'),

        prevent_initial_call=True
    )
    def display_table_graph(implicated_gene_ids, module, submitted_algo, submitted_parameter_module, layout, reset_graph_n_clicks, coexpression_is_submitted):
        if coexpression_is_submitted:
            if submitted_algo and submitted_algo in submitted_parameter_module:
                parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

                return load_module_graph(
                    implicated_gene_ids, module, submitted_algo, parameters, layout) + ({'visibility': 'visible'}, )

        raise PreventUpdate

    @app.callback(
        Output('coexpression-clustering-algo-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-parameter-module-saved-input',
               'data', allow_duplicate=True),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value'),
        State('coexpression-parameter-slider', 'marks'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-parameter-module-saved-input', 'data'),
        prevent_initial_call=True
    )
    def set_input_coexpression_session_state(algo, parameter_value, parameter_mark, is_submitted, input_parameter_module):
        if is_submitted:
            input_paramater_module_value = Input_parameter_module(
                parameter_mark, parameter_value)._asdict()

            if input_parameter_module:
                input_parameter_module[algo] = input_paramater_module_value

            else:
                input_parameter_module = {algo: input_paramater_module_value}

            return algo, input_parameter_module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-submitted-parameter-module',
               'data', allow_duplicate=True),
        Input('coexpression-modules', 'value'),
        Input('coexpression-graph-layout', 'value'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('lift-over-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
        prevent_initial_call=True
    )
    def set_submitted_coexpression_session_state(module, layout, submitted_algo, is_submitted, submitted_parameter_module):
        if is_submitted:
            if submitted_parameter_module and submitted_algo in submitted_parameter_module:
                submitted_parameter_module[submitted_algo]['param_module'] = module
                submitted_parameter_module[submitted_algo]['layout'] = layout

                return submitted_parameter_module

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

    @app.callback(
        Output('coexpression-graph-layout', 'value'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data')
    )
    def display_selected_graph_layout(submitted_algo, coexpression_is_submitted, submitted_parameter_module):
        if coexpression_is_submitted:
            if submitted_algo and submitted_algo in submitted_parameter_module:
                if submitted_parameter_module[submitted_algo]['layout']:
                    return submitted_parameter_module[submitted_algo]['layout']

            return 'circle'

        raise PreventUpdate

    @app.callback(
        Output('coexpression-results-container',
               'style', allow_duplicate=True),
        Input('coexpression-clustering-algo-saved-input', 'data'),
        State('coexpression-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def display_submitted_results(algo, coexpression_is_submitted):
        if coexpression_is_submitted:
            return {'display': 'block'}

        raise PreventUpdate

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
