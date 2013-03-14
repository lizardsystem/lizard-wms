from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.test import TestCase
# from django.utils import simplejson as json

from lizard_wms.tests import factories
from lizard_wms import popup_renderers


class FeatureLineTest(TestCase):

    def setUp(self):
        self.feature_line = factories.FeatureLineFactory.create()

    def test_smoke(self):
        self.assertTrue(self.feature_line)

    def test_render_url(self):
        self.feature_line.render_as = popup_renderers.RENDER_URL
        result = self.feature_line.as_popup_info('http://reinout.vanrees.org')
        self.assertEquals(result['value'], 'http://reinout.vanrees.org')

    def test_render_url_like(self):
        self.feature_line.render_as = popup_renderers.RENDER_URL_LIKE
        result = self.feature_line.as_popup_info('reinout.vanrees.org')
        self.assertEquals(result['value'], 'http://reinout.vanrees.org')
        self.assertEquals(result['link_name'], 'reinout.vanrees.org')

    def test_render_url_more(self):
        self.feature_line.render_as = popup_renderers.RENDER_URL_MORE_LINK
        result = self.feature_line.as_popup_info('reinout.vanrees.org')
        self.assertEquals(result['value'], 'http://reinout.vanrees.org')
        self.assertTrue('click here' in result['link_name'].lower())
