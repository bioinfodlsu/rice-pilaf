from dash import html

import pages.analysis.lift_over as lift_over
import pages.analysis.co_expr as co_expr
import pages.analysis.tf_enrich as tf_enrich
import pages.analysis.browse_loci as browse_loci

def get_analaysis_layout_dictionary():
    return {
        'lift-over': 'Gene List and Lift-Over',
        'co-expression': 'Co-Expression Network Analysis',
        'tf-enrich': 'Regulatory Feature Enrichment',
        'browse-loci': 'Browse Loci'
    }

layout = html.Div(children=[
    lift_over.layout, 
    co_expr.layout, 
    tf_enrich.layout, 
    browse_loci.layout
])

