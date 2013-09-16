from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import mock

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

    def test_parse_empty_response(self):
        response = mock.Mock()
        response.text = """{"type":"FeatureCollection","features":[]}"""

        wms_source = WMSSourceFactory.build()
        self.assertEquals(wms_source._parse_response(response),
                          [])

    def test_parse_response(self):
        response = mock.Mock()
        response.status_code = 200
        response.text = """{"type":"FeatureCollection","features":[{"type":"Feature","id":"o1313_schadeperpand.45232","geometry":{"type":"MultiPolygon","coordinates":[[[[133154.267,519727.43],[133153.218,519730.56],[133253.22,519764.078],[133255.763,519756.493],[133293.689,519769.205],[133375.13,519526.229],[133341.405,519514.921],[133414.843,519295.905],[133393.511,519288.752],[133395.545,519282.684],[133365.679,519272.67],[133367.714,519266.602],[133313.766,519248.513],[133236.361,519479.361],[133238.805,519480.181],[133232.887,519497.88],[133267.185,519509.365],[133261.765,519525.509],[133260.344,519525.029],[133255.727,519538.699],[133287.255,519549.261],[133282.751,519562.707],[133216.876,519540.634],[133154.267,519727.43]]]]},"geometry_name":"the_geom","properties":{"PAND_ID":"0405100000555756","BOUWJAAR":1970,"STATUS":"Pand in gebruik","DATUM_STRT":20001122,"DATUM_EIND":20110331,"DOCUMENT":"20000738","DATUM_DOC":20001122,"ONDERZOEK":"N","INDICATIE":"N","INACTIEF":"N","WSS":0,"ET_ID":0,"Rowid_":6878,"PAND_ID_1":"0405100000555756","ZONE_CODE":37236,"COUNT":105657,"AREA":26414.3,"SUM":1.71568E7}}],"crs":{"type":"EPSG","properties":{"code":"28992"}}}"""
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response(response)
        self.assertEquals(len(parsed_response[0]), 18)

    def test_parse_response_exception(self):
        response = mock.Mock()
        response.status_code = 200
        response.text = '{"exceptions": [{"locator": "noLocator", "code": "noApplicableCode", "text": "java.text.ParseException: Invalid date: 2013-08-28T12:32:42ZAJASDFHASDFA\\nInvalid date: 2013-08-28T12:32:42ZAJASDFHASDFA"}], "version": "1.1.1"}'
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response(response)
        self.assertEquals(parsed_response, [])

    def test_parse_response_code_not_200(self):
        response = mock.Mock()
        response.status_code = False
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response(response)
        self.assertEquals(parsed_response, [])
