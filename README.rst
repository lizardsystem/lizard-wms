lizard-wms
==========================================

Lizard-wms makes remote WMS layers accessible in Lizard.

.. image:: https://secure.travis-ci.org/lizardsystem/lizard-wms.png?branch=master
   :target: http://travis-ci.org/#!/lizardsystem/lizard-wms


Usage
-----

You need both lizard-wms *and* lizard-maptree. The WMS sources are displayed
in a tree using lizard-maptree, so add both to your settings'
``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'lizard_wms',
        'lizard_maptree',
        ...
        ]

Include the following URL in your main ``urls.py``::

    (r'^webmap/', include('lizard_wms.urls')),

You don't need to separately include URLs from lizard-maptree.

After this, you can define WMS sources and/or WMS connections in the admin.

.. note::

   The full documentation is available at http://doc.lizardsystem.nl/libs/lizard-wms/
