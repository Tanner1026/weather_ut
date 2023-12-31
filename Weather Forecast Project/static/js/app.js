// get your key from app.tomorrow.io/development/keys
const API_KEY = 'wOYs2qlYuW7tA76UC3WTeHGpa4LWkXPR'; 

// pick the field (like temperature, precipitationIntensity or cloudCover)
const PRECIP = 'precipitationIntensity';

// set the ISO timestamp (now for all fields, up to 6 hour out for precipitationIntensity)
const TIMESTAMP = (new Date()).toISOString(); 

// initialize the map
var precip_map = L.map('precip_map', {
    minZoom: 3,
    maxZoom: 10
}).setView([40.7608, -111.8910], 1);

// set the streetview
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(precip_map);

// inject the tile layer
L.tileLayer(`https://api.tomorrow.io/v4/map/tile/{z}/{x}/{y}/${PRECIP}/${TIMESTAMP}.png?apikey=${API_KEY}`, {
    attribution: '&copy; <a href="https://www.tomorrow.io/weather-api">Powered by Tomorrow.io</a>',
}).addTo(precip_map);


const HUMIDITY = 'humidity';

// initialize the map
var hum_map = L.map('hum_map', {
    minZoom: 3,
    maxZoom: 10
}).setView([40.7608, -111.8910], 1);

// set the streetview
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(hum_map);

// inject the tile layer
L.tileLayer(`https://api.tomorrow.io/v4/map/tile/{z}/{x}/{y}/${HUMIDITY}/${TIMESTAMP}.png?apikey=${API_KEY}`, {
    attribution: '&copy; <a href="https://www.tomorrow.io/weather-api">Powered by Tomorrow.io</a>',
}).addTo(hum_map);

const VISIBILITY = 'visibility';

// initialize the map
var vis_map = L.map('vis_map', {
    minZoom: 3,
    maxZoom: 10
}).setView([40.7608, -111.8910], 1);

// set the streetview
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(vis_map);

// inject the tile layer
L.tileLayer(`https://api.tomorrow.io/v4/map/tile/{z}/{x}/{y}/${VISIBILITY}/${TIMESTAMP}.png?apikey=${API_KEY}`, {
    attribution: '&copy; <a href="https://www.tomorrow.io/weather-api">Powered by Tomorrow.io</a>',
}).addTo(vis_map);

const PRESSURE_SURFACE = 'pressureSeaLevel';

// initialize the map
var pressure_map = L.map('pressure_map', {
    minZoom: 3,
    maxZoom: 10
}).setView([40.7608, -111.8910], 1);

// set the streetview
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(pressure_map);

// inject the tile layer
L.tileLayer(`https://api.tomorrow.io/v4/map/tile/{z}/{x}/{y}/${PRESSURE_SURFACE}/${TIMESTAMP}.png?apikey=${API_KEY}`, {
    attribution: '&copy; <a href="https://www.tomorrow.io/weather-api">Powered by Tomorrow.io</a>',
}).addTo(pressure_map);