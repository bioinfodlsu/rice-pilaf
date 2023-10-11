import os
import shutil
from ..style_util import *
from ..constants import Constants
from ..file_util import *

import sqlite3


example_genomic_intervals = {
    'pre-harvest': 'Chr01:1523625-1770814;Chr04:4662701-4670717',
    'anaerobic-germination': 'Chr07:6000000-6900000'}


def clear_cache_folder():
    if os.path.exists(Constants.TEMP):
        shutil.rmtree(Constants.TEMP, ignore_errors=True)

    # Recreate the database
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


def get_cleared_dccStore_data_excluding_some_data(dccStore_children, *args):
    for i in range(len(dccStore_children)):
        dccStore_ID = dccStore_children[i]['props']['id']

        if args:
            flag = False
            for arg in args:
                if arg in dccStore_ID:
                    flag = True

            if not flag:
                dccStore_children[i]['props']['data'] = ''

        else:
            dccStore_children[i]['props']['data'] = ''

    return dccStore_children


def get_example_genomic_interval(description):
    return example_genomic_intervals[description]


def set_active_class(display_map, active_class):
    class_names = []
    for page, layout_link in display_map.items():
        if page == active_class:
            class_name = add_class_name('active', layout_link.link_class)
        else:
            class_name = remove_class_name('active', layout_link.link_class)

        class_names.append(class_name)

    return tuple(class_names)
