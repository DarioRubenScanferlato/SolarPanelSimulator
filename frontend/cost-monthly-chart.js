// Cost monthly breakdown chart — stacked bar showing monthly revenue, costs, and profit across 12 months

let monthlyChart = null;

export function initCostMonthlyChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element with id "${canvasId}" not found`);
        return;
    }

    const ctx = canvas.getContext('2d');
    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [
                {
                    label: 'Monthly Savings (Revenue)',
                    data: [],
                    backgroundColor: '#2ecc71',
                    borderColor: '#27ae60',
                    borderWidth: 1
                },
                {
                    label: 'System Cost Allocation',
                    data: [],
                    backgroundColor: '#f39c12',
                    borderColor: '#e67e22',
                    borderWidth: 1
                },
                {
                    label: 'Net Monthly Profit',
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
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Amount (€)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '€' + value.toFixed(0);
                        }
                    }
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
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 13 },
                    bodyFont: { size: 12 },
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return label + ': €' + value.toFixed(0);
                        }
                    }
                }
            }
        }
    });
}

export function updateCostMonthlyChart(monthlyData) {
    if (!monthlyChart) {
        console.error('updateCostMonthlyChart: chart not initialized');
        return;
    }

    if (!monthlyData || !monthlyData.monthly_savings || !monthlyData.monthly_cost_allocation) {
        console.error('updateCostMonthlyChart: missing required arrays (monthly_savings or monthly_cost_allocation)');
        return;
    }

    // Validate array lengths match 12 months (critical for chart alignment)
    if (!Array.isArray(monthlyData.monthly_savings) || monthlyData.monthly_savings.length !== 12 ||
        !Array.isArray(monthlyData.monthly_cost_allocation) || monthlyData.monthly_cost_allocation.length !== 12) {
        console.error(`updateCostMonthlyChart: arrays must have exactly 12 months; got ${monthlyData.monthly_savings?.length || '?'} and ${monthlyData.monthly_cost_allocation?.length || '?'}`);
        return;
    }

    // Use pre-computed net profit from calculateMonthlyBreakdown if available, otherwise compute
    const netProfit = monthlyData.monthly_net_profit || monthlyData.monthly_savings.map((savings, i) => {
        return savings - monthlyData.monthly_cost_allocation[i];
    });

    monthlyChart.data.datasets[0].data = monthlyData.monthly_savings;
    monthlyChart.data.datasets[1].data = monthlyData.monthly_cost_allocation;
    monthlyChart.data.datasets[2].data = netProfit;
    monthlyChart.update();
}
