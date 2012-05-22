# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import owslib.wms
import logging
import requests

from django.db import models
from django.db import transaction

# json only became available in Python 2.6. As some of our sites still use
# Python 2.5, we have to use the following workaround (ticket 2688).
try:
    import json
    json  # Pyflakes...
except ImportError:
    import simplejson as json

from lizard_maptree.models import Category
from lizard_map.models import ADAPTER_CLASS_WMS


logger = logging.getLogger(__name__)


class WMSConnection(models.Model):
    """Definition of a WMS Connection."""

    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    url = models.URLField(verify_exists=False)
    version = models.CharField(max_length=20, default='1.3.0',
                               help_text=u"Version number for Lizard.")

    params = models.TextField(
        default='{"height": "256", "width": "256", "layers": "%s", '
        '"styles": "", "format": "image/png", "tiled": "true", '
        '"transparent": "true"}'
        )
    options = models.TextField(
        default='{"buffer": 0, "reproject": true, "isBaseLayer": false, '
        '"opacity": 0.5}')
    category = models.ManyToManyField(Category, null=True, blank=True)

    def __unicode__(self):
        return u'%s' % (self.title or self.slug, )

    @transaction.commit_on_success
    def fetch(self):
        """Fetches layers belonging to this WMS connection and stored
        them in the database, including all the metadata we can easily
        get at.

        Returns a set of fetched layer names."""

        wms = owslib.wms.WebMapService(self.url)

        fetched = set()

        for name, layer in wms.contents.iteritems():
            if layer.layers:
                #Meta layer, don't use
                continue

            kwargs = {'connection': self,
                      'name': name}
            layer_instance, created = \
                WMSSource.objects.get_or_create(**kwargs)

            layer_style = layer.styles.values()
            # Not all layers have a description/legend.
            if len(layer_style):
                layer_instance.description = '<img src="%s" alt="%s" />' % (
                    layer_style[0]['legend'],
                    layer_style[0]['title'])
            else:
                layer_instance.description = None

            for attribute in ('url', 'options'):
                attr_value = getattr(self, attribute)
                setattr(layer_instance, attribute, attr_value)
            layer_instance.category = self.category.all()
            layer_instance.params = self.params % layer.name
            layer_instance.save()
            fetched.add(name)

        return fetched

    def delete_layers(self, keep_layers=set()):
        """Deletes layers belonging to this WMS connection of which
        the names don't occur in the set keep_layers."""

        for layer in self.wmssource_set.all():
            if layer.name not in keep_layers:
                layer.delete()


class WMSSource(models.Model):
    """
    Definition of a wms source.
    """

    name = models.CharField(max_length=80)
    url = models.URLField(verify_exists=False)
    params = models.TextField(null=True, blank=True)  # {layers: 'basic'}
    options = models.TextField(null=True, blank=True)  # {buffer: 0}

    description = models.TextField(null=True, blank=True)
    category = models.ManyToManyField(Category, null=True, blank=True)

    connection = models.ForeignKey(WMSConnection, blank=True, null=True)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u'%s' % self.name

    def workspace_acceptable(self):
        return {'name': self.name,
                'type': 'workspace-acceptable',
                'description': self.description,
                'adapter_layer_json': json.dumps({
                    'name': self.name,
                    'url': self.url,
                    'params': self.params,
                    'options': self.options}),
                'adapter_name': ADAPTER_CLASS_WMS}

    def _get_feature_info(self, x=None, y=None):
        """Gets feature info from the server, at point (x,y) in Google coordinates."""

        # We use a tiny custom radius, because otherwise we don't have
        # enough control over which feature is returned, there is no
        # mechanism to choose the feature closest to x, y.
        radius = 10

        params = json.loads(self.params)

        payload = {
            'REQUEST': 'GetFeatureInfo',
            'EXCEPTIONS': 'application/vnd.ogc.se_xml',
            'INFO_FORMAT': 'text/plain',
            'SERVICE': 'WMS',
            'SRS': 'EPSG:900913',  # Always Google

            # Get a single feature
            'FEATURE_COUNT': 1,

            # Set the layer we want
            'LAYERS': params['layers'],
            'QUERY_LAYERS': params['layers'],

            # Construct the "bounding box", a tiny area around (x,y)
            'BBOX': ','.join(str(coord)
                             for coord in
                             (x - radius, y - radius, x + radius, y + radius)),

            # Get the value at the single pixel of a 1x1 picture
            'HEIGHT': 1,
            'WIDTH': 1,
            'X': 0,
            'Y': 0,

            # Version from parameter
            'VERSION': '1.3.0',
        }

        r = requests.get(self.url, params=payload)
        logger.info("GetFeatureInfo says: " + r.content)

        # XXX Check result code etc

        if 'no features were found' in r.content:
            return None

        # Parse
        values = dict()
        for line in r.content.split("\n"):
            line = line.strip()
            parts = line.split(" = ")
            if len(parts) != 2:
                continue
            logger.info("LINE: "+line)
            logger.info(str(parts))
            feature, value = parts
            values[feature] = value

        self._store_features(values)
        return values

    def _store_features(self, values):
        """Make sure the features in the 'values' dict are stored as FeatureLines
        in the database."""

        values = set(values)  # Copy so we can safely mutate it

        for feature_line in self.featureline_set.all():
            if feature_line.name in values:
                values.remove(feature_line.name)

        for name in values:
            # Loop over the names not removed yet
            feature_line = FeatureLine(
                wms_layer=self,
                name=name)
            feature_line.save()

    def get_feature_for_hover(self, x, y):
        """Return feature as a string useful for the mouse hover function"""
        values = self._get_feature_info(x, y)

        parts = []
        for feature_line in (self.featureline_set.filter(in_hover=True).
                             order_by('order_using')):
            if feature_line.name in values:
                parts.append(values[feature_line.name])

        return " ".join(parts)


class FeatureLine(models.Model):
    """A WMS layer has features. We want to store them in the database
    once we know about them, so that they can be edited in the admin.

    Several options should be editable:
    - Show this field in the popup or not
    - The order in which they should be shown
    - Which feature to use as a feature ID, if any
    - How to render the feature: as text? as a link to an image?
    - Which fields to show in the mouse hover function
    """

    wms_layer = models.ForeignKey(WMSSource, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)

    visible = models.BooleanField(default=True)
    use_as_id = models.BooleanField(default=False)
    render_as = models.CharField(max_length=1, choices = (
            ('T', "Tekst"),
            ('I', "Link naar een image")), default='T')
    in_hover = models.BooleanField(default=False)
    order_using = models.IntegerField(default=1000)

    def __unicode__(self):
        return self.name
