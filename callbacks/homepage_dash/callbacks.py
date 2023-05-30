from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
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
        Output('lift-over-reset', 'n_clicks'),

        Output('lift-over-is-resetted', 'data'),

        Output('lift-over-submit', 'n_clicks'),

        Output('lift-over-active-tab', 'data', allow_duplicate=True),
        Output('lift-over-active-filter', 'data', allow_duplicate=True),
        Output('igv-selected-genomic-intervals-saved-input',
               'data', allow_duplicate=True),
        Output('igv-active-filter', 'data', allow_duplicate=True),

        Input('lift-over-submit', 'n_clicks'),
        Input('lift-over-reset', 'n_clicks'),

        State('lift-over-genomic-intervals', 'value'),
        State('lift-over-other-refs', 'value'),
        State('lift-over-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def parse_input(n_clicks, reset_n_clicks, nb_intervals_str, other_refs, is_submitted):
        if is_submitted and reset_n_clicks >= 1:
            return None, {'display': 'none'}, False, '', '', reset_n_clicks, True, n_clicks, None, None, None, None

        if n_clicks >= 1:
            if nb_intervals_str:
                intervals = lift_over_util.get_genomic_intervals_from_input(
                    nb_intervals_str)
                other_refs = lift_over_util.sanitize_other_refs(other_refs)

                if lift_over_util.is_error(intervals):
                    return [f'Error encountered while parsing genomic interval {intervals[1]}', html.Br(), lift_over_util.get_error_message(intervals[0])], \
                        {'display': 'block'}, str(
                            True), nb_intervals_str, other_refs, 0, False, 0, None, None, None, None
                else:
                    track_db = [[const.ANNOTATIONS_NB, 'IRGSPMSU.gff.db', 'gff'],
                                [const.OPEN_CHROMATIN_PANICLE, 'SRR7126116_ATAC-Seq_Panicles.bed', 'bed']]

                    for db in track_db:
                        if db[2] != 'bed':
                            browse_loci_util.get_data_base_on_loci(
                                f'{db[0]}/{db[1]}', db[1], nb_intervals_str, db[2])
                    return None, {'display': 'none'}, True, nb_intervals_str, other_refs, 0, False, 0, None, None, None, None
            else:
                return [f'Error: Input for genomic interval should not be empty.'], \
                    {'display': 'block'}, \
                    True, nb_intervals_str, other_refs, 0, False, 0, None, None, None, None

        raise PreventUpdate
    """
    @app.callback(
        Output('homepage-dash-navlink', 'disabled'),
        Input('lift-over-is-submitted', 'data'),
    )
    def disable_side_bars(is_submitted):
        if is_submitted:
            return True
        else:
            return False
    """
