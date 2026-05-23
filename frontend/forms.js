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

export function loadDefaults() {
    document.getElementById('latitude').value = DEFAULTS.latitude;
    document.getElementById('longitude').value = DEFAULTS.longitude;
    document.getElementById('panelCount').value = DEFAULTS.panelCount;
    document.getElementById('panelArea').value = DEFAULTS.panelArea;
    document.getElementById('efficiency').value = DEFAULTS.efficiency;
    document.getElementById('tiltAngle').value = DEFAULTS.tiltAngle;
    document.getElementById('azimuth').value = DEFAULTS.azimuth;
    document.getElementById('startDate').value = DEFAULTS.startDate;
    document.getElementById('duration').value = DEFAULTS.duration;

    // Initialize all required inputs with aria-invalid="false" for consistent ARIA state
    document.querySelectorAll('input[aria-required="true"]').forEach(input => {
        if (!input.hasAttribute('aria-invalid')) {
            input.setAttribute('aria-invalid', 'false');
        }
    });
}

export function readSolarForm() {
    const formData = new FormData(document.getElementById('simulatorForm'));
    return {
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
}

export function showFieldError(fieldId, message) {
    const input = document.getElementById(fieldId);
    if (!input) return;
    const errorElement = input.parentElement.querySelector('.error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
        // Add ARIA attributes to announce error to screen readers
        input.setAttribute('aria-invalid', 'true');
        input.setAttribute('aria-describedby', `error-${fieldId}`);
    }
}

export function clearFieldError(fieldName) {
    const input = document.getElementById(fieldName);
    if (input) {
        const errorElement = input.parentElement.querySelector('.error');
        if (errorElement) {
            errorElement.classList.remove('show');
            // Clear error text immediately to avoid orphaned aria-describedby references
            errorElement.textContent = '';
        }
        // Synchronize ARIA state: only update if input currently has error state
        if (input.getAttribute('aria-invalid') === 'true') {
            input.setAttribute('aria-invalid', 'false');
            input.removeAttribute('aria-describedby');
        }
    }
}

export function clearErrors() {
    document.querySelectorAll('.form-group .error').forEach(el => {
        el.classList.remove('show');
    });
    // Remove ARIA error attributes from all inputs
    document.querySelectorAll('input[aria-invalid]').forEach(input => {
        input.setAttribute('aria-invalid', 'false');
        input.removeAttribute('aria-describedby');
    });
}

export function showFormError(message) {
    const errorDiv = document.getElementById('formError');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

export function updateResultCards(data) {
    document.getElementById('annualEnergy').textContent = data.annual_energy_kwh.toFixed(1);
    document.getElementById('dailyAverage').textContent = data.average_daily_kwh.toFixed(2);
    document.getElementById('peakHour').textContent = data.peak_hour_kw.toFixed(2);
    document.getElementById('capacity').textContent = data.system_capacity_kw.toFixed(2);
}
