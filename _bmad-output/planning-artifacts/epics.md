---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
completedAt: '2026-05-22'
inputDocuments:
  - .claude/artifacts/prd-solar-simulator.md
  - _bmad-output/planning-artifacts/architecture.md
project_name: bmad-solar-panels
---

# bmad-solar-panels - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for bmad-solar-panels, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: Calculate total solar energy output (kWh) for a given location, system config, and duration using a physics-based irradiance pipeline
FR-2: Calculate civil sunrise and sunset times for given latitude, longitude, and date using NOAA algorithm
FR-3: Display hourly energy production curve for the first day of simulation (daily generation graph)
FR-4: Display monthly energy totals as a bar chart for the simulation period (yearly generation graph)
FR-5: Display summary result cards: annual energy (kWh), daily average (kWh/day), peak hour (kW), system capacity (kW)
FR-6: Provide interactive parameter input form (location, system params, date, duration) with server-side validation and inline 422 error display
FR-7: Load sensible placeholder defaults on page load so users can simulate immediately (Turin, 10 panels, 2m², 20%, 35°, 180°, today, 365 days)
FR-8: Use an 8-step heuristic irradiance model (Spencer → Kasten-Young → Laue/Meinel → seasonal cloud factor → Erbs decomposition → isotropic transposition) with no external weather API

### NonFunctional Requirements

NFR-1: Graph update <1 second after input change; page load <2 seconds; simulate <500ms
NFR-2: Calculation accuracy within ±10% of PVGIS for same inputs (validated at ±6% for Turin 4 kWp)
NFR-3: Backend test coverage >80% (pytest-cov gate); frontend Jest coverage target 80%+
NFR-4: No persistence layer, no authentication, no real-time streaming
NFR-5: Modern browser support (Chrome, Firefox, Safari, Edge); desktop-first

### Additional Requirements

- ARCH-1: Extend /simulate with optional battery fields (all-or-none validation); backwards compatible — existing calls without battery fields must continue to work
- ARCH-2: Battery simulation implemented in battery.py only — never in calculator.py or main.py
- ARCH-3: Frontend modularised into 7 ES6 native modules: app.js, api.js, charts.js, forms.js, tabs.js, battery-forms.js, battery-charts.js — no bundler, no build step
- ARCH-4: Tab-based UI: Solar Simulation tab (existing), Battery Simulation tab (new), Cost Analysis tab (placeholder only)
- ARCH-5: Chart lifecycle: update in-place (chart.data + chart.update()) — never destroy/recreate
- ARCH-6: app.js is sole orchestrator; no circular imports; api.js is only file allowed to call fetch()
- ARCH-7: All API fields snake_case — frontend reads them directly, no camelCase conversion
- ARCH-8: httpx==0.24.1 must be added to pyproject.toml (currently installed in Docker only)
- ARCH-9: Frontend refactor (Epic 1) is pre-condition for battery UI (Epic 2) — must complete first

### UX Design Requirements

None — no UX spec exists for this project. UI patterns are defined in the Architecture document (tab pattern, loading state, error display) and are captured in ARCH-3 through ARCH-7 above.

### FR Coverage Map

FR-1: Epic 1 — preserved/regression-tested during refactor (calculator.py untouched)
FR-2: Epic 1 — preserved/regression-tested during refactor (solar_position.py untouched)
FR-3: Epic 1 — charts.js extracted from app.js, daily graph behaviour preserved
FR-4: Epic 1 — charts.js extracted from app.js, yearly graph behaviour preserved
FR-5: Epic 1 — forms.js extracted from app.js, result card updates preserved
FR-6: Epic 1 — forms.js extracted from app.js, validation and defaults preserved
FR-7: Epic 1 — forms.js loads defaults on DOMContentLoaded, Turin values preserved
FR-8: Epic 1 — irradiance.py untouched; regression tests must pass after refactor
Battery simulation: Epic 2 — new capability (battery.py + battery UI)

## Epic List

### Epic 1: Frontend Modularisation

Restructure the existing single-file frontend (app.js) into clean ES6 modules and introduce a 3-tab layout — preserving all existing simulation functionality while enabling maintainable development and unlocking the battery UI in Epic 2.

**User outcome:** The Solar Simulation tab works identically after refactor; a 3-tab shell is in place for Battery and Cost Analysis tabs.
**FRs reinforced:** FR-3, FR-4, FR-5, FR-6, FR-7
**ARCH covered:** ARCH-3, ARCH-4, ARCH-5, ARCH-6, ARCH-7, ARCH-9

### Epic 2: Battery Storage Simulation

