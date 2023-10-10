import regex as re
import os
from .constants import Constants

import time
import sqlite3


def path_exists(path):
    """
    Checks if given path exists

    Parameters:
    - path: Path to be checked if it exists

    Returns:
    - True if the path exists; False, otherwise
    """
    return os.path.exists(path)


def make_dir(directory):
    """
    Creates given directory if it does not yet exist

    Parameters:
    - directory: Directory to be created
    """
    if not path_exists(directory):
        os.makedirs(directory)


def convert_text_to_path(text):
    """
    Converts given text into a well-formed path

    Parameters:
    - text: Text to be converted into a well-formed path

    Returns:
    - Well-formed path
    """
    return text.strip().replace(
        ":", "_").replace(";", "__").replace("-", "_").replace('.', '_').replace(' ', '')


def get_path_to_temp(genomic_interval, analysis_type, *args):
    """
    Forms the path to temporary (file-cached) results of given post-GWAS analysis
    This function returns only the path name. It does not create the actual file or directory

    Parameters:
    - genomic_interval: Genomic interval entered by the user
    - analysis_type: Post-GWAS analysis
    - args: Subfolder names appended to the path

    Returns:
    - Path to temporary (file-cached) results of post-GWAS analysis
    """
    genomic_interval_foldername = shorten_name(convert_text_to_path(
        genomic_interval))

    analysis_type = convert_text_to_path(analysis_type)

    temp_dir = f'{Constants.TEMP}/{genomic_interval_foldername}/{analysis_type}'
    for folder in args:
        temp_dir += f'/{convert_text_to_path(folder)}'

    temp_dir = re.sub(r'/+', '/', temp_dir)

    return temp_dir


def get_path_to_text_mining_temp(analysis_type, *args):
    analysis_type = convert_text_to_path(analysis_type)

    temp_dir = f'{Constants.TEMP}/{analysis_type}'
    for folder in args:
        temp_dir += f'/{convert_text_to_path(folder)}'

    temp_dir = re.sub(r'/+', '/', temp_dir)

    return temp_dir


def shorten_name(name):
    if name and len(name) > 0:
        # Recreate the database

        # We have to recreate the database here to address the problem in the deployed version
        #    where the Clear Cache button is not exposed to the user.

        # Since the Clear Cache button is not exposed to the user, clearing the cache
        #    is done using some script in the server. However, due to permission complications
        #    in Linux, this results in the database being read-only. As a workaround, the database
        #    has to be created by the application itself (not by some other script in the server).
        make_dir(Constants.TEMP)

        try:
            connection = sqlite3.connect(Constants.FILE_STATUS_DB)
            cursor = connection.cursor()

            query = f'CREATE TABLE IF NOT EXISTS {Constants.FILE_STATUS_TABLE} (name TEXT, UNIQUE(name));'

            cursor.execute(query)
            connection.commit()

            cursor.close()
            connection.close()
        except sqlite3.Error as error:
            pass

        # Insert the name into the database
        try:
            connection = sqlite3.connect(Constants.FILE_STATUS_DB)
            cursor = connection.cursor()

            query = f'INSERT OR IGNORE INTO {Constants.FILE_STATUS_TABLE}(name) VALUES("{name}")'

            cursor.execute(query)
            connection.commit()

            cursor.close()
            connection.close()
        except sqlite3.Error:
            pass

        # Retrieve the shortened name from the database
        try:
            connection = sqlite3.connect(Constants.FILE_STATUS_DB)
            cursor = connection.cursor()

            query = f'SELECT rowid FROM {Constants.FILE_STATUS_TABLE} WHERE name = "{name}"'
            cursor.execute(query)
            row_id = cursor.fetchall()[0][0]

            cursor.close()
            connection.close()
        except sqlite3.Error:
            pass

        return str(row_id)

    return name


def append_timestamp_to_filename(filename):
    return f'{filename}.{time.time_ns() // 1000}'
