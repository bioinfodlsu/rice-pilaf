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

)
