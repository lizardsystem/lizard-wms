from django.conf import settings
from appconf import AppConf


class LizardWmsConf(AppConf):
    # Override this setting in settings.py as
    # 'WMS_PROXIED_WMS_SERVERS'
    PROXIED_WMS_SERVERS = {
#        'http://geoserver6.lizard.net/geoserver': '/geoserver6/',
        }

    class Meta:
        prefix = 'wms'
