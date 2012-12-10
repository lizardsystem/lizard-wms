from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import os
import factory

import mock

from django.test import TestCase

from lizard_wms import models


class WMSConnectionFactory(factory.Factory):
    FACTORY_FOR = models.WMSConnection
    title = "WMS title"
    slug = "wmsslug"
    url = "http://test.com/wms"
    xml = open(os.path.join(os.path.dirname(__file__),
                            'getCapabilities.xml')).read()


class Geoserver(TestCase):

    @mock.patch('lizard_wms.models.WMSSource.import_bounding_box')
    def test_fetch(self, import_bounding_box):
        import_bounding_box.return_value = None

        wmsconnection = WMSConnectionFactory.create()
        result = wmsconnection.fetch()
        self.assertEqual(models.WMSSource.objects.count(), 40)
        self.assertEqual(len(result), 40)
