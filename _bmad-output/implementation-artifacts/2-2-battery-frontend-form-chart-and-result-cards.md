---
storyKey: 2-2-battery-frontend-form-chart-and-result-cards
storyId: "2.2"
title: Battery Frontend — Form, Chart, and Result Cards
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-23'
startedAt: null
completedAt: null
---

# Story 2-2: Battery Frontend — Form, Chart, and Result Cards

## Story

As a homeowner or solar enthusiast,
I want a Battery Simulation tab with an input form, a 24-hour SoC chart, and result cards for self-consumption and grid metrics,
So that I can model how a battery would affect my solar system's performance.

**Requirements Covered:** FR-9 (Battery Simulation UI), ARCH-3, ARCH-4, ARCH-5, Tab Data Inheritance

---

## Acceptance Criteria

**Given** the Battery Simulation tab,
**When** I view it,
**Then** the form contains labelled inputs for: Battery Capacity (kWh), Charge Efficiency (%), Discharge Efficiency (%), Daily Load (kWh), Initial State of Charge (%), and a "Simulate" button

**Given** the Battery Simulation tab loads for the first time,
**When** the form renders,
**Then** it pre-fills with sensible defaults: capacity 10 kWh, charge efficiency 95%, discharge efficiency 95%, daily load 10 kWh, initial SoC 50%

**Given** valid inputs in both Solar and Battery forms,
**When** I click Simulate on the Battery tab,
**Then** `simulateSolar()` is called with a payload containing all solar fields plus all five battery fields

**Given** a successful battery simulation response,
**When** the results arrive,
**Then** a line chart renders in the Battery tab showing 24 hourly SoC values (x-axis: hours 0–23, y-axis: SoC in kWh)

**Given** a successful battery simulation response,
**When** the results arrive,
**Then** result cards display: Self Consumption (%), Grid Export (kWh), Grid Import (kWh) — all formatted to 1 decimal place

**Given** an invalid battery field value (e.g., capacity < 0.5 kWh),
**When** the server returns a 422 error,
**Then** the error message appears inline next to the relevant battery form field — not as a generic alert

**Given** I switch from Battery tab to Solar tab and back,
**When** I return to Battery tab after a simulation,
**Then** the SoC chart and result cards retain their last values — no re-fetch on tab switch

---

## Tasks & Subtasks

- [ ] Create `frontend/battery-forms.js` module (ES6 native module)
  - [ ] Export `initBatteryForm()` function
  - [ ] Render battery form HTML inside #battery-panel with inputs:
    - [ ] Battery Capacity (kWh): `<input id="battery_capacity_kwh" type="number" min="1" step="0.1" />`
    - [ ] Charge Efficiency (%): `<input id="battery_charge_efficiency" type="number" min="80" max="99" value="95" />`
    - [ ] Discharge Efficiency (%): `<input id="battery_discharge_efficiency" type="number" min="80" max="99" value="95" />`
    - [ ] Daily Load (kWh): `<input id="daily_load_kwh" type="number" min="0.1" step="0.1" />`
    - [ ] Initial SoC (%): `<input id="initial_soc_pct" type="number" min="0" max="100" value="50" />`
  - [ ] Load defaults on form init: capacity=10, charge_eff=95, discharge_eff=95, daily_load=10, initial_soc=50
  - [ ] Export `getBatteryInput()` function that returns current form values as object
  - [ ] Export `showFieldError(field, message)` function to display inline error messages next to field
  - [ ] Export `clearErrors()` function to remove all error messages on new Simulate click

- [ ] Create `frontend/battery-charts.js` module (ES6 native module)
  - [ ] Export `initBatterySoCChart(container_id)` function
  - [ ] Initialize Chart.js Line chart for SoC visualization
    - [ ] X-axis: hours 0–23 with labels (Hour 0, Hour 1, ..., Hour 23)
    - [ ] Y-axis: SoC in kWh with auto-scale
    - [ ] Line color: #667eea (brand blue)
    - [ ] No data initially (empty dataset)
  - [ ] Export `updateBatterySoCChart(hourly_soc_list)` function
    - [ ] Update chart.data.datasets[0].data = hourly_soc_list (preserve existing chart object, use chart.update())
    - [ ] Clamp display to valid data range
  - [ ] Ensure chart.update() is used instead of destroying/recreating (ARCH-5 compliance)

- [ ] Create battery result cards section in HTML (if not exists)
  - [ ] Add #battery-results-cards div to #battery-panel with three card containers:
    - [ ] #battery-self-consumption-card (Self Consumption %)
    - [ ] #battery-grid-export-card (Grid Export kWh)
    - [ ] #battery-grid-import-card (Grid Import kWh)
  - [ ] Card layout: title + value, styled consistently with solar results cards

- [ ] Update `frontend/app.js` orchestration to wire Battery tab Simulate
  - [ ] In initializeApp(), call battery-forms.initBatteryForm() to populate form
  - [ ] In initializeApp(), call battery-charts.initBatterySoCChart('#battery-chart') to initialize chart
  - [ ] Add battery tab Simulate button click listener
    - [ ] Get current solar form values (via forms.getSolarInput())
    - [ ] Get current battery form values (via battery-forms.getBatteryInput())
    - [ ] Merge into single payload object with all solar + all battery fields
    - [ ] Call api.simulateSolar(payload)
  - [ ] In response handler for battery simulation:
    - [ ] If successful: call battery-charts.updateBatterySoCChart(response.battery_hourly_soc)
    - [ ] Update result cards: self_consumption_pct, grid_export_kwh, grid_import_kwh (format to 1 decimal)
    - [ ] Clear any previous error messages
    - [ ] Set #battery-panel display to visible
  - [ ] In error handler for battery simulation:
    - [ ] For each error in response.detail array:
      - [ ] Call battery-forms.showFieldError(field, message) to display inline
  - [ ] Ensure error clearing happens on next Simulate click (call battery-forms.clearErrors())

