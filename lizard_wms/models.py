# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models

# json only became available in Python 2.6. As some of our sites still use
# Python 2.5, we have to use the following workaround (ticket 2688).
try:
    import json
except ImportError:
    import simplejson as json

from lizard_maptree.models import Category
from lizard_map.models import ADAPTER_CLASS_WMS
from lizard_map.lizard_widgets import WorkspaceAcceptable


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

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u'%s' % self.name

    def workspace_acceptable(self):
        return WorkspaceAcceptable(
            name=self.name,
            description=self.description,
            adapter_layer_json=json.dumps({
                    'name': self.name,
                    'url': self.url,
                    'params': self.params,
                    'options': self.options}),
            adapter_name=ADAPTER_CLASS_WMS)
