import dash_bootstrap_components as dbc
from dash import ALL, Patch

"""
navbar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink(
                    'Gene List and Lift-Over', id='lift-over-link', className='ps-4')),
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
"""



def navbar():
    nav_item_names = [
        'Gene List and Lift-Over', 
        'Co-Expression Network Analysis', 
        'Regulatory Feature Enrichment', 
        'Browse Loci'
    ]

    nav_list = []
    for i in range(len(nav_item_names)):
        item = dbc.NavItem(dbc.NavLink(
            nav_item_names[i], 
            className='ps-4',
            id={
                'type': 'analysis-nav',
                'index': i #f'{sanitize_link(nav_item_names[i])}-link'
            },
            n_clicks = 0
        ))
        nav_list.append(item)

    return dbc.Nav(
        [
            item for item in nav_list
        ],
        vertical=True,
        pills=True,
        className='bg-light',
        id='homepage-dash-nav'
    )

def sanitize_link(link):
    return link.replace(' ', '-')
