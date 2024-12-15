let map = L.map( 'map', {
    center: [53.4794892,-2.2451148],
    minZoom: 5,
    maxZoom: 12,
    zoom: 6
});

L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png', { //{s}.tile.openstreetmap.org
    attribution: '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright/" target="_blank">OpenStreetMap</a>',
}).addTo(map);

// Legend
let legend = L.control({ position: 'topright' });

legend.onAdd = function () {
    const div = L.DomUtil.create('div', 'legend');

    div.innerHTML = `
      <label>
        <input type="checkbox" id="toggle-users" checked />
        <i class="icon-users"></i> Show members
        <input type="checkbox" id="toggle-trips" checked />
        <i class="icon-trips"></i> Show meetups
      </label>
    `;
    L.DomEvent.disableClickPropagation(div);
    return div;
};
legend.addTo(map);

let markers = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 20,
});
let markers2 = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 5,
});

document.getElementById('toggle-users').addEventListener('change', function (e) {
    if (e.target.checked) {map.addLayer(markers);
    } else {map.removeLayer(markers);}
});

document.getElementById('toggle-trips').addEventListener('change', function (e) {
    if (e.target.checked) {map.addLayer(markers2);
    } else {map.removeLayer(markers2);}
});

let passwordModal = new bootstrap.Modal(document.getElementById('passwordModal'));
let welcomeModal = new bootstrap.Modal(document.getElementById('welcomeModal'));

function buildUserPopup(name, location, phone, auth_level) {
    let name_text = `<b>${name}</b>`;
    let location_text = `<br>📍 ${location}`
    let phone_text = (phone == "") ? "" : `<br>📞 ${phone}`;
    let show_more_text = (auth_level === "PUBLIC" || auth_level === "DENIED") ? '<br><button onclick="displayAuth()">Show more...</button>' : '';
    return `${name_text}${location_text}${phone_text}<br>In Heylo community${show_more_text}`
}

function buildTripPopup(name, details, location, date, auth_level) {
    let name_text = `<b>${name}</b>`;
    let detail_text = `<br>${details}`;
    let location_text = `<br>📍 ${location}`
    let date_text = (date == "") ? "" : `<br>📅 ${date}`;
    return `${name_text}${detail_text}${location_text}${date_text}`
}

let goldIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

async function getUsers(password) {
    const URL = "http://127.0.0.1:5000"//"https://eseaoutdoorsuk-map.vercel.app" //
    try {
        document.getElementById('spinner').style.display = 'block'
        const response = await fetch(`${URL}/getUsers?password=${password}`);
        if (response) {
            document.getElementById('spinner').style.display = 'none'
            document.getElementById('spinner').style.width = 0
            document.getElementById('spinner').style.height = 0
            document.getElementById('spinner').style.zIndex = 1
            document.getElementById('overlay').style.display = 'none'
            document.getElementById('overlay').style.width = 0
            document.getElementById('overlay').style.height = 0
            document.getElementById('overlay').style.zIndex = 1
        }
        const data = await response.json();
        data.users.forEach(user => {
            user.locations.forEach(location => {
                let [lat, lon] = location.coords.split(',');
                markers.addLayer(
                    L.marker([lat, lon]).bindPopup(buildUserPopup(user.name, location.name, user.phone, data.auth_level))
                );
            })
        });
        data.trips.forEach(trip => {
            trip.locations.forEach(location => {
                let [lat, lon] = location.coords.split(',');
                let marker = L.marker([lat, lon], {icon: goldIcon}).bindPopup(buildTripPopup(trip.name, trip.details, location.name, trip.date, data.auth_level))
                markers2.addLayer(marker);
            })
        });        
        map.addLayer(markers);
        map.addLayer(markers2);

        return data.auth_level;
    } catch (error) {
        console.error('Error:', error);
        return "";
    }
}

function displayAuth() {
    document.getElementById("errorLabel").style.display = "none";
    document.getElementById('passwordInput').value = "";
    passwordModal.show();
}

function onStartup() {
    passwordModal.hide();
    welcomeModal.show();
    getUsers("");
}

async function onLogin() {
    let password = document.getElementById('passwordInput').value;
    let errorLabel = document.getElementById("errorLabel");
    errorLabel.style.display = "none";

    if (password == "") {
        errorLabel.style.display = "inline";
        errorLabel.textContent = "Please enter a password.";
    } else {
        switch (await getUsers(password)) {
            case 'DENIED':
                errorLabel.style.display = "inline";
                errorLabel.textContent = "Incorrect password. Please try again.";
                break;
            case '':
                errorLabel.style.display = "inline";
                errorLabel.textContent = "Unknown error occured. Please try again later.";
                break;
            default:
                passwordModal.hide();
        };
    }
}