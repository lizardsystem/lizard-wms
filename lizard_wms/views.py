# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from lizard_map.daterange import DateRangeForm
from lizard_map.daterange import current_start_end_dates
from lizard_map.workspace import WorkspaceManager

from lizard_wms.models import Category


def homepage(request, root_slug=None, template="lizard_wms/homepage.html"):
    """
    Main page for WebMap.
    """
    tree = []

    parent_category = None
    if root_slug is not None:
        parent_category = get_object_or_404(Category, slug=root_slug)
    shapes_tree = get_tree(parent_category)

    workspace_manager = WorkspaceManager(request)
    workspaces = workspace_manager.load_or_create()
    date_range_form = DateRangeForm(
        current_start_end_dates(request, for_form=True))

    return render_to_response(
        template,
        {'date_range_form': date_range_form,
         'workspaces': workspaces,
         'tree': tree,
         'parent_category': parent_category},
        RequestContext(request))
