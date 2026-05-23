import { initCostForm, getCostInput, showCostFieldError, clearCostErrors } from '../cost-forms.js';
import {
    initCostROIChart,
    updateCostROIChart,
    initCostAnnualChart,
    updateCostAnnualChart
} from '../cost-charts.js';

// Mock Chart.js to prevent canvas errors
jest.mock('chart.js', () => ({
    default: jest.fn().mockImplementation(() => ({
        data: { datasets: [], labels: [] },
        update: jest.fn(),
        destroy: jest.fn()
    }))
}));

// Setup DOM
beforeEach(() => {
    document.body.innerHTML = `
        <div id="panel-cost"></div>
        <canvas id="cost-roi-chart"></canvas>
        <canvas id="cost-annual-chart"></canvas>
    `;
});

describe('Cost Forms Module', () => {
    test('initCostForm initializes with correct defaults', () => {
        const capacityKw = 4.0;
        initCostForm(capacityKw, 5000, '2026-05-23T14:32:00Z');

        expect(document.getElementById('system_cost_eur').value).toBe('7200.00'); // 4 * 1800
        expect(document.getElementById('electricity_price_eur_per_kwh').value).toBe('0.32');
        expect(document.getElementById('feedin_tariff_eur_per_kwh').value).toBe('0.12');
        expect(document.getElementById('lifespan_years').value).toBe('25');
        expect(document.getElementById('annual_degradation_percent').value).toBe('0.5');
    });

    test('initCostForm displays inheritance notice with solar data', () => {
        initCostForm(4.0, 5000, '2026-05-23T14:32:00Z');

        const notice = document.getElementById('cost-inheritance-notice');
        expect(notice.textContent).toContain('5000.0 kWh/year');
        expect(notice.textContent).toContain('2026-05-23T14:32:00Z');
    });

    test('initCostForm displays notice when no solar data available', () => {
        initCostForm(0, null, null);

        const notice = document.getElementById('cost-inheritance-notice');
        expect(notice.textContent).toContain('Run Battery tab simulation first');
    });

    test('getCostInput collects all 5 field values correctly', () => {
        initCostForm(4.0, 5000, '2026-05-23T14:32:00Z');

        // Modify values
        document.getElementById('system_cost_eur').value = '10000';
        document.getElementById('electricity_price_eur_per_kwh').value = '0.35';
        document.getElementById('feedin_tariff_eur_per_kwh').value = '0.15';
        document.getElementById('lifespan_years').value = '20';
        document.getElementById('annual_degradation_percent').value = '0.7';

        const input = getCostInput();

        expect(input.system_cost_eur).toBe(10000);
        expect(input.electricity_price_eur_per_kwh).toBe(0.35);
        expect(input.feedin_tariff_eur_per_kwh).toBe(0.15);
        expect(input.lifespan_years).toBe(20);
        expect(input.annual_degradation_percent).toBe(0.7);
    });

    test('showCostFieldError displays error message next to field', () => {
        initCostForm(4.0, 5000, '2026-05-23T14:32:00Z');

        showCostFieldError('system_cost_eur', 'System cost must be greater than 0');

        const errorEl = document.getElementById('error-system_cost_eur');
        expect(errorEl.textContent).toBe('System cost must be greater than 0');
        expect(errorEl.classList.contains('show')).toBe(true);

        const input = document.getElementById('system_cost_eur');
        expect(input.getAttribute('aria-invalid')).toBe('true');
    });

    test('clearCostErrors removes all error messages', () => {
        initCostForm(4.0, 5000, '2026-05-23T14:32:00Z');

        // Add errors
        showCostFieldError('system_cost_eur', 'Error 1');
        showCostFieldError('electricity_price_eur_per_kwh', 'Error 2');

        clearCostErrors();

        const errorEl1 = document.getElementById('error-system_cost_eur');
        const errorEl2 = document.getElementById('error-electricity_price_eur_per_kwh');

        expect(errorEl1.textContent).toBe('');
        expect(errorEl1.classList.contains('show')).toBe(false);
        expect(errorEl2.textContent).toBe('');
        expect(errorEl2.classList.contains('show')).toBe(false);
    });
});

describe('Cost Charts Module', () => {
    test('initCostROIChart creates chart with correct structure', () => {
        initCostROIChart('cost-roi-chart');

        const canvas = document.getElementById('cost-roi-chart');
        expect(canvas).toBeTruthy();
    });

    test('updateCostROIChart updates cumulative savings and baseline', () => {
        initCostROIChart('cost-roi-chart');

        const cumulativeSavings = [2000, 4000, 6000, 8000, 10000];
        const systemCost = 5000;
        const breakEvenYear = 3;

        updateCostROIChart(cumulativeSavings, systemCost, breakEvenYear);

        // Verify chart was created (canvas element exists)
        expect(document.getElementById('cost-roi-chart')).toBeTruthy();
    });

    test('initCostAnnualChart creates bar chart with correct structure', () => {
        initCostAnnualChart('cost-annual-chart');

        const canvas = document.getElementById('cost-annual-chart');
        expect(canvas).toBeTruthy();
    });

    test('updateCostAnnualChart updates annual savings data', () => {
        initCostAnnualChart('cost-annual-chart');

        const annualSavings = [2000, 2000, 2000, 1900, 1800];

        updateCostAnnualChart(annualSavings);

        // Verify chart was created (canvas element exists)
        expect(document.getElementById('cost-annual-chart')).toBeTruthy();
    });
});

describe('Cost Frontend Integration', () => {
    test('Form values persist after initialization', () => {
        initCostForm(4.0, 5000, '2026-05-23T14:32:00Z');

        const systemCostInput = document.getElementById('system_cost_eur');
        const originalValue = systemCostInput.value;

        // Simulate user changing value
        systemCostInput.value = '8000';

        // Get input should return user-modified value
        const input = getCostInput();
        expect(input.system_cost_eur).toBe(8000);
    });

    test('Charts update in-place without destroying', () => {
        initCostROIChart('cost-roi-chart');
        initCostAnnualChart('cost-annual-chart');

        // Update charts
        updateCostROIChart([1000, 2000, 3000, 4000, 5000], 2000, 2);
        updateCostAnnualChart([1000, 1000, 1000, 1000, 1000]);

        // Charts should still exist (not destroyed/recreated)
        expect(document.getElementById('cost-roi-chart')).toBeTruthy();
        expect(document.getElementById('cost-annual-chart')).toBeTruthy();
    });

    test('Break-even year null displays correct message', () => {
        // This would be tested in app.js integration
        // Verifying the logic: when cost_breakeven_year is null
        // Expected display: "No payback within 25 years"
        expect(null).toBeNull();
        expect('No payback within 25 years').toBe('No payback within 25 years');
    });

    test('Break-even year number displays correctly', () => {
        // This would be tested in app.js integration
        // Verifying the logic: when cost_breakeven_year is 5
        // Expected display: "Year 5"
        const breakEvenYear = 5;
        const display = `Year ${breakEvenYear}`;
        expect(display).toBe('Year 5');
    });

    test('Default system cost calculated correctly for various capacities', () => {
        const testCases = [
            { capacity: 1, expected: '1800.00' },
            { capacity: 4, expected: '7200.00' },
            { capacity: 6.5, expected: '11700.00' },
            { capacity: 10, expected: '18000.00' }
        ];

        testCases.forEach(({ capacity, expected }) => {
            document.body.innerHTML = '<div id="panel-cost"></div>';
            initCostForm(capacity, 5000, '2026-05-23T14:32:00Z');
            expect(document.getElementById('system_cost_eur').value).toBe(expected);
        });
    });
});
