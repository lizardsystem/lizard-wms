"""Defining lizard_wms' adapter."""
import logging

from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from lizard_map.workspace import WorkspaceItemAdapter, adapter_serialize

from lizard_wms import models

from tls import request

logger = logging.getLogger(__name__)


class AdapterWMS(WorkspaceItemAdapter):
    """
    Adapter. Tries to get information for X,Y points using
    GetFeatureInfo requests.
    """

    search_with_request = True

    @property
    def wms_source(self):
        """Helper method that returns this layer's WMSSource
        object. wms_source_id is given in adapter_layer_json."""
        if not hasattr(self, '_wms_source'):
            pk = self.layer_arguments.get('wms_source_id')
            if pk is None:
                # This shouldn't happen, but it does
                # Just ignore it and carry on.
                return
            self._wms_source = models.WMSSource.objects.get(pk=pk)
        return self._wms_source

    def edit_link(self):
        if not self.wms_source:
            return
        return reverse('admin:lizard_wms_wmssource_change',
                       args=(self.wms_source.id,))

    def layer(self, layer_ids=None, request=None):
        return [], {}

    def location(self, x, y, radius):
        """This can't possibly be correct, but it works."""

        search = self.search(x, y, radius, request=request)
        if search:
            return search[0]

    def search(self, lon, lat, radius=None, request=None):
        """Get information about features at x, y from this WMS layer.

        The construction of the result is somewhat difficult: what do we use
        as the identifier of whatever is returned, what as the name?

        It seems that we can't do better than use a x, y value as
        identifier, it's the only bit of information we have that can
        be used to reconstruct the object.
        """
        if not self.wms_source.enable_search:
            return []

        params = self._build_search_parameters(request)
        feature_info = self.wms_source.search_one_item(*params)

        if feature_info:
            return [{
                    'name': self.wms_source.get_feature_name(feature_info),
                    'distance': 0,
                    'workspace_item': self.workspace_item,
                    'identifier': {
                        'x': lon,
                        'y': lat,
                        'radius': radius},
                    }]
        return []

    def _build_search_parameters(self, request):
        bbox = ','.join(map(request.GET.get, ['extent_left', 'extent_bottom',
                                              'extent_right', 'extent_top']))
        width, height = map(request.GET.get, ['width', 'height'])
        x, y = map(request.GET.get, ['x_pixel', 'y_pixel'])
        cql_filters = request.GET.get('cql_filters', None)
        if cql_filters is not None:
            cql_filters = json.loads(cql_filters)
        return x, y, bbox, width, height, cql_filters

    def html(self, identifiers, layout_options=None,
             template="lizard_wms/popup.html"):
        identifier = identifiers[0]

        params = self._build_search_parameters(layout_options['request'])
        feature_info = self.wms_source.search_one_item(*params)

        return self.html_default(
            identifiers=identifiers,
            template=template,
            layout_options=layout_options,
            extra_render_kwargs={
                'feature_info': self.wms_source.get_popup_info(feature_info),
                'workspace_item': self.workspace_item,
                'identifier': adapter_serialize(identifier),
                })

    def symbol_url(self, identifier=None, start_date=None, end_date=None):
        """
        returns symbol
        """
        icon_style = {
            'icon': 'polygon.png',
            'mask': ('mask.png', ),
            'color': (0, 1, 0, 0)}

        return super(AdapterWMS, self).symbol_url(

            start_date=start_date,
            end_date=end_date,
            icon_style=icon_style)

    def legend_image_urls(self):
        """Return url with WMS legend image."""

        if not self.wms_source.show_legend:
            return []
        if 'legend_url' in self.layer_arguments:
            legend_url = self.layer_arguments['legend_url']
            if legend_url:
                return [legend_url]
        wms_url = self.layer_arguments['url']
        params_json = self.layer_arguments['params']
        try:
            params = json.loads(params_json)
        except ValueError, e:
            logger.error("Invalid json in workspace item: %s", e)
            return []
        layers = params['layers'].split(",")
        urls = []
        url_template = (
            "%s?REQUEST=GetLegendGraphic&FORMAT=image/png" +
            "&WIDTH=20&HEIGHT=20&transparent=true&" +
            "LAYER=%s")
        for layer in layers:
            urls.append(url_template % (wms_url, layer))
        return urls

    def extent(self, identifiers=None):
        extent = {'north': None, 'south': None, 'east': None, 'west': None}

        if self.wms_source and self.wms_source.bbox:
            minx, miny, maxx, maxy = self.wms_source.bounding_box
            extent = {'north': maxy, 'south': miny, 'east': maxx, 'west': minx}

        # logger.debug("EXTENT: " + repr(extent))
        return extent

    def metadata(self):
        return self.wms_source.metadata_for_display
