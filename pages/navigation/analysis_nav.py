import dash_bootstrap_components as dbc
import pages.analysis_layout as analysis_layout


def navbar():
    analysis_layout_dict = analysis_layout.get_analaysis_layout_dictionary()

    nav_list = [dbc.NavItem(
        dbc.NavLink(
            analysis_layout_dict[key],
            className='ps-4',
            id={
                'type': 'analysis-nav',
                'label': key
            },
            n_clicks=0
        )
    ) for key in analysis_layout_dict.keys()]

    return dbc.Nav(
        [
            item for item in nav_list
        ],
        vertical=True,
        pills=True,
        className='bg-light',
        id='homepage-dash-nav'
    )
