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
        State('homepage-submitted-genomic-intervals', 'data'),
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
        Output('igv-tracks', 'options'),
        Output('igv-tracks', 'value'),
        Input('epigenome-tissue', 'value'),
        State('epigenome-submitted-tissue', 'data'),
    )
    def set_track_options(selected_tissue, submitted_selected_tissue):
        return [{'label': i, 'value': i} for i in RICE_ENCODE_SAMPLES[selected_tissue]], []

    @app.callback(
        Output('igv-is-submitted', 'data', allow_duplicate=True),
        Output('igv-submitted-genomic-intervals',
               'data', allow_duplicate=True),
        Output('epigenome-submitted-tissue', 'data', allow_duplicate=True),
        Output('igv-submitted-tracks', 'data', allow_duplicate=True),
        Input('igv-submit', 'n_clicks'),
        State('igv-genomic-intervals', 'value'),
        State('epigenome-tissue', 'value'),
        State('igv-tracks', 'value'),
        State('homepage-is-submitted', 'data'),
        prevent_initial_call=True
    )
    def submit_igv_input(igv_submit_n_clicks, selected_nb_interval, selected_tissue, selected_tracks, homepage_is_submitted):
        if homepage_is_submitted and igv_submit_n_clicks >= 1:
            return True, selected_nb_interval, selected_tissue, selected_tracks

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

    """
    Helpful for debugging: tells you if there's a problem with Flask serving the file
    """
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

    """
    If the app sees the route ('/genomes..'), this callback will be called
    """
    @app.server.route('/genomes_nipponbare/<path:filename>')
    def send_genomes_nipponbare_url(filename):
        try:
            # serves / retrieves the file using Flask
            return send_from_directory(Constants.GENOMES_NIPPONBARE, filename)
        except FileNotFoundError:
            abort(404)

    """
    If the app sees the route ('/annotations..'), this callback will be called
    """
    @app.server.route('/annotations_nb/<nb_intervals_str>/<path:foldername>/<selected_interval_str>/<file_format>')
    def send_annotations_nb_url(nb_intervals_str, foldername, selected_interval_str, file_format):
        try:
            # gets the path to the temp igv folder
            temp_output_folder_dir = get_path_to_temp(
                nb_intervals_str, Constants.TEMP_IGV, foldername)

            # sanitizes the filename for the nb_interval
            selected_interval_str_filename = convert_text_to_path(
                selected_interval_str)

            # appends the file extension (file_format)
            selected_interval_str_file = f'{selected_interval_str_filename}.{file_format}'

            return send_from_directory(temp_output_folder_dir, selected_interval_str_file)

        except FileNotFoundError:
            abort(404)

    @app.server.route('/<tissue>/<path:filename>')
    def send_track_url(tissue, filename):
        try:
            return send_from_directory(f'{Constants.EPIGENOME}/{tissue}', filename)

        except FileNotFoundError:
            abort(404)

    @app.callback(
        Output('igv-genomic-intervals', 'options'),
        #Output('igv-genomic-intervals', 'value'),
        Input('homepage-submitted-genomic-intervals', 'data'),

        State('homepage-is-submitted', 'data'),
        #State('igv-saved-genomic-intervals', 'data'),
        Input('igv-submit', 'n_clicks')
    )
    def display_selected_genomic_intervals(nb_intervals_str, homepage_is_submitted, *_): #selected_nb_interval, *_):
        if homepage_is_submitted:
            # sanitizes the genomic intervals from the homepage and splits the genomic intervals by ';'
            igv_options = util.sanitize_nb_intervals_str(nb_intervals_str)
            igv_options = igv_options.split(';')

            # if no genomic intervals are selected, use the first option
            #if not selected_nb_interval:
            #    selected_nb_interval = igv_options[0]

            return igv_options#, selected_nb_interval

        raise PreventUpdate

    @app.callback(
        Output('igv-display', 'children'),
        State('igv-submitted-genomic-intervals', 'data'),
        State('epigenome-submitted-tissue', 'data'),
        State('igv-submitted-tracks', 'data'),
        State('homepage-is-submitted', 'data'),
        Input('igv-is-submitted', 'data'),
        State('homepage-submitted-genomic-intervals', 'data')
    )
    def display_igv(selected_nb_intervals_str, selected_tissue, selected_tracks, homepage_is_submitted, igv_is_submitted, nb_intervals_str):
        if homepage_is_submitted and igv_is_submitted:
            # list of tracks info
            gene_annotation_track = {
                "name": "MSU V7 genes",
                "format": "gff3",
                "description": " <a target = \"_blank\" href = \"http://rice.uga.edu/\">Rice Genome Annotation Project</a>",
                # this will call out the send_annotations_nb_url callback function
                "url": f"annotations_nb/{nb_intervals_str}/IRGSPMSU.gff.db/{selected_nb_intervals_str}/gff",
                "displayMode": "EXPANDED",
            }

            # only display the tracks that were chosen by user. gene annotation track is always shown
            display_tracks = [gene_annotation_track] + \
                generate_tracks(selected_tissue, selected_tracks)

            # sanitize the selected nb interval so that if user inputs a "chr1", the nb interval will become "Chr01" so that it will be valid
            # the igv will be only displayed if the input follows the format of "Chr01"
            selected_nb_intervals_str = lift_over_util.to_genomic_interval(
                selected_nb_intervals_str)
            selected_nb_intervals_str = str(selected_nb_intervals_str.chrom) + ':' + str(
                selected_nb_intervals_str.start) + '-' + str(selected_nb_intervals_str.stop)

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
    """
    # saves the input objects to the respective dcc Stores
    @app.callback(
        Output('igv-saved-genomic-intervals', 'data', allow_duplicate=True),
        Output('epigenome-saved-tissue', 'data', allow_duplicate=True),
        Output('igv-saved-tracks', 'data', allow_duplicate=True),


        Input('igv-genomic-intervals', 'value'),
        Input('epigenome-tissue', 'value'),
        Input('igv-tracks', 'value'),

        State('homepage-is-submitted', 'data'),

        prevent_initial_call=True
    )
    def set_input_igv_session_state(selected_nb_intervals_str, selected_tissue, igv_tracks, homepage_is_submitted):
        if homepage_is_submitted:
            return selected_nb_intervals_str, selected_tissue, igv_tracks

        raise PreventUpdate

    # displays the saved inputs to the respective input objects
    @app.callback(
        Output('epigenome-tissue', 'value'),
        Output('igv-tracks', 'value'),
        State('epigenome-saved-tissue', 'data'),
        State('igv-saved-tracks', 'data'),
        State('homepage-is-submitted', 'data'),
        Input('igv-submit', 'n_clicks'),

        prevent_initial_call=True
    )
    def get_input_igv_session_state(epigenome_tissue, igv_tracks, homepage_is_submitted, *_):
        if homepage_is_submitted:
            return epigenome_tissue, igv_tracks

        raise PreventUpdate
    """
