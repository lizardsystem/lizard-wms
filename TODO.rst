TODO
====

A single Geoserver supports both WMS and WFS protocols. WMS is
primarily used for map images (visible layers in Lizard), while WFS is
directly about the underlying data (popups, mouseovers etc in Lizard).

We want a workflow like:

- Configure a server in Lizard admin

- Automatically, whenever the configuration changes or at specific moments (say every hour),

  - Available map layers are retrieved from the server

  - For each map layer, available features are imported

  - These features have configuration themselves (visible or not, order of showing)
    so they should continue to exist and not be deleted whenever.

We want to use lizard-task so that tasks can also be run from the
admin. Tasks are strictly better than management commands.

It appears that (at least for Geoserver), WMS and WFS can be reached at
the same URL, replacing 'service=wms' by 'service=wfs' in its
parameters. The URL should therefore be configured without the service
parameter.

Features have types -- string, int, float are definitely available,
but it was mentioned that image URLs also exist. Hopefully they are a
separate type.

Features found by WFS may have IDs! They can be retrieved using them,
so hopefully they can also be found in the data returned by
GetFeature.

There is an output format called "zipped shapefiles". Go figure.

Tests
-----

Add more tests for Connections and Sources, including the bounding box update.
