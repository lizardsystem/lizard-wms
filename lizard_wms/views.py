# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
# from django.core.urlresolvers import reverse
from lizard_map.views import MapView
# from lizard_ui.views import UiView

from lizard_wms import models


class FilterPageView(MapView):
    """Simple view with a map."""
    # template_name = 'lizard_wms/filterpage.html'
    # page_title = 'sdfsdf'

    @property
    def filter_page(self):
        """Return our FilterPage object."""
        slug = self.kwargs['slug']
        return get_object_or_404(models.FilterPage, slug=slug)
