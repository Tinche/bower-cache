from django.db import models

from .query import ClonedRepoQuerySet

class ClonedRepoManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        from .models import ClonedRepo
        return ClonedRepoQuerySet(model=ClonedRepo)
