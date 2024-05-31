from dotenv import dotenv_values

from config.generate_config import DEFAULTS


def is_deployed_version():
    config = dotenv_values(".env")
    return config["DEPLOYED"].lower() == "true"


def is_debug_mode():
    config = dotenv_values(".env")
    return config["DEBUG"].lower() == "true"


def show_if_deployed():
    if is_deployed_version():
        return {"display": "block"}

    return {"display": "none"}


def show_if_not_deployed():
    if not is_deployed_version():
        return {"display": "block"}

    return {"display": "none"}


def get_release_version():
    try:
        config = dotenv_values(".env")
        if config["VERSION"].startswith("dev"):
            return config["VERSION"]

        return f'v{config["VERSION"]}'
    except KeyError:
        return DEFAULTS["release_version"]


def is_logging_mode():
    try:
        config = dotenv_values(".env")
        return config["LOGGING"].lower() == "true"
    except KeyError:
        return DEFAULTS["logging"]


def get_max_logging_gb():
    try:
        config = dotenv_values(".env")
        return float(config["MAX_LOGGING_GB"])
    except KeyError:
        return DEFAULTS["max_logging_gb"]
