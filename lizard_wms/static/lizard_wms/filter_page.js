function refreshFormAndLayers() {
  return $.ajax({
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
      });
    }
  });
}


function setUpFilterPageForm() {
  $("#filter-page-form").submit(function(e) {
    e.preventDefault();
    return refreshFormAndLayers();
  })
}


$(document).ready(function () {
    setUpFilterPageForm();
});
