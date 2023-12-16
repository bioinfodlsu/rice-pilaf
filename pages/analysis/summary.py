from dash import html
from callbacks.constants import Constants

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_SUMMARY
    },
    hidden=True,
    children=[
        html.Div([
            html.P(
                [
                    Constants.INTRO_SUMMARY,
                    # ' Click ',
                    # dcc.Link(
                    #     ['here ', html.I(
                    #         id='demo-link',
                    #         className='fa-solid fa-up-right-from-square fa-2xs'
                    #     )],
                    #     href='https://github.com/bioinfodlsu/rice-pilaf/wiki/2.2-Gene-retrieval-by-text-mining',
                    #     target='_blank',
                    #     className='top-navbar-item'
                    # ),
                    # ' for the user guide.'
                ]

            ),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='summary-genomic-intervals-input'),
        ], className='analysis-intro p-3'),

        html.Br(),
    ]
)
