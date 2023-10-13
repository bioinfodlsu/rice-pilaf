import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html
from callbacks.constants import Constants
from callbacks.tf_enrich.util import *

# ===========================
# Prediction Technique Modal
# ===========================

fun_tfbs = html.Li([
    html.B('FunTFBS'), html.Br(),
    html.Span('Identification of binding sites with transcriptional regulatory functions based on the correlation between binding motif frequencies and conservation scores',
              className='algo-desc'),
    html.Div([
        html.Span(
            'Tian, F., Yang, D. C., Meng, Y. Q., Jin, J., & Gao, G. (2020). PlantRegMap: Charting functional regulatory maps in plants. '),
        html.I('Nucleic Acids Research, 48'),
        html.Span('(D1), D1104–D1113. '),
        html.A(
            'https://doi.org/10.1093/nar/gkz1020',
            href='https://doi.org/10.1093/nar/gkz1020',
            target='_blank')
    ], className='reference')
])

motif_conservation = html.Li([
    html.B('Motif Conservation'), html.Br(),
    html.Span('Motif scanning paired with conserved element information',
              className='algo-desc'),
    html.Div([
        html.Span(
            'Tian, F., Yang, D. C., Meng, Y. Q., Jin, J., & Gao, G. (2020). PlantRegMap: Charting functional regulatory maps in plants. '),
        html.I('Nucleic Acids Research, 48'),
        html.Span('(D1), D1104–D1113. '),
        html.A(
            'https://doi.org/10.1093/nar/gkz1020',
            href='https://doi.org/10.1093/nar/gkz1020',
            target='_blank')
    ], className='reference')
])

motif_scanning = html.Li([
    html.B('Motif Scan'), html.Br(),
    html.Span('Simple motif scanning using FIMO',
              className='algo-desc'),
    html.Div([
        html.Span(
            'Grant, C. E., Bailey, T. L., & Noble, W. S. (2011). FIMO: Scanning for occurrences of a given motif. '),
        html.I('Bioinformatics, 27'),
        html.Span('(7), 1017–1018. '),
        html.A(
            'https://doi.org/10.1093/bioinformatics/btr064',
            href='https://doi.org/10.1093/bioinformatics/btr064',
            target='_blank')
    ], className='reference')
])

prediction_technique_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle(
            'Transcription Factor Binding Site Prediction Technique'),
    ),
    dbc.ModalBody([
        html.P(
            'In performing regulatory feature enrichment, RicePilaf uses binding site information of transcription factors obtained from PlantRegMap.'),
        html.P(
            'PlantRegMap provides several sets of predicted binding sites depending on how the prediction was performed:'),
        html.Ul([
            fun_tfbs,
            html.Br(),
            motif_conservation,
            html.Br(),
            motif_scanning
        ])
    ])],
    id='tfbs-prediction-technique-modal',
    is_open=False,
    size='xl',
    scrollable=True
)

# ============================
# Set (Target Sequence) Modal
# ============================

set_modal = dbc.Modal([
    dbc.ModalHeader(
        dbc.ModalTitle(
            'Target Sequence for Transcription Factor Binding Site Prediction'),
    ),
    dbc.ModalBody([
        html.P(
            'In performing regulatory feature enrichment, RicePilaf uses binding site information of transcription factors obtained from PlantRegMap.'),
        html.P(
            'PlantRegMap provides several sets of predicted binding sites depending on the target sequence used: '),
        html.Ul([
            html.Li(
                'Promoter region (defined as –500/+100 bp of the transcription start site)'),
            html.Li('Whole genome')
        ]),
        html.Div([
            html.Span(
                'Tian, F., Yang, D. C., Meng, Y. Q., Jin, J., & Gao, G. (2020). PlantRegMap: Charting functional regulatory maps in plants. '),
            html.I('Nucleic Acids Research, 48'),
            html.Span('(D1), D1104–D1113. '),
            html.A(
                'https://doi.org/10.1093/nar/gkz1020',
                href='https://doi.org/10.1093/nar/gkz1020',
                target='_blank')
        ], className='reference')
    ])],
    id='tfbs-set-modal',
    is_open=False,
    size='xl',
    scrollable=True
)

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
    id='tfbs-converter-modal',
    is_open=False,
    size='lg',
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
            dbc.Alert(
                id='tfbs-addl-genes-error',
                color='danger',
                style={'display': 'none'}
            ),
            dbc.Textarea(id='tfbs-addl-genes'),

            html.Br(),

            dbc.Label(['Select a transcription factor binding site prediction technique',
                       html.I(
                           className='bi bi-info-circle',
                           id='tfbs-prediction-technique-tooltip',
                           n_clicks=0
                       )]),

            prediction_technique_modal,
            dbc.RadioItems(
                id='tfbs-prediction-technique',
                options=TFBS_PREDICTION_TECHNIQUE_VALUE_LABEL,
                value='FunTFBS',
                inline=True,
                className='ms-3 mt-1'
            ),

            html.Br(),
            dbc.Label(['Consider transcription factor binding sites in the following regions',
                       html.I(
                           className='bi bi-info-circle',
                           id='tfbs-set-tooltip',
                           n_clicks=0
                       )]),

            set_modal,
            dbc.RadioItems(
                id='tfbs-set',
                options=TFBS_SET_VALUE_LABEL,
                value='promoters',
                inline=True,
                className='ms-3 mt-1'
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

                            html.P(
                                'The table below lists these transcription factors, along with the significance of the overlap.',
                                className='text-start'
                            ),

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
