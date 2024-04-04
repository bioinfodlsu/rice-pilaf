from pathlib import Path


def is_deployed_version():
    return Path("./.deploy").exists()


def show_if_deployed():
    if is_deployed_version():
        return {"display": "block"}

    return {"display": "none"}


def show_if_not_in_demo_branch():
    if not is_deployed_version():
        return {"display": "block"}

    return {"display": "none"}


def get_release_version():
    try:
        version_file = Path(".version")
        with version_file.open("r") as f:
            for line in f:
                return line.strip()
    except:
        return ""
