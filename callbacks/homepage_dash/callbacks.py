from dash import Input, Output, State, html, ctx
from dash.exceptions import PreventUpdate
from .util import *
from ..lift_over import util as lift_over_util
from ..browse_loci import util as browse_loci_util
from ..constants import Constants
const = Constants()


def init_callback(app):

    @app.callback(
        Output('input-error', 'children'),
        Output('input-error', 'style'),
        Output('lift-over-is-submitted', 'data'),

        Output('lift-over-genomic-intervals-saved-input', 'data'),
        Output('lift-over-other-refs-saved-input', 'data'),

        Output('lift-over-active-tab', 'data', allow_duplicate=True),
        Output('lift-over-active-filter', 'data', allow_duplicate=True),

        Output('igv-selected-genomic-intervals-saved-input',
               'data', allow_duplicate=True),
        Output('igv-active-filter', 'data', allow_duplicate=True),

        Output('coexpression-clustering-algo-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-parameter-module-saved-input',
               'data', allow_duplicate=True),

        Output('coexpression-is-submitted', 'data', allow_duplicate=True),
        Output('coexpression-submitted-clustering-algo',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-parameter-module',
               'data', allow_duplicate=True),

        Output('tfbs-is-submitted', 'data', allow_duplicate=True),
        Output('tfbs-submitted-input', 'data', allow_duplicate=True),
        Output('tfbs-saved-input', 'data', allow_duplicate=True),

        Input('lift-over-submit', 'n_clicks'),
        Input('lift-over-reset', 'n_clicks'),
        Input('lift-over-clear-cache', 'n_clicks'),

        State('lift-over-genomic-intervals', 'value'),
        State('lift-over-other-refs', 'value'),

        prevent_initial_call=True
    )
    def parse_input(n_clicks, reset_n_clicks, clear_cache_n_clicks, nb_intervals_str, other_refs):
        if 'lift-over-clear-cache' == ctx.triggered_id:
            clear_cache_folder()

        if 'lift-over-reset' == ctx.triggered_id:
            return None, {'display': 'none'}, False, '', '', \
                None, None, None, None, None, None, None, None, None, None, None, None

        if 'lift-over-submit' == ctx.triggered_id:
            if nb_intervals_str:
                intervals = lift_over_util.get_genomic_intervals_from_input(
                    nb_intervals_str)
                other_refs = lift_over_util.sanitize_other_refs(other_refs)

                if lift_over_util.is_error(intervals):
                    return [f'Error encountered while parsing genomic interval {intervals[1]}', html.Br(), lift_over_util.get_error_message(intervals[0])], \
                        {'display': 'block'}, str(
                            True), nb_intervals_str, other_refs, \
                        None, None, None, None, None, None, None, None, None, None, None, None
                else:
                    track_db = [[const.ANNOTATIONS_NB, 'IRGSPMSU.gff.db', 'gff'],
                                [const.OPEN_CHROMATIN_PANICLE, 'SRR7126116_ATAC-Seq_Panicles.bed', 'bed']]

                    for db in track_db:
                        if db[2] != 'bed':
                            browse_loci_util.get_data_base_on_loci(
                                f'{db[0]}/{db[1]}', db[1], nb_intervals_str, db[2])
                    return None, {'display': 'none'}, True, nb_intervals_str, other_refs, \
                        None, None, None, None, None, None, None, None, None, None, None, None
            else:
                return [f'Error: Input for genomic interval should not be empty.'], \
                    {'display': 'block'}, \
                    True, nb_intervals_str, other_refs, \
                    None, None, None, None, None, None, None, None, None, None, None, None

        raise PreventUpdate

    @app.callback(
        Output('lift-over-genomic-intervals', 'value'),
        Output('lift-over-other-refs', 'value'),
        Input('lift-over-reset', 'n_clicks'),
        State('lift-over-other-refs', 'multi')
    )
    def clear_input_fields(reset_n_clicks, is_multi_other_refs):
        if reset_n_clicks >= 1:
            if is_multi_other_refs:
                return None, []
            else:
                return None, None

        raise PreventUpdate

    @app.callback(
        Output('post-gwas-analysis-container', 'hidden'),
        Output('lift-over-reset', 'href'),
        Input('lift-over-is-submitted', 'data'),
    )
    def hide_side_bars(is_submitted):
        if is_submitted:
            return False, '/'
        else:
            return True, '/'
