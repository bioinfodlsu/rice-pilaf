from dash import html
from callbacks.constants import Constants

# ============
# Main Layout
# ============


layout = html.Div(
    id={
        'type': 'analysis-layout',
        'label': Constants.LABEL_TEMPLATE # Replace the Constants.LABEL_TEMPLATE with the constant variable you have defined in the Constants.py for consistency
    },
    hidden=True,
    children=[
        
        # Place the necessary UI here
        html.Div('Hello World')

    ], className='mt-2 mb-4'
)
