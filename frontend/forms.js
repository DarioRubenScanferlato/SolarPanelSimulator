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
    }
}

export function clearFieldError(fieldName) {
    const input = document.getElementById(fieldName);
    if (input) {
        const errorElement = input.parentElement.querySelector('.error');
        if (errorElement) {
            errorElement.classList.remove('show');
        }
    }
}

export function clearErrors() {
    document.querySelectorAll('.form-group .error').forEach(el => {
        el.classList.remove('show');
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
