import os
import shutil
from ..style_util import *
from ..constants import Constants

const = Constants()

example_genomic_intervals = {
    'example-preharvest': 'Chr01:1523625-1770814;Chr04:4662701-4670717'}


def clear_cache_folder():
    if os.path.exists(const.TEMP):
        shutil.rmtree(const.TEMP, ignore_errors=True)


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