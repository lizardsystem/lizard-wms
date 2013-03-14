# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import json
import logging

from django.utils.translation import ugettext_lazy as _
# ^^^ Note: the lasy ugettext as choices() is used in a model.

from lizard_wms.chart import google_column_chart_url


RENDER_NONE = ''
RENDER_TEXT = 'T'
RENDER_IMAGE = 'I'
RENDER_URL = 'U'
RENDER_URL_MORE_LINK = 'M'
RENDER_URL_LIKE = 'W'
RENDER_GC_COLUMN = 'C'
RENDER_XLS_DATE = 'X'

DEFAULT_RENDERER = RENDER_TEXT


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


def popup_info(feature_line, value):
    """Return dict with info for the WMS popup."""
    label_on_separate_line = 'true'
    link_name = ''
    if feature_line.render_as == RENDER_GC_COLUMN:
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
            feature_line.render_as = RENDER_NONE
        else:
            feature_line.render_as = RENDER_IMAGE
        label_on_separate_line = 'false'
    elif feature_line.render_as == RENDER_XLS_DATE:
        try:
            date_value = float(value)
        except ValueError:
            logger.warn("Not a float-like value for XLS date: %r", value)
            return
        value = xls_date_to_string(date_value)
        feature_line.render_as = RENDER_TEXT
    elif feature_line.render_as == RENDER_URL_LIKE:
        link_name = value
        value = 'http://' + value
        # Quite brittle, but equal to the code from the template that it
        # replaces.
    elif feature_line.render_as == RENDER_URL_MORE_LINK:
        link_name = _("Click here for more information")
        if not 'http://' in value:
            value = 'http://' + value
            # Yes, this means we could do the same for RENDER_URL_LIKE
            # options, but I'm leaving that one alone for the moment.
    return {
        'name': (feature_line.description or feature_line.name),
        'value': value,
        'link_name': link_name,
        'render_as': feature_line.render_as,
        'label_on_separate_line': label_on_separate_line,
        }
