// Secure IoT Dashboard JavaScript

// API endpoint for sensor data (updated port from 5000 to 5001)
const API_URL = 'http://localhost:5001/api/sensor-data';  //REST API

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

// Security elements
const authenticationStatusElement = document.getElementById('authentication-status');
const integrityStatusElement = document.getElementById('integrity-status');
const deviceIdElement = document.getElementById('device-id');
const lastVerifiedElement = document.getElementById('last-verified');

// Format the date and time
function formatDateTime(timestamp) {
    if (!timestamp) return 'Never';
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

// Update security status display
function updateSecurityStatus(securityStatus) {
    // Update authentication status
    if (authenticationStatusElement) {
        const isAuthenticated = securityStatus.is_authenticated;
        authenticationStatusElement.textContent = isAuthenticated ? 'Verified' : 'Unverified';
        
        // Update indicator classes
        const authIndicator = authenticationStatusElement.previousElementSibling;
        if (authIndicator) {
            authIndicator.className = 'security-indicator';
            authIndicator.classList.add(isAuthenticated ? 'security-secure' : 'security-warning');
        }
    }
    
    // Update message integrity status
    if (integrityStatusElement) {
        const integrityStatus = securityStatus.message_integrity;
        let integrityText = 'Unknown';
        let integrityClass = 'security-unknown';
        
        switch (integrityStatus) {
            case 'verified':
                integrityText = 'Verified';
                integrityClass = 'security-secure';
                break;
            case 'verified_encrypted':
                integrityText = 'Verified & Encrypted';
                integrityClass = 'security-secure';
                break;
            case 'unverified':
                integrityText = 'Unverified';
                integrityClass = 'security-warning';
                break;
            case 'invalid':
                integrityText = 'Invalid Signature';
                integrityClass = 'security-breach';
                break;
            case 'decryption_failed':
                integrityText = 'Decryption Failed';
                integrityClass = 'security-breach';
                break;
            default:
                integrityText = 'Unknown';
                integrityClass = 'security-unknown';
        }
        
        integrityStatusElement.textContent = integrityText;
        const integrityIndicator = integrityStatusElement.previousElementSibling;
        if (integrityIndicator) {
            integrityIndicator.className = 'security-indicator';
            integrityIndicator.classList.add(integrityClass);
        }
    }
    
    // Update last verified time
    if (lastVerifiedElement) {
        if (securityStatus.last_verified_timestamp) {
            lastVerifiedElement.textContent = formatDateTime(securityStatus.last_verified_timestamp);
        } else {
            lastVerifiedElement.textContent = 'Never';
        }
    }
    
    // Update device ID
    if (deviceIdElement && securityStatus.device_id) {
        deviceIdElement.textContent = securityStatus.device_id || 'Unknown';
    }
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
            console.log('Received data:', data);
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
    
    // Update security status
    if (data.security_status) {
        updateSecurityStatus(data.security_status);
    }
    
    // Update alerts
    if (data.alerts && Array.isArray(data.alerts)) {
        if (data.alerts.length > 0) {
            // Create HTML for alerts with special styling for security alerts
            const alertsHTML = data.alerts.map(alert => {
                if (alert.includes('SECURITY ALERT')) {
                    return `<div class="security-alert">${alert}</div>`;
                } else {
                    return `<div class="alert-item">${alert}</div>`;
                }
            }).join('');
            
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
console.log('Secure IoT Agriculture Monitoring Dashboard started'); 