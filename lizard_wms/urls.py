"""Urls for lizard_wms."""
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin

from lizard_maptree.views import MaptreeHomepageView
from lizard_wms import views


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
    url(r'^page/(?P<slug>.*)/$',
        views.FilterPageView.as_view(),
        name='lizard_wms.filter_page'),
    url(r'^page/(?P<slug>.*).csv$',
        views.FilterPageDownload.as_view(),
        name='lizard_wms.filter_page_export'),
    url(r'^proxy/(?P<wms_source_id>\d+)/',
        views.wms_proxy_view,
        name='lizard_wms.wms_proxy'),
    )

if getattr(settings, 'LIZARD_WMS_STANDALONE', False):
    admin.autodiscover()
    urlpatterns += patterns(
        '',
        (r'^ui/', include('lizard_ui.urls')),
        (r'^map/', include('lizard_map.urls')),
        (r'^admin/', include(admin.site.urls)),
        (r'', include('django.contrib.staticfiles.urls')),
    )
