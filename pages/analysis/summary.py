from dash import dash_table, dcc, html
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

        dbc.Button('Generate Summary',
                   id='summary-submit',
                   n_clicks=0,
                   className='page-button mb-3'),

        html.Br(),

        html.Div(
            id='summary-results-container',
            style={'display': 'none'},
            children=[
                dcc.Loading([
                    html.Hr(className='mt-3 mb-3'),

                    html.Br(),

                    html.Div(
                        id='summary-input',
                        className='analysis-intro p-3',
                    ),

                    html.Br(),

                    html.P(
                        html.Div([
                            html.P(
                                'The table below summarizes the results of the different post-GWAS analyses.',
                                className='text-start'
                            ),

                            dbc.Button([html.I(
                                className='bi bi-download me-2'),
                                'Export to CSV'],
                                id='summary-export-table',
                                n_clicks=0,
                                color='light', size='sm', className='table-button'),
                            dcc.Download(id='tfbs-download-df-to-csv'),
                            dbc.Button([html.I(
                                className='bi bi-arrow-clockwise me-2'),
                                'Reset Table'],
                                id='summary-reset-table',
                                color='light', size='sm', className='ms-3 table-button')
                        ], style={'textAlign': 'right'})
                    ),

                    html.Br(),

                    dash_table.DataTable(
                        id='summary-results-table',
                        style_cell={
                            'whiteSpace': 'pre-line'
                        },
                        markdown_options={'html': True},
                        sort_action='native',
                        sort_mode='multi',
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
