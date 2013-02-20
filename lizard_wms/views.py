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
        return '%(left)s,%(bottom)s,%(right)s,%(top)s' % self.start_extent()

    @property
    def dropdowns(self):
        """Return list of dropdowns."""
        result = []
        values_per_dropdown = self.values_per_dropdown
        for feature_line in self.wms_source.featureline_set.all():
            dropdown = {
                'label': feature_line.title,
                'options': values_per_dropdown.get(feature_line.name, [])}
            result.append(dropdown)
        return result
