import dash
from dash import dcc, html


dash.register_page(__name__, path='/help', name='Help')


layout = html.Div(id='help-container', children=[
    dcc.Markdown('''
    Help Me    
    '''),
])
