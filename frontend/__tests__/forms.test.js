const {
  loadDefaults,
  readSolarForm,
  showFieldError,
  clearFieldError,
  clearErrors,
  showFormError,
  updateResultCards
} = require('../forms.js');

describe('forms.js', () => {
  beforeEach(() => {
    // Setup form DOM structure
    document.body.innerHTML = `
      <form id="simulatorForm">
        <div class="form-group">
          <input id="latitude" name="latitude" value="">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="longitude" name="longitude" value="">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="panelCount" name="panelCount" value="">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="panelArea" name="panelArea" value="">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="efficiency" name="efficiency" value="">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="tiltAngle" name="tiltAngle" value="">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="azimuth" name="azimuth" value="">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="startDate" name="startDate" value="">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="duration" name="duration" value="">
          <span class="error"></span>
        </div>
      </form>
      <div id="formError"></div>
      <div id="annualEnergy">0</div>
      <div id="dailyAverage">0</div>
      <div id="peakHour">0</div>
      <div id="capacity">0</div>
    `;
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('loadDefaults', () => {
    test('sets all form fields to Turin default values', () => {
      loadDefaults();

      expect(document.getElementById('latitude').value).toBe('45.0703');
      expect(document.getElementById('longitude').value).toBe('7.6869');
      expect(document.getElementById('panelCount').value).toBe('10');
      expect(document.getElementById('panelArea').value).toBe('2');
      expect(document.getElementById('efficiency').value).toBe('20');
      expect(document.getElementById('tiltAngle').value).toBe('35');
      expect(document.getElementById('azimuth').value).toBe('180');
      expect(document.getElementById('duration').value).toBe('365');
    });

    test('sets startDate to today', () => {
      const today = new Date().toISOString().split('T')[0];
      loadDefaults();
      expect(document.getElementById('startDate').value).toBe(today);
    });
  });

  describe('readSolarForm', () => {
    test('collects all form values', () => {
      document.getElementById('latitude').value = '45';
      document.getElementById('longitude').value = '7';
      document.getElementById('panelCount').value = '10';
      document.getElementById('panelArea').value = '2';
      document.getElementById('efficiency').value = '20';
      document.getElementById('tiltAngle').value = '35';
      document.getElementById('azimuth').value = '180';
      document.getElementById('startDate').value = '2026-05-22';
      document.getElementById('duration').value = '365';

      const payload = readSolarForm();

      expect(payload.latitude).toBe(45);
      expect(payload.longitude).toBe(7);
      expect(payload.panel_count).toBe(10);
      expect(payload.panel_area_m2).toBe(2);
      expect(payload.panel_efficiency).toBe(20);
      expect(payload.tilt_angle_deg).toBe(35);
      expect(payload.azimuth_deg).toBe(180);
      expect(payload.start_date).toBe('2026-05-22');
      expect(payload.duration_days).toBe(365);
    });

    test('converts camelCase field names to snake_case in payload', () => {
      document.getElementById('panelCount').value = '5';
      document.getElementById('panelArea').value = '1.5';
      document.getElementById('tiltAngle').value = '45';

      const payload = readSolarForm();

      expect(payload.panel_count).toBe(5);
      expect(payload.panel_area_m2).toBe(1.5);
      expect(payload.tilt_angle_deg).toBe(45);
    });

    test('parses numeric values correctly', () => {
      document.getElementById('latitude').value = '45.5';
      document.getElementById('efficiency').value = '22.5';
      document.getElementById('duration').value = '100';

      const payload = readSolarForm();

      expect(typeof payload.latitude).toBe('number');
      expect(typeof payload.panel_efficiency).toBe('number');
      expect(typeof payload.duration_days).toBe('number');
      expect(payload.latitude).toBe(45.5);
      expect(payload.panel_efficiency).toBe(22.5);
      expect(payload.duration_days).toBe(100);
    });
  });

  describe('showFieldError', () => {
    test('displays error message in field error span', () => {
      const errorSpan = document.querySelector('#latitude').parentElement.querySelector('.error');
      expect(errorSpan.classList.contains('show')).toBe(false);

      showFieldError('latitude', 'Invalid latitude');

      expect(errorSpan.textContent).toBe('Invalid latitude');
      expect(errorSpan.classList.contains('show')).toBe(true);
    });

    test('handles multiple fields with different errors', () => {
      showFieldError('latitude', 'Too high');
      showFieldError('longitude', 'Too low');

      const latError = document.querySelector('#latitude').parentElement.querySelector('.error');
      const longError = document.querySelector('#longitude').parentElement.querySelector('.error');

      expect(latError.textContent).toBe('Too high');
      expect(longError.textContent).toBe('Too low');
    });

    test('does nothing if field not found', () => {
      expect(() => {
        showFieldError('nonexistent', 'Error message');
      }).not.toThrow();
    });
  });

  describe('clearFieldError', () => {
    test('removes .show class from field error', () => {
      showFieldError('latitude', 'Error');
      const errorSpan = document.querySelector('#latitude').parentElement.querySelector('.error');

      expect(errorSpan.classList.contains('show')).toBe(true);

      clearFieldError('latitude');

      expect(errorSpan.classList.contains('show')).toBe(false);
    });

    test('clears only specified field error', () => {
      showFieldError('latitude', 'Error 1');
      showFieldError('longitude', 'Error 2');

      clearFieldError('latitude');

      const latError = document.querySelector('#latitude').parentElement.querySelector('.error');
      const longError = document.querySelector('#longitude').parentElement.querySelector('.error');

      expect(latError.classList.contains('show')).toBe(false);
      expect(longError.classList.contains('show')).toBe(true);
    });
  });

  describe('clearErrors', () => {
    test('removes .show class from all error spans', () => {
      showFieldError('latitude', 'Error 1');
      showFieldError('longitude', 'Error 2');
      showFieldError('panelCount', 'Error 3');

      clearErrors();

      document.querySelectorAll('.error').forEach(el => {
        expect(el.classList.contains('show')).toBe(false);
      });
    });
  });

  describe('clearFieldError', () => {
    test('removes show class from field error', () => {
      const latitudeInput = document.getElementById('latitude');
      const errorSpan = latitudeInput.parentElement.querySelector('.error');

      errorSpan.classList.add('show');
      clearFieldError('latitude');

      expect(errorSpan.classList.contains('show')).toBe(false);
    });

    test('handles non-existent field gracefully', () => {
      // Should not throw error if field doesn't exist
      expect(() => {
        clearFieldError('nonexistent');
      }).not.toThrow();
    });
  });

  describe('showFormError', () => {
    test('displays error message in formError div', () => {
      const errorDiv = document.getElementById('formError');
      errorDiv.style.display = 'none';

      showFormError('Simulation failed');

      expect(errorDiv.textContent).toBe('Simulation failed');
      expect(errorDiv.style.display).toBe('block');
    });

    test('replaces previous error message', () => {
      const errorDiv = document.getElementById('formError');

      showFormError('Error 1');
      expect(errorDiv.textContent).toBe('Error 1');

      showFormError('Error 2');
      expect(errorDiv.textContent).toBe('Error 2');
    });
  });

  describe('showFieldError edge cases', () => {
    test('handles missing input element gracefully', () => {
      // Should not throw if input doesn't exist
      expect(() => {
        showFieldError('nonexistent', 'Error message');
      }).not.toThrow();
    });

    test('handles missing error span gracefully', () => {
      // Create an input without an error span
      const input = document.createElement('input');
      input.id = 'testInput';
      const group = document.createElement('div');
      group.appendChild(input);
      document.body.appendChild(group);

      expect(() => {
        showFieldError('testInput', 'Error');
      }).not.toThrow();

      document.body.removeChild(group);
    });
  });

  describe('updateResultCards', () => {
    test('updates all result card values from API response', () => {
      const data = {
        annual_energy_kwh: 5000.5,
        average_daily_kwh: 13.691234,
        peak_hour_kw: 2.926,
        system_capacity_kw: 4.0
      };

      updateResultCards(data);

      expect(document.getElementById('annualEnergy').textContent).toBe('5000.5');
      expect(document.getElementById('dailyAverage').textContent).toBe('13.69');
      expect(document.getElementById('peakHour').textContent).toBe('2.93');
      expect(document.getElementById('capacity').textContent).toBe('4.00');
    });

    test('formats annual energy to 1 decimal place', () => {
      updateResultCards({ annual_energy_kwh: 1234.567, average_daily_kwh: 3.4, peak_hour_kw: 1.2, system_capacity_kw: 2.0 });
      expect(document.getElementById('annualEnergy').textContent).toBe('1234.6');
    });

    test('formats average daily to 2 decimal places', () => {
      updateResultCards({ annual_energy_kwh: 5000, average_daily_kwh: 13.691234, peak_hour_kw: 2.5, system_capacity_kw: 4.0 });
      expect(document.getElementById('dailyAverage').textContent).toBe('13.69');
    });

    test('formats peak hour to 2 decimal places', () => {
      updateResultCards({ annual_energy_kwh: 5000, average_daily_kwh: 13.69, peak_hour_kw: 2.926, system_capacity_kw: 4.0 });
      expect(document.getElementById('peakHour').textContent).toBe('2.93');
    });

    test('formats capacity to 2 decimal places', () => {
      updateResultCards({ annual_energy_kwh: 5000, average_daily_kwh: 13.69, peak_hour_kw: 2.93, system_capacity_kw: 4.0 });
      expect(document.getElementById('capacity').textContent).toBe('4.00');
    });
  });
});