Enable users to model the impact of adding a home battery to their solar installation — visualising hourly state-of-charge, self-consumption rate, and grid import/export alongside existing solar results.

**User outcome:** Users enter battery parameters and see a SoC chart plus self-consumption and grid metrics in the Battery Simulation tab.
**FRs covered:** New capability (post-MVP battery feature)
**ARCH covered:** ARCH-1, ARCH-2, ARCH-8

---

## Epic 1: Frontend Modularisation

Restructure the existing single-file frontend (app.js) into clean ES6 modules and introduce a 3-tab layout — preserving all existing simulation functionality while enabling maintainable development and unlocking the battery UI in Epic 2.

### Story 1.1: 3-Tab Layout and Tab Switching

As a developer,
I want a 3-tab shell in `index.html` with a `tabs.js` module handling tab switching,
So that the Solar Simulation tab works as before while Battery and Cost Analysis panel slots are ready for future content.

**Acceptance Criteria:**

**Given** the page loads,
**When** I view the navigation area,
**Then** three tab buttons appear: "Solar Simulation" (active by default), "Battery Simulation", "Cost Analysis"

**Given** the page loads,
**When** I view the Solar Simulation panel,
**Then** the existing parameter form, result cards, and chart canvases are visible and functional

**Given** the page loads,
**When** I view the Battery Simulation panel,
**Then** a static placeholder message is visible (e.g., "Coming soon") — no errors or blank screen

**Given** the page loads,
**When** I view the Cost Analysis panel,
**Then** a static placeholder message is visible — no errors or blank screen

**Given** I am on any tab,
**When** I click a different tab button,
**Then** that tab's panel becomes visible (`hidden` attribute removed), all other panels are hidden, and the clicked button receives the `tab-active` CSS class

**Given** `tabs.js` exports `switchTab(tabId)`,
**When** called with a valid tabId,
**Then** it sets all `.tab-panel` elements `hidden=true`, sets `panel-{tabId}` `hidden=false`, removes `tab-active` from all `.tab-btn` elements, and adds `tab-active` to `[data-tab="{tabId}"]`

**Given** the Solar Simulation tab is active,
**When** I run a simulation end-to-end,
**Then** results render correctly — no regressions from the tab shell introduction

---

### Story 1.2: Extract API Module

As a developer,
I want all fetch logic extracted into `api.js` with a single `simulateSolar(payload)` export,
So that no other module calls `fetch()` directly and error normalisation is centralised.

**Acceptance Criteria:**

**Given** `api.js` exists and exports `simulateSolar(payload)`,
**When** called with a valid solar input payload,
**Then** it POSTs to `/simulate`, awaits the response, and returns the parsed JSON

**Given** `simulateSolar` is called,
**When** the request is in flight,
**Then** the Simulate button is `disabled` and its text reads "Simulating…"

**Given** the request completes (success or failure),
**When** the `finally` block runs,
**Then** the Simulate button is re-enabled and its text reverts to "Simulate"

**Given** the server returns HTTP 422,
**When** `simulateSolar` receives the response,
**Then** it returns a structured object containing the `detail` array from the response body (not a thrown exception that crashes the caller)

**Given** `api.js` is extracted,
**When** I inspect `app.js`, `forms.js`, and `charts.js`,
**Then** none of them contain a `fetch()` call

**Given** the full simulate flow,
**When** I click Simulate with Turin defaults,
**Then** results are identical to before extraction — no regressions in values or chart rendering

---

### Story 1.3: Extract Forms and Charts Modules; Refactor app.js

As a developer,
I want `forms.js` and `charts.js` extracted from `app.js`, with `app.js` reduced to an entry-point-only orchestrator,
So that each module has a single responsibility and the codebase is ready for battery UI additions.

**Acceptance Criteria:**

