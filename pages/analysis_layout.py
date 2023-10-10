from dash import html

import pages.analysis.intro as intro
import pages.analysis.lift_over as lift_over
import pages.analysis.co_expr as co_expr
import pages.analysis.tf_enrich as tf_enrich
import pages.analysis.browse_loci as browse_loci
import pages.analysis.text_mining as text_mining

from collections import OrderedDict

from callbacks.constants import Constants


def get_analaysis_layout_dictionary():
    return OrderedDict({
        Constants.LABEL_LIFT_OVER: 'Gene List and Lift-Over',
        Constants.LABEL_TEXT_MINING: 'Gene Retrieval by Text Mining',
        Constants.LABEL_COEXPRESSION: 'Co-Expression Network Analysis',
        Constants.LABEL_TFBS: 'Regulatory Feature Enrichment',
        Constants.LABEL_IGV: 'Epigenomic Information'
    })


layout = html.Div(
    children=[
        intro.layout,
        lift_over.layout,
        text_mining.layout,
        co_expr.layout,
        tf_enrich.layout,
        browse_loci.layout
    ]
)
