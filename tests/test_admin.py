"""Tests for the admin additions."""
import re
import mock

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