# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import json
import logging
from collections import defaultdict

# from django.utils.translation import ugettext as _
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.html import escapejs
from lizard_map.views import MapView
from lizard_ui.layout import Action
from lizard_wms.conf import settings
import unicodecsv

from lizard_wms import models
from lizard_wms import url_utils

EMPTY_OPTION = ''

logger = logging.getLogger(__name__)


class FilterPageView(MapView):
    """Simple view with a map."""
    template_name = 'lizard_wms/filter_page.html'

    @property
    def workspace(self):
        """Return workspace, but ensure our wms source is included."""
        ws = super(FilterPageView, self).workspace
        ws_acceptable = self.wms_source.workspace_acceptable()
        ws.add_workspace_item(ws_acceptable.name,
                              ws_acceptable.adapter_name,
                              ws_acceptable.adapter_layer_json)
        # ^^^ Note: add_workspace_item() first looks whether the item is
        # already available before adding. So it is a good way of ensuring it
        # is present, without the risk of duplication.
        return ws

    @property
    def filter_page(self):
        """Return our FilterPage object."""
        slug = self.kwargs['slug']
        return get_object_or_404(models.FilterPage, slug=slug)

    @property
    def wms_source(self):
        """Return our FilterPage's WMSSource."""
        return self.filter_page.wms_source

    @property
    def edit_link(self):
        """Return our admin url."""
        return "/admin/lizard_wms/filterpage/%s/" % self.filter_page.id

    @property
    def page_title(self):
        return self.filter_page.title

    @property
    def breadcrumbs(self):
        result = super(FilterPageView, self).breadcrumbs
        our_url = self.filter_page.get_absolute_url()
        if our_url == self.best_matching_application_icon:
            return result
        # Look for a wms category to append. URL-wise we're below the root
        # /webmap, not inside a category, which is really what we normally
        # want.
        categories = self.wms_source.category.all()
        if categories:
            category = categories[0]
            result.append(Action(name=category.name,
                                 url=category.get_absolute_url()))
        # We need to append ourselves.
        result.append(self.our_own_breadcrumb_element)
        return result

    def features(self, cql_filter_string=None):
        return self.wms_source.get_feature_info(
            bbox=self.bbox,
            feature_count=100,
            cql_filter_string=cql_filter_string)

    @property
    def filters(self):
        """Return filters from GET parameters."""
        result = {}
        allowed_keys = [name for (name, title) in self.available_filters]
        logger.debug("Allowed keys: %s", allowed_keys)
        for k in self.request.GET:
            if k not in allowed_keys:
                logger.warn("Unknown filter (%s) in GET parameters.", k)
                continue
            v = self.request.GET.getlist(k)
            v = [item for item in v if item]  # Weed out an empty string.
            if not v:
                continue
            result[k] = v
        logger.debug("Found filters: %s", result)
        return result

    @property
    def values_per_dropdown(self):
        intermediate_result = defaultdict(set)
        for feature in self.features():
            for k, v in feature.items():
                intermediate_result[k].add(v)
        result = {}
        for k, v in intermediate_result.items():
            result[k] = sorted(v)
        return result

    @property
    def bbox(self):
        extent = self.start_extent()
        x_size = float(extent['right']) - float(extent['left'])
        y_size = float(extent['top']) - float(extent['bottom'])
        logger.debug("Got a bbox %s wide and %s high.", x_size, y_size)
        return '%(left)s,%(bottom)s,%(right)s,%(top)s' % extent

    @property
    def available_filters(self):
        """Return available filters.

        For now: the visible featurelines. Later: our own list.
        """
        return [(featureline.name, featureline.title) for featureline in
                self.filter_page.available_filters.all()]

    @property
    def dropdowns(self):
        """Return list of dropdowns."""
        result = []
        choiced_made = self.filters
        values_per_dropdown = self.values_per_dropdown
        for select_name, select_label in self.available_filters:
            dropdown = {
                'label': select_label,
                'field_name': select_name,
                'options': values_per_dropdown.get(select_name, []),
                'selected': choiced_made.get(select_name, EMPTY_OPTION),
                }
            result.append(dropdown)
        return result

    @property
    def cql_filter_string(self):
        filter_parts = []
        for key, values in self.filters.items():
            values = ["'%s'" % value for value in values]
            values = ', '.join(values)
            filter_parts.append("%s in (%s)" % (key, values))
        filter_string = ' AND '.join(filter_parts)
        return filter_string

    def wms_layers(self):
        layers = super(FilterPageView, self).wms_layers()
        if not self.filters:
            return layers
        for layer in layers:
            if not (self.wms_source.name == layer['name'] and
                    self.wms_source.url == layer['url']):
                continue
            filter_string = escapejs(self.cql_filter_string)
            unpacked = json.loads(layer['params'])
            # layer['cql_filter'] = filter_string
            unpacked['cql_filter'] = filter_string
            layer['params'] = json.dumps(unpacked)
            logger.debug("Added filter string to params: %r", layer['params'])
        return layers

    def csv_download_link(self):
        url = reverse('lizard_wms.filter_page_export', kwargs=self.kwargs)
        if self.filters:
            url += '?'
            query_parts = ['='.join([k, v]) for k, v in self.filters.items()]
            url += '&'.join(query_parts)
        return url


