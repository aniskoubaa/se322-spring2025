// IoT Dashboard JavaScript

// API endpoint for sensor data
const API_URL = 'http://localhost:5000/api/sensor-data';

// Update interval in milliseconds (2 seconds)
const UPDATE_INTERVAL = 2000;

// Thresholds for highlighting values
const THRESHOLDS = {
    temperature: { min: 0, max: 35 },
    humidity: { min: 30, max: 100 },
    soil_moisture: { min: 250, max: 800 }
};

// Elements to update
const temperatureElement = document.getElementById('temperature');
const humidityElement = document.getElementById('humidity');
const soilMoistureElement = document.getElementById('soil-moisture');
const alertsContainer = document.getElementById('alerts-container');
const lastUpdateElement = document.getElementById('last-update');

// Format the date and time
function formatDateTime(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

// Check if a value is in the normal range
function isInNormalRange(value, type) {
    return value >= THRESHOLDS[type].min && value <= THRESHOLDS[type].max;
}

// Add appropriate class based on value
function setValueClass(element, value, type) {
    element.classList.remove('normal', 'warning');
    element.classList.add(isInNormalRange(value, type) ? 'normal' : 'warning');
}

// Fetch data from the API
function fetchSensorData() {
    fetch(API_URL)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateDashboard(data);
        })
        .catch(error => {
            console.error('Error fetching sensor data:', error);
        });
}

// Update the dashboard with new data
function updateDashboard(data) {
    // Update sensor values
    if (data.temperature) {
        temperatureElement.textContent = data.temperature;
        setValueClass(temperatureElement, data.temperature, 'temperature');
    }
    
    if (data.humidity) {
        humidityElement.textContent = data.humidity;
        setValueClass(humidityElement, data.humidity, 'humidity');
    }
    
    if (data.soil_moisture) {
        soilMoistureElement.textContent = data.soil_moisture;
        setValueClass(soilMoistureElement, data.soil_moisture, 'soil_moisture');
    }
    
    // Update alerts
    if (data.alerts && Array.isArray(data.alerts)) {
        if (data.alerts.length > 0) {
            // Create HTML for alerts
            const alertsHTML = data.alerts.map(alert => 
                `<div class="alert-item">${alert}</div>`
            ).join('');
            alertsContainer.innerHTML = alertsHTML;
        } else {
            alertsContainer.innerHTML = '<div class="no-alerts">No alerts at this time</div>';
        }
    }
    
    // Update last update time
    if (data.timestamp) {
        lastUpdateElement.textContent = `Last updated: ${formatDateTime(data.timestamp)}`;
    }
}

// Initial data fetch
fetchSensorData();

// Set up periodic updates
setInterval(fetchSensorData, UPDATE_INTERVAL);

// Log to console that the dashboard is running
console.log('IoT Agriculture Monitoring Dashboard started'); 