// Configuration
const API_URL = 'http://localhost:8000/simulate';
const DEFAULTS = {
    latitude: 45.0703,
    longitude: 7.6869,
    panelCount: 10,
    panelArea: 2.0,
    efficiency: 20,
    tiltAngle: 35,
    azimuth: 180,
    startDate: new Date().toISOString().split('T')[0],
    duration: 365
};

// Chart instances
let dailyChart = null;
let yearlyChart = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDefaults();
    setupForm();
    initializeCharts();
});

function loadDefaults() {
    document.getElementById('latitude').value = DEFAULTS.latitude;
    document.getElementById('longitude').value = DEFAULTS.longitude;
    document.getElementById('panelCount').value = DEFAULTS.panelCount;
    document.getElementById('panelArea').value = DEFAULTS.panelArea;
    document.getElementById('efficiency').value = DEFAULTS.efficiency;
    document.getElementById('tiltAngle').value = DEFAULTS.tiltAngle;
    document.getElementById('azimuth').value = DEFAULTS.azimuth;
    document.getElementById('startDate').value = DEFAULTS.startDate;
    document.getElementById('duration').value = DEFAULTS.duration;
}

function setupForm() {
    const form = document.getElementById('simulatorForm');
    form.addEventListener('submit', handleSubmit);

    // Clear errors on input
    form.querySelectorAll('input').forEach(input => {
        input.addEventListener('change', () => {
            clearFieldError(input.name);
        });
    });
}

function initializeCharts() {
    const dailyCtx = document.getElementById('dailyChart').getContext('2d');
    dailyChart = new Chart(dailyCtx, {
        type: 'line',
        data: {
            labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
            datasets: [{
                label: 'Power (kW)',
                data: Array(24).fill(0),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.parsed.y.toFixed(2)} kW`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (value) => `${value} kW` }
                }
            }
        }
    });

    const yearlyCtx = document.getElementById('yearlyChart').getContext('2d');
    yearlyChart = new Chart(yearlyCtx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Energy (kWh)',
                data: Array(12).fill(0),
                backgroundColor: '#764ba2',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.parsed.y.toFixed(1)} kWh`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (value) => `${value} kWh` }
                }
            }
        }
    });
}

async function handleSubmit(e) {
    e.preventDefault();

    // Clear previous errors and results
    clearAllErrors();
    document.getElementById('formError').style.display = 'none';

    // Get form data
    const formData = new FormData(document.getElementById('simulatorForm'));
    const payload = {
        latitude: parseFloat(formData.get('latitude')),
        longitude: parseFloat(formData.get('longitude')),
        panel_count: parseInt(formData.get('panelCount')),
        panel_area_m2: parseFloat(formData.get('panelArea')),
        panel_efficiency: parseFloat(formData.get('efficiency')),
        tilt_angle_deg: parseFloat(formData.get('tiltAngle')),
        azimuth_deg: parseFloat(formData.get('azimuth')),
        start_date: formData.get('startDate'),
        duration_days: parseInt(formData.get('duration'))
    };

    // Show loading indicator
    document.getElementById('loadingIndicator').style.display = 'flex';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('simulateBtn').disabled = true;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            handleApiError(errorData, response.status);
            return;
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        showFormError(`Failed to connect to backend: ${error.message}`);
    } finally {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('simulateBtn').disabled = false;
    }
}

function handleApiError(errorData, status) {
    if (status === 422) {
        // Validation errors from Pydantic
        errorData.detail.forEach(err => {
            const fieldName = err.loc[1];
            showFieldError(fieldName, err.msg);
        });
    } else {
        showFormError(errorData.detail || 'Simulation failed');
    }
}

function displayResults(data) {
    // Update cards
    document.getElementById('annualEnergy').textContent = data.annual_energy_kwh.toFixed(1);
    document.getElementById('dailyAverage').textContent = data.average_daily_kwh.toFixed(2);
    document.getElementById('peakHour').textContent = data.peak_hour_kw.toFixed(2);
    document.getElementById('capacity').textContent = data.system_capacity_kw.toFixed(2);

    // Update daily chart
    dailyChart.data.datasets[0].data = data.daily_hourly_generation;
    dailyChart.update();

    // Update daily info
    document.getElementById('dailyInfo').textContent =
        `${data.daily_sunrise} - ${data.daily_sunset} | Daily Total: ${
            data.daily_hourly_generation.reduce((a, b) => a + b, 0).toFixed(2)
        } kWh`;

    // Update yearly chart
    yearlyChart.data.datasets[0].data = data.monthly_energy_kwh;
    yearlyChart.update();

    // Show results
    document.getElementById('resultsSection').style.display = 'block';
    document.querySelector('main').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showFieldError(fieldName, message) {
    const input = document.getElementById(
        fieldName.replace(/_/g, '')  // Remove underscores for input id matching
            .replace(/([A-Z])/g, (m) => m.toLowerCase())  // camelCase to lowercase
    );

    if (!input) return;

    const errorElement = input.parentElement.querySelector('.error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
}

function clearFieldError(fieldName) {
    const input = document.getElementById(fieldName);
    if (input) {
        const errorElement = input.parentElement.querySelector('.error');
        if (errorElement) {
            errorElement.classList.remove('show');
        }
    }
}

function clearAllErrors() {
    document.querySelectorAll('.form-group .error').forEach(el => {
        el.classList.remove('show');
    });
}

function showFormError(message) {
    const errorDiv = document.getElementById('formError');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}
