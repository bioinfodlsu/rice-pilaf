import os
import pandas as pd
from .constants import Constants
const = Constants()


def dir_exist(directory):
    return os.path.exists(directory)


def create_dir(directory):
    if not dir_exist(directory):
        os.makedirs(directory)


def write_df_to_csv(df, directory):
    create_dir(directory)

    df.to_csv(f'{directory}')


def load_csv_from_dir(directory):
    return pd.read_csv(directory)


def sanitize_text_to_foldername_format(text):
    return text.replace(
        ":", "_").replace(";", "__").replace("-", "_").replace('.', '_')


def sanitize_text_to_filename_format(text):
    return text.replace(
        ":", "_").replace(";", "__").replace("-", "_").replace('.', '_')


def get_temp_output_folder_dir(genomic_interval, analysis_type, output):
    genomic_interval_filename = sanitize_text_to_foldername_format(
        genomic_interval)

    output = sanitize_text_to_foldername_format(output)

    return f'{const.TEMP}/{genomic_interval_filename}/{analysis_type}/{output}'
