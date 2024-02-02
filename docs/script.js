let map = L.map( 'map', {
    center: [53.4794892,-2.2451148],
    minZoom: 5,
    maxZoom: 8,
    zoom: 6
});

L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png', { //{s}.tile.openstreetmap.org
    attribution: '&copy; <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright/" target="_blank">OpenStreetMap</a>',
}).addTo(map);

let passwordModal = new bootstrap.Modal(document.getElementById('passwordModal'));

function buildPopup(name, location, phone, auth_level) {
    let name_text = `<b>${name}</b>`;
    let location_text = `<br>Location: ${location}`
    let phone_text = (phone == "") ? "" : `<br>Phone: ${phone}`;
    let show_more_text = (auth_level === "PUBLIC" || auth_level === "DENIED") ? '<br><button onclick="displayAuth()">Show more...</button>' : '';
    return `${name_text}${location_text}${phone_text}<br>In WhatsApp group${show_more_text}`
}

async function getUsers(password) {
    const URL = "https://eseaoutdoorsuk-map.vercel.app" //"http://127.0.0.1:5000"//
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
        let markers = L.markerClusterGroup({
            showCoverageOnHover: false,
            maxClusterRadius: 20,
        });
        data.users.forEach(user => {
            user.locations.forEach(location => {
                let [lat, lon] = location.coords.split(',');
                markers.addLayer(
                    L.marker([lat, lon]).bindPopup(buildPopup(user.name, location.name, user.phone, data.auth_level))//.addTo(map);
                );
            })
        });
        map.addLayer(markers);
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