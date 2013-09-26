from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import mock

from django.template import Context
from django.test import TestCase
from django.template.loader import get_template

from lizard_wms.tests import factories
from lizard_wms import popup_renderers
from lizard_wms import models


class FeatureLineCreationTest(TestCase):

    text = """{"features":[{"properties":{"KDUIDENT": "KDU-Q-34096","BODEMHOOGT":-1.18000006676,"OPMERKING": "Afgeleid van (BOKBO_L + BOKBE_L) / 2","KSYIDENT": "", "OVKIDENT": "", "IWS_CATEGO": 0, "BREEDTE": 0.699999988079, "opm_breedt": "Afgeleid van KDUBREED", "OPM_kunstw": "", "Breedte_2D": 0.699999988079, "TYPE": 14, "Typering": "Duiker (boezem)", "OWAIDENT": "", "ET_Source": "", "x_start": 0.0, "y_start":0.0, "x_end": 0.0, "y_end": 0.0, "OPM_BODEMH": "", "OPM_BREED": ""}}]}"""

    @mock.patch('requests.get',
                return_value=type(str('cls'), (), {'text': text,
                                                   'status_code': 200}))
    def test_get_feature_info(self, request):
        models.WMSSource._parse_response = \
            models.WMSSource._parse_response_json
        result = models.WMSSource().get_feature_info(bbox=True)
        self.assertEqual(len(result[0].keys()), 20)
        models.WMSSource._parse_response = models.WMSSource._parse_response_gml


class FeatureLineTest(TestCase):

    def setUp(self):
        self.feature_line = factories.FeatureLineFactory.create()

    def test_smoke(self):
        self.assertTrue(self.feature_line)

    def test_render_integer(self):
        self.feature_line.render_as = popup_renderers.RENDER_INTEGER
        result = self.feature_line.as_popup_info('10.6')
        self.assertEquals(result['value'], '11')

    def test_render_integer_with_error(self):
        self.feature_line.render_as = popup_renderers.RENDER_INTEGER
        result = self.feature_line.as_popup_info('bla bla')
        self.assertEquals(result, None)

    def test_render_float1(self):
        self.feature_line.render_as = popup_renderers.RENDER_TWO_DECIMALS
        result = self.feature_line.as_popup_info('10.678')
        self.assertEquals(result['value'], '10.68')

    def test_render_float2(self):
        self.feature_line.render_as = popup_renderers.RENDER_TWO_DECIMALS
        result = self.feature_line.as_popup_info('10')
        self.assertEquals(result['value'], '10.00')

    def test_render_float_with_error(self):
        self.feature_line.render_as = popup_renderers.RENDER_TWO_DECIMALS
        result = self.feature_line.as_popup_info('bla bla')
        self.assertEquals(result, None)

    def test_render_xls_date(self):
        self.feature_line.render_as = popup_renderers.RENDER_XLS_DATE
        result = self.feature_line.as_popup_info('26658')
        expected = '1972-12-25'
        self.assertTrue(expected in result['value'])

    def test_render_xls_date_with_error(self):
        self.feature_line.render_as = popup_renderers.RENDER_XLS_DATE
        result = self.feature_line.as_popup_info('my birthday')
        self.assertEquals(result, None)

    def test_render_url(self):
        self.feature_line.render_as = popup_renderers.RENDER_URL
        result = self.feature_line.as_popup_info('http://reinout.vanrees.org')
        expected = 'href="http://reinout.vanrees.org"'
        self.assertTrue(expected in result['value'])

    def test_render_url_like(self):
        self.feature_line.render_as = popup_renderers.RENDER_URL_LIKE
        result = self.feature_line.as_popup_info('reinout.vanrees.org')
        expected = 'href="http://reinout.vanrees.org"'
        self.assertTrue(expected in result['value'])

    def test_render_url_more(self):
        self.feature_line.render_as = popup_renderers.RENDER_URL_MORE_LINK
        result = self.feature_line.as_popup_info('reinout.vanrees.org')
        expected1 = 'href="http://reinout.vanrees.org"'
        expected2 = 'Click here'
        self.assertTrue(expected1 in result['value'])
        self.assertTrue(expected2 in result['value'])

    def test_render_google_chart_error1(self):
        self.feature_line.render_as = popup_renderers.RENDER_GC_COLUMN
        result = self.feature_line.as_popup_info(None)
        expected = 'Error converting'
        self.assertTrue(expected in result['value'])

    def test_render_google_chart_error2(self):
        self.feature_line.render_as = popup_renderers.RENDER_GC_COLUMN
        result = self.feature_line.as_popup_info('')
        expected = 'Error converting'
        self.assertTrue(expected in result['value'])

    def test_functional(self):
        # Bare-bones template test to check if mark_safe works properly.
        template = get_template('lizard_wms/popup.html')
        self.feature_line.render_as = popup_renderers.RENDER_URL
        result1 = self.feature_line.as_popup_info(
            'http://reinout.vanrees.org')
        self.feature_line.render_as = popup_renderers.RENDER_IMAGE
        result2 = self.feature_line.as_popup_info(
            'http://reinout.vanrees.org/logo.png')
        context = Context({'feature_info': [result1, result2]})
        output = template.render(context)
        expected1 = '<img src'
        expected2 = '<a href'
        self.assertTrue(expected1 in output)
        self.assertTrue(expected2 in output)
