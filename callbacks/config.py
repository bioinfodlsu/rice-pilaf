from dotenv import dotenv_values

DEFAULT_MAX_LOGGING_GB = 1


def is_deployed_version():
    config = dotenv_values(".env")
    return config["DEPLOYED"].lower() == "true"


def is_debug_mode():
    config = dotenv_values(".env")
    if is_deployed_version():
        return False

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
        return f'v{config["VERSION"]}'
    except:
        # The VERSION key is not a requirement in the .env file
        return ""


def is_logging_mode():
    config = dotenv_values(".env")
    return config["LOGGING"].lower() == "true"


def get_max_logging_gb():
    config = dotenv_values(".env")
    try:
        max_logging_gb = float(config["MAX_LOGGING_GB"])
        return max_logging_gb
    except:
        return DEFAULT_MAX_LOGGING_GB
