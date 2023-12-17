from dash import Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate

from ..lift_over import util as lift_over_util
from ..coexpression import util as coexpression_util


def init_callback(app):
    @app.callback(
        Output('summary-genomic-intervals-input', 'children'),
        State('homepage-submitted-genomic-intervals', 'data'),
        Input('homepage-is-submitted', 'data'),
        Input('summary-submit', 'n_clicks')
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('summary-is-submitted', 'data', allow_duplicate=True),
        Output('summary-submitted-addl-genes',
               'data', allow_duplicate=True),
        Output('summary-valid-addl-genes',
               'data', allow_duplicate=True),
        Output('summary-combined-genes',
               'data', allow_duplicate=True),

        Output('summary-addl-genes-error', 'style'),
        Output('summary-addl-genes-error', 'children'),

        Input('summary-submit', 'n_clicks'),
        State('homepage-is-submitted', 'data'),

        State('homepage-submitted-genomic-intervals', 'data'),
        State('summary-addl-genes', 'value'),
        prevent_initial_call=True
    )
    def submit_summary_input(summary_submitted_n_clicks, homepage_is_submitted,
                             genomic_intervals, submitted_addl_genes):
        if homepage_is_submitted and summary_submitted_n_clicks >= 1:
            if submitted_addl_genes:
                submitted_addl_genes = submitted_addl_genes.strip()
            else:
                submitted_addl_genes = ''

            list_addl_genes = list(
                filter(None, [gene.strip() for gene in submitted_addl_genes.split(';')]))

            # Check which genes are valid MSU IDs
            list_addl_genes, invalid_genes = coexpression_util.check_if_valid_msu_ids(
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

            return True, submitted_addl_genes, list_addl_genes, gene_ids, error_display, error

        raise PreventUpdate

    @app.callback(
        Output('summary-converter-modal', 'is_open'),
        Input('summary-converter-tooltip', 'n_clicks'),
    )
    def open_modals(summary_converter_tooltip_n_clicks):
        if ctx.triggered_id == 'summary-converter-tooltip' and summary_converter_tooltip_n_clicks > 0:
            return True

        raise PreventUpdate
