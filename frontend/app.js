// ES6 module imports
import { switchTab } from './tabs.js';
import { simulateSolar } from './api.js';
import {
    loadDefaults,
    readSolarForm,
    showFieldError,
    clearErrors,
    showFormError,
    updateResultCards
} from './forms.js';
import {
    initDailyChart,
    initYearlyChart,
    updateDailyChart,
    updateYearlyChart
} from './charts.js';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    loadDefaults();
    setupForm();
    initDailyChart(document.getElementById('dailyChart'));
    initYearlyChart(document.getElementById('yearlyChart'));
});

function setupTabs() {
    // Attach click listeners to all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            switchTab(tabId);
        });
    });

    // Initialize to Solar tab
    switchTab('solar');
}

function setupForm() {
    const form = document.getElementById('simulatorForm');
    form.addEventListener('submit', handleSubmit);

    // Clear errors on input
    form.querySelectorAll('input').forEach(input => {
        input.addEventListener('change', () => {
            clearErrors();
        });
    });
}

async function handleSubmit(e) {
    e.preventDefault();

    // Clear previous errors and results
    clearErrors();
    document.getElementById('formError').style.display = 'none';
    document.getElementById('loadingIndicator').style.display = 'flex';
    document.getElementById('resultsSection').style.display = 'none';

    // Get form data and call API
    const payload = readSolarForm();
    const result = await simulateSolar(payload);

    // Hide loading indicator
    document.getElementById('loadingIndicator').style.display = 'none';

    // Handle response
    if (result.error) {
        if (result.status === 422) {
            handleApiError({ detail: result.detail }, 422);
        } else {
            showFormError(result.message);
        }
        return;
    }

    displayResults(result);
}

function handleApiError(errorData, status) {
    if (status === 422) {
        // Validation errors from Pydantic
        errorData.detail.forEach(err => {
            const fieldName = err.loc[1];
            const fieldId = convertFieldNameToId(fieldName);
            showFieldError(fieldId, err.msg);
        });
    } else {
        showFormError(errorData.detail || 'Simulation failed');
    }
}

function convertFieldNameToId(fieldName) {
    // Convert snake_case API field names to camelCase input IDs
    // "panel_count" -> "panelCount", "tilt_angle_deg" -> "tiltAngle", etc.
    return fieldName.replace(/_([a-z])/g, (_, char) => char.toUpperCase());
}

function displayResults(data) {
    // Update result cards
    updateResultCards(data);

    // Update daily chart
    updateDailyChart(data.daily_hourly_generation);

    // Update daily info
    document.getElementById('dailyInfo').textContent =
        `${data.daily_sunrise} - ${data.daily_sunset} | Daily Total: ${
            data.daily_hourly_generation.reduce((a, b) => a + b, 0).toFixed(2)
        } kWh`;

    // Update yearly chart
    updateYearlyChart(data.monthly_energy_kwh);

    // Show results
    document.getElementById('resultsSection').style.display = 'block';
    document.querySelector('main').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
