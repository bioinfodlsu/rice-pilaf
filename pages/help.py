import dash
from dash import dcc, html


dash.register_page(__name__, path='/help', name='Help')


layout = html.Div(id='lift-over-container', children=[
    dcc.Markdown('''
    Help Me    
    '''),
])
