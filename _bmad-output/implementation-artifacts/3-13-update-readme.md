---
storyKey: 3-13-update-readme
storyId: "3.13"
title: Update README
epicId: 3
epicTitle: Quality, Reliability & Security
status: review
createdAt: '2026-05-25'
completedAt: '2026-05-25'
---

# Story 3.13: Update README

Status: review

## Story

As a developer or user discovering the bmad-solar-panels project,
I want an accurate and complete README that reflects the current state of the application,
so that I can quickly understand what the app does, how to run it, and how to contribute.

## Acceptance Criteria

1. **Project Structure section** is replaced with the actual current directory tree, including all ES6 frontend modules (`api.js`, `charts.js`, `forms.js`, `tabs.js`, `battery-forms.js`, `battery-charts.js`, `battery-balance-chart.js`, `battery-breakdown-chart.js`, `battery-yearly-chart.js`, `cost-forms.js`, `cost-charts.js`, `cost-monthly-chart.js`, `cost-timeline-chart.js`) and backend modules (`battery.py`, `cost.py`). The `(TODO: update)` annotation is removed.

2. **Features section** lists all three simulation tabs: Solar Simulation, Battery Storage Simulation, and Cost Analysis — including their key outputs.

3. **Inputs section** covers all three tabs: solar parameters (existing), battery parameters (capacity, daily load), and cost parameters (system cost, electricity price, feed-in tariff).

4. **Outputs section** covers all three tabs: solar outputs (existing), battery outputs (self-consumption rate, grid import/export, hourly state of charge), and cost outputs (payback year, 25-year ROI, cumulative savings).

5. **Calculation Details section** `TODO: UPDATE FORMULAS` annotation is removed; a brief accurate description of the irradiance pipeline (8-step heuristic model) and battery physics model is added.

6. **Future Enhancements section** removes "Battery simulation" from the list (already implemented). Updates the list to reflect actual remaining opportunities.

7. **Known Issues section** is reviewed and updated; "Energy production calculation is inaccurate" is removed or replaced with an accurate statement about the ±6% accuracy validated against PVGIS for Turin 4 kWp.

8. **Technology Stack** section includes the full frontend module list (ES6 native modules, no bundler) and backend modules (`battery.py`, `cost.py`). It also mentions Playwright (E2E) and Jest (unit tests) under Development Tools.

9. All existing sections that are already accurate (Quick Start, Deployment, Manual Setup, Development/Testing commands) are preserved without change.

10. No new placeholder TODOs, broken links, or inaccurate claims are introduced.

## Tasks / Subtasks

- [x] Audit existing README for outdated content (AC: 1, 2, 3, 4, 5, 6, 7, 8)
  - [x] Identify all `TODO` annotations
  - [x] Identify features mentioned as "future" that are now implemented
  - [x] Identify sections with stale information
- [x] Update Project Structure section (AC: 1)
  - [x] Replace directory tree to reflect current modular file layout
  - [x] Include all 10 frontend ES6 modules and test files
  - [x] Include `battery.py` and `cost.py` in backend listing
  - [x] Include root-level docs: `DEPLOYMENT.md`, `SECURITY.md`, `ACCESSIBILITY.md`, `playwright.config.ts`
- [x] Update Features section (AC: 2)
  - [x] Add Battery Storage Simulation feature bullet
  - [x] Add Cost Analysis feature bullet
  - [x] Keep existing solar simulation bullets intact
- [x] Update Inputs section (AC: 3)
  - [x] Add battery inputs: battery capacity (kWh), max charge/discharge power (kW), daily household load (kWh), initial SoC (%)
  - [x] Add cost inputs: system cost (€), electricity price (€/kWh), feed-in tariff (€/kWh), annual price increase (%)
- [x] Update Outputs section (AC: 4)
  - [x] Add battery outputs: self-consumption rate (%), grid import (kWh), grid export (kWh), SoC curve
  - [x] Add cost outputs: payback year, 25-year ROI (€), cumulative savings chart, monthly profit breakdown
- [x] Update Calculation Details section (AC: 5)
  - [x] Remove `TODO: UPDATE FORMULAS` comment
  - [x] Add concise description of 8-step heuristic irradiance model
  - [x] Add battery physics model summary (hourly SoC state machine)
  - [x] Add cost model summary (25-year NPV with 0.5%/year panel degradation)
- [x] Update Future Enhancements (AC: 6)
  - [x] Remove "Battery simulation" item
  - [x] Remove "Cost analysis / ROI" if listed (already done)
  - [x] Keep genuinely future items: real weather API, scenario comparison, export, mobile app
- [x] Update Known Issues (AC: 7)
  - [x] Remove or replace "Energy production calculation is inaccurate"
  - [x] Optionally note the ±6% accuracy validated vs PVGIS for Turin 4 kWp
- [x] Update Technology Stack section (AC: 8)
  - [x] Add Playwright under Development Tools
  - [x] Add Jest (jsdom) under Development Tools
  - [x] Clarify frontend is ES6 native modules (no bundler, no build step)

## Dev Notes

