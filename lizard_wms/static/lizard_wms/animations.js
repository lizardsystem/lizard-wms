/*
Support for animations

.btn-start-stop -> start/stop animation
.btn-reset -> reset animation (time=0)
*/

STATUS_STOP = 0;
STATUS_PLAY = 1;

controller_status = STATUS_STOP;
current_timestep = 0;

// For each .workspace-wms-layer that is an animation,
// associative using 'id'
wms_ani_layers = [];  
single_frame = null;  // for testing
base_name = 'name';
base_url = 'http://localhost:5000/wms'; // for testing
base_params = {
  "styles": "",
  "format": "image/png",
  "height": "256",
  "width": "256",
  "tiled": "true",
  "time": 0,
  "dataset": "/home/user/git/nens/threedi-server/threedi_server/../var/data/subgrid_map.nc",
  "transparent": "true"
};
base_options = {"buffer": 0, "isBaseLayer": false, "opacity": 0.45};


function updateTime(time){
  $("#time").text(time);
  // TODO: change, manage openlayers layer
  //var dataset = $('select#dataset option:selected').val()
  //depth.setUrl("/wms?dataset=" + dataset + "&time=" + time);
  //depth.redraw()
}

// Slider
function slide(ui, slider){
  current_timestep = slider.value;
  updateTime(slider.value);
}


function animation_loop() {
  if (controller_status == STATUS_PLAY) {
    // increase animation with one step
    current_timestep += 1;
    console.log('current_timestep: ' + current_timestep);
    updateTime(current_timestep);
    // set slider position
    $("#slider").slider("value", current_timestep);
    // most important part: interact with OpenLayers.

    //testing: single frame
    if (single_frame !== null) {
      map.removeLayer(single_frame);
    }

    var params = base_params;
    params.time = current_timestep;
    
    single_frame = new OpenLayers.Layer.WMS(base_name, base_url, params, base_options);
    map.addLayer(single_frame);

  } else {
    return;  // Not setting next animation step
  }
    
  setTimeout(animation_loop, 1000); // every second
}


// Place all animation layers in animation_layers, run prepare on animation
//  * (?). Parts taken from lizard_map.js
function init_animation() {
  // Assume for now that all .workspace-wms-layers are animations
  $(".workspace-wms-layer").each(function () {
        var name, url, params, options, id, index, animation_layer;
        // WMS id, different than workspace ids.
        id = $(this).attr("data-workspace-wms-id");
        //ids_found.push(id);
        name = $(this).attr("data-workspace-wms-name");
        url = $(this).attr("data-workspace-wms-url");
        params = $(this).attr("data-workspace-wms-params");
        params = $.parseJSON(params);
        // Fix for partial images on tiles
        params['tilesorigin'] = [map.maxExtent.left, map.maxExtent.bottom];
        options = $(this).attr("data-workspace-wms-options");
        options = $.parseJSON(options);
        // HACK: force reproject = false for layers which still have this defined (in the database no less)
        // reprojection is deprecated
        if (options.reproject) {
            delete options['reproject'];
        }
        index = parseInt($(this).attr("data-workspace-wms-index"));
        if (wms_ani_layers[id] === undefined) {
            // Create it. Assume 143 timesteps
            for (var i=0; i < 10; i++) {
              // replace time=xx in params with time=i
              //console.log(name, url, params, options);
              //console.log(OpenLayers);
              //animation_layer[i] = new OpenLayers.Layer.WMS(name, url, params, options);
              //map.addLayer(animation_layer[i]);
            }
            //wms_ani_layers[id] = animation_layer;
            //layer.setZIndex(1000 - index); // looks like passing this via options won't work properly
        } else {
            // Update it.
            //var layer = wms_ani_layers[id];
            //layer.setZIndex(1000 - index);
        }

  });
}


$(document).ready(function() {
  // $("#sidebar").append("Hello, World");
  $("#slider").slider({
    min: 0,
    max: 143,
    slide: slide
  });
  $(".btn-start-stop").click(function() {
    if (controller_status == STATUS_STOP) {
      console.log('play');
      controller_status = STATUS_PLAY;
      $("a.btn-start-stop i").removeClass("icon-play");
      $("a.btn-start-stop i").addClass("icon-pause");
      $("#html-start-stop").html("Pause");
      animation_loop();
    } else {
      console.log('stop');
      $("a.btn-start-stop i").addClass("icon-play");
      $("a.btn-start-stop i").removeClass("icon-pause");
      $("#html-start-stop").html("Start");
      controller_status = STATUS_STOP;
    }
  });
  init_animation();
});
