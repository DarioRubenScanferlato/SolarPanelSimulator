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
import {
    initBatteryBreakdownChart,
    updateBatteryBreakdownChart
} from './battery-breakdown-chart.js';
import {
    initBatteryBalanceChart,
    updateBatteryBalanceChart
} from './battery-balance-chart.js';
import {
    initBatteryYearlyChart,
    updateBatteryYearlyChart
} from './battery-yearly-chart.js';
import {
    initCostForm,
    getCostInput,
    showCostFieldError,
    clearCostErrors
} from './cost-forms.js';
import {
    initCostROIChart,
    updateCostROIChart,
    initCostAnnualChart,
    updateCostAnnualChart
} from './cost-charts.js';
import {
    initCostTimelineChart,
    updateCostTimelineChart
} from './cost-timeline-chart.js';
import {
    initCostMonthlyChart,
    updateCostMonthlyChart
} from './cost-monthly-chart.js';

// Tab data inheritance: store solar results for cost tab to use
let lastSolarResult = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    loadDefaults();
    setupForm();
    setupBatteryForm();
    setupCostForm();
    initDailyChart(document.getElementById('dailyChart'));
    initYearlyChart(document.getElementById('yearlyChart'));
    initCostROIChart('cost-roi-chart');
    initCostAnnualChart('cost-annual-chart');
    initCostTimelineChart('cost-timeline-chart');
    initCostMonthlyChart('cost-monthly-chart');
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

    // Initialize battery charts
    initBatterySoCChart('battery-soc-chart');
    initBatteryBreakdownChart('battery-breakdown-chart');
    initBatteryBalanceChart('battery-balance-chart');
    initBatteryYearlyChart('battery-yearly-chart-canvas');

    // Add battery Simulate button listener
    const batteryBtn = document.getElementById('batterySimulateBtn');
    if (batteryBtn) {
        batteryBtn.addEventListener('click', handleBatterySubmit);
    }
}

