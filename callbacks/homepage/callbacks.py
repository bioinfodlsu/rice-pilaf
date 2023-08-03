from collections import namedtuple, OrderedDict
import pages.analysis.lift_over as lift_over
import pages.analysis.co_expr as co_expr
import pages.analysis.tf_enrich as tf_enrich
import pages.analysis.browse_loci as browse_loci
import pages.analysis.text_mining as text_mining

from dash import Input, Output, State, html, ctx, ALL
from dash.exceptions import PreventUpdate
from .util import *
from ..lift_over import util as lift_over_util
from ..browse_loci import util as browse_loci_util
from ..constants import Constants

const = Constants()


def init_callback(app):
    @app.callback(
        Output('page', 'children'),
        Output('page', 'style'),

        Output('lift-over-link', 'className'),
        Output('coexpression-link', 'className'),
        Output('tf-enrichment-link', 'className'),
        Output('text-mining-link', 'className'),
        Output('igv-link', 'className'),

        State('lift-over-link', 'className'),
        State('coexpression-link', 'className'),
        State('tf-enrichment-link', 'className'),
        State('text-mining-link', 'className'),
        State('igv-link', 'className'),

        Input('lift-over-link', 'n_clicks'),
        Input('coexpression-link', 'n_clicks'),
        Input('tf-enrichment-link', 'n_clicks'),
        Input('text-mining-link', 'n_clicks'),
        Input('igv-link', 'n_clicks'),

        prevent_initial_call=True
    )
    def display_specific_analysis_page(lift_over_link_class, coexpression_link_class, tf_enrichment_link_class,
                                       text_mining_link_class,igv_class, *_):

        layout_link = namedtuple('layout_link', 'layout link_class')

        display_map = OrderedDict()

        # IMPORTANT:
        # The insertion of items should follow the same order as the declaration of the parameters
        display_map['lift-over-link'] = layout_link(
            lift_over.layout, lift_over_link_class)
        display_map['coexpression-link'] = layout_link(
            co_expr.layout, coexpression_link_class)
        display_map['tf-enrichment-link'] = layout_link(
            tf_enrich.layout, tf_enrichment_link_class)
        display_map['text-mining-link'] = layout_link(
            text_mining.layout, text_mining_link_class)
        display_map['igv-link'] = layout_link(
            browse_loci.layout, igv_class)

        return display_map[ctx.triggered_id].layout, {'display': 'block'}, *set_active_class(display_map, ctx.triggered_id)

    @app.callback(
        Output('input-error', 'children'),
        Output('input-error', 'style'),
        Output('homepage-is-submitted', 'data'),

        Output('homepage-genomic-intervals-submitted-input', 'data'),

        Output('lift-over-is-submitted', 'data', allow_duplicate=True),
        Output('lift-over-other-refs-submitted-input',
               'data', allow_duplicate=True),
        Output('lift-over-other-refs-saved-input',
               'data', allow_duplicate=True),

        Output('lift-over-active-tab', 'data', allow_duplicate=True),
        Output('lift-over-active-filter', 'data', allow_duplicate=True),

        Output('igv-is-submitted', 'data', allow_duplicate=True),
        Output('igv-selected-genomic-intervals-saved-input',
               'data', allow_duplicate=True),
        Output('igv-selected-genomic-intervals-submitted-input',
               'data', allow_duplicate=True),
        Output('igv-selected-tracks-submitted-input',
               'data', allow_duplicate=True),

        Output('coexpression-network-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-clustering-algo-saved-input',
               'data', allow_duplicate=True),
        Output('coexpression-parameter-module-saved-input',
               'data', allow_duplicate=True),

        Output('coexpression-is-submitted', 'data', allow_duplicate=True),
        Output('coexpression-submitted-network',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-clustering-algo',
               'data', allow_duplicate=True),
        Output('coexpression-submitted-parameter-module',
               'data', allow_duplicate=True),

        Output('tfbs-is-submitted', 'data', allow_duplicate=True),
        Output('tfbs-submitted-input', 'data', allow_duplicate=True),
        Output('tfbs-saved-input', 'data', allow_duplicate=True),

        State('homepage-genomic-intervals', 'value'),

        Input('homepage-submit', 'n_clicks'),
        Input('homepage-reset', 'n_clicks'),
        Input('homepage-clear-cache', 'n_clicks'),

        prevent_initial_call=True
    )
    def parse_input(nb_intervals_str, n_clicks, *_):
        if 'homepage-clear-cache' == ctx.triggered_id:
            clear_cache_folder()

        if 'homepage-reset' == ctx.triggered_id:
            return None, {'display': 'none'}, False, \
                '', \
                None, None, None, \
                None, None, \
                None, None, None, None, \
                None, None, None, \
                None, None, None, None, \
                None, None, None

        if 'homepage-submit' == ctx.triggered_id and n_clicks >= 1:
            if nb_intervals_str:
                intervals = lift_over_util.get_genomic_intervals_from_input(
                    nb_intervals_str)

                if lift_over_util.is_error(intervals):
                    return [f'Error encountered while parsing genomic interval {intervals[1]}', html.Br(), lift_over_util.get_error_message(intervals[0])], \
                        {'display': 'block'}, False, \
                        nb_intervals_str, \
                        None, None, None, \
                        None, None, \
                        None, None, None, None, \
                        None, None, None, \
                        None, None, None, None, \
                        None, None, None
                else:
                    track_db = [[const.ANNOTATIONS_NB, 'IRGSPMSU.gff.db', 'gff'],
                                [const.OPEN_CHROMATIN_PANICLE, 'SRR7126116_ATAC-Seq_Panicles.bed', 'bed']]

                    for db in track_db:
                        if db[2] != 'bed':
                            browse_loci_util.write_igv_tracks_to_file(
                                f'{db[0]}/{db[1]}', db[1], nb_intervals_str, db[2])
                    return None, {'display': 'none'}, True, \
                        nb_intervals_str, \
                        None, None, None, \
                        None, None, \
                        None, None, None, None, \
                        None, None, None, \
                        None, None, None, None, \
                        None, None, None
            else:
                return [f'Error: Input for genomic interval should not be empty.'], \
                    {'display': 'block'}, False, \
                    nb_intervals_str, \
                    None, None, None, \
                    None, None, \
                    None, None, None, None, \
                    None, None, None, \
                    None, None, None, None, \
                    None, None, None

        raise PreventUpdate

    @app.callback(
        Output('lift-over-nb-table', 'data'),
        Output('lift_over_nb_entire_table', 'data'),
        Input('homepage-genomic-intervals-submitted-input', 'data'),
        State('homepage-is-submitted', 'data')
    )
    def get_nipponbare_gene_ids(nb_intervals_str, homepage_is_submitted):
        if homepage_is_submitted:
            if nb_intervals_str:
                nb_intervals = lift_over_util.get_genomic_intervals_from_input(
                    nb_intervals_str)

                if not lift_over_util.is_error(nb_intervals):
                    genes_from_Nb = lift_over_util.get_genes_from_Nb(
                        nb_intervals)

                    return genes_from_Nb[1], genes_from_Nb[0].to_dict('records')

        raise PreventUpdate

    @app.callback(
        Output('homepage-genomic-intervals-saved-input', 'data', allow_duplicate=True),
        Input('homepage-genomic-intervals', 'value'),
        #Output('homepage-genomic-intervals', 'value', allow_duplicate=True),
        Input('homepage-reset', 'n_clicks'),
        Input({'type': 'example-genomic-interval',
              'description': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )
    def set_input_fields(genomic_intervals, *_):    
        if ctx.triggered_id:
            if 'homepage-reset' == ctx.triggered_id:
                return None

            if 'homepage-genomic-intervals' == ctx.triggered_id:
                return genomic_intervals
                
            return get_example_genomic_interval(ctx.triggered_id['description'])

        raise PreventUpdate

    """
    @app.callback(
        Output('post-gwas-analysis-container', 'hidden'),
        Output('homepage-reset', 'href'),
        Input('homepage-is-submitted', 'data')
    )
    def hide_side_bars(homepage_is_submitted):
        if homepage_is_submitted:
            return False, '/'
        else:
            return True, '/'
    """
    @app.callback(
        Output('homepage-results-container','style'),
        Input('homepage-is-submitted', 'data'),
        Input('homepage-submit', 'n_clicks')
    )
    def display_homepage_output(homepage_is_submitted, *_):
        if homepage_is_submitted:
            return {'display': 'block'}

        else:
            return {'display': 'none'}
    """
    @app.callback(
        #Output('homepage-genomic-intervals-saved-input', 'data', allow_duplicate=True),
        Output('homepage-genomic-intervals-saved-input', 'data'),
        Input('homepage-genomic-intervals', 'value'),
        #prevent_initial_call=True
    )
    def set_input_homepage_session_state(genomic_intervals):
        return genomic_intervals
    """
    
    @app.callback(
        Output('homepage-genomic-intervals', 'value'),
        Input('homepage-genomic-intervals-saved-input', 'data'),
    )
    def get_input_homepage_session_state(genomic_intervals):
        return genomic_intervals
    
    @app.callback(
        Output('genomic-interval-modal', 'is_open'),
        Input('genomic-interval-tooltip', 'n_clicks')
    )
    def open_modals(tooltip_n_clicks):
        if tooltip_n_clicks > 0:
            return True

        raise PreventUpdate