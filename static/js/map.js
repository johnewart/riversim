var RIVERSIM = RIVERSIM || {};

var map=null;
var maplayers = null;


$(document).ready(function() {
		OLinit();
});
  
function OLinit() {
  //var extent = new OpenLayers.Bounds(-123.45, 36.47, -118.52, 39);
	var extent = new OpenLayers.Bounds(-13644436, 4308640, -13099593, 4720034);
														
  var options = { 
      units : "m",
      numZoomLevels : 15,
      projection : new OpenLayers.Projection("EPSG:900913"),
      //maxExtent : new OpenLayers.Bounds(-13497331.429139, 4419222.7566768, -13313882.561281, 4602671.6245356),
      displayProjection: new OpenLayers.Projection("EPSG:4326"),
			maxExtent: extent,
			restrictedExtent: extent
  };

  map = new OpenLayers.Map('map', options);
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  map.addControl(new OpenLayers.Control.Scale());
  map.addControl(new OpenLayers.Control.MousePosition());
  map.addControl(new OpenLayers.Control.PanZoomBar());

  var renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
  renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;
	

  // Base Layer
  var osm = new OpenLayers.Layer.OSM.Mapnik("OpenStreetMap");

  /* Rivers */
  rivers = new OpenLayers.Layer.Vector("Rivers",                 
								{  
									 projection: new OpenLayers.Projection("EPSG:4326"),
									 strategies: [new OpenLayers.Strategy.BBOX()],
									 protocol: new OpenLayers.Protocol.HTTP({
										 url: RIVERSIM.layers.rivers.url,
										 format: new OpenLayers.Format.KML({
											 extractAttributes: true,
											 extractStyles: true,
										 }),
									 }),
								   renderers: renderer
                }
  );

  var rivers_control = new OpenLayers.Control.SelectFeature(rivers);
  
  function rivers_onPopupClose(evt) { 
    rivers_control.unselect(this.feature);  
  }
  
  function rivers_select(evt) {
     feature = evt.feature;
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
									 projection: new OpenLayers.Projection("EPSG:4326"),
									 strategies: [new OpenLayers.Strategy.BBOX()],
									 protocol: new OpenLayers.Protocol.HTTP({
										 url: RIVERSIM.layers.lidartiles.url,
										 format: new OpenLayers.Format.KML({
											 extractAttributes: true,
											 extractStyles: true,
										 }),
									 }),
								   renderers: renderer
                }
  );
  
  selected_lidar_tiles = new OpenLayers.Layer.Vector("Selected LiDAR Tiles",  
								 {
                    projection: new OpenLayers.Projection("EPSG:4326"),
										strategies: [new OpenLayers.Strategy.BBOX()],
										protocol: new OpenLayers.Protocol.HTTP({
												url: RIVERSIM.layers.selected_lidartiles.url, 
												format: new OpenLayers.Format.KML({
														extractAttributes: true,
														extractStyles: true,
												}),
                     }),
										 renderers: renderer
                  }
  );

  /* CDEC Stations */
  cdec_stations = new OpenLayers.Layer.Vector("CDEC Stations", 
								{ 
									styleMap: new OpenLayers.StyleMap({'default':{
                strokeColor: "#00FF00",
                strokeOpacity: 1,
                strokeWidth: 3,
                fillColor: "#FF5500",
                fillOpacity: 0.5,
                pointRadius: 6,
                pointerEvents: "visiblePainted",
                label : "${name}",
                fontColor: "#000000",
                fontSize: "16px",
                fontFamily: "Proxima Nova",
                fontWeight: "bold",
                labelAlign: "${align}",
                labelXOffset: "0",
                labelYOffset: "-10"
            }}),
									projection: new OpenLayers.Projection("EPSG:4326"),
									strategies: [new OpenLayers.Strategy.BBOX()],
									protocol: new OpenLayers.Protocol.HTTP({
										url: RIVERSIM.layers.cdec_stations.url,
                    format: new OpenLayers.Format.KML({
		                    extractAttributes: true,
												//extractStyles: true,
                    }),
								   }),
									 renderers: renderer,
                }
  );

  var cdec_control = new OpenLayers.Control.SelectFeature(cdec_stations);

  function cdec_onPopupClose(evt) { 
    rivers_control.unselect(this.feature);  
  }

  function cdec_select(evt) {
     feature = evt.feature;
     popup = new OpenLayers.Popup.FramedCloud(this.name + " Popup",
                                              feature.geometry.getBounds().getCenterLonLat(),
                                              new OpenLayers.Size(100,100),
                                              "<h2>"+feature.data.name + "</h2><h3>" + feature.data.description + "</h3>",
                                              null,
                                              true,
                                              cdec_onPopupClose);
     feature.popup = popup;
     popup.feature = feature;
     map.addPopup(popup);
  }
  
  function cdec_unselect(evt) {
     feature = evt.feature;
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


  // Generic stuff..
  maplayers = [ osm, lidar_tiles, selected_lidar_tiles, rivers, cdec_stations,];
  map.addLayers(maplayers);
	//map.setCenter(new OpenLayers.LonLat(-120.47827, 37.29261), 3); // Not needed since the next line will also do this.
  map.zoomToExtent(extent); //map.getExtent()); // Since OSM uses the world by default..
  //map.zoomToMaxExtent();


}

function changeRiverSelection() {
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
    $.get(RIVERSIM.urls.filter_rivers, data);

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
