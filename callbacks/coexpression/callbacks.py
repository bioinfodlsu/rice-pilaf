from dash import Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util

Input_parameter_module = namedtuple('Input_parameter_module', [
    'param_slider_marks', 'param_slider_value'])

Submitted_parameter_module = namedtuple('Submitted_parameter_module', [
    'param_slider_marks', 'param_slider_value', 'param_module', 'layout', 'pathway_active_tab'])


def init_callback(app):
    @app.callback(
        Output('coexpression-genomic-intervals-input', 'children'),
        State('homepage-genomic-intervals-submitted-input', 'data'),
        Input('homepage-is-submitted', 'data'),
        Input('coexpression-submit', 'n_clicks')
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('coexpression-is-submitted', 'data', allow_duplicate=True),
        Output('coexpression-submitted-network',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-clustering-algo',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-parameter-module',
               'data', allow_duplicate=True),

        Input('coexpression-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),

        State('coexpression-network', 'value'),
        State('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-slider', 'marks'),
        State('coexpression-parameter-slider', 'value'),
        prevent_initial_call=True
    )
    def submit_coexpression_input(coexpression_submit_n_clicks, homepage_is_submitted, submitted_network, submitted_algo, submitted_slider_marks, submitted_slider_value):
        if homepage_is_submitted and coexpression_submit_n_clicks >= 1:
            paramater_module_value = Submitted_parameter_module(
                submitted_slider_marks, submitted_slider_value, '', 'circle', 'tab-0')._asdict()

            submitted_parameter_module = {
                submitted_algo: paramater_module_value}

            return True, submitted_network, submitted_algo, submitted_parameter_module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-results-container', 'style'),
        Input('coexpression-is-submitted', 'data'),
    )
    def display_coexpression_output(coexpression_is_submitted):
        if coexpression_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    @app.callback(
        Output('coexpression-parameter-slider', 'marks'),
        Output('coexpression-parameter-slider', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-module-saved-input', 'data')
    )
    def set_parameter_slider(algo, parameter_module):
        if parameter_module and algo in parameter_module:
            return parameter_module[algo]['param_slider_marks'], parameter_module[algo]['param_slider_value']

        return get_parameters_for_algo(algo), module_detection_algos[algo].default_param * module_detection_algos[algo].multiplier

    @app.callback(
        Output('coexpression-module-graph', 'elements'),
        Output('coexpression-module-graph', 'layout'),
        Output('coexpression-module-graph', 'style'),
        Output('coexpression-graph-container', 'style'),

        State('lift-over-nb-table', 'data'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
    )
    def hide_table_graph(implicated_gene_ids, submitted_network, submitted_algo, coexpression_is_submitted, submitted_parameter_module):
        if coexpression_is_submitted:
            if submitted_algo and submitted_algo in submitted_parameter_module:
                parameters = submitted_parameter_module[submitted_algo]['param_slider_value']
                layout = submitted_parameter_module[submitted_algo]['layout']

                return load_module_graph(
                    implicated_gene_ids, None, submitted_network, submitted_algo, parameters, layout) + ({'visibility': 'hidden'}, )

        raise PreventUpdate

    @app.callback(
        Output('coexpression-modules', 'options'),
        Output('coexpression-modules', 'value'),
        Output('coexpression-results-module-tabs-container', 'style'),
        Output('coexpression-module-stats', 'children'),

        State('lift-over-nb-table', 'data'),
        State('homepage-genomic-intervals-submitted-input', 'data'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('homepage-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def perform_module_enrichment(implicated_gene_ids, genomic_intervals, submitted_network, submitted_algo, homepage_is_submitted, submitted_parameter_module, coexpression_is_submitted):
        if homepage_is_submitted:
            if coexpression_is_submitted:
                if submitted_algo and submitted_algo in submitted_parameter_module:
                    parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

                    enriched_modules = do_module_enrichment_analysis(
                        implicated_gene_ids, genomic_intervals, submitted_network, submitted_algo, parameters)

                    num_enriched_modules = len(enriched_modules)
                    total_num_modules = count_modules(
                        submitted_network, submitted_algo, parameters)
                    stats = f'{num_enriched_modules} out of {total_num_modules} '
                    if total_num_modules == 1:
                        stats += 'module '
                    else:
                        stats += 'modules '

                    if num_enriched_modules == 1:
                        stats += 'was found to be enriched (adjusted p-value < 0.05).'
                    else:
                        stats += 'were found to be enriched (adjusted p-value < 0.05).'

                    first_module = None
                    if enriched_modules:
                        first_module = enriched_modules[0]
                    else:
                        return enriched_modules, first_module, {'display': 'none'}, stats

                    if submitted_parameter_module and submitted_algo in submitted_parameter_module:
                        if submitted_parameter_module[submitted_algo]['param_module']:
                            first_module = submitted_parameter_module[submitted_algo]['param_module']

                    return enriched_modules, first_module, {'display': 'block'}, stats

        raise PreventUpdate

    @app.callback(
        Output('coexpression-pathways', 'data'),
        Output('coexpression-pathways', 'columns'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        Input('coexpression-modules-pathway', 'active_tab'),
        Input('coexpression-modules', 'value'),
        State('coexpression-submitted-parameter-module', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def display_pathways(submitted_network, submitted_algo, active_tab, module, submitted_parameter_module, coexpression_is_submitted):
        if coexpression_is_submitted:
            if submitted_network and submitted_algo and submitted_algo in submitted_parameter_module:
                parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

                try:
                    module_idx = module.split(' ')[1]
                    table, empty = convert_to_df(
                        active_tab, module_idx, submitted_network, submitted_algo, parameters)
                except Exception as e:
                    table, empty = convert_to_df(
                        active_tab, None, submitted_network, submitted_algo, parameters)

                columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
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

        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),

        Input('coexpression-graph-layout', 'value'),
        State('coexpression-is-submitted', 'data'),

        State('coexpression-modules', 'options'),

        Input('coexpression-reset-graph', 'n_clicks'),

        prevent_initial_call=True
    )
    def display_table_graph(implicated_gene_ids, module, submitted_network, submitted_algo, submitted_parameter_module,
                            layout, coexpression_is_submitted, modules, *_):
        if coexpression_is_submitted:
            if submitted_network and submitted_algo and submitted_algo in submitted_parameter_module:
                parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

                # No enriched modules
                if not modules:
                    return load_module_graph(
                        implicated_gene_ids, None, submitted_network, submitted_algo, parameters, layout) + ({'display': 'None'}, )

                return load_module_graph(
                    implicated_gene_ids, module, submitted_network, submitted_algo, parameters, layout) + ({'visibility': 'visible'}, )

        raise PreventUpdate

    @app.callback(
        Output('coexpression-network-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-clustering-algo-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-parameter-module-saved-input',
               'data', allow_duplicate=True),

        Input('coexpression-network', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value'),
        State('coexpression-parameter-slider', 'marks'),
        State('homepage-is-submitted', 'data'),
        State('coexpression-parameter-module-saved-input', 'data'),
        prevent_initial_call='True'
    )
    def set_input_coexpression_session_state(network, algo, parameter_value, parameter_mark, homepage_is_submitted, input_parameter_module):
        if homepage_is_submitted:
            input_paramater_module_value = Input_parameter_module(
                parameter_mark, parameter_value)._asdict()

            if input_parameter_module:
                input_parameter_module[algo] = input_paramater_module_value

            else:
                input_parameter_module = {algo: input_paramater_module_value}

            return network, algo, input_parameter_module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-submitted-parameter-module',
               'data', allow_duplicate=True),

        Input('coexpression-modules', 'value'),
        Input('coexpression-graph-layout', 'value'),
        Input('coexpression-modules-pathway', 'active_tab'),

        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('homepage-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
        prevent_initial_call=True
    )
    def set_submitted_coexpression_session_state(module, layout, active_tab, submitted_network, submitted_algo, homepage_is_submitted, submitted_parameter_module):
        if homepage_is_submitted:
            if submitted_network and submitted_parameter_module and submitted_algo in submitted_parameter_module:
                submitted_parameter_module[submitted_algo]['param_module'] = module
                submitted_parameter_module[submitted_algo]['layout'] = layout
                submitted_parameter_module[submitted_algo]['pathway_active_tab'] = active_tab

                return submitted_parameter_module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-network', 'value'),

        State('homepage-is-submitted', 'data'),
        State('coexpression-network-saved-input', 'data'),

        Input('homepage-genomic-intervals-submitted-input', 'data')
    )
    def display_selected_coexpression_network(homepage_is_submitted, network, *_):
        if homepage_is_submitted:
            if not network:
                return 'OS-CX'

            return network

        raise PreventUpdate

    @app.callback(
        Output('coexpression-clustering-algo', 'value'),

        State('homepage-is-submitted', 'data'),
        State('coexpression-clustering-algo-saved-input', 'data'),

        Input('homepage-genomic-intervals-submitted-input', 'data')
    )
    def get_selected_clustering_algo(homepage_is_submitted, algo, *_):
        if homepage_is_submitted:
            if not algo:
                return 'clusterone'

            return algo

        raise PreventUpdate

    @app.callback(
        Output('coexpression-graph-layout', 'value'),
        Output('coexpression-modules-pathway', 'active_tab'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data')
    )
    def display_selected_graph_layout(submitted_network, submitted_algo, coexpression_is_submitted, submitted_parameter_module):
        if coexpression_is_submitted:
            if submitted_network and submitted_algo and submitted_algo in submitted_parameter_module:
                layout = 'circle'
                if submitted_parameter_module[submitted_algo]['layout']:
                    layout = submitted_parameter_module[submitted_algo]['layout']

                active_tab = 'tab-0'
                if submitted_parameter_module[submitted_algo]['pathway_active_tab']:
                    active_tab = submitted_parameter_module[submitted_algo]['pathway_active_tab']

                return layout, active_tab

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
    def reset_table_filters(*_):
        return ''

    @app.callback(
        Output('coexpression-download-df-to-csv', 'data'),
        Input('coexpression-export-table', 'n_clicks'),
        State('coexpression-pathways', 'data'),
        State('homepage-genomic-intervals-submitted-input', 'data')
    )
    def download_coexpression_table_to_csv(download_n_clicks, coexpression_df, genomic_intervals):
        if download_n_clicks >= 1:
            df = pd.DataFrame(coexpression_df)
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Co-Expression Network Analysis Table.csv', index=False)

        raise PreventUpdate

    @app.callback(
        Output('coexpression-download-graph-to-json', 'data'),
        Input('coexpression-export-graph', 'n_clicks'),
        State('coexpression-module-graph', 'elements'),
        State('homepage-genomic-intervals-submitted-input', 'data')
    )
    def download_coexpression_table_to_csv(download_n_clicks, coexpression_dict, genomic_intervals):
        if download_n_clicks >= 1:
            return dict(content='Hello world!', filename=f'[{genomic_intervals}] Co-Expression Network Analysis Graph.txt')

        raise PreventUpdate
