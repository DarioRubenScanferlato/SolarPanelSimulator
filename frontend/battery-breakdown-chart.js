// Battery hourly energy breakdown chart — three-series line chart showing solar/grid/export flows

let breakdownChart = null;

export function initBatteryBreakdownChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element with id "${canvasId}" not found`);
        return;
    }

    const ctx = canvas.getContext('2d');
    breakdownChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [
                'Hour 0', 'Hour 1', 'Hour 2', 'Hour 3', 'Hour 4', 'Hour 5',
                'Hour 6', 'Hour 7', 'Hour 8', 'Hour 9', 'Hour 10', 'Hour 11',
                'Hour 12', 'Hour 13', 'Hour 14', 'Hour 15', 'Hour 16', 'Hour 17',
                'Hour 18', 'Hour 19', 'Hour 20', 'Hour 21', 'Hour 22', 'Hour 23'
            ],
            datasets: [
                {
                    label: 'Solar Consumption',
                    data: [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.05)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: '#2ecc71'
                },
                {
                    label: 'Grid Consumption',
                    data: [],
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.05)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: '#f39c12'
                },
                {
                    label: 'Sold to Grid',
                    data: [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.05)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: '#e74c3c'
                },
                {
                    label: 'Battery Charge',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.05)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: '#3498db'
                },
                {
                    label: 'Total Household Consumption',
                    data: [],
                    borderColor: '#34495e',
                    backgroundColor: 'rgba(52, 73, 94, 0.05)',
                    borderWidth: 2,
                    tension: 0,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: '#34495e'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 13 },
                    bodyFont: { size: 12 },
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(2) + ' kWh';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: true,
                        drawBorder: true,
                        color: 'rgba(200, 200, 200, 0.1)'
                    },
                    ticks: {
                        font: { size: 10 }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        color: 'rgba(200, 200, 200, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + ' kWh';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Energy (kWh)'
                    }
                }
            }
        }
    });
}

export function updateBatteryBreakdownChart(breakdownData) {
    if (!breakdownChart) {
        console.warn('Breakdown chart not initialized');
        return;
    }

    if (!breakdownData || !breakdownData.hourly_solar_consumption ||
        !breakdownData.hourly_grid_consumption || !breakdownData.hourly_grid_export ||
        !breakdownData.hourly_battery_charge || !breakdownData.hourly_load) {
        console.warn('Invalid breakdown data: missing required arrays');
        return;
    }

    // Validate all arrays have exactly 24 hourly values (critical for data alignment)
    const arrays = [
        breakdownData.hourly_solar_consumption,
        breakdownData.hourly_grid_consumption,
        breakdownData.hourly_grid_export,
        breakdownData.hourly_battery_charge,
        breakdownData.hourly_load
    ];

    if (!arrays.every(arr => Array.isArray(arr) && arr.length === 24)) {
        console.warn('Invalid breakdown data: all arrays must have exactly 24 hourly values');
        return;
    }

    // Update chart data in-place (ARCH-5 compliance: never destroy/recreate)
    breakdownChart.data.datasets[0].data = breakdownData.hourly_solar_consumption;
    breakdownChart.data.datasets[1].data = breakdownData.hourly_grid_consumption;
    breakdownChart.data.datasets[2].data = breakdownData.hourly_grid_export;
    breakdownChart.data.datasets[3].data = breakdownData.hourly_battery_charge;
    breakdownChart.data.datasets[4].data = breakdownData.hourly_load;
    breakdownChart.update();
}
