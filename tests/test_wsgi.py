"""Just tests for WSGI boilerplate."""
from __future__ import absolute_import

def test_wsgi_config():
    """Test for presence of a WSGI app."""
    import registry.wsgi

    assert callable(registry.wsgi.application)