function setupCostForm() {
    // Initialize cost form with solar data if available
    const capacityKw = lastSolarResult ? lastSolarResult.system_capacity_kw : 0;
    const annualEnergyKwh = lastSolarResult ? lastSolarResult.annual_energy_kwh : null;
    const timestamp = lastSolarResult ? lastSolarResult.calculation_date : null;

    initCostForm(capacityKw, annualEnergyKwh, timestamp);

    // Add cost Simulate button listener
    const costBtn = document.getElementById('costSimulateBtn');
    if (costBtn) {
        costBtn.addEventListener('click', handleCostSubmit);
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
    // Validate battery response has required hourly data
    const missingFields = [];
    if (!data.battery_hourly_soc) missingFields.push('battery_hourly_soc');
    if (!data.battery_hourly_solar_consumption) missingFields.push('battery_hourly_solar_consumption');
    if (!data.battery_hourly_grid_consumption) missingFields.push('battery_hourly_grid_consumption');
    if (!data.battery_hourly_grid_export) missingFields.push('battery_hourly_grid_export');
    if (!data.battery_hourly_charge) missingFields.push('battery_hourly_charge');
    if (!data.hourly_load) missingFields.push('hourly_load');

    if (missingFields.length > 0) {
        console.error('displayBatteryResults: API response missing required fields:', missingFields.join(', '));
        console.warn('Battery charts will be empty until all required fields are provided');
    }

    // Update SoC chart
    if (data.battery_hourly_soc) {
        updateBatterySoCChart(data.battery_hourly_soc);
    } else {
        console.warn('displayBatteryResults: cannot update SoC chart - battery_hourly_soc missing');
    }

    // Update breakdown chart (all 5 hourly arrays MUST be present and valid)
    if (data.battery_hourly_solar_consumption && data.battery_hourly_grid_consumption &&
        data.battery_hourly_grid_export && data.battery_hourly_charge && data.hourly_load) {
        updateBatteryBreakdownChart({
            hourly_solar_consumption: data.battery_hourly_solar_consumption,
            hourly_grid_consumption: data.battery_hourly_grid_consumption,
            hourly_grid_export: data.battery_hourly_grid_export,
            hourly_battery_charge: data.battery_hourly_charge,
            hourly_load: data.hourly_load
        });
    } else {
        console.warn('displayBatteryResults: cannot update breakdown chart - missing or incomplete hourly data');
    }

    // Update yearly chart
    if (data.battery_monthly_solar_consumption || data.battery_monthly_grid_consumption || data.battery_monthly_battery_discharge) {
        updateBatteryYearlyChart({
            monthly_solar_consumption: data.battery_monthly_solar_consumption || [],
            monthly_grid_consumption: data.battery_monthly_grid_consumption || [],
            monthly_battery_discharge: data.battery_monthly_battery_discharge || []
        });
    }

    // Update daily balance chart
    if (data.battery_hourly_solar_consumption || data.battery_hourly_charge ||
        data.battery_hourly_grid_consumption || data.battery_hourly_grid_export) {
        const dailySolarConsumption = (data.battery_hourly_solar_consumption || []).reduce((a, b) => a + b, 0);
        const dailyBatteryCharge = (data.battery_hourly_charge || []).reduce((a, b) => a + b, 0);
        const dailyGridImport = (data.battery_hourly_grid_consumption || []).reduce((a, b) => a + b, 0);
        const dailyGridExport = (data.battery_hourly_grid_export || []).reduce((a, b) => a + b, 0);

        updateBatteryBalanceChart({
            daily_solar_consumption: dailySolarConsumption,
            daily_battery_charge: dailyBatteryCharge,
            daily_grid_import: dailyGridImport,
            daily_grid_export: dailyGridExport
        });
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

async function handleCostSubmit() {
    // Clear previous errors and results
    clearCostErrors();
    document.getElementById('costFormError').hidden = true;
    document.getElementById('costLoadingIndicator').hidden = false;
    document.getElementById('costResultsSection').hidden = true;

    // Get solar form data (from last simulation)
    const solarPayload = readSolarForm();

    // Get cost form data
    const costInput = getCostInput();

    // Merge into single payload
    const payload = { ...solarPayload, ...costInput };

    // DEBUG: Log what's being sent to the backend
    console.log('Cost simulation payload:', payload);
    console.log('Cost fields:', {
        system_cost_eur: payload.system_cost_eur,
        electricity_price_eur_per_kwh: payload.electricity_price_eur_per_kwh,
        feedin_tariff_eur_per_kwh: payload.feedin_tariff_eur_per_kwh,
        lifespan_years: payload.lifespan_years,
        annual_degradation_percent: payload.annual_degradation_percent
    });

    const btn = document.getElementById('costSimulateBtn');
    btn.disabled = true;
    btn.textContent = 'Simulating…';

    try {
        const result = await simulateSolar(payload);

        // Hide loading indicator
        document.getElementById('costLoadingIndicator').hidden = true;

        // DEBUG: Log API response
        console.log('Cost simulation API response:', result);
        console.log('Cost response fields:', {
            cost_year_1_savings: result.cost_year_1_savings,
            cost_breakeven_year: result.cost_breakeven_year,
            cost_cumulative_savings: result.cost_cumulative_savings,
            cost_total_25year_savings: result.cost_total_25year_savings
        });

        // Handle response
        if (result.error) {
            if (result.status === 422) {
                handleCostApiError({ detail: result.detail }, 422);
            } else {
                document.getElementById('costFormError').textContent = result.message;
                document.getElementById('costFormError').hidden = false;
            }
            return;
        }

        displayCostResults(result);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Simulate';
    }
}

function handleCostApiError(errorData, status) {
    if (status === 422) {
        // Validation errors from Pydantic
        errorData.detail.forEach(err => {
            const fieldName = err.loc ? err.loc[1] : err.field;
            showCostFieldError(fieldName, err.msg || err.message);
        });
    } else {
        document.getElementById('costFormError').textContent = errorData.detail || 'Simulation failed';
        document.getElementById('costFormError').hidden = false;
    }
}

function calculateMonthlyBreakdown(data) {
    // Prefer backend-calculated monthly data if available
    if (data.cost_monthly_savings && data.cost_monthly_cost_allocation) {
        if (!Array.isArray(data.cost_monthly_savings) || data.cost_monthly_savings.length !== 12) {
            console.error(`calculateMonthlyBreakdown: cost_monthly_savings must be 12-element array, got ${data.cost_monthly_savings?.length || 'non-array'}`);
            // Fall through to legacy calculation
        } else if (!Array.isArray(data.cost_monthly_cost_allocation) || data.cost_monthly_cost_allocation.length !== 12) {
            console.error(`calculateMonthlyBreakdown: cost_monthly_cost_allocation must be 12-element array, got ${data.cost_monthly_cost_allocation?.length || 'non-array'}`);
            // Fall through to legacy calculation
        } else {
            const netProfit = data.cost_monthly_savings.map((savings, i) => savings - data.cost_monthly_cost_allocation[i]);
            return {
                monthly_savings: data.cost_monthly_savings,
                monthly_cost_allocation: data.cost_monthly_cost_allocation,
                monthly_net_profit: netProfit
            };
        }
    }

    // Legacy calculation: fall back to deriving from annual savings and monthly energy
    if (!data.cost_year_1_savings || !data.monthly_energy_kwh) {
        console.warn('calculateMonthlyBreakdown: missing backend monthly data and unable to calculate from annual savings');
        return null;
    }

    const monthlyEnergyKwh = data.monthly_energy_kwh;

    // Validate array length BEFORE doing expensive calculations
    if (!Array.isArray(monthlyEnergyKwh) || monthlyEnergyKwh.length !== 12) {
        console.error(`calculateMonthlyBreakdown: monthly_energy_kwh must be 12-element array, got ${monthlyEnergyKwh?.length || 'non-array'}`);
        return null;
    }

    const totalAnnualEnergy = monthlyEnergyKwh.reduce((a, b) => a + b, 0);

    // Guard against zero-energy generation (critical financial accuracy)
    if (totalAnnualEnergy === 0) {
        console.warn('calculateMonthlyBreakdown: zero annual generation - cost analysis skipped');
        return null;
    }

    // Distribute annual savings by monthly energy proportion
    const annualSavings = data.cost_year_1_savings;
    const monthlyContribution = monthlyEnergyKwh.map(energy => {
        return (energy / totalAnnualEnergy) * annualSavings;
    });

    // Calculate monthly cost allocation (system cost amortized over 25 years)
    const systemCost = data.cost_system_cost_eur || 0;
    const monthlyAmortization = systemCost / (25 * 12);
    const monthlyCostAllocation = Array(12).fill(monthlyAmortization);

    // Pre-compute net profit to avoid recalculation in cost-monthly-chart.js
    const netProfit = monthlyContribution.map((savings, i) => savings - monthlyCostAllocation[i]);

    return {
        monthly_savings: monthlyContribution,
        monthly_cost_allocation: monthlyCostAllocation,
        monthly_net_profit: netProfit
    };
}

function displayCostResults(data) {
    // Update ROI chart
    if (data.cost_cumulative_savings && data.cost_total_25year_savings !== undefined) {
        updateCostROIChart(
            data.cost_cumulative_savings,
            data.system_cost_eur || 0,
            data.cost_breakeven_year
        );
    }

    // Update annual savings chart
    if (data.cost_cumulative_savings) {
        // Convert cumulative to annual savings
        const annualSavings = data.cost_cumulative_savings.map((cumulative, index) => {
            return index === 0 ? cumulative : cumulative - data.cost_cumulative_savings[index - 1];
        });
        updateCostAnnualChart(annualSavings);
    }

    // Update timeline chart
    if (data.cost_cumulative_savings && data.cost_system_cost_eur !== undefined) {
        if (!Array.isArray(data.cost_cumulative_savings)) {
            console.error('displayCostResults: cost_cumulative_savings is not an array; timeline chart cannot be updated');
        } else if (data.cost_cumulative_savings.length !== 25) {
            console.error(`displayCostResults: cost_cumulative_savings has ${data.cost_cumulative_savings.length} elements; timeline chart requires 25`);
        }
        updateCostTimelineChart({
            system_cost_eur: data.cost_system_cost_eur || 0,
            breakeven_year: data.cost_breakeven_year,
            cumulative_savings: data.cost_cumulative_savings
        });
    } else {
        console.warn('displayCostResults: cannot update timeline chart - missing cost_cumulative_savings or cost_system_cost_eur');
    }

    // Update monthly breakdown chart
    const monthlyBreakdown = calculateMonthlyBreakdown(data);
    if (monthlyBreakdown) {
        updateCostMonthlyChart(monthlyBreakdown);
    } else {
        console.warn('displayCostResults: monthly breakdown not available - check console errors above');
        if (data.cost_year_1_savings === 0) {
            const errorMsg = document.createElement('p');
            errorMsg.className = 'cost-error-message';
            errorMsg.textContent = 'Monthly breakdown unavailable: system generated zero energy';
            const costSection = document.getElementById('costResultsSection');
            costSection.querySelector('.cost-error-message')?.remove();
            costSection.insertBefore(errorMsg, costSection.firstChild);
        }
    }

    // Update result cards
    if (data.cost_year_1_savings !== undefined) {
        document.getElementById('cost-year1-savings-card').textContent = data.cost_year_1_savings.toFixed(2);
    }
    if (data.cost_breakeven_year !== undefined && data.cost_breakeven_year !== null) {
        document.getElementById('cost-breakeven-card').textContent = `Year ${data.cost_breakeven_year}`;
    } else {
        document.getElementById('cost-breakeven-card').textContent = 'No payback within 25 years';
    }
    if (data.cost_total_25year_savings !== undefined) {
        document.getElementById('cost-total-25year-card').textContent = data.cost_total_25year_savings.toFixed(2);
    }

    // Show results
    Promise.resolve().then(() => {
        document.getElementById('costResultsSection').hidden = false;
    });
    document.querySelector('main').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function displayResults(data) {
    // Store solar result for cost tab inheritance
    lastSolarResult = data;

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
