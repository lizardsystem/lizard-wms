# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from lizard_map.lizard_widgets import WorkspaceAcceptable


class WmsWorkspaceAcceptable(WorkspaceAcceptable):
    """Subclass that allows extra filter_page_url parameter.

    We also override the template to optionally add a filter icon for the
    filter page.
    """
    template_name = 'lizard_wms/wms_workspace_acceptable.html'

    def __init__(self, filter_page_url=None, time_page_url=None, **kwargs):
        super(WmsWorkspaceAcceptable, self).__init__(**kwargs)
        self.filter_page_url = filter_page_url
        self.time_page_url = time_page_url
