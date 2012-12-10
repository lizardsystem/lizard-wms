from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import factory

from django.test import TestCase


from lizard_wms.models import WMSSource


class WMSSourceFactory(factory.Factory):
    FACTORY_FOR = WMSSource
    layer_name = 'layer_name'
    display_name = 'Display Name'
    url = 'http://test.com'
    params = """{"height": "256", "width": "256",
               "styles": "", "format": "image/png", "tiled": "true",
               "transparent": "true,
               "layers": "%s" }""" % layer_name

    options = {"buffer": 0, "isBaseLayer": False, "opacity": 1}


class WMSSourceTest(TestCase):

    def test_parse_layer_workspace_acceptable(self):
        wms_source = WMSSourceFactory.build()
        factory_params = WMSSourceFactory.attributes()['params']
        self.assertEquals(wms_source.params, factory_params)
