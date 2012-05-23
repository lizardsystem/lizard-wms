from django.utils import simplejson as json
from lizard_map.workspace import WorkspaceItemAdapter


class AdapterWMS(WorkspaceItemAdapter):
    """Dummy adapter. It satisfies the GUI.
    Registerd as 'wms'.
    """

    def layer(self, layer_ids=None, request=None):
        return [], {}

    def search(self, x, y, radius=None):
        """Never find anything"""
        return []

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

    def legend_image_url(self):
        """Return url with WMS legend image."""
        wms_url = self.layer_arguments['url']
        params_json = self.layer_arguments['params']
        params = json.loads(params_json)
        layer = params['layers']
        url_template = (
            "%s?REQUEST=GetLegendGraphic&FORMAT=image/png" +
            "&WIDTH=20&HEIGHT=20&transparent=false&bgcolor=0xffffff&" +
            "LAYER=%s")
        return url_template % (wms_url, layer)
