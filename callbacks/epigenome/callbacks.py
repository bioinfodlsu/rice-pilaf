import json
from collections import namedtuple

import dash_bio as dashbio
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
from flask import abort, json, send_from_directory
from werkzeug.exceptions import HTTPException

from ..constants import Constants
from ..file_util import convert_text_to_path, get_path_to_temp
from ..lift_over.util import (
    get_genomic_intervals_from_input,
    is_error,
    sanitize_nb_intervals_str,
    to_genomic_interval_str,
)
from .util import (
    RICE_ENCODE_SAMPLES,
    convert_text_to_path,
    generate_tracks,
    write_igv_tracks_to_file,
)

Tissue_tracks = namedtuple("Tissue_tracks", ["tracks"])


def init_callback(app):
    @app.callback(
        Output("epigenome-genomic-intervals-input", "children"),
        State("homepage-submitted-genomic-intervals", "data"),
        Input("homepage-is-submitted", "data"),
        Input("epigenome-submit", "n_clicks"),
    )
    def display_input(nb_intervals_str, homepage_is_submitted, *_):
        """
        Displays the genomic interval input in the epigenome page

        Parameters:
        - nb_intervals_str: Saved genomic interval value found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - *_: Other input that facilitates displaying of the submitted genomic interval

        Returns:
        - ('lift-over-genomic-intervals-input', 'children'): Genomic interval text
        """

        if homepage_is_submitted:
            if nb_intervals_str and not is_error(
                get_genomic_intervals_from_input(nb_intervals_str)
            ):
                return [html.B("Your Input Intervals: "), html.Span(nb_intervals_str)]
            else:
                return None

        raise PreventUpdate

    # =================
    # Input-related
    # =================

    @app.callback(
        Output("epigenome-is-submitted", "data", allow_duplicate=True),
        Output("epigenome-submitted-genomic-intervals", "data", allow_duplicate=True),
        Output("epigenome-submitted-tissue", "data", allow_duplicate=True),
        Output("epigenome-submitted-tracks", "data", allow_duplicate=True),
        Input("epigenome-submit", "n_clicks"),
        State("epigenome-genomic-intervals", "value"),
        State("epigenome-tissue", "value"),
        State("epigenome-tracks", "value"),
        State("homepage-is-submitted", "data"),
        State("homepage-submitted-genomic-intervals", "data"),
        prevent_initial_call=True,
    )
    def submit_epigenome_input(
        epigenome_submit_n_clicks,
        selected_nb_interval,
        selected_tissue,
        selected_tracks,
        homepage_is_submitted,
        nb_intervals_str,
    ):
        """
        Parses epigenome input and displays the epigenome result container
        - If user clicks on the epigenome submit button, the inputs will be parsed and the epigenome results container will appear

        Parameters:
        - epigenome_submit_n_clicks: Number of clicks pressed on the epigenome submit button
        - selected_nb_interval: Selected epigenome genomic interval
        - selected_tissue: Selected tissue value
        - selected_tracks: Selected list of tracks
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input

        Returns:
        - ('epigenome-is-submitted', 'data'): [Epigenome] True for submitted valid input; otherwise False
        - ('epigenome-submitted-genomic-intervals', 'data'): Submitted selected epigenome genomic interval
        - ('epigenome-submitted-tissue', 'data'): Submitted tissue
        - ('epigenome-submitted-tracks', 'data): Submitted list of tracks for the selected tissue
        """

        if homepage_is_submitted and epigenome_submit_n_clicks >= 1:
            tissue_tracks_value = Tissue_tracks(selected_tracks)._asdict()
            submitted_tissue_tracks = {selected_tissue: tissue_tracks_value}

            write_igv_tracks_to_file(nb_intervals_str)

            return True, selected_nb_interval, selected_tissue, submitted_tissue_tracks

        raise PreventUpdate

    @app.callback(
        Output("epigenome-results-container", "style"),
        Input("epigenome-is-submitted", "data"),
    )
    def display_epigenome_output(epigenome_is_submitted):
        """
        Displays the epigenome results container

        Parameters:
        - epigenome_is_submitted: [Epigenome] Saved boolean value of submitted valid input

        Returns:
        - ('epigenome-results-container', 'style'): {'display': 'block'} for displaying the epigenome results container; otherwise {'display': 'none'}
        """

        if epigenome_is_submitted:
            return {"display": "block"}
        else:
            return {"display": "none"}

    @app.callback(
        Output("epigenome-genomic-intervals", "options"),
        Output("epigenome-genomic-intervals", "value"),
        Input("homepage-submitted-genomic-intervals", "data"),
        State("homepage-is-submitted", "data"),
        State("epigenome-submitted-genomic-intervals", "data"),
        Input("epigenome-is-submitted", "data"),
    )
    def display_selected_genomic_intervals(
        nb_intervals_str, homepage_is_submitted, selected_nb_interval, *_
    ):
        """
        Sets the genomic interval dropdown choices and value

        Parameters:
        - nb_intervals_str: Saved genomic interval found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - selected_nb_interval: Saved selected epigenome genomic interval found in the dcc.Store
        - *_: Other inputs that facilitates the saved state of the epigenome genomic interval input

        Returns:
        - ('epigenome-genomic-intervals', 'options'): List of available tracks for the selected tissue
        - ('epigenome-genomic-intervals', 'value'): List of selected tracks
        """

        if homepage_is_submitted:
            # sanitizes the genomic intervals from the homepage and splits the genomic intervals by ';'
            epigenome_options = sanitize_nb_intervals_str(nb_intervals_str)
            epigenome_options = epigenome_options.split(";")

            # if no genomic intervals are selected, use the first option
            if not selected_nb_interval:
                selected_nb_interval = epigenome_options[0]

            return epigenome_options, selected_nb_interval

        raise PreventUpdate

    @app.callback(
        Output("epigenome-tracks", "options"),
        Output("epigenome-tracks", "value"),
        Input("epigenome-tissue", "value"),
        State("epigenome-submitted-tracks", "data"),
    )
    def set_track_options(selected_tissue, submitted_selected_tracks):
        """
        Sets the list of tracks available depending on the selected tissue

        Parameters:
        - selected_tissue: Selected tissue option
        - submitted_selected_tracks: Saved tissue tracks found in the dcc.Store

        Returns:
        - ('epigenome-tracks', 'options'): List of available tracks for the selected tissue
        - ('epigenome-tracks', 'value'): List of selected tracks
        """

        selected_tracks = []
        # If there was a submitted tracks before for this specific tissue, display that list of selected tracks
        if submitted_selected_tracks and selected_tissue in submitted_selected_tracks:
            selected_tracks = submitted_selected_tracks[selected_tissue]["tracks"]

        return [
            {"label": i, "value": i} for i in RICE_ENCODE_SAMPLES[selected_tissue]
        ], selected_tracks

    # =================
    # Dash-bio-related
    # =================
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
        response.data = json.dumps(
            {
                "code": e.code,
                "name": e.name,
                "description": e.description,
            }
        )
        response.content_type = "application/json"
        return response

    """
    If the app sees the route ('/genomes..'), this callback will be called
    """

    @app.server.route("/genomes_nipponbare/<path:filename>")
    def send_genomes_nipponbare_url(filename):
        """
        Serves a file through Flask

        Parameters:
        - filename: Name of the file

        Returns:
        - File
        """

        try:
            # serves / retrieves the file using Flask
            return send_from_directory(Constants.GENOMES_NIPPONBARE, filename)
        except FileNotFoundError:
            abort(404)

    """
    If the app sees the route ('/annotations..'), this callback will be called
    """

    @app.server.route(
        "/annotations_nb/<nb_intervals_str>/<path:foldername>/<selected_interval_str>/<file_format>"
    )
    def send_annotations_nb_url(
        nb_intervals_str, foldername, selected_interval_str, file_format
    ):
        """
        Serves a file through Flask

        Parameters:
        - nb_intervals_str: Selected tissue
        - foldername: Name of the folder
        - selected_interval_str: Selected epigenome genomic interval
        - file_format: extension format of the file (e.g. gff)

        Returns:
        - File
        """

        try:
            # gets the path to the temp epigenome folder
            temp_output_folder_dir = get_path_to_temp(
                nb_intervals_str, Constants.TEMP_EPIGENOME, foldername
            )

            # sanitizes the filename for the nb_interval
            selected_interval_str_filename = convert_text_to_path(selected_interval_str)

            # appends the file extension (file_format)
            selected_interval_str_file = (
                f"{selected_interval_str_filename}.{file_format}"
            )

            return send_from_directory(
                temp_output_folder_dir, selected_interval_str_file
            )

        except FileNotFoundError:
            abort(404)

    @app.server.route("/<tissue>/<path:filename>")
    def send_track_url(tissue, filename):
        """
        Serves a file through Flask

        Parameters:
        - tissue: Selected tissue
        - filename: Name of the file

        Returns:
        - File
        """

        try:
            return send_from_directory(f"{Constants.EPIGENOME}/{tissue}", filename)

        except FileNotFoundError:
            abort(404)

    @app.callback(
        Output("epigenome-display", "children"),
        State("epigenome-submitted-genomic-intervals", "data"),
        State("epigenome-submitted-tissue", "data"),
        State("epigenome-submitted-tracks", "data"),
        State("homepage-is-submitted", "data"),
        Input("epigenome-is-submitted", "data"),
        State("homepage-submitted-genomic-intervals", "data"),
    )
    def display_epigenome(
        selected_nb_intervals_str,
        selected_tissue,
        selected_tracks,
        homepage_is_submitted,
        epigenome_is_submitted,
        nb_intervals_str,
    ):
        """
        Displays the dash-bio visualization graph according to the selected inputs

        Parameters:
        - selected_nb_intervals_str: Saved selected epigenome genomic interval found in the dcc.Store
        - selected_tissue: Saved tissue value found in the dcc.Store
        - selected_tracks: Saved list of selected tracks found in the dcc.Store
        - homepage_is_submitted: [Homepage] Saved boolean value of submitted valid input
        - epigenome_is_submitted: [Epigenome] Saved boolean value of submitted valid input
        - nb_intervals_str: Saved genomic interval found in the dcc.Store

        Returns:
        - ('epigenome-display', 'children'): Dash-bio visualization graph according to the selected inputs
        """

        if homepage_is_submitted and epigenome_is_submitted:
            # list of tracks info
            gene_annotation_track = {
                "name": "MSU V7 genes",
                "format": "gff3",
                "description": ' <a target = "_blank" href = "http://rice.uga.edu/">Rice Genome Annotation Project</a>',
                # this will call out the send_annotations_nb_url callback function
                "url": f"annotations_nb/{nb_intervals_str}/IRGSPMSU.gff.db/{selected_nb_intervals_str}/gff",
                "displayMode": "EXPANDED",
                "order": 1,
            }

            tracks = []
            if selected_tracks and selected_tissue in selected_tracks:
                tracks = selected_tracks[selected_tissue]["tracks"]

            # only display the tracks that were chosen by user. gene annotation track is always shown
            display_tracks = [gene_annotation_track] + generate_tracks(
                selected_tissue, tracks
            )

            # sanitize the selected nb interval so that if user inputs a "chr1", the nb interval will become "Chr01" so that it will be valid
            # the epigenome will be only displayed if the input follows the format of "Chr01"
            selected_nb_intervals_str = to_genomic_interval_str(
                selected_nb_intervals_str
            )

            return html.Div(
                [
                    dashbio.Igv(
                        id="epigenome-Nipponbare-local",
                        reference={
                            "id": "GCF_001433935.1",
                            "name": "O. sativa IRGSP-1.0 (GCF_001433935.1)",
                            "fastaURL": "genomes_nipponbare/Npb.fasta",
                            "indexURL": "genomes_nipponbare/Npb.fasta.fai",
                            "tracks": display_tracks,
                        },
                        locus=[selected_nb_intervals_str],
                    )
                ]
            )

        raise PreventUpdate

    # =================
    # Session-related
    # =================
    @app.callback(
        Output("epigenome-tissue", "value"),
        State("epigenome-submitted-tissue", "data"),
        Input("epigenome-is-submitted", "data"),
    )
    def get_input_epigenome_session_state(selected_tissue, *_):
        """
        Gets the epigenome related dcc.Store variables data in the epigenome input container and displays them

        Parameters:
        - selected_tissue: Saved tissue value found in the dcc.Store
        - *_: Other inputs in facilitating the saved state of the epigenome input

        Returns:
        - ('epigenome-tissue', 'value'): Saved tissue value found in the dcc.Store; otherwise 'Leaf' for default value
        """

        if not selected_tissue:
            selected_tissue = "Leaf"

        return selected_tissue
