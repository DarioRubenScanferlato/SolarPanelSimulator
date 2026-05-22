const { simulateSolar } = require('../api.js');

describe('api.js', () => {
  let mockButton;

  beforeEach(() => {
    // Setup button DOM
    document.body.innerHTML = '<button id="simulateBtn">Simulate</button>';
    mockButton = document.getElementById('simulateBtn');

    // Reset fetch mock
    global.fetch.mockClear();
  });

  afterEach(() => {
    document.body.innerHTML = '';
  });

  describe('simulateSolar - success response', () => {
    test('returns parsed JSON on 200 response', async () => {
      const mockResponse = {
        annual_energy_kwh: 5000,
        average_daily_kwh: 13.69,
        peak_hour_kw: 2.93,
        system_capacity_kw: 4.0,
        daily_hourly_generation: Array(24).fill(0),
        monthly_energy_kwh: Array(12).fill(0),
        daily_sunrise: '03:18',
        daily_sunset: '19:33'
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const payload = {
        latitude: 45.0703,
        longitude: 7.6869,
        panel_count: 10,
        panel_area_m2: 2.0,
        panel_efficiency: 20,
        tilt_angle_deg: 35,
        azimuth_deg: 180,
        start_date: '2026-05-22',
        duration_days: 365
      };

      const result = await simulateSolar(payload);

      expect(result.annual_energy_kwh).toBe(5000);
      expect(result.average_daily_kwh).toBe(13.69);
      expect(result.peak_hour_kw).toBe(2.93);
      expect(result.system_capacity_kw).toBe(4.0);
    });

    test('calls fetch with correct endpoint and method', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      const payload = { latitude: 45 };
      await simulateSolar(payload);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/simulate',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      );
    });

    test('sends payload as JSON in request body', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      const payload = {
        latitude: 45,
        longitude: 7.6869,
        panel_count: 10
      };

      await simulateSolar(payload);

      const callArgs = global.fetch.mock.calls[0];
      const body = JSON.parse(callArgs[1].body);

      expect(body.latitude).toBe(45);
      expect(body.longitude).toBe(7.6869);
      expect(body.panel_count).toBe(10);
    });
  });

  describe('simulateSolar - 422 validation error', () => {
    test('returns error object with detail array on 422', async () => {
      const errorResponse = {
        detail: [
          {
            loc: ['body', 'latitude'],
            msg: 'Input should be less than or equal to 90'
          }
        ]
      };

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => errorResponse
      });

      const result = await simulateSolar({ latitude: 95 });

      expect(result.error).toBe(true);
      expect(result.status).toBe(422);
      expect(result.detail).toEqual(errorResponse.detail);
    });

    test('handles multiple validation errors', async () => {
      const errorResponse = {
        detail: [
          { loc: ['body', 'latitude'], msg: 'too high' },
          { loc: ['body', 'longitude'], msg: 'too high' }
        ]
      };

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => errorResponse
      });

      const result = await simulateSolar({});

      expect(result.detail.length).toBe(2);
      expect(result.detail[0].loc[1]).toBe('latitude');
      expect(result.detail[1].loc[1]).toBe('longitude');
    });
  });

  describe('simulateSolar - network error', () => {
    test('returns error object on fetch failure', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      const result = await simulateSolar({});

      expect(result.error).toBe(true);
      expect(result.message).toContain('Failed to connect to backend');
    });

    test('includes error message in response', async () => {
      const errorMsg = 'Connection refused';
      global.fetch.mockRejectedValueOnce(new Error(errorMsg));

      const result = await simulateSolar({});

      expect(result.message).toContain(errorMsg);
    });
  });

  describe('Button state management', () => {
    test('disables button during request', async () => {
      global.fetch.mockImplementationOnce(async () => {
        // Verify button is disabled during fetch
        expect(mockButton.disabled).toBe(true);
        return { ok: true, json: async () => ({}) };
      });

      await simulateSolar({});
    });

    test('changes button text to "Simulating…" during request', async () => {
      global.fetch.mockImplementationOnce(async () => {
        expect(mockButton.textContent).toBe('Simulating…');
        return { ok: true, json: async () => ({}) };
      });

      await simulateSolar({});
    });

    test('re-enables button after success', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      await simulateSolar({});

      expect(mockButton.disabled).toBe(false);
      expect(mockButton.textContent).toBe('Simulate');
    });

    test('re-enables button after error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      await simulateSolar({});

      expect(mockButton.disabled).toBe(false);
      expect(mockButton.textContent).toBe('Simulate');
    });

    test('re-enables button after 422 validation error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({ detail: [] })
      });

      await simulateSolar({});

      expect(mockButton.disabled).toBe(false);
      expect(mockButton.textContent).toBe('Simulate');
    });
  });

  describe('Response format validation', () => {
    test('response object has error property set to false on success', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ annual_energy_kwh: 5000 })
      });

      const result = await simulateSolar({});

      expect(result.error).toBeUndefined();
    });

    test('error response has error property set to true', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({ detail: [] })
      });

      const result = await simulateSolar({});

      expect(result.error).toBe(true);
    });
  });
});
