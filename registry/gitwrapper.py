"""Wrappers for the systemwide git installation.

Since no current Python git libraries fulfill the needs of the project,
the git binary is invoked via the envoy module.

"""
import logging
import urlparse

import envoy

LOG = logging.getLogger(__name__)

GIT_PULL_CMD = "git --work-tree={0} --git-dir={0}/.git pull origin master -q"
GIT_CLONE_CMD = "git clone {0} {1} -q"


class GitException(Exception):
    """Indicates an error from the git process."""
    pass


def pull_from_origin(repo_url):
    """Execute 'git pull' at the provided repo_path."""
    LOG.info("Pulling from %s." % repo_url)
    command = GIT_PULL_CMD.format(repo_url)
    try:
        resp = envoy.run(command)
        assert resp.status_code == 0
    except AssertionError:
        LOG.exception("Pull failed.")
        raise GitException(resp.std_err)
    else:
        LOG.info("Pull successful.")


def clone_from(repo_url, repo_dir):
    """Clone a remote git repo into a local directory."""
    repo_url = _fix_repo_url(repo_url)
    LOG.info("Cloning %s into %s." % (repo_url, repo_dir))
    cmd = GIT_CLONE_CMD.format(repo_url, repo_dir)
    resp = envoy.run(cmd)
    if resp.status_code != 0:
        LOG.error("Cloned failed: %s" % resp.std_err)
        raise GitException(resp.std_err)
    LOG.info("Clone successful.")


def _fix_repo_url(repo_url):
    """Add empty credentials to a repo URL if not set, but only for HTTP/HTTPS.

       This is to make git not hang while trying to read the username and
       password from standard input."""
    parsed = urlparse.urlparse(repo_url)
    
    if parsed.scheme not in ('http', 'https'):
        # Fix only for http and https.
        return repo_url

    username = parsed.username or ""
    password = parsed.password or ""
    port = ":" + parsed.port if parsed.port else ""
    netloc = "".join((username, ":", password, "@", parsed.hostname, port))
    part_list = list(parsed)
    part_list[1] = netloc
    return urlparse.urlunparse(part_list)
