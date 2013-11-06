from registry import bowerlib


def test_get_package():
    """Test package retrieval. Will use the real Bower registry!"""
    upstream_bower = 'https://bower.herokuapp.com'
    pkg = bowerlib.get_package(upstream_bower, 'jquery')
    assert pkg['name'] == 'jquery'


def test_package_not_found():
    """Test package retrieval. Will use the real Bower registry!"""
    upstream_bower = 'https://bower.herokuapp.com'
    pkg_name = 'ihopethisnevergetsputonthebowerregistry'
    pkg = bowerlib.get_package(upstream_bower, pkg_name)
    assert pkg is None
