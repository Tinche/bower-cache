"""Wrappers for the systemwide git installation.

Since no current Python git libraries fulfill the needs of the project,
the git binary is invoked via the subprocess module.

"""
import logging
import subprocess

logger = logging.getLogger(__name__)
GIT_PULL_CMD = "git --work-tree={0} --git-dir={0}/.git pull origin master -q"

def pull_from_origin(repo_path):
    """Execute 'git pull' at the provided repo_path."""
    logger.info("Pulling from %s." % repo_path)
    command = GIT_PULL_CMD.format(repo_path)
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as exc:
        logger.exception("Pull failed.")
    else:
        logger.info("Pull successful.")
