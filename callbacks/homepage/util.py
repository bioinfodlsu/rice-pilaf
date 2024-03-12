import os
import shutil
from ..style_util import *
from ..constants import Constants
from ..file_util import *

import sqlite3


example_genomic_intervals = {
    "pre-harvest": "Chr01:1523625-1770814; Chr04:4662701-4670717",
    "anaerobic-germination": "Chr07:6000000-6900000",
}


def clear_cache_folder():
    """
    Removes the static/temp cache folder and recreates the database

    Parameters:
    - none

    Returns:
    - none
    """
    if os.path.exists(Constants.TEMP):
        shutil.rmtree(Constants.TEMP, ignore_errors=True)

    # Recreate the database
    make_dir(Constants.TEMP)

    try:
        connection = sqlite3.connect(Constants.FILE_STATUS_DB)
        cursor = connection.cursor()

        query = f"CREATE TABLE IF NOT EXISTS {Constants.FILE_STATUS_TABLE} (name TEXT, UNIQUE(name));"

        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()
    except sqlite3.Error as error:
        pass


def clear_specific_dccStore_data(dccStore_children, *args):
    """
    Removes the data in all the dcc.Store variables excluding some variables

    Parameters:
    - dccStore_children: List of dcc.Store data
    - *args: Substrings in dcc.Store IDs that will be cleared of their data in the dcc.Store variables

    Returns:
    - Sanitized dcc.Store data
    """

    for i in range(len(dccStore_children)):
        dccStore_ID = dccStore_children[i]["props"]["id"]

        if args:
            flag = False
            for arg in args:
                if arg in dccStore_ID:
                    flag = True

            if flag:
                dccStore_children[i]["props"]["data"] = ""

        else:
            dccStore_children[i]["props"]["data"] = ""

    return dccStore_children


def get_example_genomic_interval(description):
    """
    Returns the genomic interval of the selected description

    Parameters:
    - description: selected choice among the example choices of genomic intervals

    Returns:
    - Genomic interval of the selected description
    """
    return example_genomic_intervals[description]
