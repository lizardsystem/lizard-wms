Changelog of lizard-wms
===================================================


1.10 (2012-11-27)
-----------------

- Properly set dependency versions.


1.9 (2012-11-29)
----------------

- Add sort for WMSSource by index and display name; in admin sort is on display 
name.


1.8 (2012-11-27)
----------------

- Added a checkbox on wms sources to omit them when searching (="clicking on
  the map").

- Added jsonfield-based metadata field to wms sources. The old metadata text
  field has been removed. The metadata is shown in the description (which
  means a popup for workspace acceptables).

- Split WMSSource name into a display_name and a layer_name, so synchonization won't
  break the display name.


1.7 (2012-10-18)
----------------

- Added cql_filter options in the adapter_layer_json.

- Added a migration that removes the reproject option from all WMSSource and WMSConnection instances.


1.6 (2012-10-04)
----------------

- Put a timeout of 10 seconds on WMS calls.

- Made legend background transparent.

- Support GetFeatureInfo for multi-layers.

- Added Google column chart support.

- Added popup with subtabs.

- Support ascending and descending sort on column charts.


1.5 (2012-08-14)
----------------

- Added multi-url legend support.


1.4 (2012-08-02)
----------------

- Added error handling for GetCapabilities 1.1.1 calls.


1.3 (2012-07-10)
----------------

- Added checkbox for showing the legend of a WMS source (default: True). This
  way you can hide the legend if you know it to be bad or unclear.


1.2 (2012-06-20)
----------------

- Hardcoded WMS version to 1.1.1 because owslib doesn't support 1.3.0. See
  https://github.com/lizardsystem/lizard-wms/issues/5

- Added admin site action for reloading WMS connections. This replaces the
  ``fetch_wms_layers`` management command. There is reasonable error reporting
  to help debug what's wrong with a WMS connection.

- Add a custom label for the category selection field.

- Support custom legend url for map layers and show them in the sidebar. Do
  not show legends in the hover popup.

- Update WMS source features upon 'save'. Also added action to update the
  bounding boxes for all sources.

- Deal with zoom ratio (radius) on mouseover and popup (click) searches.


1.1 (2012-06-07)
----------------

- Some popup table styling.

- XML attribute of WMS connections doesn't need to be filled in


1.0 (2012-05-29)
----------------

- Added lots of geoserver integration including getFeatureInfo.


0.5.3 (2012-05-10)
------------------

- Fixed wrong graft in MANIFEST.in.


0.5.2 (2012-05-10)
------------------

- Included management commands in MANIFEST.in.


0.5.1 (2012-05-10)
------------------

- README and CHANGES files are included in releases.


0.5 (2012-05-10)
----------------

- Added rudimentary WMS getCapabilities support.


0.4 (2011-11-11)
----------------

- Updated views to use the new lizard-maptree (0.3).

- Set minimum requirements for lizard-maptree, -map and -ui.

0.3 (2011-05-13)
----------------

- Implemented workaround to handle the case that standard Python module "json"
  is only available in Python 2.6 and later versions (ticket 2688).


0.2 (2011-03-01)
----------------

- Replaced view function with generic maptree view.


0.1 (2011-03-01)
----------------

- Added initial functionality.

- Initial library skeleton created by nensskel.  [Jack Ha]
