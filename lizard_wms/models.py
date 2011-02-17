# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models
import json

from lizard_maptree.models import Category
from lizard_map.models import ADAPTER_NAME_WMS


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
        return {'name': self.name,
                'type': 'workspace-acceptable',
                'description': 'description',
                'adapter_layer_json': json.dumps({'url': self.url}),
                'adapter_name': ADAPTER_NAME_WMS}
