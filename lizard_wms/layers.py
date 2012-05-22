import json
import logging
import requests

from lizard_map.workspace import WorkspaceItemAdapter

logger = logging.getLogger(__name__)


def get_feature_info(url, layer, version, x, y):
    """Send feature info request. Define a bounding box and ask for a 1x1
    picture in which we want the value at the pixel (0,0).

    x, y are Google coordinates."""

    # We use a tiny custom radius, because otherwise we don't have
    # enough control over which feature is returned, there is no
    # mechanism to choose the feature closest to x, y.
    radius = 10

    payload = {
        'REQUEST': 'GetFeatureInfo',
        'EXCEPTIONS': 'application/vnd.ogc.se_xml',
        'INFO_FORMAT': 'text/plain',
        'SERVICE': 'WMS',
        'SRS': 'EPSG:900913',  # Always Google

        # Get a single feature
        'FEATURE_COUNT': 1,

        # Set the layer we want
        'LAYERS': layer,
        'QUERY_LAYERS': layer,

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
        'VERSION': version,
        }

    r = requests.get(url, params=payload)
    logger.info("GetFeatureInfo says: " + r.content)

    # XXX Check result code etc

    if 'no features were found' in r.content:
        return None

    return r.content


class AdapterWMS(WorkspaceItemAdapter):
    """
    Adapter. Tries to get information for X,Y points using
    GetFeatureInfo requests.
    """

    def __init__(self, *args, **kwargs):
        super(AdapterWMS, self).__init__(*args, **kwargs)

        # TODO: Put the actual WMS model objects in layer_arguments
        # (or their slugs, rather), so we can use them to get at
        # e.g. the WMS version.

        self.url = self.layer_arguments['url']
        self.params = json.loads(self.layer_arguments.get('params', '{}'))
        self.name = self.layer_arguments['name']
        self.options = json.loads(self.layer_arguments.get('options', '{}'))

    def layer(self, layer_ids=None, request=None):
        return [], {}

    def search(self, x, y, radius=None):
        """Get information about features at x, y from this WMS layer.

        The construction of the result is somewhat difficult: what do we use
        as the identifier of whatever is returned, what as the name?

        It seems that we can't do better than use a x, y value as
        identifier, it's the only bit of information we have that can
        be used to reconstruct the object.
        """

        feature_info = get_feature_info(
            url=self.url,
            layer=self.params['layers'],
            version='1.3.0',
            x=x, y=y)

        if feature_info:
            return [{
                    'name': feature_info,
                    'distance': 0,
                    'workspace_item': self.workspace_item,
                    'identifier': {
                        'x': x,
                        'y': y
                        },
                    }]

        return []

    def html(self, identifiers, layout_options=None):
        pass

    def symbol_url(self, identifier=None, start_date=None, end_date=None):
        """
        returns symbol
        """
        icon_style = {
            'icon': 'polygon.png',
            'mask': ('mask.png', ),
            'color': (0, 1, 0, 0)}
        return super(AdapterWMS, self).symbol_url(
            identifier=identifier,
            start_date=start_date,
            end_date=end_date,
            icon_style=icon_style)
