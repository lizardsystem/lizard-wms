"""Models for lizard_wms"""
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import print_function
from __future__ import unicode_literals
from urllib import urlencode
import cgi
import json
import logging

import owslib.wms
import requests

from django.db import models
from django.db import transaction
from django.template.defaultfilters import urlizetrunc
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONField
from lizard_map import coordinates
from lizard_map.lizard_widgets import WorkspaceAcceptable
from lizard_map.models import ADAPTER_CLASS_WMS
from lizard_maptree.models import Category

from lizard_wms.chart import google_column_chart_url

FIXED_WMS_API_VERSION = '1.1.1'
WMS_TIMEOUT = 10
#FIXED_WMS_API_VERSION = '1.3.0'
RENDER_NONE = ''
RENDER_TEXT = 'T'
RENDER_IMAGE = 'I'
RENDER_URL = 'U'
RENDER_URL_LIKE = 'W'
RENDER_GC_COLUMN = 'C'


logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    pass


def timeout(func, args=(), kwargs={}, timeout_duration=45, default=None):
    """This function will spawn a thread and run the given function
    using the args, kwargs and return the given default value if the
    timeout_duration is exceeded.
    """
    import threading

    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = default

        def run(self):
            self.result = func(*args, **kwargs)

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
        raise TimeoutException("Timeout of %s s expired calling %s " %
                               (timeout_duration, func.__name__))
    return it.result


def capabilities_url(url):
    """Return the capabilities URL.

    Copy/pasted mostly from owslib/wms.py. Only used in the admin for
    debugging purposes.

    """
    qs = []
    if url.find('?') != -1:
        qs = cgi.parse_qsl(url.split('?')[1])

    params = [x[0] for x in qs]

    if 'service' not in params:
        qs.append(('service', 'WMS'))
    if 'request' not in params:
        qs.append(('request', 'GetCapabilities'))
    if 'version' not in params:
        qs.append(('version', FIXED_WMS_API_VERSION))

    urlqs = urlencode(tuple(qs))
    return url.split('?')[0] + '?' + urlqs


class WMSConnection(models.Model):
    """Definition of a WMS Connection."""

    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    url = models.URLField(verify_exists=False)
    version = models.CharField(
        max_length=20,
        default='1.3.0',
        help_text=(
            u"Version number for WMS service. Not used. 1.1.1 is used " +
            u"because owslib can only handle 1.1.1."))

    params = models.TextField(
        default='{"height": "256", "width": "256", "layers": "%s", '
        '"styles": "", "format": "image/png", "tiled": "true", '
        '"transparent": "true"}')
    options = models.TextField(
        default='{"buffer": 0, "isBaseLayer": false, '
        '"opacity": 0.5}')
    category = models.ManyToManyField(Category, null=True, blank=True)
    xml = models.TextField(
        default="",
        blank=True,
        help_text="""Normally, leave this empty. If filled, this xml is used
instead of the xml from the WMS server. So use it only for temp repairs or
overwrites.""")

    def __unicode__(self):
        return self.title or self.slug

    @transaction.commit_on_success
    def fetch(self):
        """Fetches layers belonging to this WMS connection and stored
        them in the database, including all the metadata we can easily
        get at.

        Returns a set of fetched layer names."""

        wms_kwargs = {'version': FIXED_WMS_API_VERSION}
        if self.xml:
            wms_kwargs['xml'] = self.xml.encode('utf8').strip()

        wms = owslib.wms.WebMapService(self.url, **wms_kwargs)

        fetched = set()
        for name, layer in wms.contents.iteritems():
            try:
                logger.debug("Fetching layer name %s" % (name,))
                if layer.layers:
                    # Meta layer, don't use
                    continue
                name = name.split(':', 1)[-1]
                # ^^^ owslib prepends with 'workspace:'.
                layer_instance, created = WMSSource.objects.get_or_create(
                    connection=self, layer_name=name)
                if created:
                    layer_instance.display_name = layer.title

                layer_style = layer.styles.values()
                # Not all layers have a description/legend.
                if len(layer_style):
                    layer_instance.description = layer_style[0]['title']
                    layer_instance.legend_url = layer_style[0]['legend']
                else:
                    layer_instance.description = None
                    layer_instance.legend_url = None

                layer_instance.url = self.url
                layer_instance.options = self.options
                layer_instance.category = self.category.all()
                layer_instance._params = self.params % layer.name
                layer_instance.import_bounding_box(layer)
            except:
                logger.exception("Something went wrong. We skip this layer")

            else:
                layer_instance.save()

                if layer_instance.bbox:
                    layer_instance.get_feature_info()

                fetched.add(name)

        return fetched

    def delete_layers(self, keep_layers=frozenset()):
        """Deletes layers belonging to this WMS connection of which
        the names don't occur in keep_layers."""
        num_deleted = 0
        for layer in self.wmssource_set.all():
            if layer.layer_name not in keep_layers:
                layer.delete()
                num_deleted += 1
        return num_deleted

    def capabilities_url(self):
        return capabilities_url(self.url)


