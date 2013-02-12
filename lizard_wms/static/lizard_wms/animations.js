/*
Support for animations

.btn-start-stop -> start/stop animation
.btn-reset -> reset animation (time=0)
*/

function updateTime(time){
  $("#time").text(time)
  // TODO: change, manage openlayers layer
  //var dataset = $('select#dataset option:selected').val()
  //depth.setUrl("/wms?dataset=" + dataset + "&time=" + time);
  //depth.redraw()
}

// Slider
function slide(ui, slider){
  updateTime(slider.value);
}


$(document).ready(function() {
  //$("#sidebar").append("Hello, World");
  $("#slider").slider({
    min: 0,
    max: 143,
    slide: slide
  });
  
});
