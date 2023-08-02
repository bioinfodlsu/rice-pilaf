import dash_bootstrap_components as dbc
import pages.analysis_layout as analysis_layout

def navbar():
    analysis_layout_dict = analysis_layout.get_analaysis_layout_dictionary()

    nav_list = []
    for key in analysis_layout_dict.keys():
        item = dbc.NavItem(dbc.NavLink(
            analysis_layout_dict[key], 
            className='ps-4',
            id={
                'type': 'analysis-nav',
                'label': key
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

    """
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
                'index': i 
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
    """