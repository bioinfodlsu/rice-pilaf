from dash import html
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
                        Constants.INTRO_LIFT_OVER],
                        className='pb-3'),
                html.Li([html.B('Gene Retrieval by Text Mining'), html.Br(),
                         Constants.INTRO_TEXT_MINING],
                        className='pb-3'),
                html.Li([html.B('Co-Expression Network Analysis'), html.Br(),
                         Constants.INTRO_COEXPRESSION],
                        className='pb-3'),
                html.Li([html.B('Regulatory Feature Enrichment'), html.Br(),
                         Constants.INTRO_TFBS],
                        className='pb-3'),
                html.Li([html.B('Epigenomic Information'), html.Br(),
                         Constants.INTRO_EPIGENOME],
                         className='pb-3'),
                html.Li([html.B('Summary'), html.Br(),
                         Constants.INTRO_SUMMARY])
            ], className='pb-0 mb-1')
        ], className='analysis-intro p-3'),
    ], className='mt-2 mb-4'
)
