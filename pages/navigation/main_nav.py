import dash_bootstrap_components as dbc
from dash import html


def navbar():
    return dbc.NavbarSimple(
        children=[
            # Insert your navigation item in the main navbar here in the order you want it to be seen
            # dbc.NavItem(dbc.NavLink('Home', active='exact',
            #             href='/', className='top-navbar-item')),
            dbc.NavItem(
                dbc.NavLink(
                    "User Guide",
                    href="https://github.com/bioinfodlsu/rice-pilaf/wiki/2.-User-Guide",
                    target="_blank",
                    className="top-navbar-item",
                )
            ),
        ],
        id="top-navbar",
        brand=[
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            src="assets/rice_pilaf_logo.png",
                            height="30px",
                            className="mx-auto",
                        ),
                        className="d-flex align-items-center",
                    ),
                    dbc.Col(dbc.NavbarBrand("RicePilaf", className="ms-3")),
                ],
                align="center",
                className="g-0",
            )
        ],
        brand_href="/",
        color="#4d987d",
        dark=True,
        fluid=True,
        className="px-5",
    )

    """
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
    """
