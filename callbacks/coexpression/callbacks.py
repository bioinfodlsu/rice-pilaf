from dash import Input, Output, State, html, dcc, ctx
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util
from ..branch import *

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

            return None

        raise PreventUpdate

    @app.callback(
        Output('coexpression-is-submitted', 'data', allow_duplicate=True),
        Output('coexpression-submitted-addl-genes',
               'data', allow_duplicate=True),
        Output('coexpression-combined-genes',
               'data', allow_duplicate=True),

        Output('coexpression-submitted-network',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-clustering-algo',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-parameter-module',
               'data', allow_duplicate=True),

        Input('coexpression-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),

        State('homepage-genomic-intervals-submitted-input', 'data'),
        State('coexpression-addl-genes', 'value'),

        State('coexpression-network', 'value'),
        State('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-slider', 'marks'),
        State('coexpression-parameter-slider', 'value'),
        prevent_initial_call=True
    )
    def submit_coexpression_input(coexpression_submit_n_clicks, homepage_is_submitted,
                                  genomic_intervals, submitted_addl_genes,
                                  submitted_network, submitted_algo, submitted_slider_marks, submitted_slider_value):
        if homepage_is_submitted and coexpression_submit_n_clicks >= 1:
            paramater_module_value = Submitted_parameter_module(
                submitted_slider_marks, submitted_slider_value, '', 'circle', 'tab-0')._asdict()

            submitted_parameter_module = {
                submitted_algo: paramater_module_value}

            if submitted_addl_genes:
                submitted_addl_genes = submitted_addl_genes.strip()
            else:
                submitted_addl_genes = ''

            list_addl_genes = list(
                filter(None, [gene.strip() for gene in submitted_addl_genes.split(';')]))

            # Perform lift-over if it has not been performed.
            # Otherwise, just fetch the results from the file
            implicated_gene_ids = lift_over_util.get_genes_in_Nb(genomic_intervals)[
                1]

            gene_ids = list(set.union(
                set(implicated_gene_ids), set(list_addl_genes)))

            return True, submitted_addl_genes, gene_ids, submitted_network, submitted_algo, submitted_parameter_module

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
        Output('coexpression-submit', 'disabled'),

        Input('coexpression-submit', 'n_clicks'),
        Input('coexpression-module-graph', 'elements'),
        Input('coexpression-pathways', 'data'),
        Input('coexpression-module-stats', 'children')
    )
    def disable_coexpression_button_upon_run(n_clicks,  *_):
        return ctx.triggered_id == 'coexpression-submit' and n_clicks > 0

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
        Output('coexpression-module-graph', 'style', allow_duplicate=True),
        Output('coexpression-graph-container', 'style'),

        Input('coexpression-combined-genes', 'data'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),

        prevent_initial_call=True
    )
    def hide_table_graph(combined_gene_ids, submitted_network, submitted_algo, coexpression_is_submitted, submitted_parameter_module):
        if coexpression_is_submitted:
            if submitted_algo and submitted_algo in submitted_parameter_module:
                parameters = submitted_parameter_module[submitted_algo]['param_slider_value']
                layout = submitted_parameter_module[submitted_algo]['layout']

                return load_module_graph(
                    combined_gene_ids, None, submitted_network, submitted_algo, parameters, layout) + ({'visibility': 'hidden'}, )

        raise PreventUpdate

    @app.callback(
        Output('coexpression-table-container', 'style', allow_duplicate=True),
        Input('coexpression-submit', 'n_clicks'),

        prevent_initial_call=True
    )
    def hide_table(*_):
        return {'visibility': 'hidden'}

    @app.callback(
        Output('coexpression-module-graph', 'style', allow_duplicate=True),
        Input('coexpression-modules', 'value'),

        prevent_initial_call=True
    )
    def hide_graph(*_):
        return {'visibility': 'hidden'}

    @app.callback(
        Output('coexpression-modules', 'options'),
        Output('coexpression-modules', 'value'),
        Output('coexpression-results-module-tabs-container', 'style'),
        Output('coexpression-module-stats', 'children'),

        State('homepage-genomic-intervals-submitted-input', 'data'),

        Input('coexpression-combined-genes', 'data'),
        Input('coexpression-submitted-addl-genes', 'data'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('homepage-is-submitted', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def perform_module_enrichment(genomic_intervals, combined_gene_ids, submitted_addl_genes,
                                  submitted_network, submitted_algo, homepage_is_submitted, submitted_parameter_module, coexpression_is_submitted):
        if homepage_is_submitted:
            if coexpression_is_submitted:
                if submitted_algo and submitted_algo in submitted_parameter_module:
                    parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

                    enriched_modules = do_module_enrichment_analysis(
                        combined_gene_ids, genomic_intervals, submitted_addl_genes, submitted_network, submitted_algo, parameters)

                    # Display statistics
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
        Output('coexpression-graph-stats', 'children'),
        Output('coexpression-table-stats', 'children'),

        Output('coexpression-table-container', 'style'),

        Input('coexpression-combined-genes', 'data'),
        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        Input('coexpression-modules-pathway', 'active_tab'),
        Input('coexpression-modules', 'value'),
        State('coexpression-submitted-parameter-module', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def display_pathways(combined_gene_ids,
                         submitted_network, submitted_algo, active_tab, module, submitted_parameter_module, coexpression_is_submitted):
        if coexpression_is_submitted:
            if submitted_network and submitted_algo and submitted_algo in submitted_parameter_module:
                parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

                try:
                    module_idx = module.split(' ')[1]
                    table, _ = convert_to_df(
                        active_tab, module_idx, submitted_network, submitted_algo, parameters)
                except Exception:
                    table, _ = convert_to_df(
                        active_tab, None, submitted_network, submitted_algo, parameters)

                columns = [{'id': x, 'name': x, 'presentation': 'markdown'}
                           for x in table.columns]

                num_enriched = get_num_unique_entries(table, 'ID')
                if num_enriched == 1:
                    stats = f'This module is enriched in {num_enriched} {get_noun_for_active_tab(active_tab).singular}.'
                else:
                    stats = f'This module is enriched in {num_enriched} {get_noun_for_active_tab(active_tab).plural}.'

                graph_stats = 'The selected module has '
                try:
                    total_num_genes, num_combined_gene_ids = count_genes_in_module(
                        combined_gene_ids, int(module_idx), submitted_network, submitted_algo, parameters)
                except UnboundLocalError:
                    total_num_genes, num_combined_gene_ids = 0, 0

                if total_num_genes == 1:
                    graph_stats += f'{total_num_genes} gene, of which {num_combined_gene_ids} '
                else:
                    graph_stats += f'{total_num_genes} genes, of which {num_combined_gene_ids} '

                if num_combined_gene_ids == 1:
                    graph_stats += 'is implicated by your GWAS/QTL or part of the gene list you manually entered.'
                else:
                    graph_stats += 'are implicated by your GWAS/QTL or part of the gene list you manually entered.'

                if total_num_genes == 0:
                    return table.to_dict('records'), columns, graph_stats, stats, {'display': 'none'}
                else:
                    return table.to_dict('records'), columns, graph_stats, stats, {'visibility': 'visible'}

        raise PreventUpdate

    @app.callback(
        Output('coexpression-module-graph', 'elements', allow_duplicate=True),
        Output('coexpression-module-graph', 'layout', allow_duplicate=True),
        Output('coexpression-module-graph', 'style', allow_duplicate=True),
        Output('coexpression-graph-container', 'style', allow_duplicate=True),
        Output('coexpression-module-graph-node-data',
               'children', allow_duplicate=True),
        Output('coexpression-extra-bottom-div', 'style', allow_duplicate=True),

        Input('coexpression-combined-genes', 'data'),
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
    def display_table_graph(combined_gene_ids, module, submitted_network, submitted_algo, submitted_parameter_module,
                            layout, coexpression_is_submitted, modules, *_):
        if coexpression_is_submitted:
            if submitted_network and submitted_algo and submitted_algo in submitted_parameter_module:
                parameters = submitted_parameter_module[submitted_algo]['param_slider_value']

                if not modules:
                    module_graph = load_module_graph(
                        combined_gene_ids, None, submitted_network, submitted_algo, parameters, layout)
                else:
                    module_graph = load_module_graph(
                        combined_gene_ids, module, submitted_network, submitted_algo, parameters, layout)

                # No enriched modules
                if not modules:
                    return module_graph + ({'display': 'none'}, None, {'height': '0em'})

                return module_graph + ({'visibility': 'visible', 'width': '100%',
                                       'height': '100vh'}, None, {'height': '1.5em'})

        raise PreventUpdate

    @app.callback(
        Output('coexpression-addl-genes-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-network-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-clustering-algo-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-parameter-module-saved-input',
               'data', allow_duplicate=True),

        State('coexpression-addl-genes', 'value'),
        Input('coexpression-network', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        Input('coexpression-parameter-slider', 'value'),
        State('coexpression-parameter-slider', 'marks'),
        State('homepage-is-submitted', 'data'),
        State('coexpression-parameter-module-saved-input', 'data'),
        prevent_initial_call='True'
    )
    def set_input_coexpression_session_state(addl_genes, network, algo, parameter_value, parameter_mark, homepage_is_submitted, input_parameter_module):
        if homepage_is_submitted:
            input_paramater_module_value = Input_parameter_module(
                parameter_mark, parameter_value)._asdict()

            if input_parameter_module:
                input_parameter_module[algo] = input_paramater_module_value

            else:
                input_parameter_module = {algo: input_paramater_module_value}

            return addl_genes, network, algo, input_parameter_module

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
        Output('coexpression-addl-genes', 'value'),

        State('homepage-is-submitted', 'data'),
        State('coexpression-addl-genes-saved-input', 'data'),

        Input('homepage-genomic-intervals-submitted-input', 'data')
    )
    def display_submitted_addl_genes(homepage_is_submitted, addl_genes, *_):
        if homepage_is_submitted:
            if not addl_genes:
                return ''

            return addl_genes

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
        Output('coexpression-input', 'children'),
        Input('coexpression-is-submitted', 'data'),
        State('coexpression-addl-genes', 'value'),
        State('coexpression-network', 'value'),
        State('coexpression-clustering-algo', 'value'),
        State('coexpression-parameter-slider', 'value')
    )
    def display_coexpression_submitted_input(coexpression_is_submitted, genes, network, algo, parameters):
        if coexpression_is_submitted:
            if not genes:
                genes = 'None'
            else:
                genes = '; '.join(
                    list(filter(None, [gene.strip() for gene in genes.split(';')])))

            return [html.B('Additional Genes: '), genes,
                    html.Br(),
                    html.B('Selected Co-Expression Network: '), get_user_facing_network(
                        network),
                    html.Br(),
                    html.B('Selected Module Detection Algorithm: '), get_user_facing_algo(
                        algo),
                    html.Br(),
                    html.B('Selected Algorithm Parameter: '), get_user_facing_parameter(algo, parameters)]

        raise PreventUpdate

    @app.callback(
        Output('coexpression-clustering-algo-modal', 'is_open'),
        Output('coexpression-network-modal', 'is_open'),
        Output('coexpression-parameter-modal', 'is_open'),

        Input('coexpression-clustering-algo-tooltip', 'n_clicks'),
        Input('coexpression-network-tooltip', 'n_clicks'),
        Input('coexpression-parameter-tooltip', 'n_clicks')
    )
    def open_modals(algo_tooltip_n_clicks, network_tooltip_n_clicks, parameter_tooltip_n_clicks):
        if ctx.triggered_id == 'coexpression-clustering-algo-tooltip' and algo_tooltip_n_clicks > 0:
            return True, False, False

        if ctx.triggered_id == 'coexpression-network-tooltip' and network_tooltip_n_clicks > 0:
            return False, True, False

        if ctx.triggered_id == 'coexpression-parameter-tooltip' and parameter_tooltip_n_clicks > 0:
            return False, False, True

        raise PreventUpdate

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
            df = pd.DataFrame(purge_html_export_table(coexpression_df))
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Co-Expression Network Analysis Table.csv', index=False)

        raise PreventUpdate

    @app.callback(
        Output('coexpression-download-graph-to-json', 'data'),
        Input('coexpression-export-graph', 'n_clicks'),
        State('homepage-genomic-intervals-submitted-input', 'data'),
        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-module', 'data'),
        State('coexpression-modules', 'value'),
    )
    def download_coexpression_graph_to_tsv(download_n_clicks, genomic_intervals, submitted_network, submitted_algo, submitted_parameter_module, module):
        if download_n_clicks >= 1:
            parameters = submitted_parameter_module[submitted_algo]['param_slider_value']
            module_idx = int(module.split(' ')[1])
            df = pd.read_csv(
                f'{Constants.TEMP}/{submitted_network}/{submitted_algo}/modules/{parameters}/module-{module_idx}.tsv', sep='\t')
            return dcc.send_data_frame(df.to_csv, f'[{genomic_intervals}] Co-Expression Network Analysis Graph.tsv', index=False, sep='\t')

        raise PreventUpdate

    @app.callback(
        Output('coexpression-module-graph-node-data', 'children'),
        Input('coexpression-module-graph', 'tapNodeData')
    )
    def display_node_data(node_data):
        if node_data:
            with open(f'{Constants.OGI_MAPPING}/Nb_to_ogi.pickle', 'rb') as ogi_file, open(Constants.QTARO_DICTIONARY, 'rb') as qtaro_file,  open(f'{Constants.IRIC}/interpro.pickle', 'rb') as interpro_file, open(f'{Constants.IRIC}/pfam.pickle', 'rb') as pfam_file,  open(f'{Constants.IRIC_MAPPING}/msu_to_iric.pickle', 'rb') as iric_mapping_file, open(f'{Constants.TEXT_MINING_PUBMED}', 'rb') as pubmed_file, open(f'{Constants.MSU_MAPPING}/msu_to_rap.pickle', 'rb') as rapdb_file:
                ogi_mapping = pickle.load(ogi_file)
                qtaro_mapping = pickle.load(qtaro_file)
                # interpro_mapping = pickle.load(interpro_file)
                # pfam_mapping = pickle.load(pfam_file)
                # iric_mapping = pickle.load(iric_mapping_file)
                # pubmed_mapping = pickle.load(pubmed_file)
                rapdb_mapping = pickle.load(rapdb_file)

                gene = node_data['id']

                node_data = [html.B('Name: '), get_rgi_genecard_link_single_str(gene, dash=True), html.Br(),
                             html.B('OGI: '), get_rgi_orthogroup_link_single_str(
                                 ogi_mapping[gene], dash=True), html.Br(),
                             html.B(
                                 'RAP-DB: ', ), get_rapdb_entry(gene, rapdb_mapping), html.Br(),

                             html.B('Description: '), html.Br(),
                             html.B(
                                 'UniProtKB/Swiss-Prot: '), html.Br(), html.Br(),

                             html.B('Pfam: '), html.Br(),
                             html.B('InterPro: '), html.Br(), html.Br(),

                             html.B('QTL Analyses: '), get_qtaro_entry(
                                 qtaro_mapping, gene), html.Br(),
                             html.B('PubMed Article IDs')]

                return node_data

        raise PreventUpdate
