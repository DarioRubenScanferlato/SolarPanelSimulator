---
storyKey: 2-11-cost-payback-timeline-visualization
storyId: "2.11"
title: Cost Payback Timeline Visualization
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-24'
startedAt: null
completedAt: null
---

# Story 2-11: Cost Payback Timeline Visualization

## Story

As a homeowner evaluating solar investment,
I want to see a clear timeline showing when my system pays for itself and key financial milestones,
So that I can quickly understand the investment timeline without needing to read multiple charts.

**Requirements Covered:** FR-10 (Cost analysis & financial viability visualization), ARCH-3, ARCH-4, ARCH-5

---

## Acceptance Criteria

**Given** the Cost Analysis tab displays results after simulation,
**When** I view the cost results section,
**Then** I see a horizontal timeline visualization showing key financial milestones:
- **Year 0 (Start):** System cost (displayed as negative/cost)
- **Break-even Year:** The year when cumulative savings cross zero (savings equal system cost)
- **Year 25 (End):** Total 25-year cumulative savings

**Given** the timeline is displayed,
**When** I view each milestone marker,
**Then** each shows: year number, milestone name, and cumulative savings amount in euros

**Given** the break-even year is calculated in the backend,
**When** the system pays for itself before year 25,
**Then** the break-even milestone is prominently displayed (e.g., "Break Even: Year X")

**Given** the system does not break even within 25 years,
**When** the break-even year is null/undefined,
**Then** the timeline shows only the Year 0 and Year 25 milestones with a note: "Break-even beyond 25 years"

**Given** the timeline is interactive,
**When** I hover over a milestone,
**Then** a tooltip shows: year number, milestone description, savings/cost amount, and percentage of 25-year total

**Given** the timeline visualization uses Chart.js,
**When** I run a new cost simulation,
**Then** the chart updates in-place using Chart.js update pattern (ARCH-5 compliance)

**Given** the Cost page now has 4 charts (existing ROI, annual, timeline, and monthly breakdown),
**When** I view the page,
**Then** all 4 charts render without layout issues in a 2x2 grid arrangement

**Given** a simulation with break-even in year 15,
**When** I view the timeline,
**Then** the break-even milestone is visually distinct and positioned at year 15 on the timeline

---

## Architecture Notes

**Data Available:**

Backend (cost.py) already returns:
- `cost_breakeven_year` — the year when cumulative savings cross zero (or null if > 25 years) ✓
- `cost_cumulative_savings` [25 values] — cumulative savings for each year ✓
- `system_cost_eur` — initial system cost ✓

All data needed for the timeline is already in the API response. No backend changes required.

**Frontend Implementation (new file: cost-timeline-chart.js):**

Create new module with visualization using Chart.js scatter plot or bar chart pattern:

```javascript
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
                    data: [],  // Will contain milestone points
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
                    data: [],  // Will contain break-even point if exists
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
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
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
    if (!timelineChart) {
        console.warn('Timeline chart not initialized');
        return;
    }

    if (!timelineData || timelineData.system_cost_eur === undefined ||
        timelineData.cumulative_savings === undefined) {
        console.warn('Invalid timeline data: missing required fields');
        return;
    }

    // Build milestone points
    const milestones = [
        { x: 0, y: -timelineData.system_cost_eur }  // Year 0: System cost (negative)
    ];

    // Add break-even point if it exists
    if (timelineData.breakeven_year !== null && timelineData.breakeven_year !== undefined) {
        milestones.push({
            x: timelineData.breakeven_year,
            y: 0  // Break-even is at 0 cumulative savings
        });
    }

    // Add year 25 endpoint
    const year25Savings = timelineData.cumulative_savings[24] || 0;
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
```

**Alternative: Bar Chart Implementation:**

If scatter plot proves difficult to style, use horizontal bar markers at key years:

```javascript
// Alternative: Milestone cards as separate visualization
// Create HTML milestone container and populate dynamically

export function renderTimelineCards(timelineData) {
    const container = document.getElementById('cost-timeline-container');
    if (!container) return;

    let html = '<div class="timeline-cards">';

    // Year 0: System Cost
    html += `
        <div class="timeline-card cost">
            <div class="timeline-year">Year 0</div>
            <div class="timeline-label">System Cost</div>
            <div class="timeline-value">-€${timelineData.system_cost_eur.toFixed(0)}</div>
        </div>
    `;

    // Break-even milestone
    if (timelineData.breakeven_year !== null) {
        html += `
            <div class="timeline-card breakeven">
                <div class="timeline-year">Year ${timelineData.breakeven_year}</div>
                <div class="timeline-label">Break Even</div>
                <div class="timeline-value">€0</div>
            </div>
        `;
    }

    // Year 25: Final savings
    const year25Savings = timelineData.cumulative_savings[24] || 0;
    html += `
        <div class="timeline-card profit">
            <div class="timeline-year">Year 25</div>
            <div class="timeline-label">Total Savings</div>
            <div class="timeline-value">€${year25Savings.toFixed(0)}</div>
        </div>
    `;

    html += '</div>';
    container.innerHTML = html;
}
```

