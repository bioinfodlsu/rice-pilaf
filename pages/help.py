import dash
import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html


dash.register_page(__name__, path='/help', name='Help')


layout = html.Div(id='lift-over-container', children=[
    dcc.Markdown('''
    Help Me    
    '''),

]
)
