const {
  initDailyChart,
  initYearlyChart,
  updateDailyChart,
  updateYearlyChart
} = require('../charts.js');

describe('charts.js', () => {
  let mockCanvasDailyChart;
  let mockCanvasYearlyChart;
  let mockChartInstances;

  beforeEach(() => {
    // Reset Chart mock
    global.Chart.mockClear();
    mockChartInstances = [];

    // Mock Chart constructor to track instances
    global.Chart.mockImplementation((ctx, config) => {
      const instance = {
        data: config.data,
        options: config.options,
        update: jest.fn(),
        destroy: jest.fn(),
        getContext: jest.fn(() => ({}))
      };
      mockChartInstances.push(instance);
      return instance;
    });

    // Setup canvas elements
    document.body.innerHTML = `
      <canvas id="dailyChart"></canvas>
      <canvas id="yearlyChart"></canvas>
    `;
    mockCanvasDailyChart = document.getElementById('dailyChart');
    mockCanvasYearlyChart = document.getElementById('yearlyChart');
  });

  afterEach(() => {
    document.body.innerHTML = '';
    mockChartInstances = [];
  });

  describe('initDailyChart', () => {
    test('creates Chart instance with correct type', () => {
      initDailyChart(mockCanvasDailyChart);

      expect(global.Chart).toHaveBeenCalled();
      const config = global.Chart.mock.calls[0][1];
      expect(config.type).toBe('line');
    });

    test('initializes with 24 hour labels', () => {
      initDailyChart(mockCanvasDailyChart);

      const config = global.Chart.mock.calls[0][1];
      expect(config.data.labels.length).toBe(24);
      expect(config.data.labels[0]).toBe('0:00');
      expect(config.data.labels[23]).toBe('23:00');
    });

    test('initializes with zero data array', () => {
      initDailyChart(mockCanvasDailyChart);

      const config = global.Chart.mock.calls[0][1];
      expect(config.data.datasets[0].data.length).toBe(24);
      expect(config.data.datasets[0].data.every(v => v === 0)).toBe(true);
    });

    test('sets correct styling properties', () => {
      initDailyChart(mockCanvasDailyChart);

      const config = global.Chart.mock.calls[0][1];
      expect(config.data.datasets[0].borderColor).toBe('#667eea');
      expect(config.data.datasets[0].label).toBe('Power (kW)');
    });
  });

  describe('initYearlyChart', () => {
    test('creates Chart instance with correct type', () => {
      initYearlyChart(mockCanvasYearlyChart);

      expect(global.Chart).toHaveBeenCalled();
      const config = global.Chart.mock.calls[0][1];
      expect(config.type).toBe('bar');
    });

    test('initializes with 12 month labels', () => {
      initYearlyChart(mockCanvasYearlyChart);

      const config = global.Chart.mock.calls[0][1];
      expect(config.data.labels.length).toBe(12);
      expect(config.data.labels[0]).toBe('Jan');
      expect(config.data.labels[11]).toBe('Dec');
    });

    test('initializes with zero data array', () => {
      initYearlyChart(mockCanvasYearlyChart);

      const config = global.Chart.mock.calls[0][1];
      expect(config.data.datasets[0].data.length).toBe(12);
      expect(config.data.datasets[0].data.every(v => v === 0)).toBe(true);
    });

    test('sets correct styling properties', () => {
      initYearlyChart(mockCanvasYearlyChart);

      const config = global.Chart.mock.calls[0][1];
      expect(config.data.datasets[0].backgroundColor).toBe('#764ba2');
      expect(config.data.datasets[0].label).toBe('Energy (kWh)');
    });
  });

  describe('updateDailyChart', () => {
    beforeEach(() => {
      initDailyChart(mockCanvasDailyChart);
    });

    test('updates chart data with new values', () => {
      const newData = Array(24).fill(1.5);
      const chartInstance = mockChartInstances[0];

      updateDailyChart(newData);

      expect(chartInstance.data.datasets[0].data).toEqual(newData);
    });

    test('calls chart.update() method', () => {
      const chartInstance = mockChartInstances[0];
      const newData = Array(24).fill(2);

      updateDailyChart(newData);

      expect(chartInstance.update).toHaveBeenCalled();
    });

    test('updates with varying data values', () => {
      const newData = [0, 0.5, 1, 1.5, 2, 2.5, 3, 2.5, 2, 1.5, 1, 0.5, 0, 0, 0, 0, 0, 0, 1, 1.5, 2, 1.5, 1, 0];
      const chartInstance = mockChartInstances[0];

      updateDailyChart(newData);

      expect(chartInstance.data.datasets[0].data[6]).toBe(3);
      expect(chartInstance.data.datasets[0].data[0]).toBe(0);
    });
  });

  describe('updateYearlyChart', () => {
    beforeEach(() => {
      initYearlyChart(mockCanvasYearlyChart);
    });

    test('updates chart data with new values', () => {
      const newData = Array(12).fill(400);
      const chartInstance = mockChartInstances[0];

      updateYearlyChart(newData);

      expect(chartInstance.data.datasets[0].data).toEqual(newData);
    });

    test('calls chart.update() method', () => {
      const chartInstance = mockChartInstances[0];
      const newData = Array(12).fill(500);

      updateYearlyChart(newData);

      expect(chartInstance.update).toHaveBeenCalled();
    });

    test('updates with varying monthly data', () => {
      const newData = [250, 280, 350, 380, 400, 420, 430, 420, 380, 320, 280, 250];
      const chartInstance = mockChartInstances[0];

      updateYearlyChart(newData);

      expect(chartInstance.data.datasets[0].data[6]).toBe(430); // July max
      expect(chartInstance.data.datasets[0].data[0]).toBe(250); // January
    });
  });

  describe('Chart lifecycle', () => {
    test('multiple chart updates persist data correctly', () => {
      initDailyChart(mockCanvasDailyChart);
      const chartInstance = mockChartInstances[0];

      const data1 = Array(24).fill(1);
      updateDailyChart(data1);
      expect(chartInstance.data.datasets[0].data[0]).toBe(1);

      const data2 = Array(24).fill(2);
      updateDailyChart(data2);
      expect(chartInstance.data.datasets[0].data[0]).toBe(2);

      expect(chartInstance.update.mock.calls.length).toBe(2);
    });

    test('does not call destroy on update', () => {
      initDailyChart(mockCanvasDailyChart);
      const chartInstance = mockChartInstances[0];

      updateDailyChart(Array(24).fill(1));

      expect(chartInstance.destroy).not.toHaveBeenCalled();
    });

    test('daily and yearly charts are separate instances', () => {
      initDailyChart(mockCanvasDailyChart);
      initYearlyChart(mockCanvasYearlyChart);

      expect(mockChartInstances.length).toBe(2);
      expect(mockChartInstances[0].data.labels.length).toBe(24);
      expect(mockChartInstances[1].data.labels.length).toBe(12);
    });
  });

  describe('Chart callback functions', () => {
    test('daily chart tooltip callback formats output correctly', () => {
      initDailyChart(mockCanvasDailyChart);
      const chartConfig = global.Chart.mock.calls[0][1];
      const tooltipCallback = chartConfig.options.plugins.tooltip.callbacks.label;

      const mockContext = { parsed: { y: 2.567 } };
      expect(tooltipCallback(mockContext)).toBe('2.57 kW');
    });

    test('yearly chart tooltip callback formats output correctly', () => {
      initYearlyChart(mockCanvasYearlyChart);
      const chartConfig = global.Chart.mock.calls[0][1];
      const tooltipCallback = chartConfig.options.plugins.tooltip.callbacks.label;

      const mockContext = { parsed: { y: 456.789 } };
      expect(tooltipCallback(mockContext)).toBe('456.8 kWh');
    });

    test('daily chart y-axis tick callback adds kW label', () => {
      initDailyChart(mockCanvasDailyChart);
      const chartConfig = global.Chart.mock.calls[0][1];
      const tickCallback = chartConfig.options.scales.y.ticks.callback;

      expect(tickCallback(5)).toBe('5 kW');
      expect(tickCallback(0)).toBe('0 kW');
    });

    test('yearly chart y-axis tick callback adds kWh label', () => {
      initYearlyChart(mockCanvasYearlyChart);
      const chartConfig = global.Chart.mock.calls[0][1];
      const tickCallback = chartConfig.options.scales.y.ticks.callback;

      expect(tickCallback(100)).toBe('100 kWh');
      expect(tickCallback(0)).toBe('0 kWh');
    });
  });
});
