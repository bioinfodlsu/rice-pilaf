import dash_bootstrap_components as dbc


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink('Home', href='/', active='exact',
                    className='top-navbar-item')),
        dbc.NavItem(dbc.NavLink(
                    'Help', href='/help', active='exact', className='top-navbar-item'))
    ],
    id='top-navbar',
    brand=['RicePilaf'],
    brand_href='/',
    color='#4d987d',
    dark=True
)
