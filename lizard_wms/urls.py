"""Urls for lizard_wms."""
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from lizard_maptree.views import MaptreeHomepageView
from rest_framework.urlpatterns import format_suffix_patterns

from lizard_wms import views

admin.autodiscover()

ITEM_MODELS = ['wmssource', ]  # for maptree items.

api_urlpatterns = patterns('',
    # url(r'^$', 'api_root'),
    # url(r'^users/$', UserList.as_view(), name='user-list'),
    url(r'^$', views.DataSourceView.as_view(), name='wms_api_root'),
    # url(r'^groups/$', GroupList.as_view(), name='group-list'),
    # url(r'^groups/(?P<pk>\d+)/$', GroupDetail.as_view(), name='group-detail'),
)
api_urlpatterns = format_suffix_patterns(api_urlpatterns, allowed=['json', 'api'])

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
    (r'^api/', include(api_urlpatterns)),
    )


if settings.DEBUG:
    # Add this also to the projects that use this application
    urlpatterns += patterns(
        '',
        (r'^admin/', include(admin.site.urls)),
        (r'', include('staticfiles.urls')),
    )
