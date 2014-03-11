lizard-wms
==========================================

Lizard-wms makes remote WMS layers accessible in Lizard.

.. image:: https://secure.travis-ci.org/lizardsystem/lizard-wms.png?branch=master
   :target: http://travis-ci.org/#!/lizardsystem/lizard-wms


Layers
-----------

When a layer has 'tijd' or 'Time' in the layer_name
a time selection is possible.


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

Proxying WMS servers
--------------------

It is possible to have lizard-wms act as a proxy for your WMS
servers. This has three possible benefits:

- If a WMS source defined in lizard_wms has a DataSet, access to the
  source is restricted to users that have access to that DataSet. The
  proxy will also only work for logged in users that have access.

- The real URL of the WMS source is hidden and behind a username, password.

- If the real WMS server is on a private network and isn't reachable
  by the outside world, then this proxying can be part of a secure
  solution for showing its layers to the outside world.

To setup the proxying, two things are needed::

1. In the site's nginx.conf, an internal URL must be defined that
   redirects to the real WMS source. This URL is internal so that it
   can't be used by external browsers, only by the proxying mechanism.

   location /geoserver6/ {
       internal;
       proxy_pass http://geoserver6.lizard.net/geoserver;
       proxy_set_header Authorization "Basic BASE64 encoded username:password";

   }

2. In the site's settings.py, a reverse mapping of same must be set::

   # Dictionary of domain names that can be handled by lizard-wms' WmsProxyView, that
   # redirects them to an internal URL defined in nginx.conf. Domains names are keys,
   # internal URLs are values.
   WMS_PROXIED_WMS_SERVERS = {
       'http://geoserver6.lizard.net/geoserver': {'url': '/geoserver6/',
                                                  'username': 'Username',
                                                  'password': 'SuperSecret'}
   }

The result is that all WMS source URLs shown in Lizard (as workspace
items) that start with 'http://geoserver6.lizard.net/geoserver' are
instead shown as URLs going to the site itself (as in
yourlizardsite.lizard.net/wms/proxy/1312/' for WMS source with id
1312). Internally, access to that WMS source is checked and if the
user has access, an internal redirect to the real Geoserver follows
that is invisible to the browser.
