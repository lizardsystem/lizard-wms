# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from lizard_maptree.views import homepage as homepage_maptree
from lizard_wms.models import Category


def homepage(request,
             root_slug=None,
             template="lizard_maptree/homepage.html"):
    """
    Main page for WebMap.
    """
    return homepage_maptree(
        request,
        root_slug=root_slug,
        item_models=['wmssource', ],
        template=template,
        title='WMS')
