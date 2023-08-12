import os
import pandas as pd
from .constants import Constants
const = Constants()


def path_exists(directory):
    return os.path.exists(directory)


def make_dir(directory):
    if not path_exists(directory):
        os.makedirs(directory)


def read_csv(file):
    return pd.read_csv(file)


def convert_text_to_dirname(text):
    return text.replace(
        ":", "_").replace(";", "__").replace("-", "_").replace('.', '_')


def convert_text_to_filename(text):
    return text.replace(
        ":", "_").replace(";", "__").replace("-", "_").replace('.', '_')


def get_path_to_temp(genomic_interval, analysis_type, *args):
    genomic_interval_foldername = convert_text_to_dirname(
        genomic_interval)

    analysis_type = convert_text_to_dirname(analysis_type)

    temp_dir = f'{const.TEMP}/{genomic_interval_foldername}/{analysis_type}'
    for arg in args:
        folder = convert_text_to_dirname(arg)
        temp_dir += f'/{folder}'

    return temp_dir
