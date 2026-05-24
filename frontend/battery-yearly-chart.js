// Battery yearly consumption analysis — monthly aggregated energy breakdown
// Shows 12-month projection of solar consumption, grid consumption, and battery discharge

let yearlyChart = null;

export function initBatteryYearlyChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element with id "${canvasId}" not found`);
        return;
    }

    const ctx = canvas.getContext('2d');
    yearlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December'],
            datasets: [
                {
                    label: 'Solar Consumption',
                    data: [],
                    backgroundColor: '#2ecc71',
                    borderColor: '#27ae60',
                    borderWidth: 1
                },
                {
                    label: 'Grid Consumption',
                    data: [],
                    backgroundColor: '#f39c12',
                    borderColor: '#e67e22',
                    borderWidth: 1
                },
                {
                    label: 'Battery Discharge',
                    data: [],
                    backgroundColor: '#3498db',
                    borderColor: '#2980b9',
                    borderWidth: 1
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
                                label += context.parsed.y.toFixed(1) + ' kWh';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: false,
                    grid: {
                        display: true,
                        drawBorder: true,
                        color: 'rgba(200, 200, 200, 0.1)'
                    },
                    ticks: {
                        font: { size: 10 }
                    },
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    grid: {
                        display: true,
                        color: 'rgba(200, 200, 200, 0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(0) + ' kWh';
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

export function updateBatteryYearlyChart(yearlyData) {
    if (!yearlyChart) {
        console.warn('Yearly chart not initialized');
        return;
    }

    // Update datasets with monthly data
    yearlyChart.data.datasets[0].data = yearlyData.monthly_solar_consumption || [];
    yearlyChart.data.datasets[1].data = yearlyData.monthly_grid_consumption || [];
    yearlyChart.data.datasets[2].data = yearlyData.monthly_battery_discharge || [];

    // Trim X-axis labels to match actual number of months in data
    const numMonths = Math.max(
        yearlyData.monthly_solar_consumption?.length || 0,
        yearlyData.monthly_grid_consumption?.length || 0,
        yearlyData.monthly_battery_discharge?.length || 0
    );
    if (numMonths > 0 && numMonths < 12) {
        yearlyChart.data.labels = yearlyChart.data.labels.slice(0, numMonths);
    }

    yearlyChart.update();
}