class TimeWmsView(MapView):
    """View for a wms layer with TIME parameter."""
    template_name = 'lizard_wms/time.html'

    # @method_decorator(cache_control(private=True,
    #                                 max_age=5 * 60))
    # def dispatch(self, *args, **kwargs):
    #     return super(TimeWmsView, self).dispatch(*args, **kwargs)

    @cached_property
    def wms_source(self):
        return get_object_or_404(models.WMSSource, pk=self.kwargs['id'])

    @cached_property
    def year(self):
        from_request = self.request.GET.get('year', None)
        if from_request is None:
            return 2014  # Default
        return int(from_request)

    @cached_property
    def years(self):
        yyyys = set([time[:4] for time in self.wms_source.times()])
        return sorted(list(yyyys))

    @cached_property
    def acceptables(self):
        if self.request.is_ajax():
            # lizard-map request to grab the new workspace. Don't render the
            # whole huge 'acceptables' list.
            return []
        return [self.wms_source.workspace_acceptable(time=time)
                for time in self.wms_source.times()
                if time.startswith(str(self.year))]

    @cached_property
    def page_title(self):
        return self.wms_source

    @cached_property
    def breadcrumbs(self):
        result = super(TimeWmsView, self).breadcrumbs
        our_url = reverse('lizard_wms.time_page', id=self.kwargs['id'])
        if our_url == self.best_matching_application_icon:
            return result
        # Look for a wms category to append. URL-wise we're below the root
        # /webmap, not inside a category, which is really what we normally
        # want.
        categories = self.wms_source.category.all()
        if categories:
            category = categories[0]
            result.append(Action(name=category.name,
                                 url=category.get_absolute_url()))
        # We need to append ourselves.
        result.append(self.our_own_breadcrumb_element)
        return result


class FilterPageDownload(FilterPageView):

    def get(self, *args, **kwargs):
        """Return a csv file."""
        filename = '%s.csv' % self.kwargs['slug']
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="%s"' % filename)

        names_titles = self.wms_source.featureline_set.filter(
            visible=True).values_list('name', 'description')
        field_names = [name for (name, title) in names_titles]
        headers = {}
        for name, title, in names_titles:
            headers[name] = title
        writer = unicodecsv.DictWriter(response, field_names, dialect='excel',
                                       extrasaction='ignore')
        writer.writerow(headers)
        for feature in self.features(
            cql_filter_string=self.cql_filter_string):
            writer.writerow(feature)

        return response


def wms_proxy_view(request, wms_source_id):
    if request.method != 'GET':
        raise PermissionDenied()

    # If lizard_security decides the current user is not allowed to see
    # this wms_source, Http404 will be raised
    wms_source = get_object_or_404(
        models.WMSSource,
        pk=wms_source_id)

    url = url_utils.combine_url_and_params(
        wms_source.url, request.GET)

    # In debug mode, just redirect
    if settings.DEBUG:
        return HttpResponseRedirect(url)

    # use Nginx X-Accel-Redirect in production
    proxied_wms_servers = settings.WMS_PROXIED_WMS_SERVERS
    for proxied_domain, proxy in proxied_wms_servers.items():
        if proxied_domain in url:
            url = url.replace(
                proxied_domain,
                proxy['url'])
            break

    response = HttpResponse()
    response['X-Accel-Redirect'] = url
    return response
