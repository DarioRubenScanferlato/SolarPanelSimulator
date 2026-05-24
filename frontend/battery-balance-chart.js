// Battery daily energy balance chart — stacked horizontal bar showing daily energy distribution

let balanceChart = null;

export function initBatteryBalanceChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element with id "${canvasId}" not found`);
        return;
    }

    const ctx = canvas.getContext('2d');
    balanceChart = new Chart(ctx, {
        type: 'bar',
        indexAxis: 'y',
        data: {
            labels: ['Daily Energy Distribution'],
            datasets: [
                {
                    label: 'Solar for Consumption',
                    data: [],
                    backgroundColor: '#2ecc71',
                    borderColor: '#27ae60',
                    borderWidth: 1
                },
                {
                    label: 'Stored in Battery',
                    data: [],
                    backgroundColor: '#3498db',
                    borderColor: '#2980b9',
                    borderWidth: 1
                },
                {
                    label: 'Grid Import',
                    data: [],
                    backgroundColor: '#f39c12',
                    borderColor: '#e67e22',
                    borderWidth: 1
                },
                {
                    label: 'Exported to Grid',
                    data: [],
                    backgroundColor: '#e74c3c',
                    borderColor: '#c0392b',
                    borderWidth: 1
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Energy (kWh)'
                    }
                },
                y: {
                    stacked: true
                }
            },
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
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.x !== null) {
                                label += context.parsed.x.toFixed(2) + ' kWh';
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

export function updateBatteryBalanceChart(balanceData) {
    if (!balanceChart) {
        console.warn('Balance chart not initialized');
        return;
    }

    if (!balanceData || balanceData.daily_solar_consumption === undefined ||
        balanceData.daily_battery_charge === undefined ||
        balanceData.daily_grid_import === undefined ||
        balanceData.daily_grid_export === undefined) {
        console.warn('Invalid balance data: missing required daily totals');
        return;
    }

    balanceChart.data.datasets[0].data = [balanceData.daily_solar_consumption];
    balanceChart.data.datasets[1].data = [balanceData.daily_battery_charge];
    balanceChart.data.datasets[2].data = [balanceData.daily_grid_import];
    balanceChart.data.datasets[3].data = [balanceData.daily_grid_export];
    balanceChart.update();
}
