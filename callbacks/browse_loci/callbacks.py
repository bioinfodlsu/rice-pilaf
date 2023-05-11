import dash_bio as dashbio
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
from flask import json, send_from_directory, abort
from werkzeug.exceptions import HTTPException

from ..constants import Constants
const = Constants()


def init_callback(app):
    # Lifted from https://flask.palletsprojects.com/en/2.2.x/errorhandling/#:~:text=When%20an%20error%20occurs%20in,user%20when%20an%20error%20occurs.
    @app.server.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    @app.server.route('/igv/<path:filename>')
    def send_igv_url(filename):
        try:
            return send_from_directory(const.IGV, filename)
        except FileNotFoundError:
            abort(404)

    @app.callback(
        Output('igv-genomic-intervals', 'options'),
        Output('igv-genomic-intervals', 'value'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        State('lift-over-is-submitted', 'data')
    )
    def display_igv_genomic_intervals(nb_intervals_str, is_submitted):
        if is_submitted:
            igv_options = nb_intervals_str.split(';')
            return igv_options, igv_options[0]

        raise PreventUpdate

    @app.callback(
        Output('igv-container', 'children'),
        Input('igv-genomic-intervals', 'value'),
        State('lift-over-is-submitted', 'data')
    )
    def display_igv(selected_nb_intervals_str, is_submitted):
        if is_submitted:
            return html.Div([
                dashbio.Igv(
                    id='igv-Nipponbare-local',
                    reference={
                        "id": "GCF_001433935.1",
                        "name": "O. sativa IRGSP-1.0 (GCF_001433935.1)",
                        "fastaURL": "igv/GCF_001433935.1_IRGSP-1.0_genomic.fna.gz",
                        "indexURL": "igv/GCF_001433935.1_IRGSP-1.0_genomic.fna.gz.fai",
                        "compressedIndexURL": "igv/GCF_001433935.1_IRGSP-1.0_genomic.fna.gz.gzi",
                        "aliasURL": "igv/GCF_001433935.1_chromAlias.tab",
                        "tracks": [
                            {
                                "name": "MSU V7 genes",
                                "format": "gff3",
                                "description": " <a target = \"_blank\" href = \"http://rice.uga.edu/\">Rice Genome Annotation Project</a>",
                                "url": "igv/MSU_V7.gff3",
                                "displayMode": "EXPANDED",
                                "height": 200
                            }
                        ]
                    },
                    locus=[selected_nb_intervals_str]
                )
            ])
