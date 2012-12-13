from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import logging

import mock

from django.test import TestCase

from lizard_wms.models import WMSSource
from lizard_wms.tests import factories


logger = logging.getLogger(__name__)


class WMSConnectionTest(TestCase):

    @mock.patch('lizard_wms.models.WMSSource.import_bounding_box',
                return_value=None)
    def setUp(self, import_bounding_box):
        self.wmsconnection = factories.WMSConnectionFactory.create()
        self.result = self.wmsconnection.fetch()

    def test_fetch(self):
        self.assertEqual(WMSSource.objects.count(), 40)
        self.assertEqual(len(self.result), 40)

    @mock.patch('lizard_wms.models.WMSSource.import_bounding_box',
                return_value=None)
    def test_options_change_are_kept_between_fetch(self, import_bounding_box):
        """tests bug fix, for fix see revision f649465

        WMSSource.options were overwritten after sources reload from admin.
        This test checks that fix.

        """

        # Stage
        new_options = '{"buffer": 0, "isBaseLayer": false, "opacity": 1.0}'
        WMSSource.objects.filter(pk=1).update(options=new_options)

        # Create
        self.wmsconnection.fetch()

        # Check
        wmssource = WMSSource.objects.get(pk=1)
        self.assertEqual(wmssource.options, new_options)
