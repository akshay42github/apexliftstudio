// Google Maps integration for ApexLiftStudio locations

function initializeMap(locations) {
    if (!locations || locations.length === 0) {
        console.error('No locations provided');
        return;
    }

    // Calculate center point (average of all locations)
    const center = {
        lat: locations.reduce((sum, loc) => sum + loc.lat, 0) / locations.length,
        lng: locations.reduce((sum, loc) => sum + loc.lng, 0) / locations.length
    };

    // Create map
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 11,
        center: center,
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'off' }]
            }
        ]
    });

    // Add markers for each location
    const bounds = new google.maps.LatLngBounds();
    const infoWindow = new google.maps.InfoWindow();

    locations.forEach(location => {
        const marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.name,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: '#FFD700',
                fillOpacity: 1,
                strokeColor: '#111827',
                strokeWeight: 2
            }
        });

        bounds.extend(marker.position);

        // Add click event to show info window
        marker.addListener('click', () => {
            const content = `
                <div style="padding: 10px; max-width: 250px;">
                    <h3 style="font-weight: bold; margin-bottom: 8px; color: #111827;">${location.name}</h3>
                    <p style="color: #666; margin-bottom: 8px;">${location.address}</p>
                    <a href="https://www.google.com/maps/dir/?api=1&destination=${location.lat},${location.lng}"
                       target="_blank"
                       style="color: #FFD700; font-weight: 600; text-decoration: none;">
                        Get Directions →
                    </a>
                </div>
            `;
            infoWindow.setContent(content);
            infoWindow.open(map, marker);
        });
    });

    // Fit map to show all markers
    if (locations.length > 1) {
        map.fitBounds(bounds);
    }
}