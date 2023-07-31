import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

import pages.navigation.user_guide_nav as user_guide_nav

dash.register_page(__name__, path='/topic1subgroup', name='Topic 1 Subgroup', location='help-sidebar')

layout = html.Div(id='topic1-container', children=[
    html.Div(
        children=[
            dbc.Row([
                dbc.Col([
                    html.H5('User Guide'),
                    user_guide_nav.navbar
                    ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
                
                dbc.Col(children=[
                    html.H5("Topic 1 Subgroup"),
                    html.P("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Nibh mauris cursus mattis molestie a iaculis at erat. Tortor vitae purus faucibus ornare suspendisse sed nisi lacus sed. Tellus pellentesque eu tincidunt tortor aliquam nulla. Euismod lacinia at quis risus sed vulputate odio ut. Nec sagittis aliquam malesuada bibendum arcu vitae. Bibendum arcu vitae elementum curabitur vitae nunc sed. Consequat interdum varius sit amet mattis vulputate enim nulla. Nibh venenatis cras sed felis. Gravida cum sociis natoque penatibus et magnis."),
                    html.Img(src='assets/images/genomic_interval_input_img.jpg', className='img-fluid')
                ],
                xs=7, sm=7, md=9, lg=9, xl=9, xxl=9)
        ], className='px-5 pt-4 pb-5')
        ]
    )
    
])

