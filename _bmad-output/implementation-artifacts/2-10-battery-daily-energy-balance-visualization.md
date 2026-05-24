---
storyKey: 2-10-battery-daily-energy-balance-visualization
storyId: "2.10"
title: Battery Daily Energy Balance Visualization
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-24'
startedAt: null
completedAt: null
---

# Story 2-10: Battery Daily Energy Balance Visualization

## Story

As a homeowner analyzing my battery system,
I want to see a visual breakdown of how my daily solar generation is distributed (stored in battery, used for household consumption, or sold to grid),
So that I can understand the complete energy allocation picture — where every kWh of solar energy goes each day.

**Requirements Covered:** FR-9 (Battery energy distribution visualization), ARCH-3, ARCH-4, ARCH-5

---

## Acceptance Criteria

**Given** the Battery Simulation tab displays results after simulation,
**When** I view the battery results section,
**Then** I see a horizontal stacked bar chart (or waterfall chart) showing daily energy distribution with four segments:
- Segment 1 (Color: #2ecc71 green): Energy used directly from solar for household consumption
- Segment 2 (Color: #3498db blue): Energy stored in battery (charged during surplus periods)
- Segment 3 (Color: #f39c12 orange): Energy imported from grid for household consumption
- Segment 4 (Color: #e74c3c red): Energy exported to grid (unsold excess solar after battery charging and demand met)

**Given** the chart displays daily totals,
**When** I hover over or interact with any segment,
**Then** a tooltip shows: segment name, kWh value, and percentage of daily generation

**Given** all four segments together represent 100% of total daily energy flows,
**When** tests validate the chart data,
**Then** the sum of all segments equals: daily_solar_generation + daily_grid_import (total available energy)

**And** the distribution of daily generation equals: solar_consumption + battery_charge + grid_export (where these account for all solar output)

**Given** the chart updates with new simulation results,
**When** I run a new battery simulation,
**Then** the chart updates in-place using Chart.js update pattern (ARCH-5 compliance)

**Given** the Battery page now has 4 charts (SoC, hourly breakdown, monthly totals, and this new daily balance),
**When** I view the page,
**Then** all 4 charts render without layout issues in a 2x2 grid arrangement

**Given** I run a simulation with high solar generation and small load,
**When** I view the chart,
**Then** the grid import segment is 0 or very small, and battery/export segments are large

**Given** I run a simulation with high household load and low solar (e.g., winter day),
**When** I view the chart,
**Then** the grid import segment is large, battery and export segments are small

---

## Architecture Notes

**Data Flow:**

Backend (battery.py) already calculates all required daily totals:
- `battery_hourly_solar_consumption` [24 values] → sum for daily solar consumption ✓
- `hourly_battery_charge` [24 values] → sum for daily battery charge ✓ (from Story 2-9)
- `battery_hourly_grid_consumption` [24 values] → sum for daily grid import ✓
- `battery_hourly_grid_export` [24 values] → sum for daily grid export ✓

All data is already available in the API response. No backend changes needed.

**Frontend Implementation (new file: battery-balance-chart.js):**

Create new module with two functions:

```javascript
export function initBatteryBalanceChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`Canvas element with id "${canvasId}" not found`);
        return;
    }

    const ctx = canvas.getContext('2d');
    balanceChart = new Chart(ctx, {
        type: 'bar',  // Horizontal bar for stacked display
        indexAxis: 'y',  // Make it horizontal
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
```

**Frontend Integration (app.js & index.html):**

1. In `index.html` Battery tab, add new chart container in the 4-chart grid:
```html
<div class="chart-box">
    <h3>Daily Energy Balance</h3>
    <div class="chart-wrapper" role="img" aria-label="Daily energy distribution stacked bar chart">
        <canvas id="battery-balance-chart"></canvas>
    </div>
    <p class="chart-info">How daily solar generation is allocated</p>
</div>
```

2. In `app.js`, import the new module:
```javascript
import {
    initBatteryBalanceChart,
    updateBatteryBalanceChart
} from './battery-balance-chart.js';
```

3. In `setupBatteryForm()` (around line 99), add initialization:
```javascript
initBatteryBalanceChart('battery-balance-chart');
```

4. In `displayBatteryResults()` (around line 260), add update call:
```javascript
// Calculate daily totals from hourly arrays
const dailySolarConsumption = (data.battery_hourly_solar_consumption || []).reduce((a, b) => a + b, 0);
const dailyBatteryCharge = (data.battery_hourly_charge || []).reduce((a, b) => a + b, 0);
const dailyGridImport = (data.battery_hourly_grid_consumption || []).reduce((a, b) => a + b, 0);
const dailyGridExport = (data.battery_hourly_grid_export || []).reduce((a, b) => a + b, 0);

updateBatteryBalanceChart({
    daily_solar_consumption: dailySolarConsumption,
    daily_battery_charge: dailyBatteryCharge,
    daily_grid_import: dailyGridImport,
    daily_grid_export: dailyGridExport
});
```

**4-Chart Grid Layout (CSS update in style.css):**

Ensure Battery results section uses a 2x2 grid:
```css
.charts-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
    margin-top: 30px;
}

/* On tablets/mobile, revert to single column */
@media (max-width: 1200px) {
    .charts-container {
        grid-template-columns: 1fr;
    }
}
```

---

## Tasks/Subtasks

- [ ] **Create battery-balance-chart.js module**
  - [ ] Define balanceChart variable
  - [ ] Implement initBatteryBalanceChart() function with stacked bar config
  - [ ] Implement updateBatteryBalanceChart() function with validation

- [ ] **Update index.html**
  - [ ] Add battery-balance-chart canvas container to Battery tab
  - [ ] Position in 2x2 grid alongside SoC, hourly, and monthly charts
  - [ ] Add proper ARIA labels and description text

- [ ] **Update app.js**
  - [ ] Import battery-balance-chart module at top
  - [ ] Call initBatteryBalanceChart() in setupBatteryForm()
  - [ ] Calculate daily totals from hourly arrays in displayBatteryResults()
  - [ ] Call updateBatteryBalanceChart() with calculated totals

- [ ] **Update style.css**
  - [ ] Ensure 2x2 grid layout for 4 charts on desktop
  - [ ] Add responsive breakpoint for mobile/tablet (single column)

- [ ] **Testing & Validation**
  - [ ] Verify chart renders with stacked bars
  - [ ] Test chart updates correctly on new simulation
  - [ ] Validate data: sum of segments matches solar generation
  - [ ] Test responsive layout on desktop, tablet, mobile
  - [ ] Verify legend shows all 4 segments with correct colors
  - [ ] Test tooltip shows kWh values on hover

---

## Dev Notes

**Important Context:**

1. **Daily Totals Calculation:** Unlike the hourly breakdown chart which receives pre-calculated hourly arrays from the backend, the daily balance chart calculates daily totals in the frontend by summing hourly arrays. This is efficient since the data is already in the browser.

2. **Stacked Bar Chart:** Chart.js `indexAxis: 'y'` creates a horizontal bar. The `stacked: true` configuration on both x and y scales makes segments stack horizontally.

3. **Data Validation:** The update function validates that all four daily total values exist before updating. Missing data triggers a warning and prevents partial updates.

4. **Layout Impact:** Adding a 4th chart requires CSS grid adjustment. The existing `charts-container` may need to change from `repeat(auto-fit, minmax(500px, 1fr))` to `repeat(2, 1fr)` for consistent 2x2 layout.

5. **Energy Balance Equation:** 
   - Daily solar generation = daily_solar_consumption + daily_battery_charge + daily_grid_export
   - Daily consumption = daily_solar_consumption + daily_grid_import + daily_battery_discharge
   - These relationships help validate chart correctness

**Previous Story Intelligence (2-9):**
- Story 2-9 added hourly_battery_charge to backend (energy going INTO battery)
- All hourly arrays are now available in API response
- Battery-breakdown-chart.js is the pattern to follow for chart implementation

**Testing Approach:**
- Unit test: verify daily totals sum correctly
- Visual test: check stacked bar renders with 4 distinct colored segments
- Edge case: high solar + small load (battery/export large, grid import ~0)
- Edge case: low solar + high load (grid import large, battery/export small)
- Responsive test: verify 2x2 grid on desktop, single column on mobile

---

## File List

**New Files:**
- `frontend/battery-balance-chart.js` — Stacked bar chart for daily energy distribution

**Modified Files:**
- `frontend/index.html` — Add chart container to Battery tab
- `frontend/app.js` — Import module, init and update chart
- `frontend/style.css` — Adjust grid layout for 4 charts (2x2)

---

## Change Log

- **2026-05-24**: Story created based on user request for 4th battery graph to complete the page layout.

---

## Completion Notes

*Dev Agent: Fill this in when implementation is complete. Include:*
- Verification that stacked bar renders correctly with all 4 segments
- Confirmation of 2x2 grid layout on desktop
- Notes on daily total calculations and energy balance validation
- Any adjustments made to chart styling or positioning
