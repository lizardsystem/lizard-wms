from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import json
import mock

from django.test import TestCase

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
        self.assertEquals(wms_source._parse_response_json(response),
                          [])

    def test_parse_response(self):
        response = mock.Mock()
        response.status_code = 200
        response.text = """{"type":"FeatureCollection","features":[{"type":"Feature","id":"o1313_schadeperpand.45232","geometry":{"type":"MultiPolygon","coordinates":[[[[133154.267,519727.43],[133153.218,519730.56],[133253.22,519764.078],[133255.763,519756.493],[133293.689,519769.205],[133375.13,519526.229],[133341.405,519514.921],[133414.843,519295.905],[133393.511,519288.752],[133395.545,519282.684],[133365.679,519272.67],[133367.714,519266.602],[133313.766,519248.513],[133236.361,519479.361],[133238.805,519480.181],[133232.887,519497.88],[133267.185,519509.365],[133261.765,519525.509],[133260.344,519525.029],[133255.727,519538.699],[133287.255,519549.261],[133282.751,519562.707],[133216.876,519540.634],[133154.267,519727.43]]]]},"geometry_name":"the_geom","properties":{"PAND_ID":"0405100000555756","BOUWJAAR":1970,"STATUS":"Pand in gebruik","DATUM_STRT":20001122,"DATUM_EIND":20110331,"DOCUMENT":"20000738","DATUM_DOC":20001122,"ONDERZOEK":"N","INDICATIE":"N","INACTIEF":"N","WSS":0,"ET_ID":0,"Rowid_":6878,"PAND_ID_1":"0405100000555756","ZONE_CODE":37236,"COUNT":105657,"AREA":26414.3,"SUM":1.71568E7}}],"crs":{"type":"EPSG","properties":{"code":"28992"}}}"""
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response_json(response)
        self.assertEquals(len(parsed_response[0]), 18)

    def test_parse_response_json_exception(self):
        response = mock.Mock()
        response.status_code = 200
        response.text = '{"exceptions": [{"locator": "noLocator", "code": "noApplicableCode", "text": "java.text.ParseException: Invalid date: 2013-08-28T12:32:42ZAJASDFHASDFA\\nInvalid date: 2013-08-28T12:32:42ZAJASDFHASDFA"}], "version": "1.1.1"}'
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response_json(response)
        self.assertEquals(parsed_response, [])

    def test_parse_response_code_not_200(self):
        response = mock.Mock()
        response.status_code = False
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response_json(response)
        self.assertEquals(parsed_response, [])

    def test_parse_response_gml(self):
        response = mock.Mock()
        response.status_code = 200
        response.text = """<?xml version="1.0" encoding="UTF-8"?><wfs:FeatureCollection xmlns="http://www.opengis.net/wfs" xmlns:wfs="http://www.opengis.net/wfs" xmlns:deltaportaal="deltaportaal" xmlns:gml="http://www.opengis.net/gml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="deltaportaal http://geoserver6.lizard.net:80/geoserver/deltaportaal/wfs?service=WFS&amp;version=1.0.0&amp;request=DescribeFeatureType&amp;typeName=deltaportaal%3Anatte_kunstwerken http://www.opengis.net/wfs http://geoserver6.lizard.net:80/geoserver/schemas/wfs/1.0.0/WFS-basic.xsd"><gml:boundedBy><gml:null>unknown</gml:null></gml:boundedBy><gml:featureMember><deltaportaal:natte_kunstwerken fid="natte_kunstwerken.191"><deltaportaal:wkb_geometry><gml:MultiPoint srsName="http://www.opengis.net/gml/srs/epsg.xml#28992"><gml:pointMember><gml:Point><gml:coordinates xmlns:gml="http://www.opengis.net/gml" decimal="." cs="," ts=" ">194306,442485</gml:coordinates></gml:Point></gml:pointMember></gml:MultiPoint></deltaportaal:wkb_geometry><deltaportaal:gml_id>id66ecb4e6-595e-4f61-93b0-75b0a3fe5d5e</deltaportaal:gml_id><deltaportaal:objectid>191</deltaportaal:objectid><deltaportaal:kw_x>194306.0</deltaportaal:kw_x><deltaportaal:kw_y>442485.0</deltaportaal:kw_y><deltaportaal:complex_naam>Westervoortsebruggen</deltaportaal:complex_naam><deltaportaal:complex_omschrijving>Bruggen over de IJssel bij Westervoort in de provincialeweg</deltaportaal:complex_omschrijving><deltaportaal:kw_netwerk>HVWN</deltaportaal:kw_netwerk><deltaportaal:kw_code>40B-004-02</deltaportaal:kw_code><deltaportaal:kw_naam>Westervoortsebruggen (fietsbrug)</deltaportaal:kw_naam><deltaportaal:kw_omschrijving>Fietsbrug over de Geldersche IJssel</deltaportaal:kw_omschrijving><deltaportaal:kw_stichtingsjaar>1981.0</deltaportaal:kw_stichtingsjaar><deltaportaal:vervangingsjaar>2061.0</deltaportaal:vervangingsjaar><deltaportaal:vervangingsjaar_klasse>2060 - 2070</deltaportaal:vervangingsjaar_klasse><deltaportaal:kw_soort>Brug Vast</deltaportaal:kw_soort><deltaportaal:kw_soort_kaart__nat_>Brug Vast</deltaportaal:kw_soort_kaart__nat_></deltaportaal:natte_kunstwerken></gml:featureMember></wfs:FeatureCollection>"""
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response_gml(response)
        self.assertEquals(len(parsed_response[0]), 15)

    def test_parse_response_gml_exception(self):
        response = mock.Mock()
        response.status_code = 200
        response.text = """<?xml version="1.0" encoding="UTF-8" standalone="no"?><!DOCTYPE ServiceExceptionReport SYSTEM "http://geoserver6.lizard.net:80/geoserver/schemas/wms/1.1.1/WMS_exception_1_1_1.dtd"> <ServiceExceptionReport version="1.1.1" >   <ServiceException code="InvalidSRS">
      Error occurred decoding the espg code EPSG:289923
No code &quot;EPSG:289923&quot; from authority &quot;European Petroleum Survey Group&quot; found for object of type &quot;IdentifiedObject&quot;.
</ServiceException></ServiceExceptionReport>"""
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response_gml(response)
        self.assertEquals(parsed_response, [])

    def test_parse_response_arcgis_wms_xml(self):
        response = mock.Mock()
        response.status_code = 200
        response.text = """<?xml version="1.0" encoding="UTF-8"?><FeatureInfoResponse xmlns:esri_wms="http://www.esri.com/wms" xmlns="http://www.esri.com/wms"><FIELDS GEOMETRIE="Polyline" Objectcode="L_OWP_NIE_AAL_0001" Naam="Aaldoncksebeek" Opgenomenin="legger" Categorie="primair" Opnamejaar="2012" Waterbeheerder="Waterschap Peel en Maasvallei" Onderhoudsplichtige="Waterschap Peel en Maasvallei" Leggerstatus="Vastgesteld" OBJECTID="423"></FIELDS></FeatureInfoResponse>"""
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response_arcgis_wms_xml(response)
        self.assertEquals(len(parsed_response), 1)

    def test_parse_response_arcgis_wms_xml_exception(self):
        response = mock.Mock()
        response.status_code = 200
        response.text ="""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<ServiceExceptionReport version="1.3.0"  xmlns="http://www.opengis.net/ogc"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  xsi:schemaLocation="http://www.opengis.net/ogc http://schemas.opengis.net/wms/1.3.0/exceptions_1_3_0.xsd">  <ServiceException code="InvalidSRS(CRS)">Parameter 'srs(crs)' has wrong value.  </ServiceException></ServiceExceptionReport>"""
        wms_source = WMSSourceFactory.build()
        parsed_response = wms_source._parse_response_arcgis_wms_xml(response)
        self.assertEquals(parsed_response, [])
