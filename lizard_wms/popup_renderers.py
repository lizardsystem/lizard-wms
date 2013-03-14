# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import datetime
import json
import logging

from django.utils.translation import ugettext_lazy as _
# ^^^ Note: the lasy ugettext as choices() is used in a model.
from django.utils.safestring import mark_safe

from lizard_wms.chart import google_column_chart_url


# Keep these constants in the order of their value.
# They need to be one character long, btw.
RENDER_GC_COLUMN = 'C'
RENDER_IMAGE = 'I'
RENDER_URL_MORE_LINK = 'M'
RENDER_TEXT = 'T'
RENDER_URL = 'U'
RENDER_URL_LIKE = 'W'
RENDER_XLS_DATE = 'X'

DEFAULT_RENDERER = RENDER_TEXT

LINK_TEMPLATE = '''
<a href="%(url)s"
   target="_blank"
   style="text-decoration:underline; color:blue;">%(link_text)s</a>
'''


logger = logging.getLogger(__name__)


def choices():
    """Return choices for the FeatureLine model."""
    return (
        (RENDER_TEXT, _("Text")),
        (RENDER_IMAGE, _("Link to an image")),
        (RENDER_XLS_DATE, _("Excel date format")),
        (RENDER_URL, _("URL")),
        (RENDER_URL_LIKE, _("URL-like text")),
        (RENDER_URL_MORE_LINK, _("URL shown as 'click here' link")),
        (RENDER_GC_COLUMN, _("Google column chart")),
        )


def xls_date_to_string(xldate):
    # Adapted from http://stackoverflow.com/a/1112664/27401
    dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=xldate)
    return dt.isoformat()[:10]  # Yes, this can be formatted more nicely.


def popup_info(feature_line, value):
    """Return dict with info for the WMS popup.

    It should return a dict with three items:

    - **label_on_separate_line**: the output is normally a two-column
      table. When this option is set to True, the label is printed on a line
      of its own with the value on a whole line of its own, below. Used for
      big google graphs.

    - **label**: the label. Shown in the first column.

    - **value**: the value to show. Use ``mark_safe()`` when returning a bunch
      of html. Note that we do some html rendering here ourselves instead of
      in the template as we know which rendering methods to use here in this
      file. The template *used* to be littered with exceptions, being tightly
      coupled to the constants in this file. Not anymore.

    """
    render_as = feature_line.render_as
    replacement_link_text = None
    label = feature_line.description or feature_line.name
    if render_as == RENDER_GC_COLUMN:
        label_on_separate_line = True
    else:
        label_on_separate_line = False

    # First some special cases that "convert" themselves to other renderers.
    if render_as == RENDER_GC_COLUMN:
        json_data = json.loads(value)
        if json_data is None:
            # See https://github.com/nens/deltaportaal/issues/4
            logger.warn(
                "https://github.com/nens/deltaportaal/issues/4 "
                "hits again")
            return
        url = google_column_chart_url(json_data)
        value = url
        if url == '':
            render_as = RENDER_TEXT
            value = _("Error converting data to a graph")
        else:
            render_as = RENDER_IMAGE
    elif render_as == RENDER_XLS_DATE:
        try:
            date_value = float(value)
        except ValueError:
            logger.warn("Not a float-like value for XLS date: %r", value)
            return
        value = xls_date_to_string(date_value)
        render_as = RENDER_TEXT
    elif render_as == RENDER_URL_LIKE:
        # Quite brittle, but equal to the code from the template that it
        # replaces.
        value = 'http://' + value
        render_as = RENDER_URL
    elif render_as == RENDER_URL_MORE_LINK:
        replacement_link_text = _("Click here for more information")
        if not 'http://' in value:
            value = 'http://' + value
            # Yes, this means we could do the same for RENDER_URL_LIKE
            # options, but I'm leaving that one alone for the moment.
        render_as = RENDER_URL

    # OK, now the actual rendering. Only text, url and image renderers are
    # left.
    if render_as == RENDER_TEXT:
        pass  # value is fine.
    elif render_as == RENDER_IMAGE:
        value = mark_safe('<img src="%s" />' % value)
    elif render_as == RENDER_URL:
        link_text = replacement_link_text or value
        value = mark_safe(LINK_TEMPLATE % {'url': value,
                                           'link_text': link_text})

    return {
        'label': label,
        'label_on_separate_line': label_on_separate_line,
        'value': value,
        }
