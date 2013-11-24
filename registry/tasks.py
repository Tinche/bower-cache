"""Celery tasks."""
import celery

from .models import ClonedRepo

@celery.task
def clone_repo(pkg_name, repo_url):
    """Create a new cloned repo with the given parameters."""
    new_repo = ClonedRepo(name=pkg_name, origin=repo_url)
    new_repo.save()
    return new_repo
