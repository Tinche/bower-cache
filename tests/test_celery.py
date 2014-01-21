"""Just tests for Celery boilerplate."""
from __future__ import absolute_import

def test_celery_config():
    """Test for presence of a Celery app."""
    from celery import Celery
    import registry.celery

    assert isinstance(registry.celery.app, Celery)