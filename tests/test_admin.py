"""Tests for the admin additions."""
import re
import mock

import os.path

from bs4 import BeautifulSoup


def test_main_view(admin_client):
    """Test the main admin view.

    This test doesn't reach out to external services.
    """
    resp = admin_client.get('/admin/')
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.content)

    # Find the link to the Registry app.
    reg_link = soup.find('a', text=re.compile('Registry'))
    # Grab the table for the registry app.
    reg_table = reg_link.find_parent('table')

    # The registry table has two rows.
    reg_rows = reg_table.find_all('tr')
    assert len(reg_rows) == 2

    for row in reg_rows:
        assert row.find(text=re.compile("Add"))
        assert row.find(text=re.compile("Change"))


def test_packages_view(admin_client):
    """Test the package admin part.

    This test doesn't reach out to external services.
    """
    resp = admin_client.get('/admin/registry/package/')
    assert resp.status_code == 200

    assert '0 packages' in resp.content
    assert 'Add package' in resp.content

    # Now add a package through the form.
    admin_client.post('/admin/registry/package/add/',
                      {'name': 'testpkg', 'url': 'git://git'})

    resp = admin_client.get('/admin/registry/package/')
    assert resp.status_code == 200

    assert '1 package' in resp.content


@mock.patch('registry.models.pull_from_origin')
def test_cloned_repo_view(pull_from_origin, tmpdir, settings, admin_client):
    """Test cloned repo views.

    This test reaches out to the Internet - both the upstream Bower registry
    and Github."""
    settings.REPO_ROOT = str(tmpdir)
    resp = admin_client.get('/admin/registry/clonedrepo/')
    assert resp.status_code == 200

    assert '0 cloned repos' in resp.content
    assert 'Add cloned repo' in resp.content

    # Now add a package through the form.
    admin_client.post('/admin/registry/clonedrepo/add/',
                      {'name': 'angular', 'origin_source': 'upstream'})

    resp = admin_client.get('/admin/registry/clonedrepo/')
    assert resp.status_code == 200

    assert '1 cloned repo' in resp.content

    # Try pulling from origin. The actual pull is mocked.
    resp = admin_client.get('/admin/registry/clonedrepo/angular/pull/')
    assert resp.status_code == 302
    pull_from_origin.assert_called_with(tmpdir.join('angular'))

    # Now remove the cloned repository.
    admin_client.post('/admin/registry/clonedrepo/angular/delete/',
                      {'post': 'yes'})

    resp = admin_client.get('/admin/registry/clonedrepo/')
    assert resp.status_code == 200

    assert '0 cloned repos' in resp.content
    assert 'Add cloned repo' in resp.content


def test_add_repo_no_origin(admin_client):
    """Test submitting a cloned repo with origin_source and without an origin_
    url.

    This test doesn't reach out to external services.
    """
    # Add a package through the form.
    resp = admin_client.post('/admin/registry/clonedrepo/add/',
                            {'name': 'angular', 'origin_source': 'origin_url'})

    assert resp.status_code == 200
    soup = BeautifulSoup(resp.content)
    assert 'Please provide an origin URL' in soup.get_text()

@mock.patch('registry.models.clone_from')
def test_add_git_error(clone_from, tmpdir, settings, admin_client):
    """Test submitting a cloned repo, the clone of which fails due to a git
    error.

    This test doesn't reach out to external services.
    """
    settings.REPO_ROOT = str(tmpdir)

    from django.conf import settings
    from registry.gitwrapper import GitException
    from registry.models import ClonedRepo
    clone_from.side_effect = GitException("Surprise!")

    url = 'git://a-url.git'
    base_path = settings.REPO_ROOT

    # Add a package through the form.
    resp = admin_client.post('/admin/registry/clonedrepo/add/',
                             {'name': 'angular', 'origin_source': 'origin_url',
                              'origin_url': url}, follow=True)

    assert resp.status_code == 200

    soup = BeautifulSoup(resp.content)
    assert 'Surprise!' in soup.get_text()

    clone_from.assert_called_with(url, os.path.join(base_path, 'angular'))
    assert not ClonedRepo.objects.all()


@mock.patch('registry.bowerlib.get_package')
def test_add_repo_bower_error(get_package, admin_client):
    """Test submitting a cloned repo, and Bower returning an IO error.

    This test doesn't reach out to external services.
    """
    get_package.side_effect = IOError("An IO Error occured.")
    # Add a package through the form.
    resp = admin_client.post('/admin/registry/clonedrepo/add/',
                             {'name': 'angular', 'origin_source': 'upstream'})

    assert resp.status_code == 200
    soup = BeautifulSoup(resp.content)
    assert get_package.side_effect.message in soup.get_text()


@mock.patch('registry.bowerlib.get_package')
def test_add_repo_bower_clueless(get_package, admin_client):
    """Test submitting a cloned repo, with Bower not knowing about it.

    This test doesn't reach out to external services.
    """
    get_package.return_value = None
    # Add a package through the form.
    resp = admin_client.post('/admin/registry/clonedrepo/add/',
                             {'name': 'angular', 'origin_source': 'upstream'})

    assert resp.status_code == 200
    soup = BeautifulSoup(resp.content)
    assert 'Upstream registry has no knowledge' in soup.get_text()
