import json

import mock
from mock import MagicMock

from registry.models import Package

from django.conf import settings
from django.test.utils import override_settings
from django.test import TestCase
from django.core.urlresolvers import reverse


@override_settings(DATABASES=
        {'default': {'ENGINE': 'django.db.backends.sqlite3', 
                     'NAME': '.test_db'}})
class PackagesListViewTests(TestCase):

    def test_returns_list_of_packages(self):
        Package.objects.create(name="ember", url="/foo")
        Package.objects.create(name="moment", url="/bar")
        url = reverse("list")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        results = json.loads(response.content)
        self.assertEqual(2, len(results))
        self.assertEqual(results[0]['url'], '/foo')
        self.assertEqual(results[0]['name'], 'ember')
        self.assertEqual(results[1]['url'], '/bar')
        self.assertEqual(results[1]['name'], 'moment')


class PackagesFindViewTests(TestCase):

    def test_returns_package_by_name(self):
        Package.objects.create(name="ember", url="/foo")
        url = reverse("find", kwargs={'name': 'ember'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content)
        self.assertEqual(result['url'], '/foo')
        self.assertEqual(result['name'], 'ember')

    @mock.patch('registry.bowerlib.get_package')
    def test_returns_404_when_package_name_not_found(self, get_package):
        # Mock the bowerlib.get_package method to avoid I/O
        # We pretend Bower has never heard of 'wat'
        get_package.return_value = None

        Package.objects.create(name="ember", url="/foo")
        url = reverse("find", kwargs={'name': 'wat'})

        response = self.client.get(url)

        self.assertEqual(404, response.status_code)
        upstream = settings.UPSTREAM_BOWER_REGISTRY
        get_package.assert_called_once_with(upstream, 'wat')

    @mock.patch('registry.tasks.clone_repo')
    @mock.patch('registry.bowerlib.get_package')
    def test_returns_503_when_package_name_not_found(self, get_package, clone):
        """Test the find API when we have to fetch from upstream."""
        from registry.tasks import TimeoutError
        # Mock the bowerlib.get_package method to avoid I/O
        # We pretend Bower knows what 'wat' is and a task has been dispatched
        # to clone it.
        get_package.return_value = {'name': 'wat', 'url': 'git://a-url.git'}

        # Mock the clone_repo task dispatch; throw an exception so we don't
        # wait.
        task = MagicMock()
        clone.delay.return_value = task
        task.get.side_effect = TimeoutError()

        Package.objects.create(name="ember", url="/foo")
        url = reverse("find", kwargs={'name': 'wat'})

        response = self.client.get(url)

        self.assertEqual(503, response.status_code)

        upstream = settings.UPSTREAM_BOWER_REGISTRY
        get_package.assert_called_once_with(upstream, 'wat')

        clone.delay.assert_called_once_with('wat', 'git://a-url.git')

    def test_returns_package_when_name_includes_hyphen(self):
        Package.objects.create(name="ember-data", url="/foo")
        url = reverse("find", kwargs={'name': 'ember-data'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        result = json.loads(response.content)
        self.assertEqual(result['url'], '/foo')
        self.assertEqual(result['name'], 'ember-data')


class PackagesSearchViewTests(TestCase):

    def test_returns_list_of_packages_when_search_finds_match(self):
        Package.objects.create(name="ember", url="/foo")
        url = reverse("search", kwargs={'name': 'mbe'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        results = json.loads(response.content)
        self.assertEqual(1, len(results))
        self.assertEqual(results[0]['url'], '/foo')
        self.assertEqual(results[0]['name'], 'ember')

    def test_returns_empty_list_when_search_finds_no_match(self):
        Package.objects.create(name="ember", url="/foo")
        url = reverse("search", kwargs={'name': 'wat'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('[]', response.content)

    def test_returns_list_of_packages_when_name_includes_hyphen(self):
        Package.objects.create(name="ember-data", url="/foo")
        url = reverse("search", kwargs={'name': 'ember-da'})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        results = json.loads(response.content)
        self.assertEqual(1, len(results))
        self.assertEqual(results[0]['url'], '/foo')
        self.assertEqual(results[0]['name'], 'ember-data')
