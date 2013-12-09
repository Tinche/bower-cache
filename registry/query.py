import logging
import os
from os import path

from django.db.models import query

from git.repo.base import Repo

logger = logging.getLogger(__name__)


class ClonedRepoQuerySet(query.QuerySet):
    """A file-system based query set for cloned repos."""
    def __init__(self, model=None, repos=None):
        self.model = model
        self._result_cache = repos
        self._for_write = False
        self._prefetch_related_lookups = []

    def get(self, *args, **kwargs):
        logger.debug("Get called with %s, %s" % (str(args), str(kwargs)))
        results = self.filter(**kwargs)
        if not results:
            raise self.model.DoesNotExist()
        return results[0]

    def __iter__(self):
        return self.iterator()

    def iterator(self):
        """Do the actual lookup and return an iterator over the results."""
        return iter(ClonedRepoQuerySet._get_all_repos())

    def exists(self):
        return False

    def filter(self, **kwargs):
        self._fetch_all()
        filtered = self._result_cache
        for key, val in kwargs.items():
            filtered = [rep for rep in filtered if getattr(rep, key) == val]
        return ClonedRepoQuerySet(model=self.model, repos=filtered)

    def __len__(self):
        self._fetch_all()
        return len(self._result_cache)

    def __getitem__(self, index):
        self._fetch_all()
        return self._result_cache[index]

    def delete(self):
        self._fetch_all()
        for repo in self._result_cache:
            repo.delete()

    @staticmethod
    def _get_origin(full_repo_dir):
        return Repo(full_repo_dir).remotes.origin.url

    @staticmethod
    def _get_all_repos():
        from .models import ClonedRepo
        from django.conf import settings
        repo_root = settings.REPO_ROOT
        repo_dirs = (dir for dir in os.listdir(repo_root)
                                 if path.isdir(path.join(repo_root, dir)))
        repos = [ClonedRepo(name=repo_dir,
                            origin=ClonedRepoQuerySet._get_origin(
                                         path.join(repo_root, repo_dir)))
                 for repo_dir in repo_dirs]
        return repos
