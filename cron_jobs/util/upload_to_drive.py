import os

# RICE_PILAF_PATH = "/app"
RICE_PILAF_PATH = "D:/Research/rice-pilaf"
LOG_PATH = f"{RICE_PILAF_PATH}/logs"
LAST_UPLOADED_TIMESTAMP_FILE = f"{LOG_PATH}/last_uploaded_timestamp"
FOR_UPLOAD_LOG_FILE = f"{LOG_PATH}/for_upload.log"


def get_timestamp(log_line):
    return log_line.split("|")[0]


def get_last_uploaded_timestamp():
    if not os.path.exists(LAST_UPLOADED_TIMESTAMP_FILE):
        return 0

    with open(LAST_UPLOADED_TIMESTAMP_FILE) as f:
        for line in f:
            return line.strip()


def prepare_log_file_for_upload():
    last_uploaded_timestamp = get_last_uploaded_timestamp()

    with open(FOR_UPLOAD_LOG_FILE, "w") as upload:
        if os.path.exists(f"{LOG_PATH}/usage.log.1"):
            with open(f"{LOG_PATH}/usage.log.1") as log:
                for line in log:
                    if str(get_timestamp(line)) > str(last_uploaded_timestamp):
                        upload.write(line)

        with open(f"{LOG_PATH}/usage.log") as log:
            for line in log:
                if str(get_timestamp(line)) > str(last_uploaded_timestamp):
                    upload.write(line)

    with open(FOR_UPLOAD_LOG_FILE) as upload, open(
        LAST_UPLOADED_TIMESTAMP_FILE, "w"
    ) as timestamp:
        for line in upload:
            pass

        timestamp.write(get_timestamp(line))


prepare_log_file_for_upload()

# scope = ["https://www.googleapis.com/auth/drive"]
# service_account_key = (
#     f"{RICE_PILAF_PATH}/cron_jobs/credentials/ricepilaf-logger-key.json"
# )
# credentials = service_account.Credentials.from_service_account_file(
#     filename=service_account_key, scopes=scope
# )
# service = build("drive", "v3", credentials=credentials)


# yesterday = datetime.now(timezone.utc).date() - timedelta(1)
# for file in os.listdir(f"{RICE_PILAF_PATH}/logs"):
#     if file.startswith(str(yesterday)):
#         LOG = f"{RICE_PILAF_PATH}/logs/{file}"
#         media = MediaFileUpload(LOG)

#         uploaded = False
#         while not uploaded:
#             try:
#                 file_metadata = {
#                     "name": LOG.split("/")[-1],
#                     "parents": ["1ECnXYVuJOlEC4CX20IggHufAiYTm91hM"],
#                 }

#                 file = (
#                     service.files()
#                     .create(body=file_metadata, media_body=media, fields="id")
#                     .execute()
#                 )

#                 uploaded = True
#                 print(LOG)
#                 os.remove(LOG)

#             except:
#                 # Try again in 5 minutes
#                 time.sleep(5 * 60)
