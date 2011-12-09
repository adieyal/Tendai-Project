var lon = 5;
var lat = 40;
var zoom = 5;
var map, select;

function initMap(){
    map = new OpenLayers.Map('map');

    osm = new OpenLayers.Layer.OSM();    
    map.addLayer(osm);

    var facilities = new OpenLayers.Layer.Vector("Facilities", {
        projection: map.displayProjection,
        strategies: [new OpenLayers.Strategy.Fixed()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "data.kml",
            format: new OpenLayers.Format.KML({
                extractStyles: true,
                extractAttributes: true
            })
        })
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
