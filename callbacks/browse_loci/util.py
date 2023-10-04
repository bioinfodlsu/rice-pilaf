from ..lift_over import util
import gffutils
from ..file_util import *
from ..constants import Constants

RICE_ENCODE_SAMPLES = {
    'Leaf':['ATAC-Seq', 'FAIRE-Seq'],
    'Panicle':['FAIRE-Seq']
}

igv_tracks = {'MSU V7 genes': 'MSU V7 genes',
             'chromatin open': 'chromatin open'}

def construct_options_igv_tracks():
    return [
        {'value': symbol, 'label': name } for symbol, name in igv_tracks.items()]


def write_igv_tracks_to_file(nb_intervals_str):
    # tracks found in igv
    track_db = [[Constants.ANNOTATIONS_NB, 'IRGSPMSU.gff.db', 'gff'],
                [Constants.OPEN_CHROMATIN_PANICLE, 'SRR7126116_ATAC-Seq_Panicles.bed', 'bed']]

    # write to file the data for igv
    for db in track_db:
        file_ext = db[2]

        if file_ext == 'gff':
            source_dir = f'{db[0]}/{db[1]}'
            source_file = db[1]

            write_gff_igv_track_to_file(
                source_dir, source_file, nb_intervals_str)


def write_gff_igv_track_to_file(source_dir, source_file, nb_intervals_str):
    if path_exists(source_dir):
        loci_list = util.sanitize_nb_intervals_str(nb_intervals_str) 
        loci_list = loci_list.split(';')
        
        genomic_interval_list = util.get_genomic_intervals_from_input(
            nb_intervals_str)

        temp_folder = get_path_to_temp(
            nb_intervals_str, Constants.TEMP_IGV, source_file)
        make_dir(temp_folder)

        for i in range(len(loci_list)):
            cur_loci = loci_list[i]

            dest_file = f'{convert_text_to_path(cur_loci)}.gff'
            dest_dir = f'{temp_folder}/{dest_file}'

            if not path_exists(dest_dir):
                genes_in_interval = get_loci_data_in_gff_file(
                    source_dir, genomic_interval_list[i])

                with open(dest_dir, 'w') as fp:
                    for line in genes_in_interval:
                        fp.write('%s\n' % line)


def get_loci_data_in_gff_file(source_dir, nb_interval):
    db = gffutils.FeatureDB(f'{source_dir}', keep_order=True)

    genes_in_interval = list(db.region(region=(nb_interval.chrom, nb_interval.start, nb_interval.stop),
                                       completely_within=False, featuretype='gene'))

    return genes_in_interval
