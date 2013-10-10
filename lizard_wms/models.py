"""Models for lizard_wms"""
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from __future__ import print_function
from __future__ import unicode_literals
from urllib import urlencode
import cgi
import json
import logging
import tls
import socket

from xml.etree import ElementTree

from lizard_wms.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db import transaction
from django.template.defaultfilters import urlizetrunc
from django.utils.html import escapejs
from django.utils.translation import ugettext_lazy as _

from jsonfield.fields import JSONField

from lizard_map import coordinates
from lizard_map.models import ADAPTER_CLASS_WMS
from lizard_map.views import get_view_state
from lizard_maptree.models import Category

import owslib.wms
import requests

from lizard_security.manager import FilteredManager
from lizard_security.models import DataSet

from lizard_wms.widgets import WmsWorkspaceAcceptable
from lizard_wms import popup_renderers

FIXED_WMS_API_VERSION = '1.1.1'
WMS_TIMEOUT = 10
#FIXED_WMS_API_VERSION = '1.3.0'

WMS_PARAMS_DEFAULT = ('{"height": "256", "width": "256", '
                      '"styles": "", "format": "image/png", "tiled": "true", '
                      '"transparent": "true"}')
WMS_OPTIONS_DEFAULT = '''{"buffer": 0, "isBaseLayer": false, "opacity": 0.5}'''


