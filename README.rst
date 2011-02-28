lizard-wms
==========================================

Introduction
------------

Add external Web Map Services (wms) in your lizard workspace. The wms
sources are displayed in a tree using lizard-maptree.

Usage
-----

Define wms sources in the admin. Include the urls.py in your main
urls.py::

    (r'^webmap/', include('lizard_wms.urls')),

That's all.
