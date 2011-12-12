var lon = 5;
var lat = 40;
var zoom = 5;
var map, select;

function initMap(){
    map = new OpenLayers.Map('map');

    osm = new OpenLayers.Layer.OSM();    
    map.addLayer(osm);

    var styles = new OpenLayers.StyleMap({
        "default": new OpenLayers.Style({
            pointRadius: "6",
            fillColor: "${color}",
            strokeColor: "#000000",
            strokeOpacity: 0.6,
            strokeWidth: 1,
            graphicZIndex: 1
        }),
        "select": new OpenLayers.Style({
            strokeWidth: 2,
            graphicZIndex: 2
        })
    });
    
    var facilities = new OpenLayers.Layer.Vector("Facilities", {
        projection: map.displayProjection,
        strategies: [new OpenLayers.Strategy.Fixed(),
		     new OpenLayers.Strategy.Refresh({interval: 5000})],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "data.kml",
            format: new OpenLayers.Format.KML({
                extractStyles: true,
                extractAttributes: true
            })
        }),
	styleMap: styles
    });
    map.addLayer(facilities);
    
    select = new OpenLayers.Control.SelectFeature(facilities);
    facilities.events.on({
        "featureselected": onFeatureSelect,
        "featureunselected": onFeatureUnselect
    });
    map.addControl(select);
    select.activate();

    var center = new OpenLayers.LonLat( 21, -25 )	
        .transform(
            new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
            map.getProjectionObject() // to Spherical Mercator Projection
        );
    var zoom=4;
    map.setCenter (center, zoom);

    $('#facility_info').hide();
}
function onPopupClose(evt) {
    select.unselectAll();
}
function onFeatureSelect(event) {
    var feature = event.feature;
    updateFacilityInfo(feature.attributes.id);
}
function onFeatureUnselect(event) {
    var feature = event.feature;
}
function updateFacilityInfo(id) {
    $.ajax({
        type: "GET",
        url: "/reports/facility/"+id+"/",
        dataType: "html",
        success: function(xml) {
            $("#facility_info").html(xml);
	    $('#facility_info').slideDown();
        },
        error: function(request, status, error) {
        }
    });    
};
