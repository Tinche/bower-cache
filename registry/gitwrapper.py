"""Wrappers for the system-wide git installation.

Since no current Python git libraries fulfill the needs of the project,
the git binary is invoked via the envoy module.

"""
import logging
import os.path
from configparser import ConfigParser

import envoy

from ._compat import urlparse

LOG = logging.getLogger(__name__)

GIT_PULL_CMD = "git --work-tree={0} --git-dir={0}/.git pull origin master -q"
GIT_CLONE_CMD = "git clone {0} {1} -q"


class GitException(Exception):
    """Indicates an error from the git process."""
    pass


def pull_from_origin(repo_path):
    """Execute 'git pull' at the provided repo_path."""
    LOG.info("Pulling from origin at %s." % repo_path)
    command = GIT_PULL_CMD.format(repo_path)
    resp = envoy.run(command)
    if resp.status_code != 0:
        LOG.exception("Pull failed.")
        raise GitException(resp.std_err)
    else:
        LOG.info("Pull successful.")


def read_remote_origin(repo_dir):
    """Read the remote origin URL from the given git repo, or None if unset."""
    conf = ConfigParser()
    conf.read(os.path.join(repo_dir, '.git/config'))
    return conf.get('remote "origin"', 'url')


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

