from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import factory

from django.test import TestCase
from django.utils import simplejson as json


from lizard_wms.models import WMSSource


class WMSSourceFactory(factory.Factory):
    FACTORY_FOR = WMSSource
    layer_name = 'layer_name'
    display_name = 'Display Name'
    url = 'http://test.com'
    _params = ('{"height": "256", "width": "256",'
               '"styles": "", "format": "image/png", "tiled": "true",'
               '"transparent": true,'
               '"layers": "%s" }' % layer_name)

    options = {"buffer": 0, "isBaseLayer": False, "opacity": 1}

    @classmethod
    def _prepare(cls, create, **kwargs):
        wms_source = super(WMSSourceFactory, cls)._prepare(create, **kwargs)
        wms_source._params = cls._params
        if create:
                wms_source.save()
        return wms_source


class WMSSourceTest(TestCase):

    def test_parse_layer_workspace_acceptable(self):
        wms_source = WMSSourceFactory.build()
        factory_params = json.loads(WMSSourceFactory._params)
        factory_params['layers'] = WMSSourceFactory.attributes()['layer_name']
        self.assertEquals(wms_source.params, factory_params)
