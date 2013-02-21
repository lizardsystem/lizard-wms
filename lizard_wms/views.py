# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import logging
from collections import defaultdict

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
# from django.core.urlresolvers import reverse
from lizard_map.views import MapView
# from lizard_ui.views import UiView

from lizard_wms import models

EMPTY_OPTION = ''

logger = logging.getLogger(__name__)


class FilterPageView(MapView):
    """Simple view with a map."""
    template_name = 'lizard_wms/filter_page.html'
    # page_title = 'sdfsdf'

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
    def features(self):
        return self.wms_source.get_feature_info(bbox=self.bbox,
                                                feature_count=100)

    @property
    def filters(self):
        """Return filters from GET parameters."""
        result = {}
        allowed_keys = [name for (name, title) in self.available_filters]
        logger.debug("Allowed keys: %s", allowed_keys)
        for k, v in self.request.GET.items():
            if k not in allowed_keys:
                logger.warn("Unknown filter (%s=%s) in GET parameters.", k, v)
                continue
            if not v:
                continue
            result[k] = v
        return result

    @property
    def values_per_dropdown(self):
        intermediate_result = defaultdict(set)
        for feature in self.features:
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
                self.wms_source.featureline_set.filter(visible=True)]

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
                'options': ([EMPTY_OPTION] +
                            values_per_dropdown.get(select_name, [])),
                'selected': choiced_made.get(select_name, EMPTY_OPTION),
                }
            result.append(dropdown)
        return result
