import os
import shutil
import sqlite3
from pathlib import Path

from dotenv import dotenv_values

RICE_PILAF_PATH = Path(__file__).parent.parent.parent
TEMP_PATH = f"{RICE_PILAF_PATH}/static/temp"
FILE_STATUS_DB = f"{TEMP_PATH}/file_status.db"
FILE_STATUS_TABLE = "file_status"

DEFAULT_MAX_CACHE_GB = 10
CACHE_CLEARING_THRESHOLD = 0.95

GB_TO_BYTES = 1e9


def get_max_cache_gb():
    config = dotenv_values(f"{RICE_PILAF_PATH}/.env")
    try:
        max_cache_gb = float(config["MAX_CACHE_GB"])
        return max_cache_gb
    except:
        return DEFAULT_MAX_CACHE_GB


def get_cache_folder_size():
    size = 0
    for root, dirs, files in os.walk(TEMP_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            size += os.path.getsize(file_path)

    return size


def clear_cache_folder():
    if os.path.exists(TEMP_PATH):
        shutil.rmtree(TEMP_PATH, ignore_errors=True)

    # Recreate the database
    os.makedirs(TEMP_PATH)

    try:
        connection = sqlite3.connect(FILE_STATUS_DB)
        cursor = connection.cursor()

        query = (
            f"CREATE TABLE IF NOT EXISTS {FILE_STATUS_TABLE} (name TEXT, UNIQUE(name));"
        )

        cursor.execute(query)
        connection.commit()

        cursor.close()
        connection.close()
    except sqlite3.Error as error:
        pass


if __name__ == "__main__":
    cache_folder_size_gb = get_cache_folder_size() / GB_TO_BYTES
    print(f"Current cache size: {cache_folder_size_gb} GB")
    if cache_folder_size_gb > CACHE_CLEARING_THRESHOLD * get_max_cache_gb():
        print(f"Exceeded {CACHE_CLEARING_THRESHOLD * 100}% of maximum cache size")
        print("Clearing cache...")
        clear_cache_folder()
        print("Success!")
    else:
        print("Cache is not yet due for clearing")