**Given** `forms.js` exports `loadDefaults()`, `readSolarForm()`, `showFieldError(fieldId, msg)`, `clearErrors()`,
**When** the page loads,
**Then** `loadDefaults()` populates all solar form fields with Turin defaults (lat 45.0703, lon 7.6869, panels 10, area 2.0, efficiency 20, tilt 35, azimuth 180, today's date, 365 days)

**Given** `charts.js` exports `initDailyChart(canvas)`, `updateDailyChart(data)`, `initYearlyChart(canvas)`, `updateYearlyChart(data)`,
**When** simulate results arrive,
**Then** charts update via `chart.data.datasets[0].data = newData; chart.update()` — no `chart.destroy()` or `new Chart()` after initialisation

**Given** `app.js` after refactor,
**When** I inspect its contents,
**Then** it contains only: ES6 import statements, a `DOMContentLoaded` listener that wires modules together, and a single simulate handler — no `fetch()` calls, no `Chart` constructor calls, no direct DOM queries beyond finding elements to pass to modules

**Given** field-level 422 errors arrive from the API,
**When** `showFieldError` is called for each error,
**Then** each message appears inline next to the correct form input

**Given** the full simulate cycle completes,
**When** result cards are updated,
**Then** annual energy, daily average, peak hour, and system capacity display correct values matching the API response

**Given** all backend tests,
**When** `pytest --cov=app` runs after this story,
**Then** zero test regressions and coverage remains ≥ 80%

---

## Epic 2: Battery Storage Simulation

Enable users to model the impact of adding a home battery to their solar installation — visualising hourly state-of-charge, self-consumption rate, and grid import/export alongside existing solar results.

### Story 2.1: Battery Backend — Physics Model, API Extension, and httpx Pin

As a developer,
I want `battery.py` implementing the hourly energy balance model, `models.py` extended with optional battery fields, and `/simulate` wired to invoke battery simulation when those fields are present,
So that the API supports battery simulation with full backwards compatibility.

**Acceptance Criteria:**

**Given** `battery.py` exports `simulate_battery(solar_output, battery_params)`,
**When** called with valid inputs,
**Then** it returns a dict with `battery_hourly_soc` (list of 24 floats in kWh), `self_consumption_pct` (float 0–100), `grid_export_kwh` (float ≥ 0), `grid_import_kwh` (float ≥ 0)

**Given** `SolarInput` extended with optional fields: `battery_capacity_kwh`, `battery_charge_efficiency`, `battery_discharge_efficiency`, `daily_load_kwh`, `initial_soc_pct` (all defaulting to `None`),
**When** POST `/simulate` is called with all battery fields populated,
**Then** the response includes `battery_hourly_soc`, `self_consumption_pct`, `grid_export_kwh`, `grid_import_kwh`

**Given** a POST `/simulate` request with no battery fields,
**When** the response is received,
**Then** it contains only solar fields — identical to the current response format (backwards compatible)

**Given** a POST `/simulate` request with only some battery fields provided (partial),
**When** the server processes the request,
**Then** it returns HTTP 422 with a clear `detail` message: all battery fields must be provided together or not at all

**Given** the hourly simulation loop,
**When** SoC is calculated for any hour,
**Then** SoC is always ≥ 0 and ≤ `battery_capacity_kwh`

**Given** `httpx==0.24.1` pinned in `pyproject.toml`,
**When** the Docker image is rebuilt from scratch,
**Then** `pytest --cov=app` passes with ≥ 80% coverage and no regressions

---

### Story 2.2: Battery Frontend — Form, Chart, and Result Cards

As a homeowner or solar enthusiast,
I want a Battery Simulation tab with an input form, a 24-hour SoC chart, and result cards for self-consumption and grid metrics,
So that I can model how a battery would affect my solar system's performance.

**Acceptance Criteria:**

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

### Story 2.3: Battery Backend Tests

As a developer,
I want comprehensive tests in `test_battery.py` covering the battery simulation physics and edge cases,
So that the energy balance model is verified and the >80% coverage gate is maintained.

**Acceptance Criteria:**

**Given** `class TestSimulateBattery` in `test_battery.py`,
**When** pytest runs,
**Then** it covers: zero-capacity returns unmodified generation values, full capacity is never exceeded across all 24 hours, SoC is never negative, grid export only occurs when solar surplus exceeds battery charge headroom, grid import only occurs when load exceeds available generation plus battery

**Given** `class TestCalculateHourlySoc`,
**When** pytest runs,
**Then** it covers: charge efficiency reduces net energy stored (stored < surplus), discharge efficiency limits draw (drawn < deficit), SoC is bounded `[0, capacity]` for every hour index 0–23

**Given** `class TestSelfConsumption`,
**When** pytest runs,
**Then** it covers: 100% self-consumption when daily load ≤ total generation and battery capacity is sufficient; 0% self-consumption when `daily_load_kwh=0`

**Given** the energy balance invariant,
**When** `test_energy_balance_holds` runs,
**Then** `grid_import_kwh + self_consumed_kwh == daily_load_kwh` within `abs=1e-6` tolerance

**Given** `pytest --cov=app` runs after adding `test_battery.py`,
**When** coverage is measured,
**Then** `battery.py` has ≥ 80% line coverage and overall `app/` coverage remains ≥ 80%

**Given** all existing test files,
**When** the full test suite runs,
**Then** zero regressions in `test_solar_position`, `test_irradiance`, `test_calculator`, `test_main`
