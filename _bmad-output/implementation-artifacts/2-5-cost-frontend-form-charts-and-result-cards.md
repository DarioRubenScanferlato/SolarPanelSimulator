---
storyKey: 2-5-cost-frontend-form-charts-and-result-cards
storyId: "2.5"
title: Cost Frontend — Form, Charts, and Result Cards
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-23'
startedAt: null
completedAt: null
---

# Story 2-5: Cost Frontend — Form, Charts, and Result Cards

## Story

As a homeowner or solar enthusiast,
I want a Cost Analysis tab with a financial parameters form, cumulative ROI chart, year-over-year savings chart, and result cards,
So that I can understand the long-term financial viability of my solar installation.

**Requirements Covered:** FR-10 (Cost Analysis & Payback), ARCH-3, ARCH-4, ARCH-5, ARCH-6, ARCH-7

---

## Acceptance Criteria

**Given** the Cost Analysis tab,
**When** I view it,
**Then** the form contains labelled inputs for: System Cost (€), Electricity Price (€/kWh), Feed-in Tariff (€/kWh), System Lifespan (years), Annual Degradation (%/year), and a "Simulate" button

**Given** the Cost Analysis tab loads for the first time,
**When** the form renders,
**Then** it displays an inheritance notice: "Using generation from Solar tab: X kWh/year (calculated at [timestamp])"

**Given** the Cost Analysis tab loads for the first time,
**When** the form renders,
**Then** it pre-fills with Italian defaults: system cost = €1,800/kW × capacity_kw, electricity price = €0.32/kWh, feed-in tariff = €0.12/kWh, lifespan = 25 years, degradation = 0.5%/year

**Given** valid inputs in both Solar and Cost forms,
**When** I click Simulate on the Cost tab,
**Then** `simulateSolar()` is called with a payload containing all solar fields plus all five cost fields

**Given** a successful cost analysis response,
**When** the results arrive,
**Then** result cards display: Year 1 Annual Savings (€), Break-even Year (or "No payback within 25 years"), 25-Year Total Savings (€) — all formatted to 2 decimal places

**Given** a successful cost analysis response,
**When** the results arrive,
**Then** a line chart renders showing cumulative savings over 25 years with a horizontal baseline at system cost and intersection point marked at break-even year

**Given** a successful cost analysis response,
**When** the results arrive,
**Then** a bar chart renders showing annual savings per year (1–25), with values declining due to panel degradation

**Given** an invalid cost field value (e.g., lifespan < 5 years),
**When** the server returns a 422 error,
**Then** the error message appears inline next to the relevant cost form field — not as a generic alert

**Given** I switch from Cost tab to Solar tab and back,
**When** I return to Cost tab after a simulation,
**Then** the charts and result cards retain their last values — no re-fetch on tab switch

---

## Tasks & Subtasks

- [ ] Create `frontend/cost-forms.js` module with form initialization and field reading
  - [ ] Export `initCostForm(capacityKw, lastSolarGeneration, lastSolarTimestamp)` — populate inheritance notice and defaults
  - [ ] Export `getCostInput()` — read all 5 cost fields from form
  - [ ] Export `showCostFieldError(fieldId, message)` — display inline error
  - [ ] Export `clearCostErrors()` — clear all error messages
  - [ ] Defaults: system_cost_eur = 1800 × capacityKw, electricity_price_eur_per_kwh = 0.32, feedin_tariff_eur_per_kwh = 0.12, lifespan_years = 25, annual_degradation_percent = 0.5
  - [ ] Inheritance notice format: "Using generation from Solar tab: [annual_energy_kwh] kWh/year (calculated at [ISO timestamp])"
  - [ ] Form structure matches battery form pattern: labeled inputs, error spans, ARIA attributes

- [ ] Create `frontend/cost-charts.js` module with chart initialization and updates
  - [ ] Export `initCostROIChart(containerId)` — create cumulative savings line chart with baseline
  - [ ] Export `updateCostROIChart(cumulativeSavingsList, systemCostEur, breakEvenYear)` — update in-place
  - [ ] Export `initCostAnnualChart(containerId)` — create annual savings bar chart
  - [ ] Export `updateCostAnnualChart(annualSavingsList)` — update in-place
  - [ ] ROI Chart: X-axis years (1-25), Y-axis cumulative €, include horizontal baseline at systemCostEur
  - [ ] Break-even visual: if breakEvenYear is not null, highlight or mark intersection point
  - [ ] Annual Chart: X-axis years (1-25), Y-axis annual savings (€), blue bars declining due to degradation
  - [ ] Use Chart.js Line and Bar chart types; colors: ROI chart #667eea (brand blue), Annual chart #667eea
  - [ ] Chart lifecycle: update in-place (chart.data.datasets[0].data = newData; chart.update()), never destroy/recreate

