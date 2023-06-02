import pandas as pd
import os
import shutil
from ..constants import Constants

const = Constants()


def clear_cache_folder():
    if os.path.exists(const.TEMP):
        shutil.rmtree(const.TEMP, ignore_errors=True)
