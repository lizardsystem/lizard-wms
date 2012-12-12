from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import os
import logging

import mock

from django.test import TestCase

from lizard_wms.models import WMSSource
from lizard_wms.tests import factories


logger = logging.getLogger(__name__)


class WMSConnectionTest(TestCase):

    @mock.patch('lizard_wms.models.WMSSource.import_bounding_box',
                return_value=None)
    def test_fetch(self, import_bounding_box):
        wmsconnection = factories.WMSConnectionFactory.create()
        result = wmsconnection.fetch()
        self.assertEqual(WMSSource.objects.count(), 40)
        self.assertEqual(len(result), 40)

    @mock.patch('lizard_wms.models.WMSSource.import_bounding_box',
        return_value=None)
    def test_fetch_after_options_change(self, import_bounding_box):
        """tests bug fix, for fix see revision f649465

        WMSSource.options were overwritten after sources reload from admin.
        This test checks that fix.

        """
        wmsconnection = factories.WMSConnectionFactory.create()
        result = wmsconnection.fetch()
        wmssource = WMSSource.objects.get(pk=1)
        default_options = '{"buffer": 0, "isBaseLayer": false, "opacity": 0.5}'
        self.assertEqual(wmssource.options, default_options)
        new_options = '{"buffer": 0, "isBaseLayer": false, "opacity": 1.0}'
        wmssource.options = new_options
        wmssource.save()
        # now fetch again
        wmsconnection.fetch()
        # and assert that the new options are still in place
        wmssource = WMSSource.objects.get(pk=1)
        self.assertEqual(wmssource.options, new_options)
