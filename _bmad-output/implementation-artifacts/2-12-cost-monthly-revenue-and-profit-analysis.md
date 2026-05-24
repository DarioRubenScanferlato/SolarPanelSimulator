---
storyKey: 2-12-cost-monthly-revenue-and-profit-analysis
storyId: "2.12"
title: Cost Monthly Revenue and Profit Analysis
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-24'
startedAt: null
completedAt: null
---

# Story 2-12: Cost Monthly Revenue and Profit Analysis

## Story

As a homeowner tracking my solar investment returns,
I want to see how my monthly savings breaks down into revenue (from solar generation and battery optimization) and costs (system amortization and operational expenses),
So that I can understand my actual monthly profit and how the system pays for itself over time.

**Requirements Covered:** FR-10 (Cost analysis with monthly granularity and cost-benefit breakdown), ARCH-3, ARCH-4, ARCH-5

---

## Acceptance Criteria

**Given** the Cost Analysis tab displays results after simulation,
**When** I view the cost results section,
**Then** I see a stacked or grouped bar chart showing monthly breakdown across all 12 months with three segments per month:
- Segment 1 (Color: #2ecc71 green): Monthly electricity savings (revenue from reduced grid consumption + feed-in tariff revenue)
- Segment 2 (Color: #f39c12 orange): Monthly system cost allocation (amortized system cost ÷ months until ROI, or fixed amortization)
- Segment 3 (Color: #3498db blue): Net monthly profit (savings minus allocated cost)

**Given** the monthly breakdown reflects seasonal variation,
**When** I view summer months vs winter months,
**Then** summer months show higher green (savings) segments due to higher solar generation, and correspondingly higher blue (profit) segments

**Given** the chart displays revenue and profit breakdown,
**When** I hover over any month,
**Then** a tooltip shows: month name, savings amount, cost allocation, net profit in euros, and profit as a percentage of savings

**Given** monthly savings vary by season,
**When** I examine the chart,
**Then** the relationship between generation (higher in summer) and profit (higher in summer) is visually apparent

**Given** the system is in payback period (months 0 to break-even year),
**When** I view early year months,
**Then** the orange (cost allocation) segment is substantial relative to green (savings), showing net profit is small or negative

**Given** the system is past payback (after break-even year),
**When** I view later year months,
**Then** the orange (cost allocation) segment shrinks or disappears, and net profit (blue) is large

**Given** the chart updates with new simulation results,
**When** I run a new cost simulation,
**Then** the chart updates in-place using Chart.js update pattern (ARCH-5 compliance)

**Given** the Cost page has 4 charts (ROI, annual savings, timeline, and this monthly breakdown),
**When** I view the page,
**Then** all 4 charts render correctly in a 2x2 grid

---

## Architecture Notes

**Data Flow & Calculations:**

Backend returns annual savings by year (25 values). Frontend must calculate monthly breakdown:

1. **Monthly Savings Calculation:**
   - Solar generation varies seasonally (monthly_energy_kwh already available from battery.py aggregation)
   - Monthly revenue = (monthly_generation_kwh × electricity_price) + (monthly_excess_to_grid × feedin_tariff)
   - For simplicity (without hourly generation by month), distribute annual savings proportionally by season

2. **Cost Allocation:**
   - Total system cost / 25 years / 12 months = monthly amortized cost
   - Or: monthly cost = 0 before break-even, then varies after (more complex model)
   - Simpler approach: constant monthly cost allocation

3. **Net Profit:**
   - Monthly profit = monthly_savings - monthly_cost_allocation

**Data Already Available:**

From Story 2-8 (battery yearly aggregation):
- `battery_monthly_solar_consumption` [12 values] — solar directly used each month
- `battery_monthly_grid_consumption` [12 values] — grid imported each month
- `battery_monthly_battery_discharge` [12 values] — battery output each month

From cost.py:
- `cost_year_1_savings` — Year 1 total savings (can be divided by 12 for baseline)
- `cost_cumulative_savings` [25 values] — yearly cumulative savings
- System cost is provided in input parameters

**Alternative: Use Year 1 Seasonal Pattern:**

Assume Year 1 solar profile is representative:
- Monthly savings Year 1 = (annual_savings × monthly_generation_pct) where monthly_generation_pct comes from monthly totals
- Apply same monthly distribution to all 25 years (simplified; degradation handled by annual variation)

**Frontend Implementation (new file: cost-monthly-chart.js):**

```javascript
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
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            const pct = context.dataset.label === 'Monthly Savings (Revenue)' ?
                                ((value / (context.dataset.data[context.dataIndex] + 0.1)) * 100).toFixed(0) : '';
                            return label + ': €' + value.toFixed(0) + (pct ? ` (${pct}%)` : '');
                        }
                    }
                }
            }
        }
    });
}

export function updateCostMonthlyChart(monthlyData) {
    if (!monthlyChart) {
        console.warn('Monthly chart not initialized');
        return;
    }

    if (!monthlyData || !monthlyData.monthly_savings || !monthlyData.monthly_cost_allocation) {
        console.warn('Invalid monthly data: missing required arrays');
        return;
    }

    // Calculate net profit: savings - cost
    const netProfit = monthlyData.monthly_savings.map((savings, i) => {
        return Math.max(0, savings - (monthlyData.monthly_cost_allocation[i] || 0));
    });

    monthlyChart.data.datasets[0].data = monthlyData.monthly_savings;
    monthlyChart.data.datasets[1].data = monthlyData.monthly_cost_allocation;
    monthlyChart.data.datasets[2].data = netProfit;
    monthlyChart.update();
}
```

**Monthly Data Calculation in app.js:**

```javascript
function calculateMonthlyBreakdown(data) {
    if (!data.cost_year_1_savings || !data.monthly_energy_kwh) {
        return null;
    }

    const annualSavings = data.cost_year_1_savings;
    const monthlyEnergyKwh = data.monthly_energy_kwh || [];
    const totalAnnualEnergy = monthlyEnergyKwh.reduce((a, b) => a + b, 0);
    
    // Distribute annual savings by monthly energy proportion
    const monthlyContribution = monthlyEnergyKwh.map(energy => {
        return totalAnnualEnergy > 0 ? (energy / totalAnnualEnergy) * annualSavings : 0;
    });

    // Calculate monthly cost allocation (system cost amortized over 25 years)
    const systemCost = data.system_cost_eur || 0;
    const monthlyAmortization = systemCost / (25 * 12);  // €X per month for 25 years
    const monthlyCostAllocation = Array(12).fill(monthlyAmortization);

    return {
        monthly_savings: monthlyContribution,
        monthly_cost_allocation: monthlyCostAllocation
    };
}
```

**Frontend Integration (app.js & index.html):**

1. In `index.html` Cost tab, add new chart:
```html
<div class="chart-box">
    <h3>Monthly Savings Breakdown</h3>
    <div class="chart-wrapper" role="img" aria-label="Monthly revenue and profit analysis stacked bar chart">
        <canvas id="cost-monthly-chart"></canvas>
    </div>
    <p class="chart-info">How monthly savings break down: revenue, costs, and profit by month</p>
</div>
```

2. In `app.js`, import the module:
```javascript
import {
    initCostMonthlyChart,
    updateCostMonthlyChart
} from './cost-monthly-chart.js';
```

3. In `setupCostForm()`, add initialization:
```javascript
initCostMonthlyChart('cost-monthly-chart');
```

4. In `displayCostResults()`, calculate and update:
```javascript
const monthlyBreakdown = calculateMonthlyBreakdown(data);
if (monthlyBreakdown) {
    updateCostMonthlyChart(monthlyBreakdown);
}
```

---

## Tasks/Subtasks

- [ ] **Create cost-monthly-chart.js module**
  - [ ] Define monthlyChart variable
  - [ ] Implement initCostMonthlyChart() with stacked bar config for 12 months
  - [ ] Implement updateCostMonthlyChart() to populate 3 data series

- [ ] **Add helper function in app.js**
  - [ ] Implement calculateMonthlyBreakdown() to distribute annual savings by monthly energy proportion
  - [ ] Calculate amortized monthly cost allocation
  - [ ] Calculate net profit per month

- [ ] **Update index.html**
  - [ ] Add cost-monthly-chart canvas to Cost tab
  - [ ] Position in 2x2 grid (4th chart alongside ROI, annual, timeline)
  - [ ] Add ARIA labels and description

- [ ] **Update app.js**
  - [ ] Import cost-monthly-chart module
  - [ ] Call initCostMonthlyChart() in setupCostForm()
  - [ ] Call calculateMonthlyBreakdown() in displayCostResults()
  - [ ] Call updateCostMonthlyChart() with calculated data

- [ ] **Update style.css**
  - [ ] Ensure 2x2 grid layout for 4 cost charts
  - [ ] Add responsive design for mobile/tablet

- [ ] **Testing & Validation**
  - [ ] Verify 12 months display with correct labels (Jan-Dec)
  - [ ] Verify summer months show higher savings (green) segments
  - [ ] Verify winter months show lower savings segments
  - [ ] Verify orange (cost allocation) is constant across months
  - [ ] Verify blue (profit) = green - orange for each month
  - [ ] Test tooltip shows all 3 values on hover
  - [ ] Verify chart updates correctly on new simulation
  - [ ] Test responsive layout on desktop and mobile

---

## Dev Notes

**Important Context:**

1. **Monthly Distribution Model:** This story uses a simplified approach: distribute annual Year 1 savings across 12 months proportional to each month's solar generation. This assumes generation patterns are representative across the 25-year lifespan.

2. **Cost Allocation Simplification:** Rather than modeling complex amortization schedules, use simple linear amortization: system_cost / (25 years × 12 months) = fixed monthly cost. In reality, the user might prefer to see decreasing cost allocation in later years (as the system is "paid off"), but this approach is clearer and easier to implement.

3. **Net Profit Calculation:** Monthly profit = monthly_savings - monthly_cost. This is always positive in the long run (after break-even) since the cost allocation decreases relative to savings.

4. **Data Dependencies:** This chart requires `monthly_energy_kwh` from the solar simulation (already calculated). It also requires battery/cost parameters to have been run previously.

5. **Missing Data Handling:** If battery simulation hasn't been run, monthly breakdown cannot be calculated. The function should validate data presence and skip update if missing.

6. **Alternative Naming:** The three segments could also be labeled as:
   - "Gross Savings" or "Revenue"
   - "Annual Amortized Cost"
   - "Net Benefit" or "Profit"

**Previous Story Intelligence:**
- Story 2-8 calculates monthly energy totals via aggregate_to_yearly()
- Monthly energy data is already returned in API response
- Cost data is complete in cost.py responses
- Both battery and cost simulations flow through calculator.py to frontend

**Testing Approach:**
- Unit test: verify monthly distribution sums to annual savings
- Visual test: summer months (Jun-Aug) should show higher savings than winter (Dec-Feb)
- Verify cost allocation is constant (horizontal across all months)
- Verify net profit trend: low/negative early, increasingly positive over time
- Edge case: very high initial cost (most months show cost > savings early on)
- Edge case: low-cost system (profit is positive and growing from month 1)

---

## File List

**New Files:**
- `frontend/cost-monthly-chart.js` — Monthly revenue and profit stacked bar chart

**Modified Files:**
- `frontend/index.html` — Add chart container to Cost tab
- `frontend/app.js` — Add calculateMonthlyBreakdown() helper and chart integration
- `frontend/style.css` — Adjust grid for 4 cost charts

---

## Change Log

- **2026-05-24**: Story created based on user request to include cost/profit breakdown showing monthly revenue vs allocated system costs.

---

## Completion Notes

*Dev Agent: Fill this in when implementation is complete. Include:*
- Verification that monthly distribution correctly sums to annual savings
- Confirmation of stacked bar rendering with 3 segments per month
- Notes on seasonal variation visibility (summer higher than winter)
- Verification of 2x2 grid layout for all 4 cost charts
- Any adjustments to cost allocation model or calculations
