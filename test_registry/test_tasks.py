"""Tests for the Celery tasks."""
import os.path

from registry import tasks
from registry.models import ClonedRepo
from test_registry._compat import mock


def test_clone_repo(tmpdir, settings):
    """Tests the cloning task.

    This task reaches out to the Internet (Github)."""
    print settings
    settings.REPO_ROOT = str(tmpdir)
    tasks.clone_repo('bower-cache', 'git://github.com/Tinche/bower-cache')
    assert len(tmpdir.listdir()) == 1
    assert tmpdir.listdir()[0].basename == 'bower-cache'


@mock.patch('registry.models.pull_from_origin')
def test_pull_origin(pull_from_origin, tmpdir, settings):
    """Test the task for pulling from origin.

    This task reaches out to the Internet (Github)."""
    test_clone_repo(tmpdir, settings)
    tasks.pull_repo('bower-cache')

    repo_path = os.path.join(str(tmpdir), 'bower-cache')

    pull_from_origin.assert_called_once_with(repo_path)


@mock.patch('registry.models.ClonedRepo.objects.all')
@mock.patch('registry.tasks.pull_repo.delay')
def test_pull_all(delay, all):
    """Test the task that dispatches pull tasks for all repos with origins."""
    # Create two mock repos, one with an origin, one without.
    repos = [
       ClonedRepo(name="repo1", origin="git://github.com/repo1/repo1.git"),
       ClonedRepo(name="repo2"),
    ]
    all.return_value = repos
    tasks.pull_all_repos()

    # Now assert only the origin repo got submitted for pulling.
    delay.assert_called_once_with(repo_name='repo1')
