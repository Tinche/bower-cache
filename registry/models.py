from os.path import join
from shutil import rmtree

from django.conf import settings
from django.db import models

from .gitwrapper import pull_from_origin, clone_from
from .managers import ClonedRepoManager

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
    origin = models.CharField(max_length=100, null=True)

    objects = ClonedRepoManager()

    def save(self, *args, **kwargs):
        repo_root = settings.REPO_ROOT
        clone_from(self.origin, join(repo_root, self.name))

    def delete(self, *args, **kwargs):
        repo_root = settings.REPO_ROOT
        rmtree(join(repo_root, self.name))

    def pull(self):
        """Pull from the origin."""
        repo_root = settings.REPO_ROOT
        pull_from_origin(join(repo_root, self.name))

    def to_package(self):
        """Return the package representation of this repo."""
        repo_url = settings.REPO_URL
        return Package(name=self.name, url=repo_url + self.name)

    def __str__(self):
        return "%s (cloned from %s)" % (self.name, self.origin)

    class Meta(object):
        managed = False
