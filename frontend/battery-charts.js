let batterySoCChart = null;

export function initBatterySoCChart(containerId) {
    const ctx = document.getElementById(containerId);
    if (!ctx) return;

    // Destroy existing chart if present
    if (batterySoCChart) {
        batterySoCChart.destroy();
    }

    // Create hours 0-23 labels
    const hours = Array.from({ length: 24 }, (_, i) => `Hour ${i}`);

    batterySoCChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'State of Charge (kWh)',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 4,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'SoC (kWh)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Hour of Day'
                    }
                }
            },
            animation: false
        }
    });
}

export function updateBatterySoCChart(hourlySoCList) {
    if (!batterySoCChart || !hourlySoCList) return;

    batterySoCChart.data.datasets[0].data = hourlySoCList;
    batterySoCChart.update();
}
