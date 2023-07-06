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


def get_temp_output_folder_dir(genomic_interval, analysis_type, *args):
    genomic_interval_foldername = sanitize_text_to_foldername_format(
        genomic_interval)

    analysis_type = sanitize_text_to_foldername_format(analysis_type)

    temp_dir = f'{const.TEMP}/{genomic_interval_foldername}/{analysis_type}'
    for arg in args:
        folder = sanitize_text_to_foldername_format(arg)
        temp_dir += f'/{folder}'

    return temp_dir
