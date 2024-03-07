from pathlib import Path


def get_active_branch_name():
    """
    Lifted from https://stackoverflow.com/questions/26134026/how-to-get-the-current-checked-out-git-branch-name-through-pygit2
    """
    head_dir = Path(".") / ".git" / "HEAD"
    with head_dir.open("r") as f:
        content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]


def is_deployed_version():
    return Path("./.deploy").exists()


def is_in_demo_branch():
    return get_active_branch_name() == 'demo' or is_deployed_version()


def show_if_in_demo_branch():
    if is_in_demo_branch():
        return {'display': 'block'}

    return {'display': 'none'}


def show_if_not_in_demo_branch():
    if not is_in_demo_branch():
        return {'display': 'block'}

    return {'display': 'none'}


def get_release_version():
    releases = Path('.git/refs/tags').glob('*')
    latest_release = max(releases, key=lambda p: p.stat().st_ctime)
    return str(latest_release).split('/')[-1]
