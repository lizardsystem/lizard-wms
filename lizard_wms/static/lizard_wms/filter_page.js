function refreshFormAndLayers() {
  $("#filter-page-spinner img").show();
  $.ajax({
    url: $("#filter-page-form").attr('action'),
    type: "GET",
    data: $("#filter-page-form").serialize(),
    success: function(data) {
      $("#lizard-map-wms").html($(data).find(
        "#lizard-map-wms").html());
      refreshWmsLayers();
      $("#filter-page-form fieldset").html($(data).find(
        "#filter-page-form fieldset").html());
      $("#filter-page-download-button").html($(data).find(
        "#filter-page-download-button").html());
      $(".workspace-wms-layer").each(function () {
        var id = $(this).attr("data-workspace-wms-id");
        var params = $(this).attr("data-workspace-wms-params");
        params = $.parseJSON(params);
        wms_layers[id].mergeNewParams(params);
      $("#filter-page-spinner img").fadeOut(100);
      });
    }
  });
}


function setUpFilterPageForm() {
  $("#filter-page-form").submit(function(e) {
    e.preventDefault();
    refreshFormAndLayers();
  });
  $("#filter-page-form input").live('change', function(e) {
    refreshFormAndLayers();
  });
  $("#filter-page-form select").live('change', function(e) {
    refreshFormAndLayers();
  });
}


$(document).ready(function () {
    setUpFilterPageForm();
});
