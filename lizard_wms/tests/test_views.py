from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import logging

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
# import mock

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

    def test_url(self):
        client = Client()
        url = reverse('lizard_wms.filter_page',
                      kwargs={'slug': self.filter_page.slug})
        response = client.get(url)
        self.assertEquals(response.status_code, 200)
