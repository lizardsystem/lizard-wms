# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase
from django.test.client import Client


class IntegrationTest(TestCase):
    fixtures = ['lizard_wms']

    def test_homepage(self):
        c = Client()
        url = '/'
        response = c.get(url)
        self.assertEquals(response.status_code, 200)