**Frontend Integration (app.js & index.html):**

1. In `index.html` Cost tab, add new chart container:
```html
<div class="chart-box">
    <h3>Payback Timeline</h3>
    <div class="chart-wrapper" role="img" aria-label="System payback timeline showing key financial milestones">
        <canvas id="cost-timeline-chart"></canvas>
    </div>
    <p class="chart-info">Key milestones: system cost, break-even year, 25-year savings</p>
</div>
```

2. In `app.js`, import the new module:
```javascript
import {
    initCostTimelineChart,
    updateCostTimelineChart
} from './cost-timeline-chart.js';
```

3. In `setupCostForm()` (around line 116), add initialization:
```javascript
initCostTimelineChart('cost-timeline-chart');
```

4. In `displayCostResults()` (around line 372), add update call:
```javascript
updateCostTimelineChart({
    system_cost_eur: data.system_cost_eur || 0,
    breakeven_year: data.cost_breakeven_year,
    cumulative_savings: data.cost_cumulative_savings || []
});
```

**4-Chart Grid Layout:**

Update `.charts-container` in style.css to use 2x2 grid (same as battery page for consistency).

---

## Tasks/Subtasks

- [ ] **Create cost-timeline-chart.js module**
  - [ ] Define timelineChart variable
  - [ ] Implement initCostTimelineChart() with scatter or bar config
  - [ ] Implement updateCostTimelineChart() to populate milestone points
  - [ ] Handle case where break-even year is null (> 25 years)

- [ ] **Update index.html**
  - [ ] Add cost-timeline-chart canvas to Cost tab
  - [ ] Position in 2x2 grid alongside ROI, annual, and monthly charts
  - [ ] Add proper ARIA labels

- [ ] **Update app.js**
  - [ ] Import cost-timeline-chart module
  - [ ] Call initCostTimelineChart() in setupCostForm()
  - [ ] Call updateCostTimelineChart() in displayCostResults()

- [ ] **Update style.css**
  - [ ] Ensure 2x2 grid for 4 cost charts
  - [ ] Add responsive breakpoints for mobile

- [ ] **Testing & Validation**
  - [ ] Verify chart displays 3 milestone points (Year 0, break-even, Year 25)
  - [ ] Test case: break-even in Year 15 (point should appear)
  - [ ] Test case: break-even beyond Year 25 (only 2 points shown)
  - [ ] Verify Year 0 shows negative system cost
  - [ ] Verify Year 25 shows correct cumulative savings
  - [ ] Test tooltip shows correct year and euro amount on hover
  - [ ] Verify chart updates correctly on new simulation

---

## Dev Notes

**Important Context:**

1. **Break-even Handling:** The cost_breakeven_year field is `null` if the system doesn't pay for itself within 25 years. The visualization must handle this gracefully by either showing only endpoints or displaying a "No payback within 25 years" message.

2. **Milestone Positioning:** Use Chart.js scatter plot with x-axis as years (0-25) and y-axis as euros. The break-even point is always at y=0 by definition. Year 0 point has negative y value (system cost as an investment).

3. **Alternative Implementation:** If Chart.js scatter proves difficult to style properly, use HTML milestone cards in a horizontal layout instead — this gives more visual control.

4. **Data Points:**
   - Year 0: y = -system_cost_eur (the upfront cost)
   - Break-even year: y = 0 (cumulative savings cross zero)
   - Year 25: y = cumulative_savings[24] (final savings)

5. **Grid Layout:** Both Battery and Cost pages now have 4 charts. Using consistent 2x2 grid layout improves UX consistency.

**Previous Story Intelligence:**
- Cost charts are implemented in cost-charts.js with ROI and annual savings
- Both use Chart.js with ARCH-5 in-place update pattern
- Tooltip formatting uses euro currency symbol (€)

**Testing Approach:**
- Unit test: verify 3 milestone points are generated correctly
- Edge case: break-even null (only 2 points)
- Visual test: verify milestone points appear at correct years on x-axis
- Verify Year 0 point is negative, break-even is 0, Year 25 is positive
- Responsive test: verify chart layout works on mobile/desktop

---

## File List

**New Files:**
- `frontend/cost-timeline-chart.js` — Timeline visualization for key financial milestones

**Modified Files:**
- `frontend/index.html` — Add chart container to Cost tab
- `frontend/app.js` — Import module, init and update chart
- `frontend/style.css` — Adjust grid for 4 cost charts

---

## Change Log

- **2026-05-24**: Story created based on user request for payback timeline visualization to improve cost clarity.

---

## Completion Notes

*Dev Agent: Fill this in when implementation is complete. Include:*
- Confirmation that milestone points render at correct years
- Notes on handling break-even null case
- Verification of 2x2 grid layout for 4 cost charts
- Any styling adjustments to make timeline visually distinct
