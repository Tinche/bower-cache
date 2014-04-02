"""The Admin module for the Bower Cache registry."""
import logging

from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.shortcuts import redirect, get_object_or_404

from . import bowerlib
from .models import ClonedRepo, Package
from .query import ClonedRepoQuerySet

LOG = logging.getLogger(__name__)


class ClonedRepoChangeList(ChangeList):

    def get_query_set(self, request):
        return self.root_queryset

    def get_results(self, request):
        all_repo_count = len(self.root_queryset)
        self.result_count = all_repo_count
        self.full_result_count = all_repo_count
        self.result_list = list(self.root_queryset)
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
            return super(ClonedRepoAdmin, self).get_form(request, obj, **kwargs)
        else:
            # Here we override the form for creation.
            return NewRepoForm

    def save_form(self, request, form, change):
        """Here we pluck out the data to create a new cloned repo.

           Form is an instance of NewRepoForm.
        """
        name = form.cleaned_data['name']
        origin_url = form.cleaned_data['origin_url']
        res = ClonedRepo(name=name, origin=origin_url)
        LOG.info("New repo form produced %s" % str(res))

        form.save(commit=False)
        return res

    def get_readonly_fields(self, request, obj=None):
        """Hide the origin field from editing, but not creation."""
        return ('origin',) if obj else ()

    def add_view(self, request, **kwargs):
        """A custom add_view, to catch exceptions from 'save_model'.

           Just to be clear, this is very filthy.
        """
        try:
            return super(ClonedRepoAdmin, self).add_view(request, **kwargs)
        except ValidationError:
            # Rerender the form, having messaged the user.
            return redirect(request.path)

    def save_model(self, request, obj, form, change):
        try:
            obj.save()
        except Exception as exc:
            self.message_user(request, "Save failed: %s" % str(exc),
                              level=messages.ERROR)
            raise ValidationError(str(exc))
        # A success message will be flashed by default

    def git_pull_view(self, request, repo_name):
        """Perform a git pull and redirect back to the repo."""
        LOG.info("Pull requested for %s." % repo_name)
        repo = get_object_or_404(self.model, name=repo_name)
        repo.pull()
        self.message_user(request, "Repo %s successfully updated." % repo_name,
                          level=messages.SUCCESS)
        return redirect('admin:registry_clonedrepo_change', repo_name)


class NewRepoForm(forms.ModelForm):
    """A special form for creating cloned repositories."""
    origin_url = forms.CharField(required=False)
    choices = [('upstream', 'from upstream Bower'),
               ('origin_url', 'from git repo:')]
    origin_widget = forms.RadioSelect
    origin_source = forms.ChoiceField(choices=choices, widget=origin_widget,
                                      initial=choices[0][0])

    def clean(self):
        """Validate the new repo form.

           Might perform a request to upstream Bower."""
        cleaned_data = super(NewRepoForm, self).clean()
        origin_url = cleaned_data['origin_url']
        origin_source = cleaned_data['origin_source']
        if origin_source == 'origin_url' and not origin_url:
            msg = 'Please provide an origin URL.'
            self._errors['origin_url'] = self.error_class([msg])

            del cleaned_data['origin_url']
            del cleaned_data['origin_source']
        elif origin_source == 'upstream':
            upstream = settings.UPSTREAM_BOWER_REGISTRY
            name = cleaned_data['name']
            try:
                upstream_pkg = bowerlib.get_package(upstream, name)
            except IOError as exc:
                msg = str(exc)
                self._errors['origin_source'] = self.error_class([msg])
            else:
                if not upstream_pkg:
                    msg = 'Upstream registry has no knowledge of %s.' % name
                    self._errors['name'] = self.error_class([msg])

                    del cleaned_data['name']
                else:
                    upstream_origin_url = upstream_pkg['url']
                    cleaned_data['origin_url'] = upstream_origin_url

        return cleaned_data

    class Meta:
        model = ClonedRepo
        exclude = ['origin']


admin.site.register(Package)
admin.site.register(ClonedRepo, ClonedRepoAdmin)
