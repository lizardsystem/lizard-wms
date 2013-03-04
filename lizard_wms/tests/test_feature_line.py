from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.test import TestCase
from django.utils import simplejson as json

from lizard_wms.tests import factories


class FeatureLineTest(TestCase):

    def setUp(self):
        self.feature_line = factories.FeatureLineFactory.create()

    def test_smoke(self):
        self.assertTrue(self.feature_line)
