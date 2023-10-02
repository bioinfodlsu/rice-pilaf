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
            html.P('Introduction')
        ], className='analysis-intro p-3'),
    ], className='mt-2'
)