- [ ] Ensure tab switching preserves battery data
  - [ ] In tabs.switchTab(), when switching FROM battery tab: do nothing (data retained in form fields and chart)
  - [ ] In tabs.switchTab(), when switching TO battery tab: do nothing (DOM already updated by switchTab)
  - [ ] Verify: clicking Battery → Solar → Battery retains previous results

- [ ] Create Jest tests for battery frontend (basic coverage)
  - [ ] Test: initBatteryForm() renders form with default values
    - [ ] Expected: all 5 inputs present with correct defaults
  - [ ] Test: getBatteryInput() returns correct object structure
    - [ ] Expected: { battery_capacity_kwh: 10, battery_charge_efficiency: 95, ... }
  - [ ] Test: updateBatterySoCChart() updates chart data (not recreates)
    - [ ] Expected: chart.data.datasets[0].data updated, chart.update() called
  - [ ] Test: showFieldError() displays error message next to field
    - [ ] Expected: error div appears with correct message
  - [ ] Test: clearErrors() removes all error messages
    - [ ] Expected: all error divs removed from DOM

- [ ] Verify full integration test: Battery tab Simulate → chart + cards update
  - [ ] Manual test: Solar tab Simulate, then switch to Battery, adjust one field, click Simulate
  - [ ] Expected: chart updates in-place (no flicker), result cards show correct values
  - [ ] Expected: error handling displays inline errors correctly

---

## Dev Notes

**Architecture Context:**

This story implements the Battery Simulation tab UI, completing the frontend for battery simulation (Story 2.1 provides the backend). The implementation follows ARCH-3 (ES6 native modules), ARCH-4 (tab structure), and ARCH-5 (chart.update() instead of recreate). The tab inherits location, system capacity, and daily generation from the Solar tab automatically via the models.

**Module Structure:**
- `battery-forms.js` — handles form state and validation display (standalone, no DOM dependencies)
- `battery-charts.js` — manages Chart.js lifecycle for SoC visualization
- `app.js` — orchestrates tab switching, API calls, and result display (existing; small additions)
- `tabs.js` — ensures Battery tab persists data when switching (no changes needed)

**Tab Data Inheritance:**
Battery tab doesn't need to "inherit" explicitly — it simply reads solar results from the previous simulate call. The solar output (daily_hourly_generation, system_capacity_kw, location) is already in memory after Solar tab Simulate. Battery forms add the battery-specific fields, and app.js merges them into a single /simulate payload.

**Default Values (from PRD):**
- Battery Capacity: 10 kWh
- Charge Efficiency: 95%
- Discharge Efficiency: 95%
- Daily Load: 10 kWh
- Initial State of Charge: 50%

**Error Handling:**
Like Solar tab, battery validation errors from the API (422) are field-level. The frontend displays them inline next to the offending input, not as a generic alert. The message is: "All battery fields must be provided together or not at all" if partial.

**Chart Details:**
- Use Chart.js (same library as solar charts)
- Line chart with grid lines, legend visible
- X-axis: 0–23 hours, Y-axis: 0–battery_capacity_kwh auto-scale
- No animation on update (users expect instant feedback)

**Previous Story Context:**
Story 1.3 (frontend modularisation) established the modular structure, tabs.js for tab switching, and charts.js for Chart.js patterns. Inherit that style: standalone modules, no globals, init functions.

Story 2.1 (backend) validates battery fields and returns battery results if all fields present. This story consumes that backend API and displays the results.

**File Relationships:**
- `battery-forms.js` (NEW) — pure form handler
- `battery-charts.js` (NEW) — pure chart handler
- `app.js` (UPDATE) — add battery tab Simulate listener, merge payloads, update display
- `tabs.js` (NO CHANGE) — already handles data persistence
- `index.html` (UPDATE) — add battery result cards section if not exists

---

## Dev Agent Record

### Implementation Plan

1. Create battery-forms.js module with form init and input retrieval
2. Create battery-charts.js module with SoC chart visualization
3. Update app.js to orchestrate battery tab Simulate (payload merge, API call, result display)
4. Update index.html to add battery result cards (if not present)
5. Verify tab data persistence (Solar → Battery → Solar → Battery)
6. Create Jest tests for battery frontend
7. Run full test suite and verify zero regressions

### Debug Log

(To be filled by dev agent during implementation)

### Completion Notes

(To be filled by dev agent at completion)

---

## File List

**New Files:**
- frontend/battery-forms.js — Battery input form module
- frontend/battery-charts.js — SoC chart visualization module
- frontend/__tests__/battery-frontend.test.js — Jest tests for battery frontend

**Modified Files:**
- frontend/app.js — Add battery tab Simulate orchestration
- frontend/index.html — Add battery result cards section (if not present)

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-23: Story 2-2 created from Epic 2 specification
  - Battery Simulation tab UI with form, SoC chart, and result cards
  - Tab data inheritance from Solar tab (automatic via API payload merge)
  - Inline error display for 422 validation errors
  - Chart persistence across tab switches

---

## Status

**Current:** ready-for-dev
**Completion:** 0% (no tasks started)
**Depends On:** Story 2-1 (backend) must be complete before testing
**Story Created:** 2026-05-23
**Next:** await dev-story agent execution

