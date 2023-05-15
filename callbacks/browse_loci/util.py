from ..lift_over import util
import gffutils
import pandas as pd
import os
from ..constants import Constants

const = Constants()


def sanitize_filename(filename):
    filename = filename.replace(':', '-')
    return filename


def sanitize_folder_name(folder_name):
    folder_name = folder_name.replace('.', '_')
    return folder_name


def get_data_base_on_loci(input_dir, input_dir_filename, nb_intervals_str):
    if os.path.exists(input_dir):
        filenames = []

        nb_intervals = util.get_genomic_intervals_from_input(
            nb_intervals_str)

        output_dir_folder = f'{const.TEMP}/{input_dir_filename}'
        if not os.path.exists(output_dir_folder):
            os.makedirs(output_dir_folder)

        for Nb_interval in nb_intervals:
            output_filename = f'{sanitize_filename(nb_intervals_str)}.gff'
            output_dir = f'{output_dir_folder}/{output_filename}'

            if not os.path.exists(output_dir):
                db = gffutils.FeatureDB(
                    f'{input_dir}', keep_order=True)

                genes_in_interval = list(db.region(region=(Nb_interval.chrom, Nb_interval.start, Nb_interval.stop),
                                                   completely_within=False, featuretype='gene'))

                with open(output_dir, 'w') as fp:
                    for line in genes_in_interval:
                        fp.write('%s\n' % line)

            filenames.append(output_filename)

        if filenames:
            return output_dir_folder, filenames[0]

    return None, None
