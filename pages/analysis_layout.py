from dash import html

import pages.analysis.lift_over as lift_over
import pages.analysis.co_expr as co_expr
import pages.analysis.tf_enrich as tf_enrich
import pages.analysis.browse_loci as browse_loci
import pages.analysis.text_mining as text_mining

layout = html.Div(children=[
    lift_over.layout, 
    co_expr.layout, 
    tf_enrich.layout, 
    browse_loci.layout,
    text_mining.layout
])