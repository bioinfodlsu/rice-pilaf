import gffutils

from ..constants import Constants
from ..file_util import *
from ..lift_over import util

RICE_ENCODE_SAMPLES = {
    "Leaf": ["ATAC-Seq", "FAIRE-Seq"],
    "Panicle": ["ATAC-Seq", "FAIRE-Seq"],
    "Root": ["ATAC-Seq", "FAIRE-Seq"],
    "Seedling": ["FAIRE-Seq", "MNase-Seq"],
}


def write_igv_tracks_to_file(nb_intervals_str):
    # tracks found in igv
    track_db = [[Constants.ANNOTATIONS_NB, "IRGSPMSU.gff.db", "gff"]]

    # write to file the data for igv
    for db in track_db:
        file_ext = db[2]

        if file_ext == "gff":
            source_dir = f"{db[0]}/{db[1]}"
            source_file = db[1]

            write_gff_igv_track_to_file(source_dir, source_file, nb_intervals_str)


def write_gff_igv_track_to_file(source_dir, source_file, nb_intervals_str):
    if path_exists(source_dir):
        loci_list = util.sanitize_nb_intervals_str(nb_intervals_str)
        loci_list = loci_list.split(";")

        genomic_interval_list = util.get_genomic_intervals_from_input(nb_intervals_str)

        temp_folder = get_path_to_temp(
            nb_intervals_str, Constants.TEMP_EPIGENOME, source_file
        )
        make_dir(temp_folder)

        for i in range(len(loci_list)):
            cur_loci = loci_list[i]

            dest_file = f"{convert_text_to_path(cur_loci)}.gff"
            dest_dir = f"{temp_folder}/{dest_file}"

            if not path_exists(dest_dir):
                genes_in_interval = get_loci_data_in_gff_file(
                    source_dir, genomic_interval_list[i]
                )

                with open(dest_dir, "w") as fp:
                    for line in genes_in_interval:
                        fp.write("%s\n" % line)


def get_loci_data_in_gff_file(source_dir, nb_interval):
    db = gffutils.FeatureDB(f"{source_dir}", keep_order=True)

    genes_in_interval = list(
        db.region(
            region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
            completely_within=False,
            featuretype="gene",
        )
    )

    return genes_in_interval


def generate_tracks(selected_tissue, selected_tracks):
    tracks = []
    for track in selected_tracks:
        tracks.append(
            {
                "name": f"{selected_tissue}-{track}",
                "description": f"{selected_tissue}-{track}",
                "format": "bed",  # hard-coded for now
                "url": f"{selected_tissue}/{track}",
                "displayMode": "EXPANDED",
            }
        )
    return tracks
