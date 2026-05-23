// Cost analysis charts — cumulative ROI and annual savings visualizations

let roiChart = null;
let annualChart = null;

export function initCostROIChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element with id "${canvasId}" not found`);
        return;
    }

    const ctx = canvas.getContext('2d');
    roiChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: 25 }, (_, i) => (i + 1).toString()),
            datasets: [
                {
                    label: 'Cumulative Savings',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.05)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: '#667eea'
                },
                {
                    label: 'System Cost Baseline',
                    data: [],
                    borderColor: '#999999',
                    backgroundColor: 'rgba(153, 153, 153, 0.05)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    tension: 0,
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 0
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
                                label += '€' + context.parsed.y.toFixed(0);
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
                    },
                    title: {
                        display: true,
                        text: 'Year'
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
                            return '€' + value.toFixed(0);
                        }
                    },
                    title: {
                        display: true,
                        text: 'Cumulative Savings (€)'
                    }
                }
            }
        }
    });
}

export function updateCostROIChart(cumulativeSavings, systemCostEur, breakEvenYear) {
    if (!roiChart) {
        console.warn('ROI chart not initialized');
        return;
    }

    // Update cumulative savings line
    roiChart.data.datasets[0].data = cumulativeSavings || [];

    // Update baseline (horizontal system cost line)
    roiChart.data.datasets[1].data = Array(25).fill(systemCostEur);

    roiChart.update();
}

export function initCostAnnualChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element with id "${canvasId}" not found`);
        return;
    }

    const ctx = canvas.getContext('2d');
    annualChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Array.from({ length: 25 }, (_, i) => (i + 1).toString()),
            datasets: [
                {
                    label: 'Annual Savings',
                    data: [],
                    backgroundColor: '#667eea',
                    borderColor: '#667eea',
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
                            return '€' + context.parsed.y.toFixed(0);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: true
                    },
                    ticks: {
                        font: { size: 10 }
                    },
                    title: {
                        display: true,
                        text: 'Year'
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
                            return '€' + value.toFixed(0);
                        }
                    },
                    title: {
                        display: true,
                        text: 'Annual Savings (€)'
                    }
                }
            }
        }
    });
}

export function updateCostAnnualChart(annualSavings) {
    if (!annualChart) {
        console.warn('Annual chart not initialized');
        return;
    }

    annualChart.data.datasets[0].data = annualSavings || [];
    annualChart.update();
}
