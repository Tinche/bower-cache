import os
from os import path

from django.db.models import query

from git.repo.base import Repo
from .settings import REPO_ROOT

class ClonedRepoQuerySet(query.QuerySet):
    def __init__(self, model=None, repos=None):
        self.repos = repos if repos is not None \
                     else ClonedRepoQuerySet._get_all_repos()
        self.model = model

    def get(self, *args, **kwargs):
        results = self.filter(**kwargs)
        if not results:
            raise self.model.DoesNotExist()
        return results[0]

    def __repr__(self):
        return str(self.repos)

    def __iter__(self):
        return iter(self.repos)

    def exists(self):
        return False

    def filter(self, **kwargs):
        filtered = self.repos
        for key, val in kwargs.items():
            filtered = [rep for rep in filtered if getattr(rep, key) == val]
        return ClonedRepoQuerySet(model=self.model, repos=filtered)

    def __len__(self):
        return len(self.repos)

    def __bool__(self):
        return len(self.repos)

    def __getitem__(self, index):
        return self.repos[index]

    def delete(self):
        for repo in self.repos:
            repo.delete()

    @staticmethod
    def _get_origin(full_repo_dir):
        return Repo(full_repo_dir).remotes.origin.url

    @staticmethod
    def _get_all_repos():
        from .models import ClonedRepo
        repo_dirs = (dir for dir in os.listdir(REPO_ROOT)
                                 if path.isdir(path.join(REPO_ROOT, dir)))
        repos = [ClonedRepo(name=repo_dir,
                            origin=ClonedRepoQuerySet._get_origin(
                                         path.join(REPO_ROOT, repo_dir)))
                 for repo_dir in repo_dirs]
        return repos
