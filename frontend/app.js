// ES6 module imports
import { switchTab, initTabKeyboard } from './tabs.js';
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
import {
    initBatteryForm,
    getBatteryInput,
    showFieldError as showBatteryFieldError,
    clearErrors as clearBatteryErrors
} from './battery-forms.js';
import {
    initBatterySoCChart,
    updateBatterySoCChart
} from './battery-charts.js';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    loadDefaults();
    setupForm();
    setupBatteryForm();
    initDailyChart(document.getElementById('dailyChart'));
    initYearlyChart(document.getElementById('yearlyChart'));
    initBatterySoCChart('battery-soc-chart');
});

function setupTabs() {
    // Attach click listeners to all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            switchTab(tabId);
        });
    });

    // Initialize keyboard navigation (Arrow keys)
    initTabKeyboard();

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

function setupBatteryForm() {
    initBatteryForm();

    // Add battery Simulate button listener
    const batteryBtn = document.getElementById('batterySimulateBtn');
    if (batteryBtn) {
        batteryBtn.addEventListener('click', handleBatterySubmit);
    }
}

async function handleSubmit(e) {
    e.preventDefault();

    const btn = document.getElementById('simulateBtn');

    try {
        // Clear previous errors and results
        clearErrors();
        document.getElementById('formError').hidden = true;
        document.getElementById('loadingIndicator').hidden = false;
        document.getElementById('resultsSection').hidden = true;

        // Show button loading state
        btn.disabled = true;
        btn.textContent = 'Simulating…';

        // Get form data and call API
        const payload = readSolarForm();
        console.log('Calling simulateSolar...');
        const result = await simulateSolar(payload);
        console.log('API returned, hiding loading indicator...');

        // Hide loading indicator
        const loadingEl = document.getElementById('loadingIndicator');
        console.log('Loading indicator element:', loadingEl);
        loadingEl.hidden = true;
        console.log('After setting hidden=true, hidden is:', loadingEl.hidden);

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
    } finally {
        // Always restore button state
        btn.disabled = false;
        btn.textContent = 'Simulate';
    }
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

async function handleBatterySubmit() {
    // Clear previous errors and results
    clearBatteryErrors();
    document.getElementById('batteryFormError').hidden = true;
    document.getElementById('batteryLoadingIndicator').hidden = false;
    document.getElementById('batteryResultsSection').hidden = true;

    // Get solar form data (must have been simulated first)
    const solarPayload = readSolarForm();

    // Get battery form data
    const batteryInput = getBatteryInput();

    // Merge into single payload
    const payload = { ...solarPayload, ...batteryInput };

    const result = await simulateSolar(payload);

    // Hide loading indicator
    document.getElementById('batteryLoadingIndicator').hidden = true;

    // Handle response
    if (result.error) {
        if (result.status === 422) {
            handleBatteryApiError({ detail: result.detail }, 422);
        } else {
            document.getElementById('batteryFormError').textContent = result.message;
            document.getElementById('batteryFormError').hidden = false;
        }
        return;
    }

    displayBatteryResults(result);
}

function handleBatteryApiError(errorData, status) {
    if (status === 422) {
        // Validation errors from Pydantic
        errorData.detail.forEach(err => {
            const fieldName = err.loc ? err.loc[1] : err.field;
            showBatteryFieldError(fieldName, err.msg || err.message);
        });
    } else {
        document.getElementById('batteryFormError').textContent = errorData.detail || 'Simulation failed';
        document.getElementById('batteryFormError').hidden = false;
    }
}

function displayBatteryResults(data) {
    // Update SoC chart
    if (data.battery_hourly_soc) {
        updateBatterySoCChart(data.battery_hourly_soc);
    }

    // Update result cards
    if (data.self_consumption_pct !== undefined) {
        document.getElementById('battery-self-consumption-card').textContent = data.self_consumption_pct.toFixed(1);
    }
    if (data.grid_export_kwh !== undefined) {
        document.getElementById('battery-grid-export-card').textContent = data.grid_export_kwh.toFixed(1);
    }
    if (data.grid_import_kwh !== undefined) {
        document.getElementById('battery-grid-import-card').textContent = data.grid_import_kwh.toFixed(1);
    }

    // Show results
    Promise.resolve().then(() => {
        document.getElementById('batteryResultsSection').hidden = false;
    });
    document.querySelector('main').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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

    // Show results (use microtask to ensure screen readers detect changes)
    Promise.resolve().then(() => {
        document.getElementById('resultsSection').hidden = false;
    });
    document.querySelector('main').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
