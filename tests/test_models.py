"""Unit tests for the models."""
from registry.models import ClonedRepo, Package


def test_cloned_repo_as_package(settings):
    """Test the cloned repo model converting itself into a package."""
    pkg_name = 'aname'
    # Mock out the REPO_URL in settings, that's how cloned repos know where
    # they're served from.
    settings.REPO_URL = "git://localhost/git/"

    cloned_repo = ClonedRepo(name=pkg_name, origin='git://test.git')

    pkg = cloned_repo.to_package()

    assert isinstance(pkg, Package)
    assert pkg.name == pkg_name
    assert pkg.url == settings.REPO_URL + "aname"