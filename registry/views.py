"""REST API views."""
import logging

from django.http import Http404
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import (ListAPIView, ListCreateAPIView,
                                     RetrieveAPIView)

from .models import Package, ClonedRepo
from .serializers import PackageSerializer
from . import bowerlib, tasks

LOG = logging.getLogger(__name__)


class ServiceUnavailable(APIException):
    """Short-circuit a view and just return the status code."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Try again later"


class PackagesListView(ListCreateAPIView):
    model = Package


class PackagesSearchView(ListAPIView):
    model = Package

    def get_queryset(self):
        search = self.kwargs['name']
        return self.model.objects.filter(name__icontains=search)


class PackagesRetrieveView(RetrieveAPIView):
    model = Package
    serializer_class = PackageSerializer

    def get_object(self):
        pkg_name = self.kwargs['name']
        LOG.info("Get request for package %s." % pkg_name)
        try:
            local_repo = ClonedRepo.objects.get(pk=pkg_name)
            return local_repo.to_package()
        except ClonedRepo.DoesNotExist:
            pass

        try:
            return self.model.objects.get(name=pkg_name)
        except Package.DoesNotExist:
            pass

        return PackagesRetrieveView.clone_from_upstream(pkg_name)

    @staticmethod
    def clone_from_upstream(pkg_name):
        """Clone a non-existent package using the upstream registry."""
        msg = "Spawning a cloning task for %s from upstream due to API req."
        LOG.info(msg % pkg_name)

        upstream_url = settings.UPSTREAM_BOWER_REGISTRY
        upstream_pkg = bowerlib.get_package(upstream_url, pkg_name)

        if upstream_pkg is None:
            raise Http404

        task = tasks.clone_repo.delay(pkg_name, upstream_pkg['url'])
        try:
            result = task.get(timeout=5)
        except tasks.TimeoutError:
            # Not done yet. What to return?
            raise ServiceUnavailable

        return result.to_package()
