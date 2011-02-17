# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
        'lizard_wms.views.homepage',
        name='lizard_wms.homepage'),
    url(r'^category/(?P<root_slug>.*)/$',
     'lizard_wms.views.homepage',
     name='lizard_wms.homepage'),
    (r'^map/', include('lizard_map.urls')),
    )


if settings.DEBUG:
    # Add this also to the projects that use this application
    urlpatterns += patterns(
        '',
        (r'^admin/', include(admin.site.urls)),
        (r'', include('staticfiles.urls')),
    )
