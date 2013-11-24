"""Tests for the Celery tasks."""

from registry import tasks


def test_clone_repo(tmpdir, settings):
    """Tests the cloning task.

    This task reaches out to the Internet (Github)."""
    settings.REPO_ROOT = str(tmpdir)
    tasks.clone_repo('bower-cache', 'git://github.com/Tinche/bower-cache')
    assert len(tmpdir.listdir()) == 1
    assert tmpdir.listdir()[0].basename == 'bower-cache'