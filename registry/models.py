from os.path import join
from shutil import rmtree

from django.db import models
from django.db.models.base import ModelBase
from git.repo.base import Repo

from .gitwrapper import pull_from_origin
from .managers import ClonedRepoManager
from .settings import REPO_ROOT, REPO_URL

import logging

logger = logging.getLogger(__name__)

class Package(models.Model):
    """A Bower package, known to the registry but not hosted by it."""
    name = models.CharField(max_length=500, db_index=True, unique=True)
    url = models.CharField(max_length=500, unique=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta(object):
        unique_together = ('name', 'url')


class ClonedRepo(models.Model):
    """A cloned Bower package git repository, local to the system."""
    name = models.CharField(max_length=50, primary_key=True)
    origin = models.CharField(max_length=100)

    objects = ClonedRepoManager()

    def save(self, *args, **kwargs):
        repo = Repo.clone_from(self.origin, join(REPO_ROOT, self.name))

    def delete(self, *args, **kwargs):
        rmtree(join(REPO_ROOT, self.name))

    def pull(self):
        """Pull from the origin."""
        pull_from_origin(join(REPO_ROOT, self.name))

    def to_package(self):
        """Return the package representation of this repo."""
        return Package(name=self.name, url=REPO_URL + self.name)

    def __str__(self):
        return "%s (cloned from [%s])" % (self.name, self.origin)

    class Meta(object):
        managed = False
