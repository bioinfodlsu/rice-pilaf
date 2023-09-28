from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks.constants import Constants

from callbacks.browse_loci.util import *

layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_INTRO
    },
    hidden=True,
    children=[
        html.Div([
            html.P('Introduction')
        ], className='analysis-intro p-3'),
    ], className='mt-2'
)
