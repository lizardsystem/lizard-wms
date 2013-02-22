from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import logging

# from django.test.utils import override_settings
import mock
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

import lizard_ui
# from lizard_wms.models import FilterPage
from lizard_wms.tests import factories
from lizard_wms.views import FilterPageView


logger = logging.getLogger(__name__)


class FilterPageViewTest(TestCase):

    def setUp(self):
        self.filter_page = factories.FilterPageFactory.create()
        self.view = FilterPageView()
        self.view.kwargs = {'slug': self.filter_page.slug}

    def test_filter_page(self):
        self.assertEquals(self.view.filter_page.id, self.filter_page.id)

    def test_edit_link(self):
        self.assertTrue('admin' in self.view.edit_link)

    def test_page_title(self):
        self.filter_page.name = 'Atilla'
        self.filter_page.save()
        self.assertEquals(self.view.page_title, 'Atilla')

    def test_filters1(self):
        # Test without any GET params.
        self.view.request = mock.Mock()
        self.view.request.GET = {}
        self.assertEquals(self.view.filters, {})

    def test_filters2(self):
        # Test with GET params that are unknown.
        self.view.request = mock.Mock()
        self.view.request.GET = {'tower_4': 'Dora'}
        self.assertEquals(self.view.filters, {})

    def test_filters3(self):
        # Test with good GET params.
        self.view.request = mock.Mock()
        with mock.patch('lizard_wms.views.FilterPageView.available_filters',
                        [('CITY', 'City'),]):
            self.view.request.GET = {'CITY': 'Nieuwegein'}
            self.assertEquals(self.view.filters, {'CITY': 'Nieuwegein'})

    def test_filters4(self):
        # Test with good, but empty GET params.
        self.view.request = mock.Mock()
        with mock.patch('lizard_wms.views.FilterPageView.available_filters',
                        [('CITY', 'City'),]):
            self.view.request.GET = {'CITY': ''}
            self.assertEquals(self.view.filters, {})

    def test_values_per_dropdown(self):
        features = [
            {'city': 'Nieuwegein',
             'inhabitant': 'Reinout'},
            {'city': 'Nieuwegein',
             'inhabitant': 'Arjan'},
            {'city': 'Arnhem',
             'inhabitant': 'Remco'}]
        with mock.patch('lizard_wms.views.FilterPageView.features',
                        lambda x: features):
            self.assertEquals(
                self.view.values_per_dropdown,
                {'city': ['Arnhem', 'Nieuwegein'],
                 'inhabitant': ['Arjan', 'Reinout', 'Remco']})



class FilterPageViewFunctionalTest(TestCase):

    def setUp(self):
        self.filter_page = factories.FilterPageFactory.create()
        home = lizard_ui.models.ApplicationScreen(slug='home')
        home.save()  # We need a home screen, otherwise the breadcrumb barfs.
        self.client = Client()
        self.url = reverse('lizard_wms.filter_page',
                           kwargs={'slug': self.filter_page.slug})

    def test_url(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
