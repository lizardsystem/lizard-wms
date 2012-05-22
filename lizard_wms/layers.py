import json
import logging
import requests

from lizard_map.workspace import WorkspaceItemAdapter
from lizard_wms import models

logger = logging.getLogger(__name__)


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

        # WRONG, name isn't unique
        wms_source = models.WMSSource.objects.get(name=self.name)

        feature_info = wms_source.get_feature_for_hover(x, y)

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
        logger.info(repr(identifiers))
        return self.html_default(identifiers=identifiers,
                                 template="lizard_wms/popup.html",
                                 layout_options=layout_options,
                                 extra_render_kwargs={
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
            identifier=identifier,
            start_date=start_date,
            end_date=end_date,
            icon_style=icon_style)
