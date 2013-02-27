Changelog of lizard-wms
===================================================


1.22 (unreleased)
-----------------

- UI fixes for filterpage: form submits itself on change automatically.

- URLs in the popup are now opened in a new window. Customers keep asking
  about this...


1.21 (2013-02-25)
-----------------

- Added dynamic refreshing of the sidebar's form. Quicker.


1.20 (2013-02-25)
-----------------

- Added filter icon to the workspace acceptable that links to the
  filterpage. The solution is not optimal, as it means more database
  queries. For a good solution, the lizard-ui/lizard-map css and sidebar
  handling needs an overhaul. And perhaps the relation filterpage-to-wmssource
  should be switched around.


1.19 (2013-02-22)
-----------------

- Using https://github.com/jdunck/python-unicodecsv instead of python's
  build-in csv module to prevent unicodedecodeerrors.

- Added parsing of excel-like dates (``40909.0``) in popups to
  ``2012-01-01``.

- If you haven't properly configured a feature line for use in the hover, we
  won't show a more-or-less debug string anymore.


1.18 (2013-02-22)
-----------------

- Added FilterPage class which links to a WMS source. The WMS source's
  featurelines can be configured on the FilterPage as available filters.

- There's a view for the FilterPage that shows the available filters as
  dropdowns. The dropdown values depend on the values that can be found in the
  bounding box. Submitting the form filters on that value. TODO: make the
  interaction more dynamic (read: javascript).

- A CSV export of the filtered data is available.

- Current limitation: max 100 items on the filterpage.


1.17 (2013-01-17)
-----------------

- Fixed issue in chart.py/models.py. If the json returned by the database
  doesn't contain any data, the google column chart url method would
  fail. There's now a check that simply returns nothing if this error
  condition occurs.


1.16 (2012-12-19)
-----------------

- Fixed collage item naming on multiselect.

- Fixed urls.py, so it won't recusively include other lizard-* URLs when
  running as part of a site.

- Pass styles in GetFeatureInfo query.

- Add vendor option 'buffer' to WMS GetFeatureInfo query so the search
  radius is slightly larger on a map click.


1.15 (2012-12-17)
-----------------

- Set some link styling in popup.


1.14 (2012-12-13)
-----------------

- Refactored the popup table head. Deltaportaal needs a popup without a
  table head.


1.13 (2012-12-12)
-----------------

- Fix a bug that resets options and categories from wms sources when reloading
their wms connection from admin.


1.12 (2012-12-10)
-----------------

- Rerelease due to missing migrations.

- Better mocking thanks to Remco.


1.11 (2012-12-10)
-----------------

- Added test for WMSSource creation from a WMSConnection.

- Added travis integration.

- WMSSource params combines _params and layer_name. This is to ease wms layer configuration.

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
