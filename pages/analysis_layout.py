from dash import html

import pages.analysis.intro as intro
import pages.analysis.lift_over as lift_over
import pages.analysis.co_expr as co_expr
import pages.analysis.tf_enrich as tf_enrich
import pages.analysis.epigenome as epigenome
import pages.analysis.text_mining as text_mining
import pages.analysis.summary as summary
import pages.analysis.template as template

from collections import OrderedDict

from callbacks.constants import Constants


def get_analaysis_layout_dictionary():
    return OrderedDict({

        # Insert your analysis option in the analysis navbar here in the order you would like it be seen 
        #Constants.LABEL_TEMPLATE: 'Template',
        Constants.LABEL_LIFT_OVER: 'Gene List and Lift-Over',
        Constants.LABEL_TEXT_MINING: 'Gene Retrieval by Text Mining',
        Constants.LABEL_COEXPRESSION: 'Co-Expression Network Analysis',
        Constants.LABEL_TFBS: 'Regulatory Feature Enrichment',
        Constants.LABEL_EPIGENOME: 'Epigenomic Information',
        Constants.LABEL_SUMMARY: 'Summary'
    })


layout = html.Div(
    children=[

        # Insert your analysis page's layout
        #template.layout,
        intro.layout,
        lift_over.layout,
        text_mining.layout,
        co_expr.layout,
        tf_enrich.layout,
        epigenome.layout,
        summary.layout
    ]
)
