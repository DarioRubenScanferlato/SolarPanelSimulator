---
storyKey: 2-7-battery-hourly-energy-breakdown-visualization
storyId: "2.7"
title: Battery Hourly Energy Breakdown Visualization
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-23'
startedAt: null
completedAt: null
---

# Story 2-7: Battery Hourly Energy Breakdown Visualization

## Story

As a homeowner analyzing my battery system,
I want to see detailed hourly breakdown of energy flows (solar consumption, grid consumption, energy sold to grid),
So that I can understand exactly how my battery is managing peak demand and minimizing grid dependence throughout the day.

**Requirements Covered:** FR-9 (Battery energy flow visualization), ARCH-3, ARCH-4, ARCH-5

---

## Acceptance Criteria

**Given** the Battery Simulation tab displays results after simulation,
**When** I view the battery results section,
**Then** I see a multi-series line chart showing three overlaid lines for the 24-hour period:
- Line 1 (Color: #2ecc71 green): Hourly consumption from solar (kWh) — energy used directly from solar panels
- Line 2 (Color: #f39c12 orange): Hourly consumption from grid (kWh) — energy imported from grid when solar + battery insufficient
- Line 3 (Color: #e74c3c red): Hourly energy sold to grid (kWh) — excess solar energy exported after battery charging/demand met

**Given** the three-line chart is displayed,
**When** I hover over any hour point,
**Then** a tooltip shows all three values for that hour with clear labels

**Given** the chart renders,
**When** I scroll or resize the container,
**Then** the chart updates responsively without distortion or data loss

**Given** I switch from Battery tab to another tab and return,
**When** I view the Battery tab again,
**Then** the hourly breakdown chart retains its last data and chart state (no re-fetch)

**Given** the chart uses Chart.js update pattern (chart.data + chart.update()),
**When** I run a new battery simulation with different parameters,
**Then** the chart updates in-place (no flicker from destroy/recreate) — ARCH-5 compliance

**Given** the energy balance must be validated,
**When** tests calculate hourly energy flows,
**Then** the sum of (solar consumption + grid consumption) for each hour equals the hourly demand

**And** the sum of (battery charging + solar consumption + grid export) equals hourly solar generation (within rounding tolerance)

---

## Architecture Notes

**Data Flow:**

Backend (battery.py) calculates hourly simulation:
```
For each hour:
  solar_generation[hour] = calculated from irradiance model
  demand[hour] = daily_load_kwh / 24 (simplified; could be hourly profile)
  battery_output: battery_hourly_soc[hour], self_consumption_pct, grid_export_kwh, grid_import_kwh
```

But currently battery.py returns **daily aggregates** (one day's result):
- `battery_hourly_soc`: [24 values] ✓ (hourly, used for existing chart)
- `self_consumption_pct`: single percent for the day
- `grid_export_kwh`: single value (total for day)
- `grid_import_kwh`: single value (total for day)

This story requires **extending battery output to include hourly breakdowns**:
- `battery_hourly_solar_consumption`: [24 values] — energy directly from solar each hour
- `battery_hourly_grid_consumption`: [24 values] — energy from grid each hour
- `battery_hourly_grid_export`: [24 values] — energy to grid each hour

**Backend Changes Required (in battery.py):**

During the hourly simulation loop, track:
1. Solar used directly (before battery/grid): `min(solar_generation[hour], demand[hour])`
2. Battery discharge used: `max(0, demand[hour] - solar_generation[hour])`
3. Grid import: `max(0, demand[hour] - solar_generation[hour] - battery_discharge[hour])`
4. Solar excess sent to grid: `max(0, solar_generation[hour] - demand[hour])`
5. Solar sent to battery: depends on battery charge/discharge state

Then aggregate into lists returned in response.

**Frontend Chart Implementation (battery-charts.js):**

Create new function `initBatteryBreakdownChart(container_id)`:
```javascript
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Hour 0', 'Hour 1', ..., 'Hour 23'],
    datasets: [
      { label: 'Solar Consumption', data: [], borderColor: '#2ecc71', ... },
      { label: 'Grid Consumption', data: [], borderColor: '#f39c12', ... },
      { label: 'Sold to Grid', data: [], borderColor: '#e74c3c', ... }
    ]
  }
});
```

Create new function `updateBatteryBreakdownChart(breakdownData)`:
```javascript
chart.data.datasets[0].data = breakdownData.hourly_solar_consumption;
chart.data.datasets[1].data = breakdownData.hourly_grid_consumption;
chart.data.datasets[2].data = breakdownData.hourly_grid_export;
chart.update();
```

**UI/UX Notes:**

1. **Chart Placement:** Add below the existing SoC chart in Battery tab (two stacked charts)
2. **Chart Height:** Similar to existing SoC chart (300px)
3. **Legend:** Display legend identifying each line (green = solar, orange = grid, red = export)
4. **Axis Labels:** X-axis = hours 0–23, Y-axis = energy (kWh) with auto-scale
5. **Grid Lines:** Light gridlines for readability

**Energy Balance Validation (for testing):**

For each hour, verify:
```
solar_consumption[h] + grid_consumption[h] = demand[h]
solar_consumption[h] + battery_charge[h] + grid_export[h] = solar_generation[h]
```

Where `battery_charge[h]` is positive if charging, negative if discharging.

---

## Tasks & Subtasks

- [ ] Extend `backend/app/battery.py` simulate_battery() to track hourly energy flows (AC: #1, #7)
  - [ ] During hourly simulation loop, initialize accumulators:
    - [ ] `hourly_solar_consumption` = [0] * 24
    - [ ] `hourly_grid_consumption` = [0] * 24
    - [ ] `hourly_grid_export` = [0] * 24
  - [ ] For each hour in range(24):
    - [ ] Calculate solar available: `solar_gen_hourly[h]` from daily_hourly_generation[h]
    - [ ] Calculate demand: `hourly_demand = daily_load_kwh / 24` (or extract from profile if available)
    - [ ] Calculate solar consumption: `solar_consumption = min(solar_gen_hourly[h], hourly_demand)`
    - [ ] Calculate grid/battery to meet demand: `remaining_demand = hourly_demand - solar_consumption`
    - [ ] Calculate battery discharge available: `battery_discharge = max(0, soc[h-1] - min_soc)` (constrain by available SoC)
    - [ ] Calculate grid import: `grid_import = max(0, remaining_demand - battery_discharge)`
    - [ ] Calculate solar excess: `solar_excess = solar_gen_hourly[h] - solar_consumption`
    - [ ] Calculate solar to battery: `solar_to_battery = min(solar_excess, battery_charge_capacity)` (depends on charge limits)
    - [ ] Calculate grid export: `grid_export = max(0, solar_excess - solar_to_battery)`
    - [ ] Store in accumulators:
      - [ ] `hourly_solar_consumption[h] = solar_consumption`
      - [ ] `hourly_grid_consumption[h] = grid_import`
      - [ ] `hourly_grid_export[h] = grid_export`
  - [ ] Return in response dict: add three new keys with hourly lists
  - [ ] Add code comments explaining energy flow calculation

- [ ] Update `backend/app/models.py` SolarOutput with hourly breakdown fields (AC: #1)
  - [ ] Add optional fields to SolarOutput:
    - [ ] `battery_hourly_solar_consumption: List[float] | None = None` (kWh per hour)
    - [ ] `battery_hourly_grid_consumption: List[float] | None = None` (kWh per hour)
    - [ ] `battery_hourly_grid_export: List[float] | None = None` (kWh per hour)

- [ ] Create `frontend/battery-breakdown-chart.js` module (AC: #1, #2, #3)
  - [ ] Export `initBatteryBreakdownChart(container_id)` function
  - [ ] Initialize Chart.js Line chart with three datasets (solar green, grid orange, export red)
  - [ ] X-axis: hours 0–23 with labels
  - [ ] Y-axis: energy in kWh with auto-scale
  - [ ] Legend visible identifying each series
  - [ ] No data initially (empty datasets)
  - [ ] Export `updateBatteryBreakdownChart(breakdownData)` function
    - [ ] breakdownData structure: `{ hourly_solar_consumption: [...], hourly_grid_consumption: [...], hourly_grid_export: [...] }`
    - [ ] Update chart via chart.data.datasets[*].data = breakdownData.* pattern
    - [ ] Call chart.update() (ARCH-5 compliance)

- [ ] Update `frontend/index.html` Battery tab to add breakdown chart (AC: #1, #3)
  - [ ] Add new `<div id="battery-breakdown-chart" class="chart-box">` below existing SoC chart
  - [ ] Include canvas `<canvas id="battery-breakdown-chart-canvas"></canvas>`
  - [ ] Style consistently with existing SoC chart container

- [ ] Update `frontend/app.js` to wire battery breakdown chart (AC: #2, #3)
  - [ ] In DOMContentLoaded/initialize: call `initBatteryBreakdownChart('battery-breakdown-chart-canvas')`
  - [ ] In handleBatterySubmit() response handler:
    - [ ] Extract `battery_hourly_solar_consumption`, `battery_hourly_grid_consumption`, `battery_hourly_grid_export` from response
    - [ ] Call `updateBatteryBreakdownChart({...})` with the three arrays
    - [ ] Handle missing fields gracefully (if response doesn't include hourly breakdown, log warning but don't crash)

- [ ] **Bonus: Move Simulate Button** (Quick cosmetic fix)
  - [ ] Move #batterySimulateBtn from current position to **below the battery form** (consistent with Solar tab)
  - [ ] Verify button styling is preserved and clickable

- [ ] Create comprehensive unit tests for energy balance validation (AC: #7)
  - [ ] Test: Energy balance — solar consumption + grid consumption = demand
    - [ ] For each hour, verify: `hourly_solar_consumption[h] + hourly_grid_consumption[h] == hourly_demand`
  - [ ] Test: Solar accounting — consumption + battery + export = generation
    - [ ] For each hour, verify energy conservation (within rounding tolerance)
  - [ ] Test: Grid export only occurs when excess solar
    - [ ] Verify: `grid_export[h] > 0` only when `solar_generation[h] > demand[h]`
  - [ ] Test: Grid import only when demand exceeds solar+battery
    - [ ] Verify: `grid_import[h] > 0` only when `demand[h] > solar_generation[h] + battery_discharge[h]`
  - [ ] Test: High self-consumption scenario (large battery)
    - [ ] Given: large battery, modest demand
    - [ ] Expected: low grid_consumption, moderate grid_export
  - [ ] Test: Low self-consumption scenario (small battery)
    - [ ] Given: small battery, high demand
    - [ ] Expected: high grid_consumption, low grid_export
  - [ ] Run: `pytest --cov=app --cov-fail-under=80`

- [ ] Create integration tests for /simulate with hourly breakdown (AC: #7)
  - [ ] Test: POST /simulate with battery fields returns hourly breakdown arrays
    - [ ] Expected: all three hourly arrays present with 24 elements each
  - [ ] Test: Verify hourly arrays sum to expected daily totals
    - [ ] `sum(hourly_solar_consumption) ≈ self_consumption_kwh` (derived from self_consumption_pct)
    - [ ] `sum(hourly_grid_export) ≈ grid_export_kwh` (from existing response)
    - [ ] `sum(hourly_grid_consumption) ≈ grid_import_kwh` (from existing response)

- [ ] Verify full test suite passes with no regressions (AC: #7)
  - [ ] Run: `pytest --cov=app --cov-fail-under=80`
  - [ ] Expected: all tests pass, coverage ≥80%, no regressions

---

## Dev Notes

**Architecture Context:**

This story extends the battery simulation backend (Story 2-1) to provide hourly energy flow breakdowns, enabling detailed visualization of grid interaction throughout the day. The frontend (Story 2-2) introduced the Battery tab; this story adds a new chart to complement the existing SoC visualization.

**Data Model Decision:**

Rather than computing hourly breakdowns on the frontend, we compute them on the backend because:
1. **Accuracy:** Backend has full context of solar generation, battery state, demand, efficiency
2. **Reusability:** Backend breakdowns can feed multiple frontend visualizations (hourly chart, yearly aggregation, cost analysis)
3. **Validation:** Backend can assert energy balance invariants

**Simplification (Accepted MVP Limit):**

Current battery.py uses `daily_load_kwh / 24` for hourly demand (uniform distribution). A future enhancement could:
- Accept hourly demand profile (peaks during morning/evening, lower at night/midday)
- Model realistic EV charging, heating cycles, etc.
For now, uniform demand is acceptable and simplifies the energy flow calculation.

**Color Scheme (Chosen for Clarity):**
- Green (#2ecc71): Solar consumption — positive user benefit
- Orange (#f39c12): Grid consumption — cost to user
- Red (#e74c3c): Sold to grid — missed opportunity (if emphasizing self-consumption)

Alternative: Red → green for export (revenue). Recommendation: test with user to see which is more intuitive.

**Energy Flow Equations (for backend developer):**

Each hour:
```
solar_generation[h] = hourly irradiance × panel area × efficiency
demand[h] = daily_load_kwh / 24

solar_consumption[h] = min(solar_generation[h], demand[h])
remaining_demand[h] = demand[h] - solar_consumption[h]

battery_discharge[h] = min(remaining_demand[h], max_discharge_rate, available_soc[h])
grid_import[h] = max(0, remaining_demand[h] - battery_discharge[h])

solar_excess[h] = solar_generation[h] - solar_consumption[h]
solar_to_battery[h] = charge_into_battery[h] (existing calc)
grid_export[h] = solar_excess[h] - solar_to_battery[h]

Validate: solar_consumption[h] + grid_import[h] = demand[h]
Validate: solar_consumption[h] + solar_to_battery[h] + grid_export[h] = solar_generation[h]
```

**Previous Story Context:**

Story 2-1 (Battery Backend) provides `simulate_battery(solar_output, battery_params)` returning SoC profile. This story extends that to also return hourly flow arrays. No breaking changes — existing fields (`battery_hourly_soc`, `self_consumption_pct`, etc.) remain unchanged.

**File Relationships:**
- `battery.py` (UPDATE) — add hourly flow tracking in simulation loop
- `models.py` (UPDATE) — add three optional hourly arrays to SolarOutput
- `battery-breakdown-chart.js` (NEW) — Chart.js Line chart for three energy series
- `app.js` (UPDATE) — wire breakdown chart initialization and updates
- `index.html` (UPDATE) — add breakdown chart container
- `test_battery.py` (UPDATE) — add energy balance tests

---

## Dev Agent Record

### Implementation Plan

1. Extend battery.py to track hourly energy flows (solar consumption, grid consumption, grid export)
2. Update models.py with three new optional SolarOutput fields
3. Create battery-breakdown-chart.js with Chart.js multi-series line chart
4. Update app.js to wire chart initialization and update on simulate
5. Update index.html with breakdown chart container
6. Create unit tests validating energy balance for each hour
7. Create integration tests verifying hourly sums match daily totals
8. Run full test suite, verify ≥80% coverage, zero regressions
9. (Bonus) Move simulate button below form for consistency

### Debug Log

[To be updated during implementation]

### Completion Notes

[To be updated during implementation]

---

## File List

**New Files:**
- frontend/battery-breakdown-chart.js — Chart.js multi-series visualization for energy flows
- (No new backend files, only updates)

**Modified Files:**
- backend/app/battery.py — Add hourly energy flow tracking
- backend/app/models.py — Add three hourly array fields to SolarOutput
- backend/tests/test_battery.py — Add energy balance validation tests
- frontend/app.js — Wire breakdown chart init and updates
- frontend/index.html — Add breakdown chart container
- frontend/style.css — (Minor: ensure breakdown chart container styled consistently)

**Deleted Files:**
None

---

## References

- Story 2-1: Battery Backend simulation (provides data foundation)
- Story 2-2: Battery Frontend (provides SoC chart pattern)
- Story 2-8: Battery Yearly Consumption Analysis (consumes hourly data for aggregation)
- ARCH-5: Chart lifecycle pattern (update in-place, never destroy/recreate)
