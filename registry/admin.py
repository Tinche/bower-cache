import logging

from django.core.exceptions import ValidationError
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.shortcuts import redirect, get_object_or_404

from .models import ClonedRepo, Package
from .query import ClonedRepoQuerySet

LOG = logging.getLogger(__name__)


class ClonedRepoChangeList(ChangeList):

    def get_query_set(self, request):
        return self.root_query_set

    def get_results(self, request):
        all_repo_count = len(self.root_query_set)
        self.result_count = all_repo_count
        self.full_result_count = all_repo_count
        self.result_list = list(self.root_query_set)
        self.can_show_all = True
        self.multi_page = False
        self.paginator = self.model_admin.get_paginator(request,
                                                        self.result_list,
                                                        self.list_per_page)


class ClonedRepoAdmin(admin.ModelAdmin):
    actions = None

    def get_urls(self):
        urls = super(ClonedRepoAdmin, self).get_urls()
        more_urls = patterns('',
            url(r'^(.+)/pull/$', self.admin_site.admin_view(self.git_pull_view),
                                 name='pull')
        )
        return more_urls + urls

    def queryset(self, request):
        return ClonedRepoQuerySet(model=ClonedRepo)

    def get_changelist(self, request, **kwargs):
        return ClonedRepoChangeList

    def get_form(self, request, obj=None, **kwargs):
        if obj is not None:
            return super(self, ClonedRepoAdmin)
        else:
            # Here we override the form for creation.
            return super(self, ClonedRepoAdmin)

    def get_readonly_fields(self, request, obj=None):
        """Hide the origin field from editing, but not creation."""
        return ('origin',) if obj else ()

    def add_view(self, request, **kwargs):
        """A custom add_view, to catch exceptions from 'save_model'."""
        try:
            return super(ClonedRepoAdmin, self).add_view(request, **kwargs)
        except ValidationError:
            # Rerender the form.
            return redirect(request.path)

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except Exception as exc:
            self.message_user(request, "Save failed: %s" % str(exc.message),
                              level=messages.ERROR)
            raise ValidationError(str(exc))
        else:
            self.message_user(request, "Save succeded.",
                              level=messages.SUCCESS)

    def git_pull_view(self, request, repo_name):
        """Perform a git pull and redirect back to the repo."""
        LOG.info("Pull requested for %s." % repo_name)
        repo = get_object_or_404(self.model, name=repo_name)
        repo.pull()
        self.message_user(request, "Repo %s successfully updated." % repo_name, 
                          level=messages.SUCCESS)
        return redirect('admin:registry_clonedrepo_change', repo_name) 

admin.site.register(Package)
admin.site.register(ClonedRepo, ClonedRepoAdmin)
