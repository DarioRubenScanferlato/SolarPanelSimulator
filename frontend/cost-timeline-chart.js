// Cost payback timeline chart — scatter plot showing financial milestones (Year 0, break-even, Year 25)

let timelineChart = null;

export function initCostTimelineChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element with id "${canvasId}" not found`);
        return;
    }

    const ctx = canvas.getContext('2d');
    timelineChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Financial Milestones',
                    data: [],
                    backgroundColor: '#667eea',
                    borderColor: '#667eea',
                    borderWidth: 2,
                    pointRadius: 8,
                    pointHoverRadius: 10,
                    showLine: true,
                    borderDash: [5, 5],
                    fill: false
                },
                {
                    label: 'Break-even Year',
                    data: [],
                    backgroundColor: '#2ecc71',
                    borderColor: '#27ae60',
                    borderWidth: 2,
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    showLine: false
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
                            const label = context.dataset.label || '';
                            const x = context.parsed.x;
                            const y = context.parsed.y;
                            return label + `: Year ${x}, €${y.toFixed(0)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    min: 0,
                    max: 25,
                    title: {
                        display: true,
                        text: 'Year'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Cumulative Savings (€)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '€' + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

export function updateCostTimelineChart(timelineData) {
    console.log('updateCostTimelineChart called with:', timelineData);

    if (!timelineChart) {
        console.error('updateCostTimelineChart: chart not initialized');
        return;
    }

    if (!timelineData) {
        console.error('updateCostTimelineChart: timelineData is null/undefined');
        return;
    }

    console.log('timelineData.system_cost_eur:', timelineData.system_cost_eur, 'type:', typeof timelineData.system_cost_eur);
    console.log('timelineData.cumulative_savings:', timelineData.cumulative_savings, 'type:', typeof timelineData.cumulative_savings);

    if (timelineData.system_cost_eur === undefined) {
        console.error('updateCostTimelineChart: missing system_cost_eur');
        return;
    }

    if (timelineData.cumulative_savings === undefined) {
        console.error('updateCostTimelineChart: missing cumulative_savings');
        return;
    }

    // Validate cumulative_savings is an array with 25 elements
    if (!Array.isArray(timelineData.cumulative_savings)) {
        console.error(`updateCostTimelineChart: cumulative_savings is not an array, got ${typeof timelineData.cumulative_savings}`);
        return;
    }

    if (timelineData.cumulative_savings.length !== 25) {
        console.error(`updateCostTimelineChart: cumulative_savings has ${timelineData.cumulative_savings.length} elements, expected 25. Data:`, timelineData.cumulative_savings);
        return;
    }

    console.log('✓ All validations passed, proceeding to render timeline chart');

    // Build milestone points
    const milestones = [
        { x: 0, y: -timelineData.system_cost_eur }
    ];

    // Add break-even point if it exists
    if (timelineData.breakeven_year != null) {
        milestones.push({
            x: timelineData.breakeven_year,
            y: 0
        });
    }

    // Add year 25 endpoint (index 24 = 25th year)
    const year25Savings = timelineData.cumulative_savings[24];
    milestones.push({
        x: 25,
        y: year25Savings
    });

    // Update chart data
    timelineChart.data.datasets[0].data = milestones;

    // Highlight break-even separately if it exists
    if (timelineData.breakeven_year !== null && timelineData.breakeven_year !== undefined) {
        timelineChart.data.datasets[1].data = [{
            x: timelineData.breakeven_year,
            y: 0
        }];
    } else {
        timelineChart.data.datasets[1].data = [];
    }

    timelineChart.update();
}
