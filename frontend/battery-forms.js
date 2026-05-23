const BATTERY_DEFAULTS = {
    capacity: 10,
    chargeEfficiency: 95,
    dischargeEfficiency: 95,
    dailyLoad: 10,
    initialSoC: 50
};

export function initBatteryForm() {
    const container = document.getElementById('battery-panel');
    if (!container) return;

    const formHTML = `
        <div class="form-section">
            <h2>Battery Parameters</h2>
            <div class="form-grid">
                <div class="form-group">
                    <label for="battery_capacity_kwh">Battery Capacity (kWh)</label>
                    <input type="number" id="battery_capacity_kwh" name="battery_capacity_kwh" min="1" step="0.1" value="${BATTERY_DEFAULTS.capacity}" required aria-required="true" aria-describedby="error-battery_capacity_kwh">
                    <span class="error" id="error-battery_capacity_kwh"></span>
                </div>

                <div class="form-group">
                    <label for="battery_charge_efficiency">Charge Efficiency (%)</label>
                    <input type="number" id="battery_charge_efficiency" name="battery_charge_efficiency" min="80" max="99" value="${BATTERY_DEFAULTS.chargeEfficiency}" required aria-required="true" aria-describedby="error-battery_charge_efficiency">
                    <span class="error" id="error-battery_charge_efficiency"></span>
                </div>

                <div class="form-group">
                    <label for="battery_discharge_efficiency">Discharge Efficiency (%)</label>
                    <input type="number" id="battery_discharge_efficiency" name="battery_discharge_efficiency" min="80" max="99" value="${BATTERY_DEFAULTS.dischargeEfficiency}" required aria-required="true" aria-describedby="error-battery_discharge_efficiency">
                    <span class="error" id="error-battery_discharge_efficiency"></span>
                </div>

                <div class="form-group">
                    <label for="daily_load_kwh">Daily Load (kWh)</label>
                    <input type="number" id="daily_load_kwh" name="daily_load_kwh" min="0.1" step="0.1" value="${BATTERY_DEFAULTS.dailyLoad}" required aria-required="true" aria-describedby="error-daily_load_kwh">
                    <span class="error" id="error-daily_load_kwh"></span>
                </div>

                <div class="form-group">
                    <label for="initial_soc_pct">Initial State of Charge (%)</label>
                    <input type="number" id="initial_soc_pct" name="initial_soc_pct" min="0" max="100" value="${BATTERY_DEFAULTS.initialSoC}" required aria-required="true" aria-describedby="error-initial_soc_pct">
                    <span class="error" id="error-initial_soc_pct"></span>
                </div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', formHTML);
}

export function getBatteryInput() {
    return {
        battery_capacity_kwh: parseFloat(document.getElementById('battery_capacity_kwh').value),
        battery_charge_efficiency: parseFloat(document.getElementById('battery_charge_efficiency').value),
        battery_discharge_efficiency: parseFloat(document.getElementById('battery_discharge_efficiency').value),
        daily_load_kwh: parseFloat(document.getElementById('daily_load_kwh').value),
        initial_soc_pct: parseFloat(document.getElementById('initial_soc_pct').value)
    };
}

export function showFieldError(fieldId, message) {
    const input = document.getElementById(fieldId);
    if (!input) return;
    const errorElement = input.parentElement.querySelector('.error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
        input.setAttribute('aria-invalid', 'true');
        input.setAttribute('aria-describedby', `error-${fieldId}`);
    }
}

export function clearErrors() {
    const container = document.getElementById('battery-panel');
    if (!container) return;
    container.querySelectorAll('.form-group .error').forEach(el => {
        el.classList.remove('show');
        el.textContent = '';
    });
    container.querySelectorAll('input[aria-invalid]').forEach(input => {
        input.setAttribute('aria-invalid', 'false');
        input.removeAttribute('aria-describedby');
    });
}
