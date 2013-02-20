# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import logging

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
    def edit_link(self):
        """Return our admin url."""
        return "/admin/lizard_wms/filterpage/%s/" % self.filter_page.id

    @property
    def page_title(self):
        return self.filter_page.title
