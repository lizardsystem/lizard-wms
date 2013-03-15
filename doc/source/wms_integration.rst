WMS integration
===============

Refreshing/loading WMS layers from a connection
-----------------------------------------------

To automatically fetch/update/delete wms layers, go to the admin screen with
the WMS connections, select the ones you want to update, and chose the
'reload' action from the dropdown.

Note that old wms layers that used to belong to the WMS connection are
deleted.

.. TODO::

   Provide better docs here.


.. _popup-choices:

GetFeatureInfo rendered in a popup
----------------------------------

It's possible to show attributes of WMS layers in a popup.  When a click on a
wms layer in lizard is registered a getFeatureInfo is requested.

There are a couple of rendering options for these attributes.

.. include:: featureline_choices.rst

.. note::

   The rendering happens in :func:`lizard_wms.popup_renderers.popup_info`.


Google Column chart
-------------------

To show a google column the attribute must have JSON in the following format::

  [[{"primary": "true"},{"units": "m/3", "sort":"desc", "color": "993366"}],
  ["'87", 35], ["'90", 40]]

.. TODO::

   Add better documentation.