- **This is a documentation-only story** — no code changes. Only `README.md` is modified.
- Do NOT modify `DEPLOYMENT.md`, `SECURITY.md`, or `ACCESSIBILITY.md` — those are separate documents already created by earlier stories.
- The README already has correct Quick Start, Deployment, Manual Setup, and testing command sections — preserve them verbatim.
- The disclaimer at the top of the README ("This app is generated by AI...") should be kept or removed at developer discretion — it is not load-bearing documentation.

### Accurate Project Structure (use this as reference)

```
bmad-solar-panels/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, API endpoints
│   │   ├── calculator.py     # Solar energy calculations
│   │   ├── solar_position.py # Sunrise/sunset (NOAA algorithm)
│   │   ├── irradiance.py     # 8-step heuristic irradiance model
│   │   ├── battery.py        # Battery storage physics model
│   │   ├── cost.py           # 25-year ROI and cost analysis
│   │   ├── models.py         # Pydantic request/response schemas
│   │   ├── constants.py      # Physical constants
│   │   └── validation.py     # Input validation helpers
│   ├── tests/                # pytest unit + integration tests
│   ├── pyproject.toml        # uv-managed dependencies
│   └── Dockerfile
├── frontend/
│   ├── index.html            # HTML with 3-tab structure
│   ├── style.css             # Responsive styling
│   ├── app.js                # Sole orchestrator (no circular imports)
│   ├── api.js                # All fetch() calls (only module allowed)
│   ├── charts.js             # Solar simulation charts
│   ├── forms.js              # Solar simulation form + result cards
│   ├── tabs.js               # Tab switching logic
│   ├── battery-forms.js      # Battery form + result cards
│   ├── battery-charts.js     # Battery chart orchestrator
│   ├── battery-balance-chart.js    # Hourly energy balance chart
│   ├── battery-breakdown-chart.js  # Charge/discharge breakdown
│   ├── battery-yearly-chart.js     # Yearly consumption analysis
│   ├── cost-forms.js         # Cost analysis form + result cards
│   ├── cost-charts.js        # Cost chart orchestrator
│   ├── cost-timeline-chart.js      # Payback timeline chart
│   ├── cost-monthly-chart.js       # Monthly revenue/profit chart
│   ├── __tests__/            # Jest unit tests (jsdom)
│   └── e2e/                  # Playwright E2E tests
├── frontend/Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx.conf.example
├── playwright.config.ts
├── README.md
├── DEPLOYMENT.md
├── SECURITY.md
└── ACCESSIBILITY.md
```

### Key Facts for Accuracy

- Accuracy validated at **±6% vs PVGIS** for Turin 4 kWp (not just "±10% target")
- Battery simulation covers: hourly SoC state machine, self-consumption rate, grid import/export, charge/discharge energy breakdown
- Cost analysis covers: 25-year horizon, 0.5%/year panel degradation, electricity savings, feed-in tariff revenue, payback year, cumulative ROI
- Frontend: **no bundler, no build step** — ES6 native modules served statically
- Backend: `uv` for package management (not pip/pip3) — `pyproject.toml` is the source of truth for dependencies
- httpx==0.24.1 is pinned in pyproject.toml (required for test compatibility)
- Test suite: backend pytest (>80% coverage gate), frontend Jest (jsdom), Playwright E2E

### References

- [Source: README.md] — current file with all `TODO` markers
- [Source: _bmad-output/planning-artifacts/epics.md#Epic 2] — FR-9 (battery), FR-10 (cost)
- [Source: _bmad-output/planning-artifacts/epics.md#Requirements Inventory] — NFR-2: ±10% accuracy target / validated ±6%
- [Source: _bmad-output/planning-artifacts/architecture.md#ARCH-3] — 7 ES6 modules, no bundler
- [Source: _bmad-output/planning-artifacts/architecture.md#ARCH-6] — app.js sole orchestrator; api.js only fetch() caller

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — documentation-only change, no code executed.

### Completion Notes List

- Removed outdated AI disclaimer and "Development is not complete" notice
- Rewrote Features section with Battery Storage Simulation and Cost Analysis tabs
- Replaced stale Project Structure tree (single `app.js`) with accurate 16-module frontend layout including all battery and cost chart modules, `__tests__/`, and `e2e/` directories
- Reorganized Inputs and Outputs into three subsections (Solar / Battery / Cost)
- Replaced "Calculation Details TODO: UPDATE FORMULAS" with accurate descriptions of the 8-step irradiance model, battery SoC state machine, and 25-year cost projection model
- Updated Technology Stack: added Jest+jsdom and Playwright under Testing; clarified frontend is ES6 native modules with no bundler
- Removed "Energy production calculation is inaccurate" Known Issues entry; replaced with accurate limitations section noting ±6% PVGIS validation
- Removed "Battery simulation" and "Cost analysis/ROI" from Future Enhancements (both implemented)
- Added ACCESSIBILITY.md link to Deployment section
- Added frontend unit test commands (`npm test`, `npm run test:coverage`) to Development section
- Preserved Quick Start, Deployment, Manual Setup, E2E testing commands, API docs, License, and Author sections verbatim

### File List

- README.md

### Change Log

- 2026-05-25: Full README rewrite to reflect current feature set (3 tabs: Solar, Battery, Cost), accurate project structure, and remove all TODO markers (Story 3-13)
