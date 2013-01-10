lizard-wms
==========================================

.. image:: https://secure.travis-ci.org/lizardsystem/lizard-wms.png?branch=master
   :target: http://travis-ci.org/#!/lizardsystem/lizard-wms

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

GetFeatureInfo
--------------

It's possible to show attributes of wms layers in a popup.
When a click on a wms layer in lizard is registered a getFeatureInfo is
requested.

There are a couple of rendering options for these attributes.
Google column chart, a link and an image.

Google Column chart
+++++++++++++++++++

To show a google column the attribute must have JSON in the following format::

  [[{"primary": "true"},{"units": "m/3", "sort":"desc", "color": "993366"}],
  ["'87", 35], ["'90", 40]]
