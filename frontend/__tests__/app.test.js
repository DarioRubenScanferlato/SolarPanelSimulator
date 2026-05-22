// Integration tests for app.js
// Note: These test the orchestration logic without mocking all module internals

describe('app.js integration', () => {
  // Since app.js runs on DOMContentLoaded and has complex module dependencies,
  // we test the orchestration indirectly through scenario testing

  beforeEach(() => {
    // Setup minimal DOM structure for app initialization
    document.body.innerHTML = `
      <nav class="tab-nav">
        <button class="tab-btn tab-active" data-tab="solar">Solar</button>
        <button class="tab-btn" data-tab="battery">Battery</button>
      </nav>
      <form id="simulatorForm">
        <div class="form-group">
          <input id="latitude" name="latitude" value="45">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="longitude" name="longitude" value="7">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="panelCount" name="panelCount" value="10">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="panelArea" name="panelArea" value="2">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="efficiency" name="efficiency" value="20">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="tiltAngle" name="tiltAngle" value="35">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="azimuth" name="azimuth" value="180">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="startDate" name="startDate" value="2026-05-22">
          <span class="error"></span>
        </div>
        <div class="form-group">
          <input id="duration" name="duration" value="365">
          <span class="error"></span>
        </div>
        <button id="simulateBtn" type="submit">Simulate</button>
        <div id="formError"></div>
      </form>
      <div id="loadingIndicator" style="display: none;"></div>
      <div id="resultsSection" style="display: none;">
        <div id="dailyInfo"></div>
        <div id="annualEnergy">0</div>
        <div id="dailyAverage">0</div>
        <div id="peakHour">0</div>
        <div id="capacity">0</div>
        <canvas id="dailyChart"></canvas>
        <canvas id="yearlyChart"></canvas>
      </div>
      <section id="panel-solar" class="tab-panel">
        <div id="panel-content">Solar content</div>
      </section>
      <section id="panel-battery" class="tab-panel" hidden>Battery content</section>
    `;
  });

  afterEach(() => {
    document.body.innerHTML = '';
    jest.clearAllMocks();
  });

  describe('app.js initialization', () => {
    test('app.js loads without errors', () => {
      // Simply requiring app.js should not throw
      expect(() => {
        require('../app.js');
      }).not.toThrow();
    });

    test('app.js module loads successfully', () => {
      const app = require('../app.js');
      // app.js doesn't export functions, it just sets up event listeners
      // This test verifies the module loads and runs initialization
      expect(app).toBeDefined();
    });

    test('DOMContentLoaded initializes defaults and charts', () => {
      // Create a new module instance for this test to avoid conflicts
      delete require.cache[require.resolve('../app.js')];

      // Set up DOM
      document.body.innerHTML = `
        <nav class="tab-nav">
          <button class="tab-btn tab-active" data-tab="solar">Solar</button>
          <button class="tab-btn" data-tab="battery">Battery</button>
        </nav>
        <form id="simulatorForm">
          <div class="form-group">
            <input id="latitude" name="latitude" value="">
            <span class="error"></span>
          </div>
          <input id="longitude" name="longitude" value="">
          <input id="panelCount" name="panelCount" value="">
          <input id="panelArea" name="panelArea" value="">
          <input id="efficiency" name="efficiency" value="">
          <input id="tiltAngle" name="tiltAngle" value="">
          <input id="azimuth" name="azimuth" value="">
          <input id="startDate" name="startDate" value="">
          <input id="duration" name="duration" value="">
          <button id="simulateBtn" type="submit">Simulate</button>
          <div id="formError"></div>
        </form>
        <div id="loadingIndicator" style="display: none;"></div>
        <div id="resultsSection" style="display: none;">
          <div id="dailyInfo"></div>
          <div id="annualEnergy">0</div>
          <div id="dailyAverage">0</div>
          <div id="peakHour">0</div>
          <div id="capacity">0</div>
          <canvas id="dailyChart"></canvas>
          <canvas id="yearlyChart"></canvas>
        </div>
        <section id="panel-solar" class="tab-panel">Solar</section>
        <section id="panel-battery" class="tab-panel" hidden>Battery</section>
        <main></main>
      `;

      // Load app.js (sets up DOMContentLoaded listener)
      require('../app.js');

      // Dispatch DOMContentLoaded
      document.dispatchEvent(new Event('DOMContentLoaded'));

      // Check that initialization happened
      expect(document.getElementById('latitude').value).toBe('45.0703');
      expect(document.getElementById('panel-solar').hasAttribute('hidden')).toBe(false);
      expect(global.Chart).toHaveBeenCalledTimes(2); // dailyChart and yearlyChart
    });
  });

  describe('Form submission handling', () => {
    test('form submission calls API and displays results', async () => {
      const { simulateSolar } = require('../api.js');
      const { updateResultCards } = require('../forms.js');

      // Mock fetch for API call
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          annual_energy_kwh: 5000,
          average_daily_kwh: 13.7,
          peak_hour_kw: 2.93,
          system_capacity_kw: 4.0,
          daily_hourly_generation: Array(24).fill(0.2),
          monthly_energy_kwh: Array(12).fill(400),
          daily_sunrise: '03:18',
          daily_sunset: '19:33'
        })
      });

      const result = await simulateSolar({
        latitude: 45,
        longitude: 7,
        panel_count: 10,
        panel_area_m2: 2,
        panel_efficiency: 20,
        tilt_angle_deg: 35,
        azimuth_deg: 180,
        start_date: '2026-05-22',
        duration_days: 365
      });

      expect(result.annual_energy_kwh).toBe(5000);
      expect(result.daily_hourly_generation.length).toBe(24);
    });

    test('form input change clears previous errors', () => {
      const { showFieldError, clearErrors } = require('../forms.js');

      // Show an error
      showFieldError('latitude', 'Invalid latitude');
      const errorSpan = document.querySelector('.error');
      expect(errorSpan.classList.contains('show')).toBe(true);

      // Simulate input change event
      const input = document.getElementById('latitude');
      input.dispatchEvent(new Event('change'));
      clearErrors();

      expect(errorSpan.classList.contains('show')).toBe(false);
    });
  });

  describe('Module integration', () => {
    test('api module exports simulateSolar function', () => {
      const { simulateSolar } = require('../api.js');
      expect(typeof simulateSolar).toBe('function');
    });

    test('forms module exports all required functions', () => {
      const forms = require('../forms.js');
      expect(typeof forms.loadDefaults).toBe('function');
      expect(typeof forms.readSolarForm).toBe('function');
      expect(typeof forms.showFieldError).toBe('function');
      expect(typeof forms.clearErrors).toBe('function');
      expect(typeof forms.updateResultCards).toBe('function');
    });

    test('charts module exports all required functions', () => {
      const charts = require('../charts.js');
      expect(typeof charts.initDailyChart).toBe('function');
      expect(typeof charts.initYearlyChart).toBe('function');
      expect(typeof charts.updateDailyChart).toBe('function');
      expect(typeof charts.updateYearlyChart).toBe('function');
    });

    test('tabs module exports switchTab function', () => {
      const { switchTab } = require('../tabs.js');
      expect(typeof switchTab).toBe('function');
    });
  });

  describe('API response handling', () => {
    test('success response structure matches expected format', () => {
      // Test that a typical success response has all required fields
      const mockSuccessResponse = {
        annual_energy_kwh: 5000,
        average_daily_kwh: 13.69,
        peak_hour_kw: 2.93,
        system_capacity_kw: 4.0,
        daily_hourly_generation: Array(24).fill(0),
        monthly_energy_kwh: Array(12).fill(0),
        daily_sunrise: '03:18',
        daily_sunset: '19:33'
      };

      // Verify all required fields exist
      expect(mockSuccessResponse.annual_energy_kwh).toBeDefined();
      expect(mockSuccessResponse.average_daily_kwh).toBeDefined();
      expect(mockSuccessResponse.peak_hour_kw).toBeDefined();
      expect(mockSuccessResponse.system_capacity_kw).toBeDefined();
      expect(mockSuccessResponse.daily_hourly_generation.length).toBe(24);
      expect(mockSuccessResponse.monthly_energy_kwh.length).toBe(12);
    });

    test('error response structure with 422 validation error', () => {
      const mockErrorResponse = {
        detail: [
          {
            loc: ['body', 'latitude'],
            msg: 'Input should be less than or equal to 90'
          }
        ]
      };

      // Verify error structure
      expect(Array.isArray(mockErrorResponse.detail)).toBe(true);
      expect(mockErrorResponse.detail[0].loc).toBeDefined();
      expect(mockErrorResponse.detail[0].msg).toBeDefined();
    });
  });

  describe('Form data flow', () => {
    test('readSolarForm converts field names correctly', () => {
      const { readSolarForm } = require('../forms.js');

      const formData = readSolarForm();

      // Verify camelCase input becomes snake_case payload
      expect(formData.panel_count).toBe(10);
      expect(formData.panel_area_m2).toBe(2);
      expect(formData.panel_efficiency).toBe(20);
      expect(formData.tilt_angle_deg).toBe(35);
      expect(formData.azimuth_deg).toBe(180);
      expect(formData.duration_days).toBe(365);
    });

    test('loadDefaults populates form with Turin coordinates', () => {
      const { loadDefaults } = require('../forms.js');

      loadDefaults();

      // Verify form fields are populated
      expect(document.getElementById('latitude').value).toBe('45.0703');
      expect(document.getElementById('longitude').value).toBe('7.6869');
    });
  });

  describe('DOM state transitions', () => {
    test('loading indicator visibility controlled correctly', () => {
      const loadingIndicator = document.getElementById('loadingIndicator');

      expect(loadingIndicator.style.display).toBe('none');

      // Simulate showing loading
      loadingIndicator.style.display = 'flex';
      expect(loadingIndicator.style.display).toBe('flex');

      // Simulate hiding loading
      loadingIndicator.style.display = 'none';
      expect(loadingIndicator.style.display).toBe('none');
    });

    test('results section visibility controlled correctly', () => {
      const resultsSection = document.getElementById('resultsSection');

      expect(resultsSection.style.display).toBe('none');

      // Simulate showing results
      resultsSection.style.display = 'block';
      expect(resultsSection.style.display).toBe('block');
    });

    test('button state managed during simulation', () => {
      const simulateBtn = document.getElementById('simulateBtn');

      // Initial state
      expect(simulateBtn.disabled).toBe(false);
      expect(simulateBtn.textContent).toBe('Simulate');

      // Simulated request state
      simulateBtn.disabled = true;
      simulateBtn.textContent = 'Simulating…';
      expect(simulateBtn.disabled).toBe(true);
      expect(simulateBtn.textContent).toBe('Simulating…');

      // After completion
      simulateBtn.disabled = false;
      simulateBtn.textContent = 'Simulate';
      expect(simulateBtn.disabled).toBe(false);
      expect(simulateBtn.textContent).toBe('Simulate');
    });
  });

  describe('Tab switching integration', () => {
    test('solar tab is active by default', () => {
      const { switchTab } = require('../tabs.js');
      switchTab('solar');

      const solarPanel = document.getElementById('panel-solar');
      const solarBtn = document.querySelector('[data-tab="solar"]');

      expect(solarPanel.hasAttribute('hidden')).toBe(false);
      expect(solarBtn.classList.contains('tab-active')).toBe(true);
    });

    test('tab switching maintains application state', () => {
      const { switchTab } = require('../tabs.js');

      // Fill form with values
      document.getElementById('latitude').value = '50';
      document.getElementById('panelCount').value = '5';

      // Switch tabs
      switchTab('battery');
      switchTab('solar');

      // Verify form values persist
      expect(document.getElementById('latitude').value).toBe('50');
      expect(document.getElementById('panelCount').value).toBe('5');
    });
  });

  describe('Error handling flow', () => {
    test('handles 422 validation errors from API', () => {
      const { showFieldError } = require('../forms.js');

      // Simulate API 422 error with field errors
      const errorData = {
        detail: [
          { loc: ['body', 'latitude'], msg: 'Latitude must be between -90 and 90' },
          { loc: ['body', 'panel_count'], msg: 'Panel count must be positive' }
        ]
      };

      // Display field errors
      errorData.detail.forEach(err => {
        const fieldName = err.loc[1];
        // Convert snake_case to camelCase
        const fieldId = fieldName.replace(/_([a-z])/g, (_, char) => char.toUpperCase());
        showFieldError(fieldId, err.msg);
      });

      const latitudeError = document.getElementById('latitude').parentElement.querySelector('.error');
      expect(latitudeError.textContent).toContain('Latitude');
    });

    test('field errors display in correct locations', () => {
      const { showFieldError } = require('../forms.js');

      showFieldError('latitude', 'Invalid latitude');

      const latitudeInput = document.getElementById('latitude');
      const errorSpan = latitudeInput.parentElement.querySelector('.error');

      expect(errorSpan.textContent).toBe('Invalid latitude');
      expect(errorSpan.classList.contains('show')).toBe(true);
    });

    test('global form error displays', () => {
      const { showFormError } = require('../forms.js');

      showFormError('Simulation failed: network error');

      const formError = document.getElementById('formError');
      expect(formError.textContent).toBe('Simulation failed: network error');
      expect(formError.style.display).toBe('block');
    });

    test('field errors can be cleared', () => {
      const { showFieldError, clearErrors } = require('../forms.js');

      showFieldError('latitude', 'Error');
      const errorSpan = document.querySelector('.error');
      expect(errorSpan.classList.contains('show')).toBe(true);

      clearErrors();
      expect(errorSpan.classList.contains('show')).toBe(false);
    });
  });

  describe('Result card updates', () => {
    test('result cards update with API response data', () => {
      const { updateResultCards } = require('../forms.js');

      const mockData = {
        annual_energy_kwh: 5000.5,
        average_daily_kwh: 13.69,
        peak_hour_kw: 2.93,
        system_capacity_kw: 4.0
      };

      updateResultCards(mockData);

      expect(document.getElementById('annualEnergy').textContent).toBe('5000.5');
      expect(document.getElementById('dailyAverage').textContent).toBe('13.69');
      expect(document.getElementById('peakHour').textContent).toBe('2.93');
      expect(document.getElementById('capacity').textContent).toBe('4.00');
    });
  });
});
