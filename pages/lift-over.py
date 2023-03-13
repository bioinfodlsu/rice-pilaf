import dash
from dash import dcc, html

dash.register_page(__name__, path ="/", name="Input and Lift-over")

layout = html.Div(
    [
        dcc.Markdown("Lift-over action happens here")
    ]
)
