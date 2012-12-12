from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import factory

from django.test import TestCase
from django.utils import simplejson as json

from lizard_wms.tests.factories import WMSSourceFactory


class WMSSourceTest(TestCase):

    def test_parse_layer_workspace_acceptable(self):
        wms_source = WMSSourceFactory.build()
        factory_params = json.loads(WMSSourceFactory._params)
        factory_params['layers'] = WMSSourceFactory.attributes()['layer_name']
        params = json.loads(wms_source.params)
        self.assertEquals(params, factory_params)

    def test_empty_input_params(self):
        wms_source = WMSSourceFactory.build(_params="")
        params = json.loads(wms_source.params)
        self.assertEquals(params, {'layers': wms_source.layer_name})
