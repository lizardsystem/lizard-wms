# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.db import models


class WMSSource(models.Model):
    """
    Definition of a wms source.
    """
    name = models.CharField(max_length=80)
    url = models.URLField(verify_exists=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u'%s' % self.name


