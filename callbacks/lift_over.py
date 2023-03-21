from dash import dcc, html, Input, Output, State

def init_callback(app):
    @app.callback(
        Output('container-button-basic', 'children'),
        Input('submit-val', 'n_clicks'),
        State('input-on-submit', 'value')
    )
    def update_output(n_clicks, value):
        return 'The input value was "{}" and the button has been clicked {} times'.format(
            value,
            n_clicks
        )
    