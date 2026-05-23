---
storyKey: 2-8-battery-yearly-consumption-analysis-graph
storyId: "2.8"
title: Battery Yearly Consumption Analysis Graph
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-23'
startedAt: null
completedAt: null
---

# Story 2-8: Battery Yearly Consumption Analysis Graph

## Story

As a homeowner planning my energy strategy,
I want to see monthly aggregated energy consumption and grid dependence over the full year,
So that I can identify seasonal patterns and understand how battery helps reduce grid dependence throughout the year.

**Requirements Covered:** FR-9 (Battery seasonal analysis), ARCH-3, ARCH-4, ARCH-5

---

## Acceptance Criteria

**Given** the Battery Simulation tab displays results,
**When** I view the battery results section,
**Then** I see a bar chart showing 12 monthly aggregates with stacked bars for each month:
- Bottom segment (Color: #2ecc71 green): Monthly solar consumption (kWh) — energy used directly from solar
- Middle segment (Color: #f39c12 orange): Monthly grid consumption (kWh) — energy imported from grid
- Top segment (Color: #3498db blue): Monthly battery discharge (kWh) — energy drawn from battery (optional, if tracked)

**Or alternatively, as three overlaid bars per month:**
- Bar 1 (green): Solar consumption
- Bar 2 (orange): Grid consumption
- Bar 3 (blue): Battery contribution to demand

**Given** the yearly consumption chart is displayed,
**When** I hover over any month,
**Then** a tooltip shows all three values for that month with clear labels and month name

**Given** the chart renders,
**When** I scroll or resize the container,
**Then** the chart updates responsively without distortion

**Given** I switch tabs and return to Battery tab,
**When** I view the Battery tab again,
**Then** the yearly consumption chart retains its data (no re-fetch)

**Given** the simulation period is 365 days (full year),
**When** yearly aggregation is calculated,
**Then** monthly values are derived by:
- Scaling hourly breakdown values from Story 2-7 (single representative day)
- Multiplying by ~30.4 days per month (or 28/29/30/31 per actual month)
- Accumulating solar/grid/battery contributions per month

**Given** the simulation period is less than 365 days,
**When** yearly aggregation is requested,
**Then** the chart shows only the months covered by the simulation with prorated values

---

## Architecture Notes

**Data Source:**

Story 2-7 provides hourly breakdown for a single representative day:
- `battery_hourly_solar_consumption`: [24 values]
- `battery_hourly_grid_consumption`: [24 values]
- `battery_hourly_grid_export`: [24 values]

To project to a full year or partial period:
1. Sum hourly values → daily totals
2. Determine which months are covered by the simulation period (start_date + duration)
3. For each month, multiply daily totals by the number of days in that month
4. Aggregate into 12 monthly bins (or fewer if simulation < 12 months)

**Simplification (Accepted MVP):**

Current battery simulation runs on a single representative day. For yearly projection:
- **Assumption:** Single day is representative of all days (no seasonal variation in solar generation or load)
- **Future enhancement:** Story 2-X could implement seasonal simulation (e.g., run for 1 day per month across the year, or full 365-day simulation)

For now, we extrapolate one day's behavior to the full year. This is acceptable because:
- User can see the pattern (grid consumption vs self-consumption)
- Values are clearly marked as projections/estimates
- Seasonal variation would be captured by re-running simulation with different date/location

**Chart Type Decision:**

Two options:
1. **Stacked Bar Chart** — shows total demand composition (solar + grid + battery per month)
   - Pro: Clear "what portion of demand comes from each source"
   - Con: Harder to compare individual series across months

2. **Grouped Bars** (3 bars per month) — shows each component side-by-side
   - Pro: Easy to compare grid consumption across months
   - Con: More visual clutter with 36 bars total

**Recommendation:** Start with **grouped bars** (Chart.js bar chart with multiple datasets). Can switch to stacked if UX feedback suggests it.

**Frontend Chart Implementation (battery-charts.js):**

Create new function `initBatteryYearlyChart(container_id)`:
```javascript
const chart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['January', 'February', ..., 'December'],
    datasets: [
      { label: 'Solar Consumption', data: [], backgroundColor: '#2ecc71', ... },
      { label: 'Grid Consumption', data: [], backgroundColor: '#f39c12', ... },
      { label: 'Battery Discharge', data: [], backgroundColor: '#3498db', ... }
    ]
  },
  options: {
    scales: {
      x: { stacked: false }, // or true for stacked bars
      y: { stacked: false }
    }
  }
});
```

Create new function `updateBatteryYearlyChart(yearlyData)`:
```javascript
chart.data.datasets[0].data = yearlyData.monthly_solar_consumption;
chart.data.datasets[1].data = yearlyData.monthly_grid_consumption;
chart.data.datasets[2].data = yearlyData.monthly_battery_discharge;
chart.update();
```

---

## Tasks & Subtasks

- [ ] Create aggregation logic in `backend/app/battery.py` or new module `backend/app/battery_yearly.py` (AC: #4)
  - [ ] Function: `aggregate_to_yearly(daily_hourly_breakdown, start_date, duration_days) -> dict`
  - [ ] Input: daily_hourly_breakdown from Story 2-7 (hourly_solar_consumption, hourly_grid_consumption, hourly_grid_export, hourly_battery_discharge)
  - [ ] Logic:
    - [ ] Sum hourly values to get daily totals: `daily_solar_sum`, `daily_grid_sum`, `daily_export_sum`, `daily_battery_sum`
    - [ ] For each month in the simulation period:
      - [ ] Determine number of days in that month (accounting for partial months)
      - [ ] Calculate monthly = daily_sum × days_in_month
      - [ ] Accumulate into 12-month bins
    - [ ] Return dict: `{ monthly_solar_consumption: [12 values], monthly_grid_consumption: [12 values], monthly_battery_discharge: [12 values] }`
  - [ ] Handle edge cases: partial months, simulation < 1 month
  - [ ] Add code comments explaining aggregation logic

- [ ] Update `backend/app/calculator.py` to invoke aggregation (AC: #4)
  - [ ] After battery simulation completes:
    - [ ] If duration >= 24 hours: call `aggregate_to_yearly(...)`
    - [ ] Add results to response with keys: `battery_monthly_solar_consumption`, `battery_monthly_grid_consumption`, `battery_monthly_battery_discharge`
    - [ ] If duration < 24 hours: set monthly arrays to empty (UI handles gracefully)

- [ ] Update `backend/app/models.py` with monthly aggregation fields (AC: #4)
  - [ ] Add optional fields to SolarOutput:
    - [ ] `battery_monthly_solar_consumption: List[float] | None = None` (kWh per month, 12 elements or fewer)
    - [ ] `battery_monthly_grid_consumption: List[float] | None = None`
    - [ ] `battery_monthly_battery_discharge: List[float] | None = None`

- [ ] Create `frontend/battery-yearly-chart.js` module (AC: #1, #2, #3)
  - [ ] Export `initBatteryYearlyChart(container_id)` function
  - [ ] Initialize Chart.js Bar chart with 3 datasets (green, orange, blue)
  - [ ] X-axis: month names (January–December)
  - [ ] Y-axis: energy (kWh) with auto-scale
  - [ ] Options: `scales: { x: { stacked: false }, y: { stacked: false } }` (grouped bars, not stacked)
  - [ ] Legend visible identifying each series
  - [ ] No data initially
  - [ ] Export `updateBatteryYearlyChart(yearlyData)` function
    - [ ] yearlyData structure: `{ monthly_solar_consumption: [...], monthly_grid_consumption: [...], monthly_battery_discharge: [...] }`
    - [ ] Update via chart.data.datasets[*].data pattern
    - [ ] Call chart.update() (ARCH-5)

- [ ] Update `frontend/index.html` Battery tab to add yearly chart (AC: #1, #3)
  - [ ] Add new `<div id="battery-yearly-chart" class="chart-box">` below the hourly breakdown chart
  - [ ] Include canvas `<canvas id="battery-yearly-chart-canvas"></canvas>`
  - [ ] Add info text: "Estimated monthly consumption based on [date] simulation"

- [ ] Update `frontend/app.js` to wire yearly chart (AC: #2, #3)
  - [ ] In DOMContentLoaded: call `initBatteryYearlyChart('battery-yearly-chart-canvas')`
  - [ ] In handleBatterySubmit() response handler:
    - [ ] Extract `battery_monthly_solar_consumption`, `battery_monthly_grid_consumption`, `battery_monthly_battery_discharge` from response
    - [ ] Call `updateBatteryYearlyChart({...})` with the three arrays
    - [ ] Handle missing fields gracefully (if not present, log warning, show message "Simulation period too short for yearly analysis")

- [ ] Create comprehensive unit tests for yearly aggregation (AC: #4)
  - [ ] Test: Daily to monthly aggregation accuracy
    - [ ] Given: daily_solar_sum = 10 kWh, month with 30 days
    - [ ] Expected: monthly_solar_consumption[month] = 300 kWh
  - [ ] Test: Partial month handling
    - [ ] Given: start_date = May 15, duration = 30 days (spans May 15 - Jun 14)
    - [ ] Expected: May aggregation accounts for 16 days only, June for 14 days only
  - [ ] Test: 365-day year covers all 12 months
    - [ ] Given: start_date = Jan 1, duration = 365
    - [ ] Expected: all 12 months populated, sum of monthly ≈ 365 × daily
  - [ ] Test: Short simulation period (< 30 days)
    - [ ] Given: duration = 7 days (1 week)
    - [ ] Expected: 1 month populated, or graceful handling of partial month
  - [ ] Test: Edge case — simulation spanning year boundary (Dec 1 - Jan 31)
    - [ ] Given: start_date = Dec 1, duration = 62 days
    - [ ] Expected: December and January populated, February empty
  - [ ] Run: `pytest --cov=app --cov-fail-under=80`

- [ ] Create integration tests for /simulate with yearly data (AC: #4)
  - [ ] Test: POST /simulate with 365-day duration returns 12-month arrays
    - [ ] Expected: all three monthly arrays present with 12 elements each
  - [ ] Test: POST /simulate with 30-day duration returns partial arrays
    - [ ] Expected: arrays reflect actual months in duration
  - [ ] Test: Monthly values aggregated correctly
    - [ ] Verify: `sum(monthly_solar_consumption) ≈ daily_solar × actual_days_in_simulation`

- [ ] Verify full test suite passes with no regressions (AC: #4)
  - [ ] Run: `pytest --cov=app --cov-fail-under=80`
  - [ ] Expected: all tests pass, coverage ≥80%, no regressions

---

## Dev Notes

**Architecture Context:**

This story adds yearly consumption analysis on top of the hourly breakdown (Story 2-7). By aggregating hourly data to monthly totals, we enable seasonal trend visualization. This is the final piece of the battery energy analysis puzzle: hourly detail → daily/monthly trends → 25-year financial impact (Story 2-6).

**Aggregation Logic:**

The aggregation function takes a single day's hourly breakdown and projects it to a full year (or partial period). The key challenge is handling:
1. **Full 365-day simulation:** Each month gets ~30.4 × daily totals
2. **Partial year:** Only months covered by simulation are populated
3. **Partial months:** Start/end months are prorated by actual days in simulation

Example:
```
If simulation is Jan 15 - Dec 31 (351 days):
  January: daily × 16 days (Jan 15-31)
  February - November: daily × 28/30/31 days
  December: daily × 31 days
```

**Data Accuracy Disclaimer:**

The yearly chart is a **projection** based on a single representative day. Users should understand:
- Solar generation varies seasonally (more in summer, less in winter)
- Demand patterns vary seasonally (heating in winter, cooling in summer)
- One day is not representative of the full year
- For accurate seasonal analysis, full 365-day simulation would be needed

**Current Limitation (Noted for Future Enhancement):**

Battery simulation currently runs on a single day. A future Story 2-X could implement:
- Full 365-day simulation (or 12 × 1 representative day per month)
- Hourly demand profile (varying throughout the day, not uniform)
- Seasonal solar variation (Erbs decomposition already per day, but not seasonal)

For now, this story accepts the MVP constraint and provides best-effort yearly projection.

**Chart Type (Grouped Bars):**

Grouped bars allow easy month-to-month comparison of grid consumption (e.g., "which months do I import most from grid?"). If users prefer stacked view (showing demand composition), this can be toggled via options.stacked = true.

**Previous Story Context:**

Story 2-7 provides the foundational hourly breakdown. This story depends on it. Development order: 2-7 → 2-8.

**File Relationships:**
- `battery.py` or `battery_yearly.py` (NEW or UPDATE) — aggregation function
- `models.py` (UPDATE) — add three monthly array fields
- `calculator.py` (UPDATE) — invoke aggregation after battery simulation
- `battery-yearly-chart.js` (NEW) — Chart.js bar chart for monthly data
- `app.js` (UPDATE) — wire yearly chart init and updates
- `index.html` (UPDATE) — add yearly chart container
- `test_battery.py` or new `test_battery_yearly.py` — aggregation logic tests

---

## Dev Agent Record

### Implementation Plan

1. Implement aggregation logic (daily → monthly) in battery.py or new battery_yearly.py
2. Update calculator.py to invoke aggregation after battery simulation
3. Update models.py with three new monthly array fields
4. Create battery-yearly-chart.js with Chart.js bar chart
5. Update app.js to wire chart initialization and updates
6. Update index.html with yearly chart container
7. Create comprehensive aggregation logic tests
8. Create integration tests for /simulate endpoint
9. Run full test suite, verify ≥80% coverage, zero regressions

### Debug Log

[To be updated during implementation]

### Completion Notes

[To be updated during implementation]

---

## File List

**New Files:**
- frontend/battery-yearly-chart.js — Chart.js bar chart for monthly energy consumption
- (Option: backend/app/battery_yearly.py for aggregation, if preferred over adding to battery.py)

**Modified Files:**
- backend/app/battery.py (or battery_yearly.py) — Add aggregation function
- backend/app/calculator.py — Invoke aggregation after battery simulation
- backend/app/models.py — Add three monthly array fields to SolarOutput
- backend/tests/test_battery.py — Add aggregation logic tests
- frontend/app.js — Wire yearly chart init and updates
- frontend/index.html — Add yearly chart container
- frontend/style.css — (Minor: ensure yearly chart container styled consistently)

**Deleted Files:**
None

---

## References

- Story 2-7: Battery Hourly Energy Breakdown (provides daily_hourly_breakdown data)
- Story 2-6: Battery-Integrated Cost Analysis (consumes yearly aggregates for 25-year projection)
- ARCH-5: Chart lifecycle pattern (update in-place, never destroy/recreate)
- Note: Yearly chart assumes single representative day; future enhancement could implement full 365-day battery simulation
