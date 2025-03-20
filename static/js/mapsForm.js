// Sebas Osorio
var tempMarker;
var tempInfoWindow;
var service;
var map;

function initMap() {
    console.log("initializing map");
    var myLatLng = { lat: 44.9727, lng: -93.23540000000003 };
    /* Create a map and place it on the div */
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 14,
        center: myLatLng
    });

    map.setCenter(myLatLng);

    service = new google.maps.places.PlacesService(map);
    console.log("got here");

    new ClickEventHandler(map, origin);
}

function isIconMouseEvent(e) {
    return "placeId" in e;
}

class ClickEventHandler {
    origin;
    map;
    placesService;

    constructor(map, origin) {
        this.map = map;
        this.placesService = new google.maps.places.PlacesService(map);
        // Listen for clicks on the map.
        this.map.addListener("click", this.handleClick.bind(this));
    }
    handleClick(event) {
        if (isIconMouseEvent(event)) {
            // event.stop();
            if (event.placeId) {
                this.getPlaceInformation(event.placeId);
            }
        }
    }

    getPlaceInformation(placeId) {
        const me = this;

        this.placesService.getDetails({ placeId: placeId }, (place, status) => {
            if (
                status === "OK" &&
                place &&
                place.geometry &&
                place.geometry.location
            ) {
                console.log(place.formatted_address);
                document.getElementById("location").value = place.formatted_address;
            }
        });
    }
}