- [ ] Update `frontend/index.html` Cost Analysis tab section
  - [ ] Add panel-cost div with hidden attribute (tab pattern)
  - [ ] Add inheritance notice div above form (id: cost-inheritance-notice)
  - [ ] Add form with labelled inputs:
    - [ ] system_cost_eur (number, step=0.01, ge=0)
    - [ ] electricity_price_eur_per_kwh (number, step=0.01, ge=0)
    - [ ] feedin_tariff_eur_per_kwh (number, step=0.01, ge=0)
    - [ ] lifespan_years (number, step=1, ge=1)
    - [ ] annual_degradation_percent (number, step=0.1, ge=0, le=100)
  - [ ] Add "Simulate" button (id: cost-simulate-btn)
  - [ ] Add result cards section: Year 1 Savings, Break-even Year, 25-Year Total Savings
  - [ ] Add two chart canvases: #cost-roi-chart and #cost-annual-chart
  - [ ] Use same form styling pattern as battery form (accessibility attributes, ARIA labels, error spans)

- [ ] Update `frontend/app.js` to initialize and wire Cost tab
  - [ ] Import cost-forms and cost-charts modules
  - [ ] Add `setupCostForm()` function — calls `initCostForm()` with solar capacity, generation, and timestamp
  - [ ] Add `handleCostSubmit()` function — reads cost form + solar form, calls `simulateSolar()` with merged payload
  - [ ] Add `displayCostResults()` function — updates result cards and charts from API response
  - [ ] Wire Simulate button on Cost tab to `handleCostSubmit()`
  - [ ] Store solar result data in module scope for cost form initialization
  - [ ] Update setupCostForm() call in DOMContentLoaded handler after solar initialization

- [ ] Ensure tab data inheritance works correctly
  - [ ] Cost form defaults require `system_capacity_kw` from last solar simulation result
  - [ ] If solar simulation not yet run (capacity unknown), show placeholder or disable cost form
  - [ ] Inheritance notice updates on each solar simulation (timestamp + generation value)
  - [ ] Cost form maintains values across tab switches (no clearing on tab change)
  - [ ] When user switches to Cost tab, solar data is already available from previous solar simulation

