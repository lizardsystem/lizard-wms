from django.contrib import admin

from lizard_wms.models import WMSConnection, WMSSource

for model in (WMSConnection, WMSSource):
    admin.site.register(model)
