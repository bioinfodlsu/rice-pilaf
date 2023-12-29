from dash import Input, Output, State, html, dcc, ctx
from dash.exceptions import PreventUpdate
from collections import namedtuple

from .util import *
from ..lift_over import util as lift_over_util
from ..branch import *

Parameter_slider = namedtuple('Parameter_slider', ['marks', 'value'])


def init_callback(app):
    @app.callback(
        Output('coexpression-genomic-intervals-input', 'children'),
        State('homepage-submitted-genomic-intervals', 'data'),
        Input('homepage-is-submitted', 'data'),
        Input('coexpression-submit', 'n_clicks')
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        """
        Displays the genomic interval input in the coexpression page

        Parameters:
        - nb_intervals_str: Submitted genomic interval
        - homepage_is_submitted: [Homepage] Saved boolean value of True / False of whether a valid input was submitted or not 
        - *_: Other input that facilitates displaying of the submitted genomic interval

        Returns:
        - Submitted genomic interval text
        """
        
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]

            return None

        raise PreventUpdate

    # =================
    # Input-related
    # =================
    @app.callback(
        Output('coexpression-is-submitted', 'data', allow_duplicate=True),
        Output('coexpression-submitted-addl-genes',
               'data', allow_duplicate=True),
        Output('coexpression-valid-addl-genes',
               'data', allow_duplicate=True),
        Output('coexpression-combined-genes',
               'data', allow_duplicate=True),

        Output('coexpression-submitted-network',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-clustering-algo',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-parameter-slider',
               'data', allow_duplicate=True),

        Output('coexpression-addl-genes-error', 'style', allow_duplicate=True),
        Output('coexpression-addl-genes-error',
               'children', allow_duplicate=True),

        Input('coexpression-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),

        State('homepage-submitted-genomic-intervals', 'data'),
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
        """
        Parses coexpression input, displays the coexpression result container
        - If user clicks on the coexpression submit button, the inputs will be parsed and either an error message or the coexpression results container will appear

        Parameters:
        - coexpression_submit_n_clicks: Number of clicks pressed on the tfbs submit button 
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input 
        - genomic_intervals: Saved genomic intervals found in the dcc.Store
        - submitted_addl_genes: Submitted coexpression additional genes
        - submitted_network: Submitted coexpression network
        - submitted_algo: Submitted coexpression clustering algorithm
        - submitted_slider_marks: Submitted parameter slider marks
        - submitted_slider_value: Submitted parameter slider value

        Returns:
        - ('coexpression-is-submitted', 'data'): [Coexpression] True for submitted valid input; otherwise False
        - ('coexpression-submitted-addl-genes', 'data'): Submitted coexpression additional genes
        - ('coexpression-valid-addl-genes', 'data'): Submitted coexpression valid additional genes
        - ('coexpression-combined-genes', 'data'): Coexpression combined genes 
        - ('coexpression-submitted-network', 'data'): Submitted coexpression network
        - ('coexpression-submitted-clustering-algo', 'data'): Submitted coexpression clustering algorithm
        - ('coexpression-submitted-parameter-slider', 'data): Submitted coexpression parameter slider tuple
        - ('coexpression-addl-genes-error', 'style'): {'display': 'block'} for displaying the error message; otherwise {'display': 'none'}
        - ('coexpression-addl-genes-error', 'children'): Error message
        """
        
        if homepage_is_submitted and coexpression_submit_n_clicks >= 1:
            parameter_slider_value = Parameter_slider(
                submitted_slider_marks, submitted_slider_value)._asdict()
            submitted_parameter_slider = {
                submitted_algo: parameter_slider_value}

            if submitted_addl_genes:
                submitted_addl_genes = submitted_addl_genes.strip()
            else:
                submitted_addl_genes = ''

            list_addl_genes = list(
                filter(None, [sanitize_msu_id(gene.strip()) for gene in submitted_addl_genes.split(';')]))

            # Check which genes are valid MSU IDs
            list_addl_genes, invalid_genes = check_if_valid_msu_ids(
                list_addl_genes)

            if not invalid_genes:
                error_display = {'display': 'none'}
                error = None
            else:
                error_display = {'display': 'block'}

                if len(invalid_genes) == 1:
                    error_msg = invalid_genes[0] + \
                        ' is not a valid MSU accession ID.'
                    error_msg_ignore = 'It'
                else:
                    if len(invalid_genes) == 2:
                        error_msg = invalid_genes[0] + \
                            ' and ' + invalid_genes[1]
                    else:
                        error_msg = ', '.join(
                            invalid_genes[:-1]) + ', and ' + invalid_genes[-1]

                    error_msg += ' are not valid MSU accession IDs.'
                    error_msg_ignore = 'They'

                error = [html.Span(error_msg), html.Br(), html.Span(
                    f'{error_msg_ignore} will be ignored when running the analysis.')]

            # Perform lift-over if it has not been performed.
            # Otherwise, just fetch the results from the file
            implicated_gene_ids = lift_over_util.get_genes_in_Nb(genomic_intervals)[
                1]

            gene_ids = list(set.union(
                set(implicated_gene_ids), set(list_addl_genes)))

            return True, submitted_addl_genes, list_addl_genes, gene_ids, submitted_network, submitted_algo, submitted_parameter_slider, error_display, error

        raise PreventUpdate

    @app.callback(
        Output('coexpression-results-container', 'style'),
        Input('coexpression-is-submitted', 'data'),
    )
    def display_coexpression_output(coexpression_is_submitted):
        """
        Displays the coexpression results container

        Parameters:
        - coexpression_is_submitted: [Coexpression] Saved boolean value of submitted valid input 

        Returns:
        - ('coexpression-results-container', 'style'): {'display': 'block'} for displaying the coexpression results container; otherwise {'display': 'none'}
        """

        if coexpression_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}

    @app.callback(
        Output('coexpression-addl-genes-error', 'style'),
        Output('coexpression-addl-genes-error', 'children'),
        Input('homepage-is-resetted', 'data')
    )
    def clear_coexpression_error_messages(homepage_is_resetted):
        """
        Clears coexpression input error 

        Parameters:
        - homepage_is_resetted: Saved boolean value of resetted analysis 

        Returns:
        - ('coexpression-addl-genes-error', 'style'): {'display': 'block'} for displaying the coexpression error container; otherwise {'display': 'none'}
        - ('coexpression-addl-genes-error', 'children'): None for no error message
        """

        if homepage_is_resetted:
            return {'display': 'none'}, None

        raise PreventUpdate

    @app.callback(
        Output('coexpression-submit', 'disabled'),

        Input('coexpression-submit', 'n_clicks'),
        Input('coexpression-module-graph', 'elements'),
        Input('coexpression-pathways', 'data'),
        Input('coexpression-module-stats', 'children')
    )
    def disable_coexpression_button_upon_run(n_clicks,  *_):
        """
        Disables the submit button in the coexpression page until computation is done in the coexpression page

        Parameters:
        - n_clicks: Number of clicks pressed on the coexpression submit button
        - *_: Other input that facilitates the disabling of the coexpressino submit button

        Returns:
        - ('coexpression-submit', 'disabled'): True for disabling the submit button; otherwise False 
        """

        return ctx.triggered_id == 'coexpression-submit' and n_clicks > 0

    @app.callback(
        Output('coexpression-clustering-algo-modal', 'is_open'),
        Output('coexpression-network-modal', 'is_open'),
        Output('coexpression-parameter-modal', 'is_open'),
        Output('coexpression-converter-modal', 'is_open'),

        Input('coexpression-clustering-algo-tooltip', 'n_clicks'),
        Input('coexpression-network-tooltip', 'n_clicks'),
        Input('coexpression-parameter-tooltip', 'n_clicks'),
        Input('coexpression-converter-tooltip', 'n_clicks')
    )
    def open_modals(algo_tooltip_n_clicks, network_tooltip_n_clicks, parameter_tooltip_n_clicks, converter_tooltip_n_clicks):
        """
        Displays the coexpression tooltip modals

        Parameters:
        - algo_tooltip_n_clicks: Number of clicks pressed for the tooltip button near the coexpression clustering algorithm input field
        - network_tooltip_n_clicks: Number of clicks pressed for the tooltip button near the coexpression network input field
        - parameter_tooltip_n_clicks: Number of clicks pressed for the tooltip button near the coexpression parameter slider input field
        - converter_tooltip_n_clicks:Number of clicks pressed for the tooltip button near the coexpression additional genes input field

        Returns:
        - ('coexpression-clustering-algo-modal', 'is_open'): True for showing the coexpression clustering algorithm tooltip; otherwise False
        - ('coexpression-network-modal', 'is_open'): True for showing the coexpression network tooltip; otherwise False
        - ('coexpression-parameter-modal', 'is_open'): True for showing the coexpression parameter slider tooltip; otherwise False
        - ('coexpression-converter-modal', 'is_open'): True for showing the tfbs additional genes tooltip; otherwise False
        """

        if ctx.triggered_id == 'coexpression-clustering-algo-tooltip' and algo_tooltip_n_clicks > 0:
            return True, False, False, False

        if ctx.triggered_id == 'coexpression-network-tooltip' and network_tooltip_n_clicks > 0:
            return False, True, False, False

        if ctx.triggered_id == 'coexpression-parameter-tooltip' and parameter_tooltip_n_clicks > 0:
            return False, False, True, False

        if ctx.triggered_id == 'coexpression-converter-tooltip' and converter_tooltip_n_clicks > 0:
            return False, False, False, True

        raise PreventUpdate

    @app.callback(
        Output('coexpression-parameter-slider', 'marks'),
        Output('coexpression-parameter-slider', 'value'),
        Input('coexpression-clustering-algo', 'value'),
        State('coexpression-submitted-parameter-slider', 'data')
    )
    def set_parameter_slider(algo, parameter_slider):
        """
        Sets the parameter slider data

        Parameters:
        - algo: Selected clustering algorithm
        - parameter_slider: Selected value of the parameter slider

        Returns:
        - ('coexpression-parameter-slider', 'marks'): Parameter slider marks
        - ('coexpression-parameter-slider', 'value'): Parameter slider value
        """

        if parameter_slider and algo in parameter_slider:
            return parameter_slider[algo]['marks'], parameter_slider[algo]['value']

        return get_parameters_for_algo(algo), module_detection_algos[algo].default_param * module_detection_algos[algo].multiplier

    @app.callback(
        Output('coexpression-input', 'children'),
        Input('coexpression-is-submitted', 'data'),
        State('coexpression-valid-addl-genes', 'data'),
        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-slider', 'data')
    )
    def display_coexpression_submitted_input(coexpression_is_submitted, genes, network, algo, submitted_parameter_slider):
        """
        Displays the coexpression submitted input

        Parameters:
        - coexpression_is_submitted: [Coexpression] Saved boolean value of submitted valid input 
        - genes: Saved coexpression valid additional genes found in the dcc.Store
        - network: Saved coexpression network found in the dcc.Store
        - submitted_parameter_slider: Saved coexpression parameter slider tuple found in the dcc.Store
        
        Returns:
        - ('coexpression-input', 'children'): Submitted coexpression inputs text
        """

        if coexpression_is_submitted:
            parameters = 0
            if submitted_parameter_slider and algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[algo]['value']

            if not genes:
                genes = 'None'
            else:
                genes = '; '.join(genes)

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

    # =================
    # Module-related
    # =================

    @app.callback(
        Output('coexpression-modules', 'options'),
        Output('coexpression-modules', 'value'),
        Output('coexpression-results-module-tabs-container', 'style'),
        Output('coexpression-module-stats', 'children'),

        State('homepage-submitted-genomic-intervals', 'data'),

        Input('coexpression-combined-genes', 'data'),
        State('coexpression-valid-addl-genes', 'data'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('homepage-is-submitted', 'data'),
        State('coexpression-submitted-parameter-slider', 'data'),
        State('coexpression-submitted-module', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def perform_module_enrichment(genomic_intervals, combined_gene_ids, valid_addl_genes,
                                  submitted_network, submitted_algo, homepage_is_submitted, submitted_parameter_slider, module, coexpression_is_submitted):
        """
        Displays the coexpression pathways table

        Parameters:
        - genomic_intervals: Saved genomic intervals found in the dcc.Store
        - combined_gene_ids: Saved combined gene ids found in the dcc.Store
        - valid_addl_genes: Saved coexpression valid additional genes found in the dcc.Store
        - submitted_network: Saved coexpression network found in the dcc.Store
        - submitted_algo: Saved coexpression clustering algorithm found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input 
        - submitted_parameter_slider: Saved parameters slider tuple found in the dcc.Store
        - module: Saved selected coexpression module found in the dcc.Store
        - coexpression_is_submitted: [Coexpression] Saved boolean value of submitted valid input 

        Returns:
        - ('coexpression-modules', 'options'): List of available modules
        - ('coexpression-modules', 'value'): Selected module value
        - ('coexpression-results-module-tabs-container', 'style'): {'display': 'block'} for displaying the module tabs container; otherwise {'display': 'none'}
        - ('coexpression-module-stats', 'children'): Stats for the coexpression module
        """

        if homepage_is_submitted and coexpression_is_submitted:
            if submitted_algo and submitted_algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[submitted_algo]['value']

                enriched_modules = do_module_enrichment_analysis(
                    combined_gene_ids, genomic_intervals, valid_addl_genes, submitted_network, submitted_algo, parameters)

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
                    stats += 'was '
                else:
                    stats += 'were '

                stats += 'found to be enriched (adjusted p-value < 0.05).'

                first_module = None
                if enriched_modules:
                    first_module = enriched_modules[0]
                    module = first_module
                else:
                    return enriched_modules, first_module, {'display': 'none'}, stats

                if module:
                    first_module = module

                return enriched_modules, first_module, {'display': 'block'}, stats

        raise PreventUpdate

    # =================
    # Table-related
    # =================

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
        State('coexpression-submitted-parameter-slider', 'data'),
        State('coexpression-is-submitted', 'data')
    )
    def display_pathways(combined_gene_ids,
                         submitted_network, submitted_algo, active_tab, module, submitted_parameter_slider, coexpression_is_submitted):
        """
        Displays the coexpression pathways table

        Parameters:
        - combined_gene_ids: Saved combined gene ids found in the dcc.Store
        - submitted_network: Saved coexpression network found in the dcc.Store
        - submitted_algo: Saved coexpression clustering algorithm found in the dcc.Store
        - active_tab: Active tab for a specific coexpression table
        - module: Selected coexpression module 
        - submitted_parameter_slider: Saved parameters slider tuple found in the dcc.Store
        - coexpression_is_submitted: [Coexpression] Saved boolean value of submitted valid input 

        Returns:
        - ('coexpression-pathways', 'data'): Data for the coexpression table depending on the active tab
        - ('coexpression-pathways', 'columns'): List of columns for a specific coexpression table
        - ('coexpression-graph-stats', 'children'): Stats for the coexpression graph
        - ('coexpression-table-stats', 'children'): Stats for the coexpression table
        - ('coexpression-table-container', 'style'): {'visibility': 'visible'} for displaying the table container; otherwise {'display': 'none'}
        """

        if coexpression_is_submitted:
            if submitted_network and submitted_algo and submitted_algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[submitted_algo]['value']

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
                stats = f'This module is enriched in {num_enriched} '
                if num_enriched == 1:
                    stats += f'{get_noun_for_active_tab(active_tab).singular}.'
                else:
                    stats += f'{get_noun_for_active_tab(active_tab).plural}.'

                graph_stats = 'The selected module has '
                try:
                    total_num_genes, num_combined_gene_ids = count_genes_in_module(
                        combined_gene_ids, int(module_idx), submitted_network, submitted_algo, parameters)
                except UnboundLocalError:
                    total_num_genes, num_combined_gene_ids = 0, 0

                if total_num_genes == 1:
                    graph_stats += f'{total_num_genes} gene'
                else:
                    graph_stats += f'{total_num_genes} genes'

                graph_stats += f', among which {num_combined_gene_ids} '

                if num_combined_gene_ids == 1:
                    graph_stats += 'is '
                else:
                    graph_stats += 'are '
                graph_stats += 'implicated by your GWAS/QTL or among those that you manually added.'

                if total_num_genes == 0:
                    return table.to_dict('records'), columns, graph_stats, stats, {'display': 'none'}
                else:
                    return table.to_dict('records'), columns, graph_stats, stats, {'visibility': 'visible'}

        raise PreventUpdate

    @app.callback(
        Output('coexpression-pathways', 'filter_query'),
        Output('coexpression-pathways', 'page_current'),

        Input('coexpression-reset-table', 'n_clicks'),
        Input('coexpression-submit', 'n_clicks'),

        Input('coexpression-modules-pathway', 'active_tab'),
        Input('coexpression-modules', 'value')
    )
    def reset_table_filter_page(*_):
        """
        Resets the coexpression table and the current page to its original state

        Parameters:
        - *_: Other input that facilitates the resetting of the coexpression table 

        Returns:
        - ('coexpression-pathways', 'filter_query'): '' for removing the filter query
        - ('coexpression-pathways', 'page_current'): 0
        """

        return '', 0

    @app.callback(
        Output('coexpression-table-container', 'style', allow_duplicate=True),
        Input('coexpression-submit', 'n_clicks'),

        prevent_initial_call=True
    )
    def hide_table(*_):
        """
        Hides the coexpression table

        Parameters:
        - *_: Other inputs to facilitate the hiding of the coexpression table
        
        Returns:
        - ('coexpression-table-container', 'style'): {'visibility': 'hidden'} for hiding the coexpression table
        """

        return {'visibility': 'hidden'}

    @app.callback(
        Output('coexpression-download-df-to-csv', 'data'),
        Input('coexpression-export-table', 'n_clicks'),
        State('coexpression-pathways', 'data'),
        State('coexpression-modules', 'value')
    )
    def download_coexpression_table_to_csv(download_n_clicks, coexpression_df, module):
        """
        Export the coexpression table in csv file format 

        Parameters:
        - download_n_clicks: Number of clicks pressed on the export coexpression table button
        - coexpression_df: coexpression table data in dataframe format
        - module: Selected coexpression module
   
        Returns:
        - ('coexpression-download-df-to-csv', 'data'): Coexpression table in csv file format data
        """

        if download_n_clicks >= 1:
            df = pd.DataFrame(purge_html_export_table(coexpression_df))
            return dcc.send_data_frame(df.to_csv, f'[{module}] Co-Expression Network Analysis Table.csv', index=False)

        raise PreventUpdate

    # =================
    # Graph-related
    # =================

    @app.callback(
        Output('coexpression-module-graph', 'elements', allow_duplicate=True),
        Output('coexpression-module-graph', 'layout', allow_duplicate=True),
        Output('coexpression-module-graph', 'style', allow_duplicate=True),
        Output('coexpression-graph-container', 'style', allow_duplicate=True),
        Output('coexpression-module-graph-node-data',
               'children', allow_duplicate=True),
        Output('coexpression-module-graph-node-data-container',
               'style', allow_duplicate=True),

        Input('coexpression-combined-genes', 'data'),
        Input('coexpression-modules', 'value'),

        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-slider', 'data'),

        Input('coexpression-graph-layout', 'value'),
        State('coexpression-is-submitted', 'data'),

        State('coexpression-modules', 'options'),

        Input('coexpression-reset-graph', 'n_clicks'),

        prevent_initial_call=True
    )
    def display_graph(combined_gene_ids, module, submitted_network, submitted_algo, submitted_parameter_slider,
                      layout, coexpression_is_submitted, modules, *_):
        """
        Displays the coexpression graph 

        Parameters:
        - combined_gene_ids: Saved coexpression combined genes found in the dcc.Store
        - module: Selected coexpression module
        - submitted_network: Saved coexpression network found in the dcc.Store
        - submitted_algo: Saved coexpression clustering algorithm in the dcc.Store
        - submitted_parameter_slider: Saved parameter slider tuple found in the dcc.Store
        - layout: Selected coexpression graph layout
        - coexpression_is_submitted: [Coexpression] Saved boolean value of submitted valid input 
        - modules: List of available modules
        - *_: Other inputs that facilitates the state of the coexpression graph
        
        Returns:
        - ('coexpression-module-graph', 'elements'): List of elements of the coexpression graph
        - ('coexpression-module-graph', 'layout'): Selected coexpression graph layout
        - ('coexpression-module-graph', 'style'): {'visibility': 'visible'} for displaying the coexpression graph; otherwise {'display': 'none'}
        - ('coexpression-graph-container', 'style'): {'visibility': 'visible'} for displaying the coexpression graph container; otherwise {'display': 'none'}
        - ('coexpression-module-graph-node-data', 'children'): Short instruction on how to display the selected node data
        - ('coexpression-module-graph-node-data-container', 'style'): {'display': 'block'} for displaying the selected node data; otherwise {'display': 'none'}
        """

        if coexpression_is_submitted:
            if submitted_network and submitted_algo and submitted_algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[submitted_algo]['value']

                if not modules:
                    module_graph = load_module_graph(
                        combined_gene_ids, 'Click on a node to display information about the gene.', submitted_network, submitted_algo, parameters, layout)
                else:
                    module_graph = load_module_graph(
                        combined_gene_ids, module, submitted_network, submitted_algo, parameters, layout)

                # No enriched modules
                if not modules:
                    return module_graph + ({'display': 'none'}, '', {'display': 'none'})

                return module_graph + ({'visibility': 'visible', 'width': '100%'}, 'Click on a node to display information about the gene.', {'display': 'block'})

        raise PreventUpdate

    @app.callback(
        Output('coexpression-module-graph-node-data', 'children'),
        Input('coexpression-module-graph', 'tapNodeData')
    )
    def display_node_data(node_data):
        """
        Displays the selected coexpression graph's node's data

        Parameters:
        - node_data: Selected coexpression graph's node's data
        
        Returns:
        - ('coexpression-module-graph-node-data', 'children'): Selected node data
        """

        if node_data:
            with open(f'{Constants.OGI_MAPPING}/Nb_to_ogi.pickle', 'rb') as ogi_file, open(Constants.QTARO_DICTIONARY, 'rb') as qtaro_file,  open(f'{Constants.IRIC}/interpro.pickle', 'rb') as interpro_file, open(f'{Constants.IRIC}/pfam.pickle', 'rb') as pfam_file,  open(f'{Constants.IRIC_MAPPING}/msu_to_iric.pickle', 'rb') as iric_mapping_file, open(f'{Constants.TEXT_MINING_PUBMED}', 'rb') as pubmed_file, open(f'{Constants.MSU_MAPPING}/msu_to_rap.pickle', 'rb') as rapdb_file, open(f'{Constants.GENE_DESCRIPTIONS}/Nb/Nb_gene_descriptions.pickle', 'rb') as gene_descriptions_file:
                ogi_mapping = pickle.load(ogi_file)
                qtaro_mapping = pickle.load(qtaro_file)
                interpro_mapping = pickle.load(interpro_file)
                pfam_mapping = pickle.load(pfam_file)
                iric_mapping = pickle.load(iric_mapping_file)
                pubmed_mapping = pickle.load(pubmed_file)
                rapdb_mapping = pickle.load(rapdb_file)
                gene_descriptions_mapping = pickle.load(gene_descriptions_file)

                gene = node_data['id']

                node_data = [html.H5('Gene Information', className='pb-3'),

                             html.B('Name: '), get_msu_browser_link_single_str(
                                 gene, dash=True), html.Br(),
                             html.B('OGI: '), get_rgi_orthogroup_link_single_str(
                                 ogi_mapping[gene], dash=True), html.Br(),
                             html.B(
                                 'RAP-DB: ', ), get_rapdb_entry(gene, rapdb_mapping), html.Br(),

                             html.B(
                                 'Description: '), get_gene_description_entry(gene, gene_descriptions_mapping), html.Br(),
                             html.B(
                                 'UniProtKB/Swiss-Prot: '), get_uniprot_entry(gene, gene_descriptions_mapping), html.Br(), html.Br(),

                             html.B('Pfam: '), get_pfam_entry(
                                 gene, pfam_mapping, iric_mapping), html.Br(),
                             html.B('InterPro: '), get_interpro_entry(
                                 gene, interpro_mapping, iric_mapping), html.Br(),

                             html.B('QTL Analyses: '), get_qtaro_entry(
                                 gene, qtaro_mapping), html.Br(),
                             html.B('PubMed Article IDs: '), get_pubmed_entry(gene, pubmed_mapping)]

                return node_data

        raise PreventUpdate

    @app.callback(
        Output('coexpression-module-graph', 'style', allow_duplicate=True),
        Input('coexpression-modules', 'value'),

        prevent_initial_call=True
    )
    def hide_graph(*_):
        """
        Hides the coexpression graph 

        Parameters:
        - *_: Other inputs to facilitate the hiding of the coexpression graph
        
        Returns:
        - ('coexpression-module-graph', 'style'): {'visibility': 'hidden'} for hiding the coexpression graph 
        """

        return {'visibility': 'hidden'}

    @app.callback(
        Output('coexpression-module-graph', 'elements'),
        Output('coexpression-module-graph', 'layout'),
        Output('coexpression-module-graph', 'style', allow_duplicate=True),
        Output('coexpression-graph-container', 'style'),

        Input('coexpression-combined-genes', 'data'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-is-submitted', 'data'),
        State('coexpression-submitted-parameter-slider', 'data'),
        State('coexpression-submitted-layout', 'data'),

        prevent_initial_call=True
    )
    def hide_table_graph(combined_gene_ids, submitted_network, submitted_algo, coexpression_is_submitted, submitted_parameter_slider, layout):
        """
        Hides the coexpression graph 

        Parameters:
        - combined_gene_ids: Saved coexpression combined genes found in the dcc.Store
        - submitted_network: Saved coexpression network found in the dcc.Store
        - submitted_algo: Saved coexpression clustering algorithm in the dcc.Store
        - coexpression_is_submitted: [Coexpression] Saved boolean value of submitted valid input 
        - submitted_parameter_slider: Saved parameter slider tuple found in the dcc.Store
        - layout: Saved coexpression graph layout in the dcc.Store
        
        Returns:
        - ('coexpression-module-graph', 'elements'): List of elements of the coexpression graph
        - ('coexpression-module-graph', 'layout'): Saved coexpression graph layout; otherwise 'circle' for default value
        - ('coexpression-module-graph', 'style'): {'visibility': 'hidden'} for hiding the coexpression graph 
        - ('coexpression-graph-container', 'style'): {'visibility': 'hidden'} for hiding the coexpression graph container
        """

        if coexpression_is_submitted:
            if submitted_algo and submitted_algo in submitted_parameter_slider:
                parameters = submitted_parameter_slider[submitted_algo]['value']
                if not layout:
                    layout = 'circle'

                return load_module_graph(
                    combined_gene_ids, None, submitted_network, submitted_algo, parameters, layout) + ({'visibility': 'hidden'}, )

        raise PreventUpdate

    @app.callback(
        Output('coexpression-download-graph-to-json', 'data'),
        Input('coexpression-export-graph', 'n_clicks'),
        State('coexpression-submitted-network', 'data'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-parameter-slider', 'data'),
        State('coexpression-modules', 'value')
    )
    def download_coexpression_graph_to_tsv(download_n_clicks, submitted_network, submitted_algo, submitted_parameter_slider, module):
        """
        Export the coexpression graph in csv / tsv file format 

        Parameters:
        - download_n_clicks: Number of clicks pressed on the export coexpression table button
        - submitted_network: Saved coexpression network found in the dcc.Store
        - submitted_algo: Saved coexpression clustering algorithm found in the dcc.Store
        - submitted_parameter_slider: Saved parameter slider tuple found in the dcc.Store
        - module: Selected coexpression module
   
        Returns:
        - ('coexpression-download-graph-to-json', 'data'): Coexpression graph in csv / tsv file format data
        """

        if download_n_clicks >= 1:
            parameters = submitted_parameter_slider[submitted_algo]['value']
            module_idx = int(module.split(' ')[1])
            df = pd.read_csv(
                f'{Constants.TEMP}/{submitted_network}/{submitted_algo}/modules/{parameters}/module-{module_idx}.tsv', sep='\t')
            return dcc.send_data_frame(df.to_csv, f'[{module}] Co-Expression Network Analysis Graph.tsv', index=False, sep='\t')

        raise PreventUpdate

    # =================
    # Session-related
    # =================

    @app.callback(
        Output('coexpression-submitted-layout', 'data', allow_duplicate=True),
        Output('coexpression-pathway-active-tab',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-module', 'data', allow_duplicate=True),

        Input('coexpression-modules', 'value'),
        Input('coexpression-graph-layout', 'value'),
        Input('coexpression-modules-pathway', 'active_tab'),

        State('homepage-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def set_submitted_coexpression_session_state(module, layout, active_tab, homepage_is_submitted):
        """
        Sets the submitted coexpression related dcc.Store variables data 

        Parameters:
        - module: Selected coexpression module
        - layout: Selected coexpression graph layout
        - active_tab: Selected tab for coexpression table
        - homepage_is_submitted: [Coexpression] Saved boolean value of submitted valid input 

        Returns:
        - ('coexpression-submitted-layout', 'data'): Selected graph layout
        - ('coexpression-pathway-active-tab', 'data'): Selected active tab for coexpression table
        - ('coexpression-submitted-module', 'data'): Selected coexpression module
        """

        if homepage_is_submitted:
            return layout, active_tab, module

        raise PreventUpdate

    @app.callback(
        Output('coexpression-graph-layout', 'value'),
        Output('coexpression-modules-pathway', 'active_tab'),

        Input('coexpression-submitted-network', 'data'),
        Input('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-is-submitted', 'data'),

        State('coexpression-submitted-layout', 'data'),
        State('coexpression-pathway-active-tab', 'data')
    )
    def get_submitted_coexpression_session_state(submitted_network, submitted_algo, coexpression_is_submitted, layout, active_tab):
        """
        Gets the [Results container] coexpression related dcc.Store data and displays them 

        Parameters:
        - submitted_network: Saved coexpression network found in the dcc.Store
        - submitted_algo: Saved clustering algorithm found in the dcc.Store
        - layout: Saved coexpression graph layout found in the dcc.Store
        - active_tab: Saved coexpression active tab for the coexpression table found in the dcc.Store

        Returns:
        - ('coexpression-graph-layout', 'value'): Saved layout found in the dcc.Store; otherwise 'circle' for default value
        - ('coexpression-modules-pathway', 'value'): Saved coexpression module pathway found in the dcc.Store; otherwise 'tab-0' for default value
        """

        if coexpression_is_submitted:
            if not layout:
                layout = 'circle'

            if not active_tab:
                active_tab = 'tab-0'

            return layout, active_tab

        raise PreventUpdate

    @app.callback(
        Output('coexpression-clustering-algo', 'value'),
        Output('coexpression-addl-genes', 'value'),
        Output('coexpression-network', 'value'),
        State('coexpression-submitted-clustering-algo', 'data'),
        State('coexpression-submitted-addl-genes', 'data'),
        State('coexpression-submitted-network', 'data'),
        Input('coexpression-is-submitted', 'data')
    )
    def get_input_coexpression_session_state(algo, genes, network, *_):
        """
        Gets the [Input container] coexpression related dcc.Store data and displays them 

        Parameters:
        - algo: Saved clustering algorithm found in the dcc.Store
        - genes: Saved coexpression genes found in the dcc.Store
        - network: Saved coexpression network found in the dcc.Store
        - *_: Other inputs in facilitating the saved state of the coexpression input

        Returns:
        - ('coexpression-clustering-algo', 'value'): Saved clustering algorithm found in the dcc.Store; otherwise 'clusterone' for default value
        - ('coexpression-addl-genes', 'value'): Saved coexpression additional genes found in the dcc.Store; otherwise '' for default value
        - ('coexpression-network', 'value'): Saved coexpression network found in the dcc.Store; otherwise 'OS-CX' for default value
        """

        if not algo:
            algo = 'clusterone'

        if not genes:
            genes = ''

        if not network:
            network = 'OS-CX'

        return algo, genes, network
