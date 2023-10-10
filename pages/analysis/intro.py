from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks.constants import Constants

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_INTRO
    },
    hidden=False,
    children=[
        html.Div([
            html.P('Select an analysis from the panel on the left:'),

            html.Ul([
                html.Li([html.B('Gene List and Lift-Over'), html.Br(),
                        'In this page, you can obtain the list of genes overlapping your input intervals. Optionally, you can choose genomes to lift-over your Nipponbare coordinates to.'],
                        className='pb-3'),
                html.Li([html.B('Gene Retrieval by Text Mining'), html.Br(),
                         'In this page, you can retrieve gene names associated with traits, diseases, chemicals, etc. from a database constructed from text-mined PubMed abstracts.'],
                        className='pb-3'),
                html.Li([html.B('Co-Expression Network Analysis'), html.Br(),
                         'In this page, you can search for modules (a.k.a. communities, clusters) in rice co-expression networks, which are significantly enriched in the genes implicated by your GWAS. Likely functions of the modules are inferred by enrichment analysis against several ontologies and pathway databases.'],
                        className='pb-3'),
                html.Li([html.B('Regulatory Feature Enrichment'), html.Br(),
                         'In this page, you can search for transcription factors whose binding sites overlap significantly with your intervals,the idea being that your intervals might contain variants that affect the binding affinity of transcription factors.'],
                        className='pb-3'),
                html.Li([html.B('Browse Loci'), html.Br(),
                         'In this page, you can genome-browse your input intervals.'])
            ], className='pb-0 mb-1')
        ], className='analysis-intro p-3'),
    ], className='mt-2 mb-4'
)
