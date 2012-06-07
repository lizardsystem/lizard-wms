"""Models for lizard_wms"""
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
import owslib.wms
import logging
import requests

from django.db import models
from django.db import transaction

from lizard_map import coordinates

# json only became available in Python 2.6. As some of our sites still use
# Python 2.5, we have to use the following workaround (ticket 2688).
try:
    import json
    json  # Pyflakes...
except ImportError:
    import simplejson as json

from lizard_maptree.models import Category
from lizard_map.models import ADAPTER_CLASS_WMS
from lizard_map.lizard_widgets import WorkspaceAcceptable


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

    xml = models.TextField(default="", blank=True)

    def __unicode__(self):
        return u'%s' % (self.title or self.slug, )

    @transaction.commit_on_success
    def fetch(self):
        """Fetches layers belonging to this WMS connection and stored
        them in the database, including all the metadata we can easily
        get at.

        Returns a set of fetched layer names."""

        if self.xml:
            xml = self.xml.encode('utf8').strip()
            wms = owslib.wms.WebMapService(self.url, xml=xml)
        else:
            wms = owslib.wms.WebMapService(self.url)

        fetched = set()

        for name, layer in wms.contents.iteritems():
            if layer.layers:
                #Meta layer, don't use
                continue

            kwargs = {'connection': self,
                      'name': name}
            layer_instance, _ = \
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

            layer_instance.import_bounding_box(layer)
            layer_instance.save()

            if layer_instance.bbox:
                layer_instance.get_feature_info()

            fetched.add(name)

        return fetched

    def delete_layers(self, keep_layers=set()):
        """Deletes layers belonging to this WMS connection of which
        the names don't occur in keep_layers."""

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

    # bbox: minx, miny, maxx, maxy in Google coordinates, separated by commas
    bbox = models.CharField(max_length=100, null=True, blank=True)

    connection = models.ForeignKey(WMSConnection, blank=True, null=True)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u'%s' % self.name

    def workspace_acceptable(self):
        return WorkspaceAcceptable(
            name=self.name,
            description=self.description,
            adapter_layer_json=json.dumps({
                    'wms_source_id': self.id,
                    'name': self.name,
                    'url': self.url,
                    'params': self.params,
                    'options': self.options}),
            adapter_name=ADAPTER_CLASS_WMS)

    def get_feature_info(self, x=None, y=None):
        """Gets feature info from the server, at point (x,y) in Google
        coordinates.

        If x, y aren't given, use this layer's bbox, if any. Useful to
        get available features immediately after fetching the layer.
        """

        if x is not None:
            # Construct the "bounding box", a tiny area around (x,y)
            # We use a tiny custom radius, because otherwise we don't have
            # enough control over which feature is returned, there is no
            # mechanism to choose the feature closest to x, y.
            radius = 10
            bbox = ','.join(str(coord)
                            for coord in
                            (x - radius, y - radius, x + radius, y + radius))
        else:
            bbox = self.bbox

        if not bbox:
            return set()

        if self.connection and self.connection.version:
            version = self.connection.version
        else:
            version = '1.1.1'

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

            'BBOX': bbox,

            # Get the value at the single pixel of a 1x1 picture
            'HEIGHT': 1,
            'WIDTH': 1,
            'X': 0,
            'Y': 0,

            # Version from parameter
            'VERSION': version,
        }

        r = requests.get(self.url, params=payload)
        logger.info("GetFeatureInfo says: " + r.text)

        # XXX Check result code etc

        if 'no features were found' in r.text:
            return dict()

        if not r.text.startswith("Results for FeatureType"):
            return dict()

        # "Parse"
        values = dict()
        for line in r.text.split("\n"):
            line = line.strip()
            parts = line.split(" = ")
            if len(parts) != 2:
                continue
            logger.info("LINE: " + line)
            logger.info(str(parts))
            feature, value = parts

            if value.startswith("[GEOMETRY"):
                # I think these are always uninteresting
                continue

            values[feature] = value

        self._store_features(values)
        return values

    def _store_features(self, values):
        """Make sure the features in the 'values' dict are stored as
        FeatureLines in the database."""

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

    def import_bounding_box(self, layer):
        """Get bounding box information from the layer; layer is an instance
        of owslib.wms.ContentMetaData."""

        logger.info("BBOX1: " + repr(layer.boundingBoxWGS84))
        logger.info("BBOX2: " + repr(layer.boundingBox))

        minx = miny = maxx = maxy = srs = None

        if layer.boundingBoxWGS84:
            minx, miny, maxx, maxy = layer.boundingBoxWGS84
            srs = 'EPSG:4326'
        else:
            minx, miny, maxx, maxy, srs = layer.boundingBox

        logger.info("SRS: " + srs)
        if srs == "ESPG:900913":
            # Yay!
            pass
        elif srs == "EPSG:28992":
            minx, miny = coordinates.rd_to_google(minx, miny)
            maxx, maxy = coordinates.rd_to_google(maxx, maxy)
        elif srs == "EPSG:4326":
            minx, miny = coordinates.wgs84_to_google(minx, miny)
            maxx, maxy = coordinates.wgs84_to_google(maxx, maxy)
        else:
            self.bbox = None
            return

        self.bbox = ",".join(str(coord) for coord in
                             (minx, miny, maxx, maxy))
        logger.info("RESULT: " + self.bbox)

    def get_feature_name(self, values):
        """
        Argument is a values dict are returned from get_feature_info().

        Return feature as a string useful for the mouse hover function
        A.k.a. the item's 'name' in Lizard.
        """
        if not values:
            return None

        parts = []
        for feature_line in (self.featureline_set.filter(in_hover=True).
                             order_by('order_using')):
            if feature_line.name in values:
                parts.append(values[feature_line.name])

        return " ".join(parts)

    def get_popup_info(self, values):
        if not values:
            return None

        info = []

        for feature_line in (self.featureline_set.filter(visible=True).
                             order_by('order_using')):
            if feature_line.name in values:
                info.append({
                        'name':
                        (feature_line.description or feature_line.name),
                        'value': values[feature_line.name],
                        'render_as': feature_line.render_as,
                        })
        return info

    @property
    def bounding_box(self):
        if self.bbox:
            return tuple(float(coord) for coord in self.bbox.split(","))
        else:
            return None


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

    # If description is given, it is used in popups instead of name
    description = models.CharField(max_length=100, null=True, blank=True)

    visible = models.BooleanField(default=True)
    use_as_id = models.BooleanField(default=False)
    render_as = models.CharField(max_length=1, choices=(
            ('T', "Tekst"),
            ('I', "Link naar een image"),
            ('U', "URL"),
            ('W', "URL-achtige tekst")), default='T')
    in_hover = models.BooleanField(default=False)
    order_using = models.IntegerField(default=1000)

    def __unicode__(self):
        return self.name
