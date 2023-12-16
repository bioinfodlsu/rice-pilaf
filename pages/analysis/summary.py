from dash import html
from callbacks.constants import Constants
import dash_bootstrap_components as dbc


# =====================
# Miscellaneous Modals
# =====================

converter_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle('Rice ID Converter')
    ),
    dbc.ModalBody([
        html.P(
            'RicePilaf requires MSU accession IDs (i.e., IDs prefixed by "LOC_Os"). '),
        html.P([
            'To convert across different rice IDs, you may use this ',
            html.A(
                'tool', href='https://rapdb.dna.affrc.go.jp/converter/', target='_blank'
            ),
            ' from The Rice Annotation Project Database.'
        ])
    ])],
    id='summary-converter-modal',
    is_open=False,
    size='lg',
    scrollable=True
)


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

        html.Div([
            dbc.Label(['Include additional genes from the pangenome lift-over or the text mining results',
                       html.I(
                           className='bi bi-info-circle', id='summary-converter-tooltip', n_clicks=0)]),
            html.Br(),
            dbc.Label(
                'Enter their MSU accession IDs, separated by a semicolon (e.g., LOC_Os01g03680; LOC_Os01g03690; LOC_Os01g04110)',
                className='small text-muted'),

            converter_modal,
            dbc.Alert(
                id='summary-addl-genes-error',
                color='danger',
                style={'display': 'none'}
            ),
            dbc.Textarea(id='summary-addl-genes'),

            html.Br(),

            dbc.Button('Generate Summary',
                       id='summary-submit',
                       n_clicks=0,
                       className='page-button'),
        ], className='analysis-intro p-3'),
    ]
)
