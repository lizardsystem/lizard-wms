from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import logging

# import mock
from django.test import TestCase

# from lizard_wms.models import FilterPage
from lizard_wms.tests import factories


logger = logging.getLogger(__name__)


class FilterPageTest(TestCase):
    def setUp(self):
        self.filter_page = factories.FilterPageFactory.create()

    def test_smoke(self):
        self.assertTrue(self.filter_page)

    def test_title1(self):
        # Grab title from the wms source.
        self.assertEquals(self.filter_page.title, 'Display Name')

    def test_title2(self):
        # Grab title from our name attribute.
        self.filter_page.name = 'Our name'
        self.assertEquals(self.filter_page.title, 'Our name')

    def test_unicode(self):
        self.assertEquals(unicode(self.filter_page), 'Display Name')

    def test_has_admin_url(self):
        self.filter_page.slug = 'atilla'
        self.assertEquals(self.filter_page.get_absolute_url(),
                          '/page/atilla/')
