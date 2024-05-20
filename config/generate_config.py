import argparse

import requests

DEFAULTS = {
    "release_version": "dev-version",
    "logging": False,
    "max_logging_gb": 1,
    "max_cache_gb": 10,
}


def generate_config(
    debug,
    deployed,
    logging=DEFAULTS["logging"],
    max_logging_gb=DEFAULTS["max_logging_gb"],
    max_cache_gb=DEFAULTS["max_cache_gb"],
    release_version=DEFAULTS["release_version"],
):
    with open(".env", "w") as f:
        f.write(f"DEBUG={debug}\n")
        f.write(f"DEPLOYED={deployed}\n")

        if deployed:
            f.write(f"LOGGING={logging}\n")
            f.write(f"MAX_LOGGING_GB={max_logging_gb}\n")
            f.write(f"MAX_CACHE_GB={max_cache_gb}\n")

        if release_version == "latest":
            latest_release = requests.get(
                "https://github.com/bioinfodlsu/rice-pilaf/releases/latest"
            ).url.split("/")[-1][1:]
            f.write(f"VERSION={latest_release}\n")
        else:
            f.write(f"VERSION={release_version}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--debug", action="store_true", help="Enable Flask's debugging mode"
    )

    parser.add_argument(
        "--deployed",
        action="store_true",
        help="Use the deployed (instead of the local) version",
    )

    parser.add_argument(
        "--logging", action="store_true", help="Enable logging for app usage analytics"
    )

    parser.add_argument(
        "--latest-version",
        action="store_true",
        help="Automatically tag the app with the latest version number. If this flag is set to True, the version manually specified using --release-version is overridden",
    )

    parser.add_argument(
        "--max-logging-gb",
        required=False,
        type=float,
        default=DEFAULTS["max_logging_gb"],
        help="Maximum storage allocation (in GB) for log files",
    )

    parser.add_argument(
        "--max-cache-gb",
        required=False,
        type=float,
        default=DEFAULTS["max_cache_gb"],
        help="Maximum storage allocation (in GB) for the results cache -- the directory that stores results of previously run analyses to avoid repeated computations",
    )

    parser.add_argument(
        "--release-version",
        required=False,
        help="For manually specifying the app's release version number",
    )

    args = parser.parse_args()

    release_version = args.release_version
    if args.latest_version:
        release_version = "latest"

    generate_config(
        args.debug,
        args.deployed,
        args.logging,
        args.max_logging_gb,
        args.max_cache_gb,
        release_version,
    )
