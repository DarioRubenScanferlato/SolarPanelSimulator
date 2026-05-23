const {
    initBatteryForm,
    getBatteryInput,
    showFieldError,
    clearErrors
} = require('../battery-forms.js');
const {
    initBatterySoCChart,
    updateBatterySoCChart
} = require('../battery-charts.js');

describe('battery-forms.js', () => {
    beforeEach(() => {
        // Setup battery panel DOM
        document.body.innerHTML = `
            <div id="battery-panel"></div>
        `;
    });

    afterEach(() => {
        document.body.innerHTML = '';
    });

    describe('initBatteryForm', () => {
        test('renders battery form with all inputs and defaults', () => {
            initBatteryForm();

            expect(document.getElementById('battery_capacity_kwh')).toBeTruthy();
            expect(document.getElementById('battery_capacity_kwh').value).toBe('10');

            expect(document.getElementById('battery_charge_efficiency')).toBeTruthy();
            expect(document.getElementById('battery_charge_efficiency').value).toBe('95');

            expect(document.getElementById('battery_discharge_efficiency')).toBeTruthy();
            expect(document.getElementById('battery_discharge_efficiency').value).toBe('95');

            expect(document.getElementById('daily_load_kwh')).toBeTruthy();
            expect(document.getElementById('daily_load_kwh').value).toBe('10');

            expect(document.getElementById('initial_soc_pct')).toBeTruthy();
            expect(document.getElementById('initial_soc_pct').value).toBe('50');
        });

        test('renders form with aria attributes for accessibility', () => {
            initBatteryForm();

            const capacityInput = document.getElementById('battery_capacity_kwh');
            expect(capacityInput.getAttribute('aria-required')).toBe('true');
            expect(capacityInput.getAttribute('aria-describedby')).toBe('error-battery_capacity_kwh');
        });

        test('creates error span elements for each field', () => {
            initBatteryForm();

            expect(document.getElementById('error-battery_capacity_kwh')).toBeTruthy();
            expect(document.getElementById('error-battery_charge_efficiency')).toBeTruthy();
            expect(document.getElementById('error-battery_discharge_efficiency')).toBeTruthy();
            expect(document.getElementById('error-daily_load_kwh')).toBeTruthy();
            expect(document.getElementById('error-initial_soc_pct')).toBeTruthy();
        });
    });

    describe('getBatteryInput', () => {
        test('returns correct object structure with form values', () => {
            initBatteryForm();

            document.getElementById('battery_capacity_kwh').value = '15';
            document.getElementById('battery_charge_efficiency').value = '92';
            document.getElementById('battery_discharge_efficiency').value = '90';
            document.getElementById('daily_load_kwh').value = '12';
            document.getElementById('initial_soc_pct').value = '75';

            const input = getBatteryInput();

            expect(input).toEqual({
                battery_capacity_kwh: 15,
                battery_charge_efficiency: 92,
                battery_discharge_efficiency: 90,
                daily_load_kwh: 12,
                initial_soc_pct: 75
            });
        });

        test('parses values as floats', () => {
            initBatteryForm();

            document.getElementById('battery_capacity_kwh').value = '10.5';
            document.getElementById('daily_load_kwh').value = '5.25';

            const input = getBatteryInput();

            expect(typeof input.battery_capacity_kwh).toBe('number');
            expect(typeof input.daily_load_kwh).toBe('number');
            expect(input.battery_capacity_kwh).toBe(10.5);
            expect(input.daily_load_kwh).toBe(5.25);
        });
    });

    describe('showFieldError', () => {
        test('displays error message next to field', () => {
            initBatteryForm();

            showFieldError('battery_capacity_kwh', 'Capacity must be at least 1 kWh');

            const errorElement = document.getElementById('error-battery_capacity_kwh');
            expect(errorElement.textContent).toBe('Capacity must be at least 1 kWh');
            expect(errorElement.classList.contains('show')).toBe(true);
        });

        test('sets aria-invalid attribute on input', () => {
            initBatteryForm();

            showFieldError('battery_capacity_kwh', 'Invalid value');

            const input = document.getElementById('battery_capacity_kwh');
            expect(input.getAttribute('aria-invalid')).toBe('true');
        });
    });

    describe('clearErrors', () => {
        test('removes all error messages', () => {
            initBatteryForm();

            showFieldError('battery_capacity_kwh', 'Error 1');
            showFieldError('daily_load_kwh', 'Error 2');

            clearErrors();

            expect(document.getElementById('error-battery_capacity_kwh').classList.contains('show')).toBe(false);
            expect(document.getElementById('error-daily_load_kwh').classList.contains('show')).toBe(false);
        });

        test('clears aria-invalid attributes', () => {
            initBatteryForm();

            showFieldError('battery_capacity_kwh', 'Error');
            clearErrors();

            const input = document.getElementById('battery_capacity_kwh');
            expect(input.getAttribute('aria-invalid')).toBe('false');
            expect(input.hasAttribute('aria-describedby')).toBe(false);
        });
    });
});

describe('battery-charts.js', () => {
    beforeEach(() => {
        // Mock Chart.js
        global.Chart = jest.fn().mockImplementation(() => ({
            destroy: jest.fn(),
            data: {
                datasets: [{ data: [] }]
            },
            update: jest.fn()
        }));

        document.body.innerHTML = `
            <canvas id="battery-soc-chart"></canvas>
        `;
    });

    afterEach(() => {
        document.body.innerHTML = '';
        jest.clearAllMocks();
    });

    describe('initBatterySoCChart', () => {
        test('creates chart with correct configuration', () => {
            initBatterySoCChart('battery-soc-chart');

            expect(global.Chart).toHaveBeenCalled();
            const callArgs = global.Chart.mock.calls[0];
            expect(callArgs[1].type).toBe('line');
            expect(callArgs[1].data.labels.length).toBe(24);
        });

        test('initializes with empty data', () => {
            initBatterySoCChart('battery-soc-chart');

            const callArgs = global.Chart.mock.calls[0];
            expect(callArgs[1].data.datasets[0].data).toEqual([]);
        });
    });

    describe('updateBatterySoCChart', () => {
        test('updates chart data without recreating', () => {
            initBatterySoCChart('battery-soc-chart');
            const mockChart = global.Chart.mock.results[0].value;

            const testData = Array(24).fill(0).map((_, i) => i + 5);
            updateBatterySoCChart(testData);

            expect(mockChart.data.datasets[0].data).toEqual(testData);
            expect(mockChart.update).toHaveBeenCalled();
        });

        test('uses chart.update() instead of recreating', () => {
            initBatterySoCChart('battery-soc-chart');
            const initialCallCount = global.Chart.mock.calls.length;

            updateBatterySoCChart(Array(24).fill(5));

            // Chart.js constructor should not be called again
            expect(global.Chart.mock.calls.length).toBe(initialCallCount);
        });
    });
});
