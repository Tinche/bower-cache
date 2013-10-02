from django.conf.urls import patterns, include, url
from .views import PackagesListView, PackagesRetrieveView, PackagesSearchView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^packages/$', PackagesListView.as_view(), name='list'),
    url(r'^packages/(?P<name>[-\w]+)/$', PackagesRetrieveView.as_view(), name='find'),
    url(r'^packages/search/(?P<name>[-\w]+)/$', PackagesSearchView.as_view(), name='search'),
    url(r'^admin/', include(admin.site.urls)),
)
