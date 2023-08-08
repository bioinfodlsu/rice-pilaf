import dash_bootstrap_components as dbc


navbar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink(
                    'Gene List and Lift-Over', id='lift-over-link', className='ps-4')),
        dbc.NavItem(dbc.NavLink(
            'Text Mining', id='text-mining-link', className='ps-4')),
        dbc.NavItem(dbc.NavLink(
            'Co-Expression Network Analysis', id='coexpression-link', className='ps-4')),
        dbc.NavItem(dbc.NavLink(
            'Regulatory Feature Enrichment', id='tf-enrichment-link', className='ps-4')),
        dbc.NavItem(dbc.NavLink(
            'Browse Loci', id='igv-link', className='ps-4'))
    ],
    vertical=True,
    pills=True,
    className='bg-light',
    id='homepage-dash-nav'
)
