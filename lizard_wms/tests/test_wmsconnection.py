from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import os
import factory

from django.test import TestCase


from lizard_wms.models import WMSConnection, WMSSource


class WMSConnectionFactory(factory.Factory):
    FACTORY_FOR = WMSConnection
    title = "WMS title"
    slug = "wmsslug"
    url = "http://test.com/wms"
    xml = open(os.path.join(os.path.dirname(__file__),
                            'getCapabilities.xml')).read()


class Geoserver(TestCase):

    def test_fetch(self):

        from lizard_wms import models
        models.WMSSource.import_bounding_box = lambda x, y: None
        wmsconnection = WMSConnectionFactory.create()
        result = wmsconnection.fetch(import_bounding_box=True)
        self.assertEqual(WMSSource.objects.count(), 40)
        self.assertEqual(len(result), 40)
