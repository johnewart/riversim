var RIVERSIM = RIVERSIM || {};

var map=null;


$(document).ready(function() {
		OLinit();
});
  
function OLinit() {
  var options = { 
      'units' : "m",
      'numZoomLevels' : 15,
      'projection' : new OpenLayers.Projection("EPSG:900913"),
      'maxExtent' : new OpenLayers.Bounds(-13497331.429139, 4419222.7566768, -13313882.561281, 4602671.6245356),
      'displayProjection': new OpenLayers.Projection("EPSG:4326"),
  };

  map = new OpenLayers.Map('map', options);
  map.addControl(new OpenLayers.Control.LayerSwitcher());
  map.addControl(new OpenLayers.Control.Scale());
  map.addControl(new OpenLayers.Control.MousePosition());
  map.addControl(new OpenLayers.Control.PanZoomBar());

  // Base Layer
  var osm = new OpenLayers.Layer.OSM.Mapnik("OpenStreetMap");

  /* Rivers */
  rivers = new OpenLayers.Layer.WFS("Rivers", RIVERSIM.layers.rivers.url, {"name": "JOAQUIN,MERCED"},
                {  projection: new OpenLayers.Projection("EPSG:4326"),
                   format: OpenLayers.Format.KML,
                   formatOptions: { 
                     extractAttributes: true,
                     extractStyles: true,
                   },
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
  lidar_tiles = new OpenLayers.Layer.WFS("LiDAR Tiles", RIVERSIM.layers.lidartiles.url, {},
                {  projection: new OpenLayers.Projection("EPSG:4326"),
                   format: OpenLayers.Format.KML,
                   formatOptions: { 
                     extractAttributes: true,
                     extractStyles: true,
                   },
                }
  );
  
  selected_lidar_tiles = new OpenLayers.Layer.WFS("LiDAR Tiles", RIVERSIM.layers.selected_lidartiles.url, {"name": "JOAQUIN,MERCED"},
                  {  projection: new OpenLayers.Projection("EPSG:4326"),
                     format: OpenLayers.Format.KML,
                     formatOptions: { 
                       extractAttributes: true,
                       extractStyles: true,
                     },
                  }
  );

  /* CDEC Stations */
  cdec_stations = new OpenLayers.Layer.WFS("CDEC Stations", RIVERSIM.layers.cdec_stations.url, {"river": "JOAQUIN,MERCED"},
                {  projection: new OpenLayers.Projection("EPSG:4326"),
                   format: OpenLayers.Format.KML,
                   formatOptions: { 
                     extractAttributes: true,
                     extractStyles: true,
                   },
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
  var maplayers = [ osm, lidar_tiles, selected_lidar_tiles, rivers, cdec_stations,];
  map.addLayers(maplayers);
  map.setCenter(new OpenLayers.LonLat(-120.47827, 37.29261), 3); // Not needed since the next line will also do this.
  map.zoomToExtent(map.maxExtent); // Since OSM uses the world by default..
}

function changeRiverSelection() {
}

function toggleRiverSelection() { 
    var data = { 'river_names' : []};
    $(".riverselect option:selected").each(function() {
        data['river_names'].push($(this).val());
    });

    // Update river selection in session
    $.get(RIVERSIM.urls.filter_rivers, data);

    // Reload layers
    rivers.refresh();
    selected_lidar_tiles.refresh();
    cdec_stations.refresh();
}
   
$(document).ready(function() { 
    $('.riverselect').change(function() {
        toggleRiverSelection();
    });
});
