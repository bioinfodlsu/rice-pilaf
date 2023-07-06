from ..lift_over import util
import gffutils
import pandas as pd
import os
from ..file_util import *
from ..constants import Constants

const = Constants()


def write_igv_tracks_to_file(input_dir, input_dir_filename, nb_intervals_str, file_format):
    if os.path.exists(input_dir):
        nb_intervals_options = nb_intervals_str.split(';')
        nb_intervals = util.get_genomic_intervals_from_input(
            nb_intervals_str)

        temp_output_folder_dir = get_temp_output_folder_dir(
            nb_intervals_str, const.TEMP_IGV, f'{input_dir_filename}')
        create_dir(temp_output_folder_dir)

        i = 0
        for Nb_interval in nb_intervals:
            if i < len(nb_intervals_options):
                cur_nb_interval_options = nb_intervals_options[i]

                cur_nb_interval_options_filename = sanitize_text_to_filename_format(
                    cur_nb_interval_options)
                temp_output_dir = f'{temp_output_folder_dir}/{cur_nb_interval_options_filename}.{file_format}'

                if not dir_exist(temp_output_dir):
                    db = gffutils.FeatureDB(
                        f'{input_dir}', keep_order=True)

                    genes_in_interval = list(db.region(region=(Nb_interval.chrom, Nb_interval.start, Nb_interval.stop),
                                                       completely_within=False, featuretype='gene'))

                    with open(temp_output_dir, 'w') as fp:
                        for line in genes_in_interval:
                            fp.write('%s\n' % line)

            i += 1
