import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from callbacks.constants import Constants
from callbacks.tf_enrich.util import *


# =====================
# Miscellaneous Modals
# =====================

converter_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle('Rice ID Converter')
    ),
    dbc.ModalBody([
        html.P(
            'RicePilaf requires MSU accession IDs (i.e., those prefixed by "LOC_Os"). '),
        html.P([
            'To convert across different rice IDs, you may use this ',
            html.A(
                'tool', href='https://rapdb.dna.affrc.go.jp/converter/', target='_blank'
            ),
            ' from The Rice Annotation Project Database.'
        ])
    ])],
    id='tfbs-converter-modal',
    is_open=False,
    size='xl',
    scrollable=True
)

# ============
# Main Layout
# ============


layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_TFBS
    },
    hidden=True,
    children=[
        html.Div([
            html.P(
                [Constants.INTRO_TFBS,
                 ' Click ',
                 dcc.Link(
                     ['here ', html.I(
                         id='demo-link',
                         className='fa-solid fa-up-right-from-square fa-2xs'
                     )],
                     href='https://github.com/bioinfodlsu/rice-pilaf/wiki/2.4-Regulatory-Feature-Enrichment',
                     target='_blank',
                     className='top-navbar-item'
                 ),
                    ' for the user guide.']
            )
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            html.I(className='bi bi-chevron-bar-right me-2 non-clickable'),
            html.Span(id='tfbs-genomic-intervals-input'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div([
            dbc.Label(['Include additional genes from the pangenome lift-over or the text mining results',
                 html.I(
                     className='bi bi-info-circle', id='tfbs-converter-tooltip', n_clicks=0)]),
            html.Br(),
            dbc.Label(
                'Enter their MSU accession IDs, separated by a semicolon (e.g., LOC_Os01g03680; LOC_Os01g03690; LOC_Os01g04110)',
                className='small text-muted'),

            converter_modal,
            dbc.Textarea(id='tfbs-addl-genes'),

            html.Br(),

            dbc.Label(['Choose TF binding site prediction technique',
                       html.I(
                           className='bi bi-info-circle',
                           id='tfbs-technique-tooltip',
                           n_clicks=0
                       )]),
            dbc.RadioItems(
                id='tfbs-prediction-technique',
                options=TFBS_PREDICTION_TECHNIQUE_VALUE_LABEL,
                value='FunTFBS',
                inline=True
            ),

            html.Br(),
            dbc.Label(['Consider TF binding sites in the following regions',
                       html.I(
                           className='bi bi-info-circle',
                           id='tfbs-binding-site-tooltip',
                           n_clicks=0
                       )]),
            dbc.RadioItems(
                id='tfbs-set',
                options=TFBS_SET_VALUE_LABEL,
                value='promoters',
                inline=True
            ),

            html.Br(),

            dbc.Button('Run Analysis',
                       id='tfbs-submit',
                       n_clicks=0,
                       className='page-button'),
        ], className='analysis-intro p-3'),

        html.Br(),

        html.Div(
            id='tfbs-results-container',
            style={'display': 'none'},
            children=[
                dcc.Loading([
                    html.Hr(className='mt-3 mb-3'),

                    html.Br(),

                    html.Div(
                        id='tfbs-input',
                        className='analysis-intro p-3'
                    ),

                    html.Br(),

                    html.P(
                        html.Div([
                            html.Div([
                                html.Span(
                                    id='tfbs-table-stats')
                            ], className='mb-3 stats'),
                            dbc.Button([html.I(
                                className='bi bi-download me-2'),
                                'Export to CSV'],
                                id='tfbs-export-table',
                                n_clicks=0,
                                color='light', size='sm', className='table-button'),
                            dcc.Download(id='tfbs-download-df-to-csv'),
                            dbc.Button([html.I(
                                className='bi bi-arrow-clockwise me-2'),
                                'Reset Table'],
                                id='tfbs-reset-table',
                                color='light', size='sm', className='ms-3 table-button')
                        ], style={'textAlign': 'right'})
                    ),

                    dash_table.DataTable(
                        id='tfbs-results-table',
                        style_cell={
                            'whiteSpace': 'pre-line'
                        },
                        markdown_options={'html': True},
                        sort_action='native',
                        filter_action='native',
                        filter_options={'case': 'insensitive',
                                        'placeholder_text': '🔎︎ Search Column'},
                        page_action='native',
                        page_size=15,
                        cell_selectable=False,
                        style_table={'overflowX': 'auto'}
                    )
                ])
            ])
    ], className='mt-2 mb-4'
)
