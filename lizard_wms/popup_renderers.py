# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
"""
Popup info rendering
--------------------

A WMS source has FeatureLines. Clicking on the map opens a popup that shows
all the lines from the WMS GetFeatureInfo call. Every line can be configured
to be rendered in a certain way. This module contains the various renderers.

"""
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
RENDER_TWO_DECIMALS = 'A'
RENDER_INTEGER = 'B'
RENDER_GC_COLUMN = 'C'
RENDER_IMAGE = 'I'
RENDER_URL_MORE_LINK = 'M'
RENDER_TEXT = 'T'
RENDER_URL = 'U'
RENDER_URL_LIKE = 'W'
RENDER_XLS_DATE = 'X'

#: The default renderer for a popup item: as text.
DEFAULT_RENDERER = RENDER_TEXT

#: Choices for popup rendering: every FeatureLine can choose how it wants to be
#: displayed.
POPUP_RENDER_CHOICES = (
    (RENDER_TEXT, _("Text")),
    (RENDER_IMAGE, _("Link to an image")),
    (RENDER_INTEGER, _("Integer")),
    (RENDER_TWO_DECIMALS, _("Float with two decimals")),
    (RENDER_XLS_DATE, _("Excel date format")),
    (RENDER_URL, _("URL")),
    (RENDER_URL_LIKE, _("URL-like text")),
    (RENDER_URL_MORE_LINK, _("URL shown as 'click here' link")),
    (RENDER_GC_COLUMN, _("Google column chart")),
    )

LINK_TEMPLATE = '''
<a href="%(url)s"
   target="_blank"
   style="text-decoration:underline; color:blue;">%(link_text)s</a>
'''

logger = logging.getLogger(__name__)


def choices():
    """Return choices for the FeatureLine model.

    See :ref:`popup-choices` for the available choices.
    """
    return POPUP_RENDER_CHOICES


def xls_date_to_string(xldate):
    """Return iso-formatted date from an excel float date.

    The method is adapted from http://stackoverflow.com/a/1112664/27401 with
    the assumption that it is a 1900-based date instead of a 1904 one...

    """
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

    The value is rendered based on the ``render_as`` attribute of the
    featureline. See :ref:`popup-choices` for the available choices.

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
        try:
            json_data = json.loads(value)
            if json_data is None:
                # See https://github.com/nens/deltaportaal/issues/4
                logger.warn(
                    "https://github.com/nens/deltaportaal/issues/4 "
                    "hits again")
                raise ValueError("Somehow the json data doesn't exist???")
            value = google_column_chart_url(json_data)
        except (TypeError, ValueError):
            logger.exception(
                "Exception when loading json google chart data")
            value = ''
        if value != '':
            render_as = RENDER_IMAGE
        else:
            render_as = RENDER_TEXT
            value = _("Error converting data to a graph")
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
    elif render_as == RENDER_INTEGER:
        try:
            value = float(value)
        except ValueError:
            logger.warn("Not a number-like value: %r", value)
            return
        value = unicode(int(round(value)))
        render_as = RENDER_TEXT
    elif render_as == RENDER_TWO_DECIMALS:
        try:
            value = float(value)
        except ValueError:
            logger.warn("Not a number-like value: %r", value)
            return
        value = '%0.2f' % value
        render_as = RENDER_TEXT

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
