import os

import factory

from lizard_wms import models


class WMSConnectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.WMSConnection

    title = "WMS title"
    slug = "wmsslug"
    url = "http://test.com/wms"
    xml = open(os.path.join(os.path.dirname(__file__),
                            'getCapabilities.xml')).read()


class WMSSourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.WMSSource

    layer_name = 'layer_name'
    display_name = 'Display Name'
    url = 'http://test.com'
    _params = ('{"height": "256", "width": "256",'
               '"styles": "", "format": "image/png", "tiled": "true",'
               '"transparent": true,'
               '"layers": "%s" }' % layer_name)

    options = '{"buffer": 0, "isBaseLayer": false, "opacity": 1}'

    @classmethod
    def _prepare(cls, create, **kwargs):
        wms_source = super(WMSSourceFactory, cls)._prepare(create, **kwargs)
        wms_source._params = kwargs.get('_params', cls._params)
        if create:
            wms_source.save()
        return wms_source


class FeatureLineFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FeatureLine

    wms_layer = factory.SubFactory(WMSSourceFactory)


class FilterPageFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FilterPage

    wms_source = factory.SubFactory(WMSSourceFactory)
    slug = factory.Sequence(lambda n: 'page{0}'.format(n))
