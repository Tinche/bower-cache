"""Tests for the gitwrapper module."""
import pytest
import mock

from registry import gitwrapper


def test_pull_from_origin(tmpdir):
    """First we clone a repo into a temporary directory, then pull.

    This test reaches out to the Internet.
    """
    gitwrapper.clone_from('git://github.com/Tinche/bower-cache', tmpdir)
    gitwrapper.pull_from_origin(tmpdir)


@mock.patch('envoy.run')
def test_pull_from_origin_fail(run):
    """Simulate a failure to pull from origin.

    This test uses mocks, and doesn't reach out to the Internet.
    """
    from envoy import Response
    resp = Response()
    resp.status_code = 1  # Set a non-0 status code

    run.return_value = resp

    with pytest.raises(gitwrapper.GitException):
        gitwrapper.pull_from_origin('/var/git/bower-cache')


def test_clone_nonexistent(tmpdir):
    """Test an unsuccessful clone."""
    repo_url = 'git://github.com/Tinche/a-repo-i-will-never-make'
    with pytest.raises(gitwrapper.GitException):
        gitwrapper.clone_from(repo_url, tmpdir)


def test_fix_repo_url():
    """Tests fixing HTTP/S URLs."""
    repo_url_git = 'git://github.com/Tinche/bower-cache'
    repo_url_https = 'https://github.com/Tinche/bower-cache'
    fixed_url_https = 'https://:@github.com/Tinche/bower-cache'
    assert repo_url_git == gitwrapper._fix_repo_url(repo_url_git)
    assert fixed_url_https == gitwrapper._fix_repo_url(repo_url_https)
