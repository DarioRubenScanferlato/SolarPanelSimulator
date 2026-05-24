const COST_DEFAULTS_MULTIPLIERS = {
    systemCostPerKwEur: 1800,  // €1,800/kW (Italian standard)
    electricityPriceEurPerKwh: 0.32,  // €0.32/kWh (Italian residential)
    feedinTariffEurPerKwh: 0.12,  // €0.12/kWh (scambio sul posto)
    lifespanYears: 25,
    annualDegradationPercent: 0.5
};

export function initCostForm(capacityKw, annualEnergyKwh, lastSimulationTimestamp) {
    const container = document.getElementById('panel-cost');
    if (!container) return;

    // Calculate system cost based on capacity, default to 25000 if no capacity provided
    const systemCostEur = capacityKw ? (capacityKw * COST_DEFAULTS_MULTIPLIERS.systemCostPerKwEur) : 25000;

    // Format inheritance notice
    const inheritanceNotice = buildInheritanceNotice(annualEnergyKwh, lastSimulationTimestamp);

    const formHTML = `
        <div id="cost-inheritance-notice" class="inheritance-notice">
            ${inheritanceNotice}
        </div>

        <div class="form-section">
            <h2>Cost Analysis Parameters</h2>
            <div class="form-grid">
                <div class="form-group">
                    <label for="system_cost_eur">System Cost (€)</label>
                    <input type="number" id="system_cost_eur" name="system_cost_eur" min="0" step="0.01" value="${systemCostEur.toFixed(2)}" required aria-required="true" aria-describedby="error-system_cost_eur">
                    <span class="error" id="error-system_cost_eur"></span>
                </div>

                <div class="form-group">
                    <label for="electricity_price_eur_per_kwh">Electricity Price (€/kWh)</label>
                    <input type="number" id="electricity_price_eur_per_kwh" name="electricity_price_eur_per_kwh" min="0" step="0.01" value="${COST_DEFAULTS_MULTIPLIERS.electricityPriceEurPerKwh}" required aria-required="true" aria-describedby="error-electricity_price_eur_per_kwh">
                    <span class="error" id="error-electricity_price_eur_per_kwh"></span>
                </div>

                <div class="form-group">
                    <label for="feedin_tariff_eur_per_kwh">Feed-in Tariff (€/kWh)</label>
                    <input type="number" id="feedin_tariff_eur_per_kwh" name="feedin_tariff_eur_per_kwh" min="0" step="0.01" value="${COST_DEFAULTS_MULTIPLIERS.feedinTariffEurPerKwh}" required aria-required="true" aria-describedby="error-feedin_tariff_eur_per_kwh">
                    <span class="error" id="error-feedin_tariff_eur_per_kwh"></span>
                </div>

                <div class="form-group">
                    <label for="lifespan_years">System Lifespan (years)</label>
                    <input type="number" id="lifespan_years" name="lifespan_years" min="1" step="1" value="${COST_DEFAULTS_MULTIPLIERS.lifespanYears}" required aria-required="true" aria-describedby="error-lifespan_years">
                    <span class="error" id="error-lifespan_years"></span>
                </div>

                <div class="form-group">
                    <label for="annual_degradation_percent">Annual Degradation (%/year)</label>
                    <input type="number" id="annual_degradation_percent" name="annual_degradation_percent" min="0" max="100" step="0.1" value="${COST_DEFAULTS_MULTIPLIERS.annualDegradationPercent}" required aria-required="true" aria-describedby="error-annual_degradation_percent">
                    <span class="error" id="error-annual_degradation_percent"></span>
                </div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', formHTML);
}

function buildInheritanceNotice(annualEnergyKwh, lastSimulationTimestamp) {
    if (!annualEnergyKwh || !lastSimulationTimestamp) {
        return 'Run Battery tab simulation first for accurate cost analysis with self-consumption rates.';
    }

    return `Using generation from Solar tab: ${annualEnergyKwh.toFixed(1)} kWh/year (calculated at ${lastSimulationTimestamp})`;
}

export function getCostInput() {
    return {
        system_cost_eur: parseFloat(document.getElementById('system_cost_eur').value),
        electricity_price_eur_per_kwh: parseFloat(document.getElementById('electricity_price_eur_per_kwh').value),
        feedin_tariff_eur_per_kwh: parseFloat(document.getElementById('feedin_tariff_eur_per_kwh').value),
        lifespan_years: parseInt(document.getElementById('lifespan_years').value),
        annual_degradation_percent: parseFloat(document.getElementById('annual_degradation_percent').value)
    };
}

export function showCostFieldError(fieldId, message) {
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

export function clearCostErrors() {
    const container = document.getElementById('panel-cost');
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
