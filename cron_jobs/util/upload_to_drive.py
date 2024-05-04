import os
import time
from pathlib import Path

from dotenv import dotenv_values
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

RICE_PILAF_PATH = Path(__file__).parent.parent.parent
LOG_PATH = f"{RICE_PILAF_PATH}/logs"
LAST_UPLOADED_TIMESTAMP_FILE = f"{LOG_PATH}/last_uploaded_timestamp"
FOR_UPLOAD_LOG_FILE = f"{LOG_PATH}/for_upload.log"

SERVICE_ACCOUNT_KEY = (
    f"{RICE_PILAF_PATH}/cron_jobs/credentials/ricepilaf-logger-key.json"
)

LOG_DRIVE_ID = "1ECnXYVuJOlEC4CX20IggHufAiYTm91hM"


def is_logging_mode():
    try:
        config = dotenv_values(f"{RICE_PILAF_PATH}/.env")
        return config["LOGGING"].lower() == "true"
    except:
        return False


def get_timestamp(log_line):
    CRITICAL_ERROR = -1
    if "|" in log_line:
        try:
            timestamp = int(log_line.split("|")[0])
        except:
            timestamp = CRITICAL_ERROR
    else:
        timestamp = CRITICAL_ERROR

    return timestamp


def get_last_uploaded_timestamp():
    if not os.path.exists(LAST_UPLOADED_TIMESTAMP_FILE):
        return 0

    with open(LAST_UPLOADED_TIMESTAMP_FILE) as f:
        for line in f:
            return int(line.strip())


def prepare_log_file_for_upload():
    last_uploaded_timestamp = get_last_uploaded_timestamp()

    with open(FOR_UPLOAD_LOG_FILE, "w") as upload:
        if os.path.exists(f"{LOG_PATH}/usage.log.1"):
            with open(f"{LOG_PATH}/usage.log.1") as log:
                for line in log:
                    if get_timestamp(line) > last_uploaded_timestamp:
                        upload.write(line)

        if os.path.exists(f"{LOG_PATH}/usage.log"):
            with open(f"{LOG_PATH}/usage.log") as log:
                for line in log:
                    if get_timestamp(line) > last_uploaded_timestamp:
                        upload.write(line)


def upload_log_file():
    scope = ["https://www.googleapis.com/auth/drive"]

    credentials = service_account.Credentials.from_service_account_file(
        filename=SERVICE_ACCOUNT_KEY, scopes=scope
    )
    service = build("drive", "v3", credentials=credentials)

    media = MediaFileUpload(FOR_UPLOAD_LOG_FILE, mimetype="text/plain")

    file_metadata = {
        "name": f"log.{time.time_ns() // 1000}",
        "parents": [LOG_DRIVE_ID],
    }

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )


def update_last_uploaded_timestamp_file():
    with open(FOR_UPLOAD_LOG_FILE) as upload, open(
        LAST_UPLOADED_TIMESTAMP_FILE, "w"
    ) as timestamp:
        for line in upload:
            pass

        timestamp.write(f"{get_timestamp(line)}")


if __name__ == "__main__":
    if is_logging_mode():
        MAX_RETRIES = 5
        retries_ctr = 0

        while retries_ctr < MAX_RETRIES:
            try:
                print("Preparing log file to upload...")
                prepare_log_file_for_upload()

                if os.stat(FOR_UPLOAD_LOG_FILE).st_size > 0:
                    print("Uploading log file...")
                    upload_log_file()
                    update_last_uploaded_timestamp_file()
                    print("Success!")
                else:
                    print("Nothing to write")

                break

            except Exception as e:
                print(e)

                # Try again in 5 minutes
                time.sleep(5 * 60)
                retries_ctr += 1
