let dailyChart = null;
let yearlyChart = null;

export function initDailyChart(canvasElement) {
    const ctx = canvasElement.getContext('2d');
    dailyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
            datasets: [{
                label: 'Power (kW)',
                data: Array(24).fill(0),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.parsed.y.toFixed(2)} kW`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (value) => `${value} kW` }
                }
            }
        }
    });
}

export function updateDailyChart(data) {
    dailyChart.data.datasets[0].data = data;
    dailyChart.update();
}

export function initYearlyChart(canvasElement) {
    const ctx = canvasElement.getContext('2d');
    yearlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Energy (kWh)',
                data: Array(12).fill(0),
                backgroundColor: '#764ba2',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.parsed.y.toFixed(1)} kWh`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (value) => `${value} kWh` }
                }
            }
        }
    });
}

export function updateYearlyChart(data) {
    yearlyChart.data.datasets[0].data = data;
    yearlyChart.update();
}
