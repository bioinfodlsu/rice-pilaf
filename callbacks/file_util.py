import os
from .constants import Constants
const = Constants()


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
    return text.replace(
        ":", "_").replace(";", "__").replace("-", "_").replace('.', '_')


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
    genomic_interval_foldername = convert_text_to_path(
        genomic_interval)

    analysis_type = convert_text_to_path(analysis_type)

    temp_dir = f'{const.TEMP}/{genomic_interval_foldername}/{analysis_type}'
    for folder in args:
        temp_dir += f'/{convert_text_to_path(folder)}'

    return temp_dir
