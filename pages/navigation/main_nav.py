import dash
from dash import html
import dash_bootstrap_components as dbc

def navbar():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(
                dbc.NavLink([
                    page["name"]
                ],
                href=page["path"],
                active="exact",
                className='top-navbar-item'
            ))
            for page in dash.page_registry.values()
            if page["location"] == 'app-topbar'
        ],
        id='top-navbar',
        brand=['RicePilaf'],
        brand_href='/',
        color='#4d987d',
        dark=True
    )
