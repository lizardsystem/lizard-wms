# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models

# json only became available in Python 2.6. As some of our sites still use
# Python 2.5, we have to use the following workaround (ticket 2688).
try:
    import json
    json  # Pyflakes...
except ImportError:
    import simplejson as json

from lizard_maptree.models import Category
from lizard_map.models import ADAPTER_CLASS_WMS


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
