import dash_bootstrap_components as dbc

navbar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink(
                    'Topic 1', className='ps-4')),
        dbc.NavItem(dbc.NavLink(
            'Topic 2', className='ps-4')),
        dbc.NavItem(dbc.NavLink(
            'Topic 3',  className='ps-4')),
        dbc.NavItem(dbc.NavLink(
            'Topic 4', className='ps-4'))
    ],
    vertical=True,
    pills=True,
    className='bg-light',
    id='user-guide-nav'
)