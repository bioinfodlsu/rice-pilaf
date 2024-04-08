import time

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

scope = ["https://www.googleapis.com/auth/drive"]
service_account_key = (
    "D:/Research/rice-pilaf/cron_jobs/credentials/ricepilaf-logger-key.json"
)
credentials = service_account.Credentials.from_service_account_file(
    filename=service_account_key, scopes=scope
)
service = build("drive", "v3", credentials=credentials)

file_metadata = {
    "name": "2024-04-08.log",
    "parents": ["1ECnXYVuJOlEC4CX20IggHufAiYTm91hM"],
}
media = MediaFileUpload("D:/Research/rice-pilaf/logs/2024-04-08.log")

uploaded = False
while not uploaded:
    try:
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        uploaded = True

    except:
        # Try again in 5 minutes
        time.sleep(5 * 60)
