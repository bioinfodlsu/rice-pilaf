from dash import html

import pages.analysis.lift_over as lift_over
import pages.analysis.co_expr as co_expr
import pages.analysis.tf_enrich as tf_enrich
import pages.analysis.browse_loci as browse_loci

from callbacks.constants import Constants
const = Constants()

def get_analaysis_layout_dictionary():
    return {
        const.LIFT_OVER: 'Gene List and Lift-Over',
        const.COEXPRESSION: 'Co-Expression Network Analysis',
        const.TFBS: 'Regulatory Feature Enrichment',
        const.IGV: 'Browse Loci'
    }

layout = html.Div(children=[
    lift_over.layout, 
    co_expr.layout, 
    tf_enrich.layout, 
    browse_loci.layout
])

