"""Celery tasks."""
from __future__ import absolute_import

from celery import shared_task
from celery.exceptions import TimeoutError

from .models import ClonedRepo

@shared_task
def clone_repo(pkg_name, repo_url):
    """Create a new cloned repo with the given parameters."""
    new_repo = ClonedRepo(name=pkg_name, origin=repo_url)
    new_repo.save()
    return new_repo


@shared_task
def pull_repo(repo_name):
    """Pull from origin for repo_name."""
    repo = ClonedRepo.objects.get(pk=repo_name)
    repo.pull()


@shared_task
def pull_all_repos():
    """Pull origin updates for all repos with origins."""
    repos = ClonedRepo.objects.all()
    for repo in repos:
        if repo.origin is not None:
            pull_repo.delay(repo_name=repo.name)