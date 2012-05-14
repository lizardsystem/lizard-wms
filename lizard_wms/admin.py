import urlparse

from django.contrib import admin

from lizard_wms.models import WMSConnection, WMSSource


def source_domain(obj):
    """Return the domain of the WMSSource url."""
    return ("%s" % urlparse.urlparse(obj.url).netloc)

source_domain.short_description = 'Domein'


class WMSSourceAdmin(admin.ModelAdmin):
    list_display = ('name', source_domain)

admin.site.register(WMSSource, WMSSourceAdmin)

for model in (WMSConnection, ):
    admin.site.register(model)
