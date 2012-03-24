var RIVERSIM = RIVERSIM || {};

var map = null;
var maplayers = null;
var request_projection =  new OpenLayers.Projection("EPSG:4326");
var view_projection =  new OpenLayers.Projection("EPSG:900913");
// Layer for polygon selection of simulation region
var selection_vector = null;
// Layer for markers
var markers = null;
var california_extent = new OpenLayers.Bounds(-13644436, 4308640, -13099593, 4720034);

function riversimInit(zoomExtent) {

    var extent_box;
    var extent;

    if (zoomExtent != null)
    {
        extent_box = zoomExtent;
        extent = extent_box.transform(request_projection, view_projection);
    } else {
        extent_box = new OpenLayers.Bounds(-121.01,36.16,-118.78,37.45);
        extent = extent_box.transform(request_projection, view_projection);
    }

    var options = {
      units : "m",
      numZoomLevels : 15,
      projection : view_projection,
      //maxExtent : new OpenLayers.Bounds(-13497331.429139, 4419222.7566768, -13313882.561281, 4602671.6245356),
      displayProjection: new OpenLayers.Projection("EPSG:4326"),
      maxExtent: california_extent,
      restrictedExtent: california_extent
    };

    var renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
    renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;

    map = new OpenLayers.Map('map', options);

    // Base Layer
    var osm = new OpenLayers.Layer.OSM.Mapnik("OpenStreetMap");

    // Markers layer
    markers = new OpenLayers.Layer.Markers( "Markers" );
    map.addLayer(markers);

    selection_vector = new OpenLayers.Layer.Vector("Vector Layer", {
        renderers: renderer
    });

    selection_vector.events.on({
        'featureselected': function(feature) {
           console.log("Selected: %d", this.selectedFeatures.length);
        },
        'featureunselected': function(feature) {
            console.log("Selected: %d", this.selectedFeatures.length);
        }
    });

    /* Rivers */
    rivers = new OpenLayers.Layer.Vector("Rivers",
								{
                                    styleMap: new OpenLayers.StyleMap({
                                        'default':{
                                            strokeColor: "#0000ff",
                                            strokeOpacity: 0.4,
                                            strokeWidth: 2,
                                            fillColor: "#FF5500",
                                            fillOpacity: 0.5,
                                            pointRadius: 6,
                                            pointerEvents: "visiblePainted",
                                            label : "${name}",
                                            fontColor: "#888888",
                                            fontSize: "12px",
                                            fontFamily: "Proxima Nova",
                                            fontOpacity: 0.7,
                                            fontWeight: "normal",
                                            labelAlign: "right",
                                            labelXOffset: "0",
                                            labelYOffset: "-10"
                                     }}),
									 projection: request_projection,
									 strategies: [new OpenLayers.Strategy.BBOX()],
									 protocol: new OpenLayers.Protocol.HTTP({
										 url: RIVERSIM.layers.rivers.url,
										 format: new OpenLayers.Format.KML({
											 extractAttributes: true,
											 extractStyles: false
										 })
									 }),
								   renderers: renderer
                }
    );

    var rivers_control = new OpenLayers.Control.SelectFeature(rivers);

    function rivers_onPopupClose(evt) {
        rivers_control.unselect(this.feature);
    }

    function rivers_select(evt) {
        var feature = evt.feature;

        if (true)
        {
            var pixel = evt.getMousePosition();
            var lonlat = map.getLonLatFromPixel(pixel);
            console.log("Lon / lat: %o", lonlat);
        } else {
            popup = new OpenLayers.Popup.FramedCloud(this.name + " Popup",
                                                  feature.geometry.getBounds().getCenterLonLat(),
                                                  new OpenLayers.Size(100,100),
                                                  "<h2>"+feature.data.name + "</h2>",
                                                  null,
                                                  true,
                                                  rivers_onPopupClose);
            feature.popup = popup;
            popup.feature = feature;
            map.addPopup(popup);
        }
    }

    function rivers_unselect(evt) {
     feature = evt.feature;
     if (feature.popup) {
        popup.feature = null;
        map.removePopup(feature.popup);
        feature.popup.destroy();
        feature.popup=null;
     }
    }
  
    map.addControl(rivers_control);

    rivers_control.activate();
    rivers.events.on({ 'featureselected': rivers_select,
                       'featureunselected': rivers_unselect });


    /* LiDAR Tiles */
	lidar_tiles = new OpenLayers.Layer.Vector("LiDAR Tiles",                 
								{  
									 projection: request_projection,
									 strategies: [new OpenLayers.Strategy.BBOX()],
									 protocol: new OpenLayers.Protocol.HTTP({
										 url: RIVERSIM.layers.lidartiles.url,
										 format: new OpenLayers.Format.KML({
											 extractAttributes: true,
											 extractStyles: true
										 })
									 }),
                                    visibility: false,
								   renderers: renderer
                }
    );
  
    selected_lidar_tiles = new OpenLayers.Layer.Vector("Selected LiDAR Tiles",
								 {
                    projection: request_projection,
										strategies: [new OpenLayers.Strategy.BBOX()],
										protocol: new OpenLayers.Protocol.HTTP({
												url: RIVERSIM.layers.selected_lidartiles.url, 
												format: new OpenLayers.Format.KML({
														extractAttributes: true,
														extractStyles: true
												})
                     }),
										 renderers: renderer
                  }
    );

    /* CDEC Stations */
    cdec_stations = new OpenLayers.Layer.Vector("CDEC Stations",
        {
            styleMap: new OpenLayers.StyleMap({
                'default':{
                strokeColor: "#00FF00",
                strokeOpacity: 1,
                strokeWidth: 3,
                fillColor: "#FF5500",
                fillOpacity: 0.5,
                pointRadius: 6,
                pointerEvents: "visiblePainted",
                label : "${name}",
                fontColor: "#000000",
                fontSize: "13px",
                fontFamily: "Proxima Nova",
                fontWeight: "bold",
                fontOpacity: 0.6,
                labelAlign: "${align}",
                labelXOffset: "0",
                labelYOffset: "-10"
            }}),
            projection: request_projection,
            strategies: [new OpenLayers.Strategy.BBOX()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: RIVERSIM.layers.cdec_stations.url,
                format: new OpenLayers.Format.KML({
                    extractAttributes: true
                    //extractStyles: true,
                })
            }),
            renderers: renderer
        }
    );

    var cdec_control = new OpenLayers.Control.SelectFeature(cdec_stations);

    function cdec_onPopupClose(evt) {
        rivers_control.unselect(this.feature);
    }

    function cdec_select(evt) {
        feature = evt.feature;

        req_params = {
            "station_id": feature.data.id
        }
        var sensors = null;

        $.get(RIVERSIM.urls.station_sensors, req_params, function(result) {
            sensors = result;

            message = "<h2>"+feature.data.id + "</h2><b>" + feature.data.description + "</b>" + sensors;

            popup = new OpenLayers.Popup.FramedCloud(this.name + " Popup",
                                                      feature.geometry.getBounds().getCenterLonLat(),
                                                      new OpenLayers.Size(100,100),
                                                      message,
                                                      null,
                                                      true,
                                                      cdec_onPopupClose);
             feature.popup = popup;
             popup.feature = feature;
             map.addPopup(popup);
        });
    }
  
    function cdec_unselect(evt) {
        var feature = evt.feature;
        if (feature.popup) {
            popup.feature = null;
            map.removePopup(feature.popup);
            feature.popup.destroy();
            feature.popup=null;
        }
    }

    map.addControl(cdec_control);

    cdec_control.activate();
    cdec_stations.events.on({ 'featureselected': cdec_select,
                              'featureunselected': cdec_unselect });



    OpenLayers.Control.CustomNavToolbar = OpenLayers.Class(OpenLayers.Control.Panel, {

        initialize: function(options) {
            OpenLayers.Control.Panel.prototype.initialize.apply(this, [options]);
            this.addControls([
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.ZoomBox({alwaysZoom:true}),
                new OpenLayers.Control.DrawFeature(
                    selection_vector, OpenLayers.Handler.Polygon
                )
            ]);
            // To make the custom navtoolbar use the regular navtoolbar style
            this.displayClass = 'olControlNavToolbar'
        },

        /**
         * Method: draw
         * calls the default draw, and then activates mouse defaults.
         */
        draw: function() {
            var div = OpenLayers.Control.Panel.prototype.draw.apply(this, arguments);
            this.defaultControl = this.controls[0];
            return div;
        }
    });

    map.addControl(new OpenLayers.Control.LayerSwitcher());
    map.addControl(new OpenLayers.Control.Scale());
    map.addControl(new OpenLayers.Control.MousePosition());
    map.addControl(new OpenLayers.Control.PanZoomBar());
    map.addControl(new OpenLayers.Control.CustomNavToolbar());



    // Generic stuff..
    maplayers = [ osm, selection_vector, lidar_tiles, selected_lidar_tiles, rivers, cdec_stations];
    map.addLayers(maplayers);
    //map.setCenter(new OpenLayers.LonLat(-120.47827, 37.29261), 3); // Not needed since the next line will also do this.
    map.zoomToExtent(extent);  //map.getExtent()); // Since OSM uses the world by default..
    //map.zoomToMaxExtent();
}

