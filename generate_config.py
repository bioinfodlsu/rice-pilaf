import argparse

import requests


def generate_config(
    debug, deployed, logging, max_logging_gb, max_cache_gb, version=None
):
    with open(".env", "w") as f:
        f.write(f"DEBUG={debug}\n")
        f.write(f"DEPLOYED={deployed}\n")

        if deployed:
            f.write(f"LOGGING={logging}\n")
            f.write(f"MAX_LOGGING_GB={max_logging_gb}\n")
            f.write(f"MAX_CACHE_GB={max_cache_gb}\n")

        if version:
            if version == "latest":
                latest_release = requests.get(
                    "https://github.com/bioinfodlsu/rice-pilaf/releases/latest"
                ).url.split("/")[-1][1:]
                f.write(f"VERSION={latest_release}\n")
            else:
                f.write(f"VERSION={version}\n")


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
        help="Automatically tag the app with the latest version number. If this flag is set to True, the version manually specified using --version is overridden",
    )

    parser.add_argument(
        "--max-logging-gb",
        required=False,
        type=float,
        default=1,
        help="Maximum storage allocation (in GB) for log files",
    )

    parser.add_argument(
        "--max-cache-gb",
        required=False,
        type=float,
        default=10,
        help="Maximum storage allocation (in GB) for the results cache -- the directory that stores results of previously run analyses to avoid repeated computations",
    )

    parser.add_argument(
        "-v",
        "--version",
        required=False,
        help="For manually specifying the app's version number",
    )

    args = parser.parse_args()

    version = args.version
    if args.latest_version:
        version = "latest"

    generate_config(
        args.debug,
        args.deployed,
        args.logging,
        args.max_logging_gb,
        args.max_cache_gb,
        version,
    )
