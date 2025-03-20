// Sebas Osorio
var tempMarker;
var tempInfoWindow;

var service;
var geocoder;

var directionsRenderer;
var map;

let markers = [];

function initMap() {
    console.log("initializing map");
    var myLatLng = { lat: 44.9727, lng: -93.23540000000003 };
    /* Create a map and place it on the div */
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 14,
        center: myLatLng
    });

    map.setCenter(myLatLng);

    directionsRenderer = new google.maps.DirectionsRenderer({ map: map });
    directionsRenderer.setMap(map);
    directionsRenderer.setPanel(document.getElementById("sidebar"));


    service = new google.maps.places.PlacesService(map);
    geocoder = new google.maps.Geocoder();

    var eventDetailList = extractEventDetails();
    eventDetailList.forEach(event => {
        var days = event.days;
        var eventName = event.eventName;
        var location = event.location;
        var times = event.times;
        findPlaceAndMark(service, map, days, eventName, location, times);
    });

}

function findPlaceAndMark(service, resultsMap, days, name, address, times) {
    var request = {
        query: address,
        fields: ['name', 'geometry'],
    };
    service.findPlaceFromQuery(request, function (results, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            tempMarker = new google.maps.Marker({
                map: resultsMap,
                position: results[0].geometry.location,
                title: address
            });
            var formattedPoints = '<ul>';
            for (let i = 0; i < days.length; i++) {
                formattedPoints += '<li>' + days[i] + ", " + times[i] + '</li>'
            }
            formattedPoints += '</ul>';
            var contentString =
                '<div>' +
                '<h3>' + name + '</h3>' +
                formattedPoints +
                '<p>' + address + '</p>' +
                '</div>';
            tempInfoWindow = new google.maps.InfoWindow({
                content: contentString
            });
            google.maps.event.addListener(tempMarker, 'click', createWindow(resultsMap, tempInfoWindow, tempMarker));
            markers.push(tempMarker);
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}


// Function to return an anonymous function that will be called when the rmarker created in the 
// geocodeAddress function is clicked	
function createWindow(rmap, rinfowindow, rmarker) {
    return function () {
        rinfowindow.open(rmap, rmarker);
    }
}

// Extract info from table
function extractEventDetails() {
    console.log("extracting event details");
    const eventDetails = [];
    const uniqueLocations = new Set();

    const rows = document.querySelectorAll('.table-container tbody tr');

    // Iterate over each row
    rows.forEach(row => {
        const columns = row.querySelectorAll('td'); // Get all columns in the row

        // Extract data from each column
        const days = [columns[0].textContent.trim()];
        const eventName = columns[1].textContent.trim();
        const times = [columns[2].textContent.trim()];
        const location = columns[3].textContent.trim();

        // Push the extracted details into the eventDetails array
        if (!uniqueLocations.has(location)) {
            eventDetails.push({
                days,
                eventName,
                times,
                location
            });
            uniqueLocations.add(location);
        } else {
            for (let i = 0; i < eventDetails.length; i++) {
                if (eventDetails[i].location == location) {
                    eventDetails[i].days.push(columns[0].textContent.trim());
                    eventDetails[i].times.push(columns[2].textContent.trim());
                }
            }
        }

    });
    return eventDetails;
}

// Location finding

var currentLocation;

function updateLocation() {
    if (navigator.geolocation) {
        return navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

function showPosition(position) {
    var coordinates = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
    }
    currentLocation = coordinates;
}

function placeSearch(event) {
    event.preventDefault();
    if (typeof currentLocation === "undefined") {
        updateLocation();
    }

    var placeType = document.querySelector('select[name="placeType"]').value;
    var searchKeyword = document.querySelector('input[name="searchKeyword"]').value;
    var range = document.querySelector('input[name="range"]').value;
    var request1 = {
        location: currentLocation,
        radius: range,
        type: [placeType]
    };
    var request2 = {
        location: currentLocation,
        radius: range,
        query: searchKeyword
    };
    if (placeType != "other") {
        service.nearbySearch(request1, nearbySearchCallback);
    } else {
        service.textSearch(request2, nearbySearchCallback);
    }

}

function nearbySearchCallback(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            markerMaker(map, results[i]);
        }
    }
}

async function markerMaker(resultsMap, result) {
    var formattedResult;
    try {


        formattedResult = await geocodeCoords(result.geometry.location);

    } catch (error) {
        console.error(error);
    }
    tempMarker = new google.maps.Marker({
        map: resultsMap,
        position: result.geometry.location,
        title: "placeSearchMarker"
    });

    var contentString =
        '<div>' +
        '<h3>' + result.name + '</h3>' +
        '<p>' + formattedResult + '</p>' +
        '</div>';
    tempInfoWindow = new google.maps.InfoWindow({
        content: contentString
    });
    google.maps.event.addListener(tempMarker, 'click', createWindow(resultsMap, tempInfoWindow, tempMarker));
    markers.push(tempMarker);
}

function geocodeCoords(thisLocation) {
    return new Promise((resolve, reject) => {
        geocoder
            .geocode({ location: thisLocation })
            .then((response) => {
                if (response.results[0]) {
                    resolve(response.results[0].formatted_address);
                } else {
                    window.alert("No results found");
                    reject('Geocode was not successful for the following reason: ');
                }
            })
            .catch((e) => window.alert("Geocoder failed due to: " + e));
    })
}

// Deletes all markers in the array by removing references to them.
function deleteMarkers() {
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }
    markers = [];
}

function toggleSearchKeyword() {
    var placeType = document.getElementById('place-type');
    var searchKeyword = document.getElementById('search-keyword');

    if (placeType.value === 'other') {
        searchKeyword.removeAttribute('disabled');
        searchKeyword.value = "";
    } else {
        searchKeyword.setAttribute('disabled', 'disabled');

        searchKeyword.value = "Enter Other Places";
    }
}

async function recieveDirections(event, destination) {
    event.preventDefault();
    if (typeof currentLocation === "undefined") {
        updateLocation();
    }

    try {
        var newDestination = await findPlaceAndReturn(service, map, destination);

        var transport = document.querySelector('input[name="transport"]:checked').value;

        const directionsService = new google.maps.DirectionsService();

        calculateAndDisplayRoute(directionsService, directionsRenderer, currentLocation, newDestination, transport);
    } catch (error) {
        console.error(error);
    }
}

function calculateAndDisplayRoute(directionsService, directionsRenderer, originData, destinationData, transportMode) {
    directionsService
        .route({
            origin: { lat: originData.lat, lng: originData.lng },
            destination: { lat: destinationData.lat, lng: destinationData.lng },
            travelMode: google.maps.TravelMode[transportMode],
        })
        .then((response) => {
            directionsRenderer.setDirections(response);
            directionsRenderer.setMap(map);
            createRoutePanel(response);
        })
        .catch((e) => window.alert("Directions request failed due to " + status));
}

function createRoutePanel(response) {
    console.log(response.route);
}

function findPlaceAndReturn(service, resultsMap, address) {
    return new Promise((resolve, reject) => {
        var request = {
            query: address,
            fields: ['name', 'geometry'],
        };

        service.findPlaceFromQuery(request, function (results, status) {
            if (status === google.maps.places.PlacesServiceStatus.OK) {
                const location = {
                    lat: results[0].geometry.location.lat(),
                    lng: results[0].geometry.location.lng()
                };
                resolve(location);
            } else {
                reject('Geocode was not successful for the following reason: ' + status);
            }
        });
    });
}
updateLocation();