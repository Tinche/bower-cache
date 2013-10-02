from .models import Package, ClonedRepo
from .serializers import PackageSerializer
from django.http import Http404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView


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
        res = None
        try:
            local_repo = ClonedRepo.objects.get(pk=self.kwargs['name'])
            res = local_repo.to_package()
        except ClonedRepo.DoesNotExist:
            try:
                res = self.model.objects.get(name=self.kwargs['name'])
            except Package.DoesNotExist:
                raise Http404
        return res