class WMSSource(models.Model):
    """
    Definition of a wms source.
    """

    layer_name = models.CharField(max_length=80)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(verify_exists=False)
    _params = models.TextField(null=True, blank=True, db_column='params')
    options = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    metadata = JSONField(
        help_text=_('''Key/value metadata for for instance copyright.
It should be a dictionary, so surround it with braces and use double quotes,
like {"key": "value", "key2": "value2"}.
'''),
        null=True,
        blank=True)

    legend_url = models.CharField(null=True, blank=True, max_length=2048)
    category = models.ManyToManyField(Category, null=True, blank=True)

    # bbox: minx, miny, maxx, maxy in Google coordinates, separated by commas
    bbox = models.CharField(max_length=100, null=True, blank=True)

    connection = models.ForeignKey(WMSConnection, blank=True, null=True)

    show_legend = models.BooleanField(
        verbose_name=_('show legend'),
        help_text=_("Uncheck it if you want to hide the legend."),
        default=True)
    enable_search = models.BooleanField(
        verbose_name=_('enable search'),
        help_text=_(
            "Uncheck it if you don't want a click on the map to search us."),
        default=True)
    index = models.IntegerField(
        verbose_name=_('index'), default=1000,
        help_text=_("Number used for ordering categories relative to each "
                    "other."))

    class Meta:
        ordering = ('index', 'display_name')

    def __unicode__(self):
        return 'WMS Layer {}'.format(self.layer_name)

    @property
    def params(self):
        return self._params

    def update_bounding_box(self, force=False):
        if force or not self.bbox:
            try:
                wms = timeout(owslib.wms.WebMapService,
                              (self.url, FIXED_WMS_API_VERSION),
                              timeout_duration=WMS_TIMEOUT)
                params = json.loads(self.params)
                for name, layer in wms.contents.iteritems():
                    if layer.name == params['layers']:
                        self.import_bounding_box(layer)
                        return True
                logger.warn(u"Layer %s not found." % params['layers'])
            except Exception, e:
                msg = ("Something went wrong when updating %s. " +
                       "Look at %s directly. %s")
                msg = msg % (self.layer_name,
                             self.capabilities_url(),
                             e)
                logger.exception(msg)
        return False

    def workspace_acceptable(self):
        django_cql_filters = self.featureline_set.all().values_list('name',
                                                                    flat=True)
        # A ValuesListQuerySet is not serializable to JSON,
        # A list is.
        description = self.description or ''
        # TODO: Do it with a template instead of hacked string tags.
        if self.metadata:
            description += '<dl>'
            for key, value in self.metadata_for_display:
                description += '<dt>%s</dt><dd>%s</dd>' % (
                    key, urlizetrunc(value, 35))
            description += '</dl>'
        cql_filters = list(django_cql_filters)
        result = WorkspaceAcceptable(
            name=self.display_name,
            description=description,
            adapter_layer_json=json.dumps(
                {'wms_source_id': self.id,
                 'name': self.layer_name,
                 'url': self.url,
                 'params': self.params,
                 'legend_url': self.legend_url,
                 'options': self.options,
                 'cql_filters': cql_filters,
                 }),
            adapter_name=ADAPTER_CLASS_WMS)
        return result

    def capabilities_url(self):
        return capabilities_url(self.url)

    def get_feature_info(self, x=None, y=None, radius=None):
        """Gets feature info from the server, at point (x,y) in Google
        coordinates.

        If x, y aren't given, use this layer's bbox, if any. Useful to
        get available features immediately after fetching the layer.
        """

        if x is not None:
            # Construct the "bounding box", a tiny area around (x,y) We use a
            # tiny custom radius, because otherwise we don't have enough
            # control over which feature is returned, there is no mechanism to
            # choose the feature closest to x, y.
            if radius is not None:
                # Adjust the estimated "radius" of an icon on the map.
                radius /= 50
                # Convert to wgs84, which is the only supported format for
                # pyproj.geodesic
                lon, lat = coordinates.google_to_wgs84(x, y)
                # Translate center coordinates to lower left and upper right.
                # Only supports wgs84.
                # Note: 180 + 45 = 225 = bbox lower left.
                geod_bbox = coordinates.translate_coords(
                    [lon] * 2, [lat] * 2, [225, 45], [radius] * 2)
                # Convert back to web mercator.
                ll = coordinates.wgs84_to_google(geod_bbox[0][0],
                                                 geod_bbox[1][0])
                ur = coordinates.wgs84_to_google(geod_bbox[0][1],
                                                 geod_bbox[1][1])
                # Format should be: minX, minY, maxX, maxY.
                bbox = '{},{},{},{}'.format(ll[0], ll[1], ur[0], ur[1])
            else:
                # Use the old method.
                fixed_radius = 10
                bbox = '{},{},{},{}'.format(x - fixed_radius, y - fixed_radius,
                                            x + fixed_radius, y + fixed_radius)
        else:
            bbox = self.bbox

        if not bbox:
            return set()

        if self.connection and self.connection.version:
            version = self.connection.version
        else:
            version = '1.1.1'

        params = json.loads(self.params)
        values = dict()
        for layer in params['layers'].split(","):
            payload = {
                'REQUEST': 'GetFeatureInfo',
                'EXCEPTIONS': 'application/vnd.ogc.se_xml',
                'INFO_FORMAT': 'text/plain',
                'SERVICE': 'WMS',
                'SRS': 'EPSG:3857',  # Always Google (web mercator)

                # Get a single feature
                'FEATURE_COUNT': 1,

                # Set the layer we want
                'LAYERS': layer,
                'QUERY_LAYERS': layer,

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
            #logger.info("GetFeatureInfo says: " + r.text)

            # XXX Check result code etc

            if 'no features were found' in r.text:
                continue

            if not r.text.startswith("Results for FeatureType"):
                continue

            # "Parse"
            for line in r.text.split("\n"):
                line = line.strip()
                parts = line.split(" = ")
                if len(parts) != 2:
                    continue
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
            return

        info = []

        for feature_line in (self.featureline_set.filter(visible=True).
                             order_by('order_using')):
            if feature_line.name in values:
                if feature_line.render_as == RENDER_GC_COLUMN:
                    data = json.loads(values[feature_line.name])
                    url = google_column_chart_url(data)
                    values[feature_line.name] = url
                    if url == '':
                        feature_line.render_as = RENDER_NONE
                    else:
                        feature_line.render_as = RENDER_IMAGE
                    feature_line.show_label = 'false'
                else:
                    feature_line.show_label = 'true'
                info.append(
                    {'name': (feature_line.description or feature_line.name),
                     'value': values[feature_line.name],
                     'render_as': feature_line.render_as,
                     'show_label': feature_line.show_label,
                     })
        return info

    @property
    def bounding_box(self):
        if self.bbox:
            return tuple(float(coord) for coord in self.bbox.split(","))

    @property
    def name(self):
        return self.display_name or self.layer_name

    @property
    def metadata_for_display(self):
        """Return list of key/value metadata tuples.

        We store the metadata as a dict, so the keys need sorting.
        """
        if not self.metadata:
            return
        keys = sorted(self.metadata.keys())
        result = [(key, self.metadata[key]) for key in keys]
        return result


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
    description = models.CharField(max_length=200, null=True, blank=True)

    visible = models.BooleanField(default=True)
    use_as_id = models.BooleanField(default=False)
    render_as = models.CharField(
        max_length=1, choices=(
            (RENDER_TEXT, "Tekst"),
            (RENDER_IMAGE, "Link naar een image"),
            (RENDER_URL, "URL"),
            (RENDER_URL_LIKE, "URL-achtige tekst"),
            (RENDER_GC_COLUMN, "Google column chart")), default=RENDER_TEXT)
    in_hover = models.BooleanField(default=False)
    order_using = models.IntegerField(default=1000)

    def __unicode__(self):
        return self.name
