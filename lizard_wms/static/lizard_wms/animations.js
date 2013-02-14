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
wms_ani_layers = {};  


/* TODO: make Backbone object for control panel */

/*
Animated layer: keep track of an animated wms.

We use a Backbone model because of its more object-oriented nature and the
possibility to sync all kinds of info with the server later on.
*/
var AnimatedLayer = Backbone.Model.extend({
  defaults: {
    current_timestep: 0,  // to be altered from outside
    current_in_map: {},  // indices if layers that are in OL.map
    current_visible: 0
  },
  constructor: function(options) {
    Backbone.Model.prototype.constructor.call(this, options);
    this.params = options.params;
    this.url = options.url;
    this.name = options.name;
    this.options = options.options;
    this.max_timesteps = 143;
    this.current_timestep = 0;  // to be altered from outside
    this.current_in_map = {};  // indices if layers that are in OL.map
    this.current_visible = null;

    var layers = [];
    for (var i=0; i < 143; i++) {
      this.params.time = i;           
      layers[i] = new OpenLayers.Layer.WMS(this.name, this.url, this.params, this.options);
    }
    this.layers = layers;
  },
  initialize: function() {  
  },
  updateMap: function() {
    // update visible layer
    // add/remove layers
    console.log('updating map');
  },
  setTimestep: function(timestep) {
      this.current_timestep = timestep;
      //console.log('timestep is now ', this.current_timestep);
      var to_delete_from_map = {};
      for (ts in this.current_in_map) {to_delete_from_map[ts] = ts};  // start with all layers
      // console.log('initial to delete ', to_delete_from_map);
      for (var ts=timestep; ts<this.max_timesteps && ts<timestep+10; ts++) {
        //console.log('we want timestep ', ts);
        if (this.current_in_map[ts] !== undefined) {
          //console.log('already in current map', ts);
          // is already in current_in_map
          delete to_delete_from_map[ts];
        } else {
          // new
          //console.log('adding to current ', ts);
          this.current_in_map[ts] = ts;
          // actually add to openlayers
          map.addLayer(this.layers[ts]);
        }
     }
     // now delete all layers from to_delete_from_map
     for (var ts in to_delete_from_map) {
       //console.log('removing from map... ts ', ts);
       map.removeLayer(this.layers[ts]);
       delete this.current_in_map[ts];
     }
     // change current_visible
     if (this.current_visible !== this.current_timestep) {
         var old_visible = this.current_visible;
         //first make new layer visible
         this.current_visible = this.current_timestep;
         this.layers[this.current_visible].setOpacity(1);  // TODO: make opacity configurable
         if (old_visible !== null) {
             this.layers[old_visible].setOpacity(0);
         }
     }
  }
});


function updateTime(time){
  $("#time").text(time);
}


function remove_layer() {
  if (single_layer !== null) {
    single_layer.setOpacity(1);
  }
  if (to_be_removed_layer !== null) {
    map.removeLayer(to_be_removed_layer);
    to_be_removed_layer = null;
  }

}


function updateLayers() {
  // Update AnimationLayer objects so openlayers gets updated
  $(".workspace-wms-layer").each(function () {
        var id = $(this).attr("data-workspace-wms-id");
        wms_ani_layers[id].setTimestep(current_timestep);
  });
}


// Slider
function slide(ui, slider){
  current_timestep = slider.value;
  //update_frame(current_timestep);
  updateTime(slider.value);
  updateLayers();
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
    updateLayers();
  } else {
    return;  // Not setting next animation step
  }
    
  setTimeout(animation_loop, 300); // animation speed in ms
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
        options.opacity = 0;
        index = parseInt($(this).attr("data-workspace-wms-index"));
        if (wms_ani_layers[id] === undefined) {
          wms_ani_layers[id] = new AnimatedLayer({
            name: name, 
            url: url, 
            params: params, 
            options: options
            });
          wms_ani_layers[id].setTimestep(0);
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