logger = logging.getLogger(__name__)


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

    title = models.CharField(
        verbose_name=_("title"),
        max_length=100)
    slug = models.CharField(
        verbose_name=_("slug"),
        max_length=100)
    url = models.URLField(verbose_name=_("URL"))
    version = models.CharField(
        verbose_name=_("version"),
        max_length=20,
        default='1.3.0',
        help_text=_(
            "Version number for WMS service. Not used. 1.1.1 is used "
            "because owslib can only handle 1.1.1."))

    params = models.TextField(default=WMS_PARAMS_DEFAULT)
    options = models.TextField(default=WMS_OPTIONS_DEFAULT)
    category = models.ManyToManyField(Category, null=True, blank=True)
    xml = models.TextField(
        default="",
        blank=True,
        help_text="""Normally, leave this empty. If filled, this xml is used
instead of the xml from the WMS server. So use it only for temp repairs or
overwrites.""")

    def __unicode__(self):
        return self.title or self.slug

    class Meta:
        verbose_name = _("WMS connection")
        verbose_name_plural = _("WMS connections")

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
            logger.debug("Fetching layer name %s" % (name,))
            if layer.layers:
                # Meta layer, don't use
                continue

            defaults = {
                'url': self.url,
                'options': self.options,
                '_params': self.params,
                'display_name': layer.title,
                'description': None,
                'legend_url': None
            }
            layer_style = layer.styles.values()
            if len(layer_style):
                defaults['description'] = layer_style[0]['title']
                defaults['legend_url'] = layer_style[0]['legend']

            layer_instance, created = WMSSource.objects.get_or_create(
                connection=self, layer_name=name, defaults=defaults)
            if created:
                layer_instance.category = self.category.all()
            layer_instance.timepositions = layer.timepositions
            layer_instance.import_bounding_box(layer)
            layer_instance.save()

            if layer_instance.bbox:
                layer_instance.search_one_item()

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

    supports_object_permissions = True
    data_set = models.ForeignKey(DataSet, null=True, blank=True)
    objects = FilteredManager()

    _params = JSONField(
        null=True, blank=True,
        default=WMS_PARAMS_DEFAULT)
    # ^^^ special db_column name
    options = models.TextField(
        null=True, blank=True,
        default=WMS_OPTIONS_DEFAULT)

    layer_name = models.TextField(verbose_name=_("layer name"))
    display_name = models.CharField(
        verbose_name=_("display name"), max_length=255, null=True, blank=True)
    url = models.URLField(verbose_name=_("URL"))
    _params = JSONField(null=True, blank=True)
    # ^^^ special db_column name
    options = models.TextField(null=True, blank=True)
    description = models.TextField(verbose_name=_("description"),
                                   null=True, blank=True)
    metadata = JSONField(
        verbose_name=_("metadata"),
        help_text=_('''Key/value metadata for for instance copyright.
It should be a dictionary, so surround it with braces and use double quotes,
like {"key": "value", "key2": "value2"}.
'''),
        null=True,
        blank=True)

    legend_url = models.CharField(
        verbose_name=_("legend URL"), null=True, blank=True, max_length=2048)
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
    timepositions = models.CharField(
        verbose_name=_("Time positions"), null=True, blank=True, max_length=2048)

    class Meta:
        ordering = ('index', 'display_name')
        verbose_name = _("WMS source")
        verbose_name_plural = _("WMS sources")

    def __unicode__(self):
        return 'WMS Layer {0}'.format(self.layer_name)

    @property
    def filter_page_url(self):
        """Return url of a filter page that links to us.

        Note that, if multiple, we just grab the first one.
        """
        try:
            return self.filter_pages.all()[0].get_absolute_url()
        except IndexError:
            # Grmbl, this won't be good for performance.
            return

    def _proxify(self, url):
        if url is None:
            return None

        proxied_wms_servers = settings.WMS_PROXIED_WMS_SERVERS
        for proxied_domain in proxied_wms_servers:
            if proxied_domain in url:
                return url.replace(
                    proxied_domain,
                    reverse('lizard_wms.wms_proxy', kwargs={
                            'wms_source_id': self.id}))
        return url

    @property
    def proxied_url(self):
        return self._proxify(self.url)

    @property
    def proxied_legend_url(self):
        return self._proxify(self.legend_url)

    @property
    def params(self):
        params = {}
        if self._params is not None:
            params = self._params.copy()
        params['layers'] = self.layer_name
        if 'cql_filter' in params:
            params['cql_filter'] = escapejs(params['cql_filter'])
        return json.dumps(params)

    def update_bounding_box(self, force=False):
        if force or not self.bbox:
            try:
                orig_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(WMS_TIMEOUT)
                wms = owslib.wms.WebMapService(
                    self.url,
                    version=FIXED_WMS_API_VERSION)
                socket.setdefaulttimeout(orig_timeout)

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
        allowed_cql_filters = self.featureline_set.filter(
            visible=True).values_list('name', flat=True)
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
        result = WmsWorkspaceAcceptable(
            name=self.display_name,
            description=description,
            filter_page_url=self.filter_page_url,
            adapter_layer_json=json.dumps(
                {'wms_source_id': self.id,
                 'name': self.layer_name,
                 'url': self.proxied_url,
                 'params': self.params,
                 'legend_url': self.proxied_legend_url,
                 'options': self.options,
                 'cql_filters': list(allowed_cql_filters),
                 'timepositions': self.timepositions,
                 }),
            adapter_name=ADAPTER_CLASS_WMS)
        return result

    def capabilities_url(self):
        return capabilities_url(self.url)

    def search_one_item(self, x=None, y=None, bbox=None,
                        width=None, height=None, cql_filters=None,
                        cql_filter_string=None):
        """Return getfeatureinfo values found for a single item."""

        if bbox is None and self.bbox:
            bbox = self.bbox

        results = self.get_feature_info(
            bbox=bbox, x=x, y=y, _buffer=16, width=width, height=height,
            cql_filters=cql_filters,
            cql_filter_string=cql_filter_string)

        # ^^^ Note Reinout: I wonder about that buffer.
        values = {}
        if results:
            for result in results:
                values.update(result)
        self._store_features(values)
        return values

    def _build_payload(self, params, layer, feature_count, version,
                       bbox, width, height, x, y,
                       cql_filters, cql_filter_string,
                       _buffer):
        """Build the request payload for GetFeatureInfo."""

        payload = {
            'REQUEST': 'GetFeatureInfo',
            'EXCEPTIONS': 'application/vnd.ogc.se_xml',
            'INFO_FORMAT': 'application/vnd.ogc.gml',
            'SERVICE': 'WMS',
            'SRS': 'EPSG:3857',  # Always Google (web mercator)
            'FEATURE_COUNT': feature_count,
            # Set the layer we want
            'LAYERS': layer,
            'QUERY_LAYERS': layer,
            'BBOX': bbox,
            # Height and width in pixels
            'HEIGHT': height,
            'WIDTH': width,
            # The clicked on pixel
            'X': x,
            'Y': y,

            # Version from parameter
            'VERSION': version,

            # Non-standard WMS parameter to slightly increase search
            # radius.  Shouldn't hurt as most WMS server software ignore
            # unknown parameters.  see
            # http://docs.geoserver.org/latest/en/user/services/wms/vendor.html
            'BUFFER': _buffer,
            }

        # Add styles to request when defined
        if 'styles' in params and params['styles']:
            payload['STYLES'] = params['styles']

        total_cql_filter = []
        # cql filter string comes from Filter Page
        if cql_filter_string:
            total_cql_filter.append(cql_filter_string)

        # cql filter defined in the wms source parameters
        if 'cql_filter' in params and params['cql_filter']:
            total_cql_filter.append(params['cql_filter'])

        # CQL filters passed through from the frontend
        if cql_filters is not None:
            allowed_filters = self.featureline_set.filter(
                visible=True, name__in=cql_filters.keys()
                ).values_list('name', flat=True)
            for key in allowed_filters:
                total_cql_filter.append('='.join([key, str(cql_filters[key])]))

        if total_cql_filter:
            payload['CQL_FILTER'] = ' AND '.join(total_cql_filter)

        if self.timepositions:
            # Get the user selected date/time selection.
            date = get_view_state(tls.request)
            formatting = '%Y-%m-%dT%H:%M:%SZ'
            payload['TIME'] = '/'.join(
                d.strftime(formatting)
                for d in [date['dt_start'], date['dt_end']])

        return payload

    def _parse_response_gml(self, response):
        if response.status_code != 200:
            return []

        root = ElementTree.fromstring(response.text)
        if 'ServiceException' in root.tag:
            logger.warning("Error in GetFeatureInfo for layer %s."
                           % (self.layer_name))
            return []

        feature = root.find('{http://www.opengis.net/gml}featureMember')
        if feature is None:
            return []
        layer = feature.getchildren()[0]
        namespace, ignored = layer.tag[1:].split('}')

        d = {}
        for item in layer.getchildren():
            if 'gml_id' in item.tag:
                continue

            # Namespace and layer can be '{SomeThing}LayerName'
            ignored, name = item.tag[1:].split('}')
            d[name] = item.text
        return [d]

    _parse_response = _parse_response_gml

    def _parse_response_json(self, response):
        if response.status_code != 200:
            return []

        response_dict = json.loads(response.text)
        if "exceptions" in response_dict:
            logger.warning("Error in GetFeatureInfo for layer %s. %s"
                           % (self.layer_name,
                              response_dict['exceptions'][0]['text']))
            return []

        features = response_dict['features']
        return [obj["properties"] for obj in features]

    def get_feature_info(self, bbox=None, width=1, height=1, x=0, y=0,
                         feature_count=1, _buffer=1,
                         cql_filters=None, cql_filter_string=None):
        """Gets feature info from the server inside the bbox.
        """
        if not bbox:
            return

        logger.warning("Getting feature info for %s item(s) in bbox %s",
                       feature_count, bbox)

        version = '1.1.1'
        if self.connection and self.connection.version:
            version = self.connection.version

        params = json.loads(self.params)
        result = []
        for layer in params['layers'].split(","):
            payload = self._build_payload(params, layer, feature_count,
                                          version, bbox, width, height, x, y,
                                          cql_filters, cql_filter_string,
                                          _buffer)
            response = requests.get(self.url, params=payload, timeout=10)
            layer_result = self._parse_response(response)

            # Store the last result, too, if applicable.
            if layer_result:
                result.extend(layer_result)
        logger.debug("Found %s GetFeatureInfo results.", len(result))
        return result

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
                popup_info = feature_line.as_popup_info(
                    values[feature_line.name])
                if popup_info:
                    info.append(popup_info)
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
    name = models.CharField(
        verbose_name=_("name"), max_length=100, null=False, blank=False)

    # If description is given, it is used in popups instead of name
    description = models.CharField(
        verbose_name=_("description"), max_length=200, null=True, blank=True)

    visible = models.BooleanField(
        verbose_name=_("visible"),
        default=True)
    use_as_id = models.BooleanField(
        verbose_name=_("use as id"),
        default=False)
    render_as = models.CharField(
        verbose_name=_("render as"),
        max_length=1,
        choices=popup_renderers.choices(),
        default=popup_renderers.DEFAULT_RENDERER)
    in_hover = models.BooleanField(verbose_name=_("in hover"), default=False)
    order_using = models.IntegerField(
        verbose_name=_("index"),
        # ^^^ Note reinout: we *always* call this one 'index'.
        default=1000)

    class Meta:
        ordering = ('order_using', 'description', 'name',)
        verbose_name = _("feature line")
        verbose_name_plural = _("feature lines")

    def __unicode__(self):
        return self.name

    @property
    def title(self):
        """Return description or else the name.

        This gives us the most user-friendly name possible.
        """
        return self.description or self.name

    def as_popup_info(self, value):
        """Return ourselves as dict for in WMSSource's popup."""
        return popup_renderers.popup_info(self, value)


class FilterPage(models.Model):
    """
    Page with filters for a single WMS source.
    """

    slug = models.SlugField(
        verbose_name=_('slug'),
        help_text=_("Set automatically from the name."))
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_(
            "Title of the page. If empty, the WMS source's name is used."),
        max_length=100,
        null=True,
        blank=True)
    wms_source = models.ForeignKey(
        WMSSource,
        verbose_name=_('WMS source'),
        help_text=_("WMS source for which we show filters."),
        related_name='filter_pages',
        blank=False)
    available_filters = models.ManyToManyField(
        FeatureLine,
        verbose_name=_('available filters'),
        help_text=_(
            "Feature lines of our WMS source that we use as filters."),
        blank=True)

    class Meta:
        ordering = ('wms_source',)
        verbose_name = _("WMS filter page")
        verbose_name_plural = _("WMS filter pages")

    @property
    def title(self):
        """Return title for use on the page.

        We can fill in our own name attribute, but we don't have to if we
        think the WMS source's name is good enough.
        """
        return self.name or self.wms_source.name

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('lizard_wms.filter_page', kwargs={'slug': self.slug})
