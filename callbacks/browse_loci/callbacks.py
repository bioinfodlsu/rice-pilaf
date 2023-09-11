import json
import dash_bio as dashbio

from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
from flask import json, send_from_directory, abort
from werkzeug.exceptions import HTTPException

from .util import *
from ..lift_over import util as lift_over_util
from ..file_util import *

from ..constants import Constants


def init_callback(app):
    @app.callback(
        Output('igv-genomic-intervals-input', 'children'),
        State('homepage-genomic-intervals-submitted-input', 'data'),
        Input('homepage-is-submitted', 'data'),
        Input('igv-submit', 'n_clicks')
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        if homepage_is_submitted:
            if nb_intervals_str and not lift_over_util.is_error(lift_over_util.get_genomic_intervals_from_input(nb_intervals_str)):
                return [html.B('Your Input Intervals: '), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    @app.callback(
        Output('igv-is-submitted', 'data', allow_duplicate=True),
        Output('igv-selected-genomic-intervals-submitted-input', 'data'),
        Input('igv-submit', 'n_clicks'),
        State('igv-genomic-intervals', 'value'),
        State('igv-track-filter', 'value'),
        State('homepage-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def submit_igv_input(igv_submit_n_clicks, selected_nb_interval, selected_tracks, homepage_is_submitted):
        if homepage_is_submitted and igv_submit_n_clicks >= 1:
            return True, selected_nb_interval

        raise PreventUpdate

    @app.callback(
        Output('igv-results-container', 'style'),
        Input('igv-is-submitted', 'data')
    )
    def display_igv_output(igv_is_submitted):
        if igv_is_submitted:
            return {'display': 'block'}
        else:
            return {'display': 'none'}

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
            return send_from_directory(Constants.GENOMES_NIPPONBARE, filename)
        except FileNotFoundError:
            abort(404)

    @app.server.route('/annotations_nb/<nb_intervals_str>/<path:foldername>/<selected_interval_str>/<file_format>')
    def send_annotations_nb_url(nb_intervals_str, foldername, selected_interval_str, file_format):
        try:
            temp_output_folder_dir = get_path_to_temp(
                nb_intervals_str, Constants.TEMP_IGV, foldername)

            selected_interval_str_filename = convert_text_to_path(
                selected_interval_str)

            selected_interval_str_file = f'{selected_interval_str_filename}.{file_format}'

            return send_from_directory(temp_output_folder_dir, selected_interval_str_file)

        except FileNotFoundError:
            abort(404)

    @app.server.route('/open_chromatin_panicle/<path:filename>')
    def send_open_chromatin_panicle_url(filename):
        try:
            return send_from_directory(Constants.OPEN_CHROMATIN_PANICLE, filename)

        except FileNotFoundError:
            abort(404)

    @app.callback(
        Output('igv-genomic-intervals', 'options'),
        Output('igv-genomic-intervals', 'value'),
        Input('homepage-genomic-intervals-submitted-input', 'data'),

        State('homepage-is-submitted', 'data'),
        State('igv-selected-genomic-intervals-saved-input', 'data')
    )
    def display_selected_genomic_intervals(nb_intervals_str, homepage_is_submitted, selected_nb_interval):
        if homepage_is_submitted:
            igv_options = util.sanitize_nb_intervals_str(nb_intervals_str) 
            igv_options = igv_options.split(';')

            if not selected_nb_interval:
                selected_nb_interval = igv_options[0]

            return igv_options, selected_nb_interval

        raise PreventUpdate

    @app.callback(
        Output('igv-track-intro', 'children'),
        Output('igv-track-filter', 'options'),
        Output('igv-track-filter', 'value'),
        Input('igv-selected-genomic-intervals-submitted-input', 'data'),
        State('homepage-is-submitted', 'data'),
        Input('igv-selected-tracks-submitted-input', 'data'),
        State('igv-is-submitted', 'data')
    )
    def display_igv_tracks_filter(nb_intervals_str, homepage_is_submitted, selected_tracks, igv_is_submitted):
        if homepage_is_submitted and igv_is_submitted:
            tracks = ['MSU V7 genes', 'chromatin open']

            if not selected_tracks:
                selected_tracks = [tracks[0]]

            return 'Select the tracks to be displayed', \
                tracks, selected_tracks
        raise PreventUpdate

    @app.callback(
        Output('igv-display', 'children'),
        State('igv-selected-genomic-intervals-submitted-input', 'data'),
        Input('igv-selected-tracks-submitted-input', 'data'),
        State('homepage-is-submitted', 'data'),
        State('igv-is-submitted', 'data'),
        State('homepage-genomic-intervals-submitted-input', 'data')
    )
    def display_igv(selected_nb_intervals_str, selected_tracks, homepage_is_submitted, igv_is_submitted, nb_intervals_str):
        if homepage_is_submitted and igv_is_submitted:
            track_info = [
                {
                    "name": "MSU V7 genes",
                    "format": "gff3",
                    "description": " <a target = \"_blank\" href = \"http://rice.uga.edu/\">Rice Genome Annotation Project</a>",
                    "url": f"annotations_nb/{nb_intervals_str}/IRGSPMSU.gff.db/{selected_nb_intervals_str}/gff",
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

            display_tracks = [
                track for track in track_info if selected_tracks and track['name'] in selected_tracks]

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

        raise PreventUpdate

    @app.callback(
        Output('igv-selected-genomic-intervals-saved-input',
               'data', allow_duplicate=True),
        Input('igv-genomic-intervals', 'value'),
        State('homepage-is-submitted', 'data'),
        Input('igv-track-filter', 'value'),

        prevent_initial_call=True
    )
    def set_input_igv_session_state(selected_nb_intervals_str, homepage_is_submitted, *_):
        if homepage_is_submitted:
            return selected_nb_intervals_str

        raise PreventUpdate

    @app.callback(
        Output('igv-selected-tracks-submitted-input',
               'data', allow_duplicate=True),
        Input('igv-track-filter', 'value'),
        State('homepage-is-submitted', 'data'),
        State('igv-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def set_submitted_igv_session_state(selected_tracks, homepage_is_submitted, igv_is_submitted):
        if homepage_is_submitted and igv_is_submitted:
            return selected_tracks

        raise PreventUpdate
