import os
import shutil
from ..constants import Constants

const = Constants()

example_genomic_intervals = {
    'example-preharvest': 'Chr01:1523625-1770814;Chr04:4662701-4670717'}


def clear_cache_folder():
    if os.path.exists(const.TEMP):
        shutil.rmtree(const.TEMP, ignore_errors=True)


def get_example_genomic_interval(description):
    return example_genomic_intervals[description]
