import json
import dash_bio as dashbio
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
from flask import json, send_from_directory, abort
from werkzeug.exceptions import HTTPException
from .util import *
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

    @app.server.route('/genomes_nipponbare/<path:filename>')
    def send_genomes_nipponbare_url(filename):
        try:
            return send_from_directory(const.GENOMES_NIPPONBARE, filename)
        except FileNotFoundError:
            abort(404)

    @app.server.route('/annotations_nb/<path:filename>/<loci>/<file_format>')
    def send_annotations_nb_url(filename, loci, file_format):
        try:
            temp_dir = f'{const.TEMP_IGV}/{sanitize_folder_name(filename)}'
            temp_dir_filename = f'{sanitize_filename(loci)}.{file_format}'

            return send_from_directory(temp_dir, temp_dir_filename)

        except FileNotFoundError:
            abort(404)

    @app.server.route('/open_chromatin_panicle/<path:filename>')
    def send_open_chromatin_panicle_url(filename):
        try:
            return send_from_directory(const.OPEN_CHROMATIN_PANICLE, filename)

        except FileNotFoundError:
            abort(404)

    @app.callback(
        Output('igv-genomic-intervals', 'options'),
        Output('igv-genomic-intervals', 'value'),
        Input('lift-over-genomic-intervals-saved-input', 'data'),
        State('lift-over-is-submitted', 'data'),
        State('lift-over-is-resetted', 'data')
    )
    def display_igv_genomic_intervals(nb_intervals_str, is_submitted, is_resetted):
        if is_resetted:
            return [], None

        if is_submitted:
            igv_options = nb_intervals_str.split(';')
            return igv_options, igv_options[0]

        raise PreventUpdate

    @app.callback(
        Output('igv-track-filter', 'options'),
        Input('igv-genomic-intervals', 'value'),
        State('lift-over-is-submitted', 'data'),
        State('lift-over-is-resetted', 'data')
    )
    def display_igv_tracks(selected_nb_intervals_str, is_submitted, is_resetteed):
        if is_resetteed:
            return []

        if is_submitted:
            return ['MSU V7 genes', 'chromatin open']
        raise PreventUpdate

    @app.callback(
        Output('igv-container', 'children'),
        Input('igv-genomic-intervals', 'value'),
        Input('igv-track-filter', 'value'),
        State('lift-over-is-submitted', 'data'),
        State('lift-over-is-resetted', 'data')
    )
    def display_igv(selected_nb_intervals_str, selected_tracks, is_submitted, is_resetted):
        if is_resetted:
            return None

        if is_submitted:
            track_info = [
                {
                    "name": "MSU V7 genes",
                    "format": "gff3",
                    "description": " <a target = \"_blank\" href = \"http://rice.uga.edu/\">Rice Genome Annotation Project</a>",
                    "url": f"annotations_nb/IRGSPMSU.gff.db/{selected_nb_intervals_str}/gff",
                    "displayMode": "EXPANDED",
                    "height": 200
                },
                {
                    "name": "chromatin open",
                    "format": "bed",
                    "description": " <a target = \"_blank\" href = \"http://rice.uga.edu/\">Rice Genome Annotation Project</a>",
                    "url": f"open_chromatin_panicle/SRR7126116_ATAC-Seq_Panicles.bed",
                    "displayMode": "EXPANDED",
                    "height": 200
                }
            ]

            display_tracks = []
            for track in track_info:
                if selected_tracks and track['name'] in selected_tracks:
                    display_tracks.append(track)

            return html.Div([
                dashbio.Igv(
                    id='igv-Nipponbare-local',
                    reference={
                        "id": "GCF_001433935.1",
                        "name": "O. sativa IRGSP-1.0 (GCF_001433935.1)",
                        "fastaURL": "genomes_nipponbare/Npb.fasta",
                        "indexURL": "genomes_nipponbare/Npb.fasta.fai",
                        "tracks": display_tracks
                    },
                    locus=[selected_nb_intervals_str]
                )
            ])
