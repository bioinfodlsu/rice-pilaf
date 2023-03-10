import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

welcome = dcc.Markdown(
    """
    Welcome ! Rice Pilaf is short for Rice Post-GWAS Dashboard.
    Ok, we are not good at abbreviations, but like a good pilaf, this dashboard combines many ingredients.
    With this tool, you can do amazing things like ... (write me)
    """
)

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
sidebar = dbc.Nav(
    [
        dbc.NavLink(
           [
               html.Div(page["name"], className="ms-2"),
           ],
           href = page["path"],
           active="exact",
        )
        for page in dash.page_registry.values()
    ],
    vertical = True,
    pills = True,
    className = "bg-light"
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.Div("Rice-Pilaf",
                                  style={'fontSize':50, 'textAlign':'center'})),
                welcome
            ]
        ),

        html.Hr(),

        dbc.Row(
            [
                dbc.Col([sidebar], xs =4, sm=4,md=2,lg=2,xl=2,xxl=2),
                dbc.Col([dash.page_container], xs =8, sm=8,md=10,lg=10,xl=10,xxl=10)
            ]
        )
    ],
    fluid = True

)

if __name__ == '__main__':
    app.run_server(debug=True)