function showMiniGraphs(station_id) {

}

function changeRiverSelection() {
}

function updateRiverSelection() {
    var extent = map.layers[0].getExtent().transform(view_projection, request_projection);
    var bbox = extent.toBBOX();
    var data = {"bbox": bbox};
    // Update river selection in session
    $.get(RIVERSIM.urls.create_simulation, data, function(result) {
        $(".riverselect").clear();
    });

}

function createSimulationFromMap() {
    // Create simulation from polygon
    var polygon = selection_vector.features[0].geometry;
    if (polygon == null)
    {
        alert("You must select a region first.");
    } else {
        polygon.transform(view_projection, request_projection);
        var data = {"polygon": polygon.toString()};
        // Update river selection in session
        $.get(RIVERSIM.urls.create_simulation, data, function(result) {
            window.location=result;
        });
    }
}

function selectSimulationPoint(where)
{
    map.events.register("click", map , function(e){
        var lonlat = null;
        var clicklonlat = map.getLonLatFromViewPortPx(e.xy).transform(view_projection, request_projection);

        var data = {
            "longitude": clicklonlat.lon,
            "latitude": clicklonlat.lat
        };

        $.get(RIVERSIM.urls.closest_point_on_river, data, function(result) {
            lonlat = new OpenLayers.LonLat(result.longitude, result.latitude).transform(request_projection, view_projection);
            var update_data = {};

            if(where == 'start')
            {
                update_data['start_point'] = result.longitude + " " + result.latitude
            }

            if (where == 'end')
            {
                update_data['end_point'] = result.longitude + " " + result.latitude
            }

            $.get("update", update_data, function(result) {
                var marker = new OpenLayers.Marker(lonlat) ;
                markers.addMarker(marker);
            });

            //var opx = map.getPixelFromLonLat(lonlat);    //getLayerPxFromViewPortPx(e.xy) ;
            //marker.map = map ;
            //marker.moveTo(opx) ;

            /*
             var size = new OpenLayers.Size(21,25);
             var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
             var icon = new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png', size, offset);
             markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(0,0),icon));
             markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(0,0),icon.clone()));
             */

        }, "json");

    });
}

function selectSimulationStartPoint()
{
    selectSimulationPoint('start');
}

function selectSimulationEndPoint()
{
    selectSimulationPoint('end');
}

function reloadLayer(layer)
{
	  layer.loaded = false;
    //setting visibility to true forces a reload of the layer//
    layer.setVisibility(true);
    //the refresh will force it to get the new KML data//
    layer.refresh({ force: true, params: { 'key': Math.random()} });
}

function toggleRiverSelection() { 
		console.log("toggleRiverSelection()");
    var data = { 'river_names' : []};
    $(".riverselect option:selected").each(function() {
        data['river_names'].push($(this).val());
    });

    // Update river selection in session
    $.get(RIVERSIM.urls.select_rivers, data);

    // Reload layers
    reloadLayer(rivers);
    reloadLayer(selected_lidar_tiles);
    reloadLayer(cdec_stations);
}
   
$(document).ready(function() { 
    $('.riverselect').change(function() {
        toggleRiverSelection();
    });
});
