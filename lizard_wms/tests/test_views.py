from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import logging

# import mock
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

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
