from dash import dash_table, dcc, html
from callbacks.constants import Constants
import dash_bootstrap_components as dbc


# =====================
# Miscellaneous Modals
# =====================

NULL_PLACEHOLDER = '–'

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

                            html.P([
                                html.B(
                                    'A value of "null" indicates that the gene was not included in the relevant post-GWAS analysis. '
                                ), 'Try including it in the list of additional genes for that analysis.'],
                                className='text-start'
                            ),

                            html.Br(),

                            dbc.Button([html.I(
                                className='bi bi-download me-2'),
                                'Export to CSV'],
                                id='summary-export-table',
                                n_clicks=0,
                                color='light', size='sm', className='table-button'),
                            dcc.Download(id='summary-download-df-to-csv'),
                            dbc.Button([html.I(
                                className='bi bi-arrow-clockwise me-2'),
                                'Reset Table'],
                                id='summary-reset-table',
                                color='light', size='sm', className='ms-3 table-button')
                        ], style={'textAlign': 'right'})
                    ),

                    dash_table.DataTable(
                        id='summary-results-table',
                        style_cell={
                            'whiteSpace': 'pre-line'
                        },
                        markdown_options={'html': True},
                        sort_as_null=[NULL_PLACEHOLDER],
                        sort_action='native',
                        sort_mode='multi',
                        filter_action='native',
                        filter_options={'case': 'insensitive',
                                        'placeholder_text': '🔎︎ Search Column'},
                        page_action='native',
                        page_size=15,
                        cell_selectable=False,
                        style_table={'overflowX': 'auto'},
                        style_header={
                            'textDecoration': 'underline',
                            'textDecorationStyle': 'dotted',
                        },
                        tooltip_header={
                            'Gene': 'Gene of interest',
                            '# Orthologs': 'Number of orthologs across Nipponbare, N22, MH63, Azu, ARC, IR64, and CMeo',
                            '# QTL Analyses': 'Number of QTL analyses featuring the gene based on QTARO',
                            '# PubMed Article IDs': 'Number of PubMed articles featuring the gene based on our in-house text-mined dataset',
                            '# Modules': 'Total number of modules that include the gene',
                            '# Enriched Modules': 'Number of enriched modules that include the gene',
                            '# Gene Ontology Terms': 'Total number of gene ontology terms related to the gene',
                            '# Enriched Gene Ontology Terms': 'Number of gene ontology terms that are overrepresented in the enriched modules containing the gene',
                            '# Trait Ontology Terms': 'Total number of trait ontology terms related to the gene',
                            '# Enriched Trait Ontology Terms': 'Number of trait ontology terms that are overrepresented in the enriched modules containing the gene',
                            '# Plant Ontology Terms': 'Total number of plant ontology terms related to the gene',
                            '# Enriched Plant Ontology Terms': 'Number of plant ontology terms that are overrepresented in the enriched modules containing the gene',
                            '# Pathways': 'Total number of pathways related to the gene',
                            '# Enriched Pathways (Over-Representation)': 'Number of pathways that are impacted in the enriched modules containing the gene (determined via over-representation analysis)',
                            '# Enriched Pathways (Pathway-Express)': 'Number of pathways that are impacted in the enriched modules containing the gene (determined via the topology-aware method Pathway-Express)',
                            '# Enriched Pathways (SPIA)': 'Number of pathways that are impacted in the enriched modules containing the gene (determined via topology-aware method SPIA)',
                        }
                    )
                ])
            ])
    ], className='mt-2 mb-4'
)
