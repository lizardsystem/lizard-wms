# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import os

from lizard_wms.popup_renderers import POPUP_RENDER_CHOICES

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lizard_wms.testsettings')


def write_popup_renderers_file():
    outfile = open('./doc/source/featureline_choices.rst', 'w')
    for (id, label) in POPUP_RENDER_CHOICES:
        outfile.write("- %s\n\n" % label)
    outfile.close()


if __name__ == '__main__':
    write_popup_renderers_file()
