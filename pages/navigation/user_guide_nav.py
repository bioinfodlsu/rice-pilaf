import dash_bootstrap_components as dbc
from dash import dcc, html

navbar = html.Div(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                title='Topic 1',
                children= [
                    dbc.NavItem(dbc.NavLink(
                    'Topic 1 Subgroup', href='topic1subgroup', className='ps-4')),
                ]
            ),
            dbc.AccordionItem(
                title='Topic 2',
                children= [
                    dbc.NavItem(dbc.NavLink(
                    'Topic 2 Subgroup', href='topic2subgroup', className='ps-4')),
                ]
            ),
            dbc.AccordionItem(
                title='Topic 3',
                children= [
                    dbc.NavItem(dbc.NavLink(
                    'Topic 3 Subgroup', href='topic3subgroup', className='ps-4')),
                ]
            )
        ],
        flush=True,
        always_open=True,
        active_item=[],
        persistence=True,
        persistence_type='session',
        id='user-guide-list'
    ),
)











"""
dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink(
                    'Topic 1', className='ps-4')),
        dbc.NavItem(dbc.NavLink(
                    'Topic 1 Subgroup', className='ps-5 bg-secondary')),
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
"""