- [ ] Create `frontend/__tests__/cost-frontend.test.js` unit tests (Jest + jsdom)
  - [ ] Test: Form initializes with correct defaults (including calculated system_cost_eur = 1800 × capacity)
  - [ ] Test: Inheritance notice displays with solar generation and ISO timestamp
  - [ ] Test: `getCostInput()` collects all 5 field values correctly
  - [ ] Test: Error message appears next to field with show class
  - [ ] Test: ROI chart updates in-place (chart.data + chart.update called, not destroy)
  - [ ] Test: Annual chart updates in-place
  - [ ] Test: Break-even year null displays "No payback within 25 years" in result card
  - [ ] Test: Break-even year renders correctly in result card (e.g., "Year 7")
  - [ ] Test: Form values persist across tab switches (tab data inheritance)
  - [ ] Test: Charts use correct colors (#667eea brand blue)
  - [ ] Run: `npm test -- cost-frontend.test.js` with ≥80% coverage for cost modules

- [ ] Verify backwards compatibility and integration
  - [ ] Run: `npm test` — all existing tests still pass
  - [ ] Test: Solar tab simulation still works without cost fields
  - [ ] Test: Battery tab simulation (if present) still works
  - [ ] Test: Switching tabs preserves form data in all tabs
  - [ ] Test: Form values are not shared between tabs (independent state per tab)
  - [ ] Test: Cost Simulate with valid fields passes all 5 cost params to API

---

## Dev Notes

**Architecture Context:**

Story 2.5 implements the frontend Cost Analysis UI, parallel to Story 2.4 (cost backend). The two are independent until the API integration happens — cost.py doesn't depend on any frontend module, and cost-forms.js/cost-charts.js only depend on api.js.

**ARCH-3 Compliance (ES6 modules, no build step):**
- `cost-forms.js` and `cost-charts.js` are standard ES6 modules
- Imported into `app.js` via `import { ... } from './cost-forms.js'`
- No bundler, no build step — nginx serves them directly

**ARCH-4 Compliance (Tab-based UI):**
- Cost Analysis tab is the third tab (after Solar Simulation and Battery Simulation)
- Initially a placeholder in Story 1.1; now receiving full form + charts
- Tab switching uses `switchTab('cost')` from tabs.js (existing)

**ARCH-5 Compliance (Chart lifecycle — update in-place):**
- Both cost charts (ROI cumulative + annual savings) use `chart.data.datasets[0].data = newData; chart.update()` pattern
- First call to `initCostROIChart()` creates Chart.js instance; subsequent calls to `updateCostROIChart()` update data only
- Chart instances stored in module scope (closure), referenced by update functions
- Never destroy/recreate on simulate click
- Example pattern (from battery-charts.js, replicate exactly):
  ```javascript
  let costROIChart = null;
  
  export function initCostROIChart(containerId) {
    const ctx = document.getElementById(containerId).getContext('2d');
    costROIChart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [{ data: [], ... }] },
      options: { ... }
    });
  }
  
  export function updateCostROIChart(cumulativeSavings, systemCost, breakEvenYear) {
    costROIChart.data.labels = Array.from({length: 25}, (_, i) => (i + 1).toString());
    costROIChart.data.datasets[0].data = cumulativeSavings;
    // Add baseline dataset for system cost
    costROIChart.data.datasets[1] = { label: 'System Cost', data: Array(25).fill(systemCost), ... };
    costROIChart.update();
  }
  ```

**ARCH-6 Compliance (app.js as sole orchestrator):**
- `cost-forms.js` and `cost-charts.js` export pure functions; no DOM queries beyond their own sections
- `api.js` is the only fetch caller
- `app.js` wires everything together: reads cost form, builds payload, calls `simulateSolar()`, dispatches results to update functions

**ARCH-7 Compliance (snake_case API fields):**
- HTML form inputs use snake_case names to match API: `system_cost_eur`, `electricity_price_eur_per_kwh`, etc.
- `getCostInput()` reads form and returns snake_case object keys
- `updateCostROIChart()` receives `cumulativeSavingsList` (list of 25 cumulative €) and `systemCostEur` from API response (already snake_case)

**Tab Data Inheritance Pattern (critical for cost tab):**
The Cost tab depends on solar generation data (annual_energy_kwh) and system capacity to calculate cost defaults. This follows the battery tab pattern:
1. Solar simulation runs first, stores results in `app.js` scope (e.g., `lastSolarResult`)
2. When Cost tab loads/initializes, `setupCostForm()` is called with `lastSolarResult.system_capacity_kw` and `lastSolarResult.annual_energy_kwh`
3. Form displays inheritance notice: "Using generation from X kWh/year (calculated at 2026-05-23T14:32:00Z)"
4. System cost defaults to 1800 × system_capacity_kw (Italian standard)
5. When user clicks Simulate on Cost tab, payload includes **all solar fields from the last run** (inherited) + new cost fields

**Example payload structure for cost simulation:**
```javascript
{
  // Solar fields (inherited from last solar simulation, not re-read from form)
  "latitude": 45.0703,
  "longitude": 7.6869,
  "panel_count": 10,
  "panel_area_m2": 2.0,
  "panel_efficiency": 20,
  "tilt_angle_deg": 35,
  "azimuth_deg": 180,
  "start_date": "2026-05-23",
  "duration_days": 365,
  
  // Cost fields (read from cost form)
  "system_cost_eur": 9000,
  "electricity_price_eur_per_kwh": 0.32,
  "feedin_tariff_eur_per_kwh": 0.12,
  "lifespan_years": 25,
  "annual_degradation_percent": 0.5
}
```

**API Response Shape (from Story 2-4):**
```javascript
{
  // Solar fields (existing)
  "annual_energy_kwh": 4987.2,
  "average_daily_kwh": 13.66,
  "peak_hour_kw": 5.2,
  "system_capacity_kw": 4.0,
  
  // Cost fields (Story 2-4 backend adds these)
  "cost_year_1_savings": 2200.0,
  "cost_breakeven_year": 5,  // or null
  "cost_cumulative_savings": [2200.0, 4400.0, ..., 55000.0],  // 25 values
  "cost_total_25year_savings": 55000.0
}
```

**Italian Defaults Rationale:**
- System cost €1,800/kW: Italian market standard (residential solar 2025)
- Electricity price €0.32/kWh: Italian residential average (includes VAT)
- Feed-in tariff €0.12/kWh: Italian "scambio sul posto" (net metering) rate
- Lifespan 25 years: standard for solar ROI analysis
- Degradation 0.5%/year: crystalline panel industry standard

**Break-even Visualization:**
- If `breakEvenYear` is null: result card shows "No payback within 25 years"
- If `breakEvenYear` is (e.g.) 5: result card shows "Year 5" and ROI chart shows cumulative curve intersecting baseline
- For the intersection marker: add a second dataset (system cost baseline) as a horizontal line; visual intersection is apparent

**Form Validation Pattern (from battery frontend & cost backend):**
- Cost fields are all-or-nothing: either ALL 5 are provided, or NONE
- Server returns 422 with field-level errors if partial
- Each error appears next to its input via `showCostFieldError(fieldId, message)`
- Simulate button shows "Simulating…" during fetch to indicate loading state

**Testing Strategy (Jest + jsdom):**
- Mock Chart.js to prevent canvas rendering errors (same pattern as battery tests)
- Mock fetch API to simulate cost results
- Test form initialization with various solar capacities
- Test chart update-in-place behavior (verify chart.update() is called, not destroy)
- Test error display for invalid field values
- Test tab-switch data persistence (cost form values don't clear)

**Frontend Module Import Order in app.js:**
```javascript
import { initCostForm, getCostInput, showCostFieldError, clearCostErrors } from './cost-forms.js';
import { initCostROIChart, updateCostROIChart, initCostAnnualChart, updateCostAnnualChart } from './cost-charts.js';
import { simulateSolar } from './api.js';
import { switchTab } from './tabs.js';
```

**Previous Story Learning (Stories 2-2, 2-4):**
- Battery frontend (2-2) showed the pattern for inheriting solar data and tab-based form/chart layout
- Cost backend (2-4) provides the calculation logic and API contract
- Both Stories 2-2 and 2-4 use all-or-nothing validation (inherited pattern for cost fields)
- Chart update-in-place pattern from battery-charts.js: store chart instance in module scope, never recreate

**File Relationships:**
- `cost-forms.js` (NEW) — form initialization, field reading, error display
- `cost-charts.js` (NEW) — chart creation/updates for ROI cumulative + annual savings
- `index.html` (UPDATE) — Cost Analysis tab section with form, charts, result cards
- `app.js` (UPDATE) — wire cost forms and charts; handle cost simulation
- `__tests__/cost-frontend.test.js` (NEW) — unit tests for cost modules

---

## Dev Agent Record

### Implementation Plan

1. Create cost-forms.js module with form initialization and defaults calculation
2. Create cost-charts.js module with ROI cumulative and annual savings charts
3. Update index.html Cost Analysis tab with full form and chart canvases
4. Update app.js to wire cost modules and handle cost simulation
5. Implement tab data inheritance (solar capacity → cost defaults)
6. Create comprehensive unit tests in test file
7. Run full test suite, verify coverage ≥80%, zero regressions
8. Verify backwards compatibility with solar and battery tabs

### Debug Log

**Session 1 (2026-05-23):**
(Implementation in progress)

### Completion Notes

(To be filled on completion)

---

## File List

**New Files:**
- frontend/cost-forms.js — Cost analysis form initialization and field reading
- frontend/cost-charts.js — Cost analysis ROI and annual savings charts
- frontend/__tests__/cost-frontend.test.js — Unit tests for cost frontend modules

**Modified Files:**
- frontend/index.html — Add Cost Analysis tab form, charts, result cards
- frontend/app.js — Wire cost modules, handle cost simulation and results

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-23: Story 2-5 created from Epic 2 specification
  - Cost Analysis tab frontend with form, charts, and result cards
  - Tab data inheritance from Solar tab (capacity, generation)
  - Italian financial defaults (€1,800/kW, €0.32/kWh, €0.12/kWh, 25 years, 0.5% degradation)
  - Two visualizations: cumulative ROI line chart with system cost baseline, annual savings bar chart
  - Backwards compatibility with solar and battery tabs

---

## Status

**Current:** ready-for-dev
**Completion:** 0% (tasks pending)
**Story Created:** 2026-05-23
**Started:** (pending)
**Completed:** (pending)
**Tests:** (pending)
**Next:** await dev-story agent execution

