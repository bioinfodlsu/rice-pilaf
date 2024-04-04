import requests


def generate_config(debug, deployed, version=None):
    with open(".env", "w") as f:
        f.write(f"DEBUG={debug}\n")
        f.write(f"DEPLOYED={deployed}\n")

        if version:
            if version == "latest":
                latest_release = requests.get(
                    "https://github.com/bioinfodlsu/rice-pilaf/releases/latest"
                ).url.split("/")[-1][1:]
                f.write(f"VERSION={latest_release}\n")
            else:
                f.write(f"VERSION={version}\n")
