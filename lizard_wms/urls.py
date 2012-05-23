"""Urls for lizard_wms."""
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

from lizard_maptree.views import MaptreeHomepageView

admin.autodiscover()

ITEM_MODELS = ['wmssource', ]  # for maptree items.

urlpatterns = patterns(
    '',
    url(r'^$',
        MaptreeHomepageView.as_view(),  # pylint: disable=E1120
        {'item_models': ITEM_MODELS},
        name='lizard_wms.homepage'),
    url(r'^category/(?P<root_slug>.*)/$',
        MaptreeHomepageView.as_view(),  # pylint: disable=E1120
        {'item_models': ITEM_MODELS},
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
