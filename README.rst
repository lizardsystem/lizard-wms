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

Refreshing/loading WMS layers
------------------------------

To automatically fetch/update/delete wms layers, go to the admin screen with
the WMS connections, select the ones you want to update, and chose the
'reload' action from the dropdown.

Note that old wms layers that used to belong to the WMS connection are
deleted.
