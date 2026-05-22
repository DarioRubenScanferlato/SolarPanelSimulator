---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-05-22'
inputDocuments:
  - .claude/artifacts/prd-solar-simulator.md
  - .claude/artifacts/product-brief-solar-simulator.md
  - _bmad-output/project-context.md
workflowType: 'architecture'
project_name: 'bmad-solar-panels'
user_name: 'Dario'
date: '2026-05-22'
---

# Architecture Decision Document — Solar Panel Simulator

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (current — 8 FRs):**
- FR-1 to FR-8: simulation pipeline, sunrise/sunset, daily/yearly charts, result cards, parameter form, defaults, 8-step irradiance model
- Validated within ±6% of PVGIS for Turin 4 kWp reference case

**Planned extensions (driving this architecture session):**
- Battery simulation: capture/discharge cycle modelling on top of existing generation output
- Frontend modularisation: split app.js into charts.js, api.js, forms.js (and potentially battery-specific modules)

**Non-Functional Requirements:**
- Graph update <1s; page load <2s; simulate <500ms
- Calculation accuracy ±10% PVGIS
- No persistence, no authentication, no real-time streaming
- Backend test coverage >80%; frontend Jest coverage target 80%+

**Scale & Complexity:**
- Primary domain: full-stack web, calculation-heavy Python backend
- Complexity level: low-medium (POC/demo scope)
- Estimated architectural components: 3 backend modules (calc engine + battery module + API layer), 4–5 frontend modules

### Technical Constraints & Dependencies

- Vanilla JS only — no framework (React, Vue, etc.) by project decision
- Python FastAPI + Pydantic for backend validation and response schemas
- Chart.js for visualisations
- Docker Compose orchestration — new deps require image rebuild
- pytest + pytest-cov (backend); Jest (frontend, in progress)

## Technology Foundation

### Primary Technology Domain

Full-stack web application — extending an existing codebase (brownfield). No new project initialisation required.

### Existing Stack (locked — do not change)

**Frontend:**
- Vanilla JavaScript (ES6 modules) — no framework by design decision
- HTML5 / plain CSS
- Chart.js for data visualisation
- Fetch API for backend communication

**Backend:**
- Python 3.11 + FastAPI
- Pydantic v2 for request/response validation
- pytest + pytest-cov (>80% coverage gate)
- UV for dependency management

**Infrastructure:**
- Docker Compose (frontend served via nginx or static file server; backend via uvicorn)
- Ruff linter + prek git hooks

### Target Module Structure (post-refactor)

**Backend (`backend/app/`):**
- `solar_position.py` — NOAA algorithm (existing)
- `irradiance.py` — Kasten-Young + Laue + Erbs + transposition (existing)
- `calculator.py` — orchestration + temperature derating (existing)
- `battery.py` — battery simulation module (new)
- `main.py` — FastAPI routes (extend for battery)
- `models.py` — Pydantic schemas (extend for battery)

**Frontend (`frontend/`):**
- `index.html` — single page shell
- `app.js` — entry point + initialisation only (refactored)
- `api.js` — fetch calls and error handling (new module)
- `charts.js` — Chart.js lifecycle: daily, yearly, battery charts (new module)
- `forms.js` — form state, defaults, validation display (new module)
- `battery.js` — battery input section + results display (new module)

**Note:** Frontend refactor (app.js → modules) is a pre-condition for battery UI and should be its own story completed before battery simulation is built.

---

## Core Architectural Decisions

### Decision Priority Analysis

**Critical (block implementation):**
- API contract extension strategy
- Battery physics model scope
- UI layout pattern (tabs)

**Important (shape architecture):**
- Frontend module system
- Battery chart placement

**Deferred (post-MVP):**
- Cost analysis implementation (placeholder tab only)
- Real weather API integration

---

### API & Communication Patterns

**Decision: Extend `/simulate` with optional battery fields**
- `SolarInput` gains optional battery parameters (`battery_capacity_kwh`, `battery_charge_efficiency`, `battery_discharge_efficiency`, `daily_load_kwh`, `initial_soc_pct`). All default to `None`.
- `SolarOutput` gains optional battery result fields (`battery_hourly_soc`, `self_consumption_pct`, `grid_export_kwh`, `grid_import_kwh`). Present only when battery inputs are provided.
- Backwards compatible: existing frontend calls without battery fields continue to work.
- Rationale: single endpoint, simpler client, consistent with POC scope.

**Error handling:** 422 if battery params are partially provided (all-or-none validation).

---

### Battery Simulation Model

**Decision: Simple hourly energy balance**

Inputs (all optional on `SolarInput`):

| Field | Type | Description |
|---|---|---|
| `battery_capacity_kwh` | float ≥ 0.5 | Usable battery capacity |
| `battery_charge_efficiency` | float 0.5–1.0 | Charge efficiency (default 0.95) |
| `battery_discharge_efficiency` | float 0.5–1.0 | Discharge efficiency (default 0.95) |
| `daily_load_kwh` | float ≥ 0 | Flat daily household load, distributed across 07:00–23:00 |
| `initial_soc_pct` | float 0–100 | Starting state of charge (default 50%) |

Simulation loop (per hour):
```
net = generation[h] - load[h]
if net > 0:  # surplus → charge battery
    soc[h] = min(capacity, soc[h-1] + net × charge_eff)
    grid_export[h] = net - (soc[h] - soc[h-1]) / charge_eff
else:  # deficit → discharge battery
    discharge = min(-net, soc[h-1] × discharge_eff)
    soc[h] = soc[h-1] - discharge / discharge_eff
    grid_import[h] = max(0, -net - discharge)
```

Outputs added to `SolarOutput`:
- `battery_hourly_soc`: `List[float]` — 24 hourly SoC values (kWh)
- `self_consumption_pct`: `float` — % of generation consumed directly or via battery
- `grid_export_kwh`: `float` — daily total exported to grid
- `grid_import_kwh`: `float` — daily total imported from grid

Backend module: `backend/app/battery.py`

---

### Frontend Architecture

**Decision: ES6 native modules via `<script type="module">`**
No bundler, no build step. Each file is a standard ES6 module imported directly by the browser.

**Decision: Tab-based UI layout (3 tabs)**

| Tab | Label | Status | Content |
|---|---|---|---|
| 1 | Solar Simulation | Active (existing) | Solar parameter form + result cards + daily chart + yearly chart |
| 2 | Battery Simulation | New | Battery parameter form + SoC chart + battery result cards |
| 3 | Cost Analysis | Placeholder | Static "coming soon" panel |

Tab switching: pure CSS/JS, no router. Active tab class toggled on click.

**Frontend module breakdown:**

| File | Responsibility |
|---|---|
| `app.js` | Entry point: initialise tabs, wire up modules, bootstrap on DOMContentLoaded |
| `api.js` | `simulateSolar(payload)` → POST /simulate; error normalisation |
| `forms.js` | Load defaults, read solar form values, show/clear field errors |
| `charts.js` | Create/update daily line chart + yearly bar chart (solar tab) |
| `battery-forms.js` | Read battery form values, show/clear battery field errors |
| `battery-charts.js` | Create/update hourly SoC line chart (battery tab) |
| `tabs.js` | Tab switching: show/hide panels, manage active state |

**Dependency graph (no circular imports):**
```
app.js
  ├── tabs.js
  ├── forms.js         → api.js → (fetch)
  ├── charts.js
  ├── battery-forms.js → api.js
  └── battery-charts.js
```

---

### Infrastructure & Deployment

No changes to Docker Compose or deployment. `battery.py` is added inside the existing backend image — no new services, ports, or dependencies beyond the Python standard library.

---

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Backend (Python) — snake_case throughout:**
- Files: `battery.py`, `solar_position.py`
- Functions: `simulate_battery()`, `calculate_hourly_soc()`
- Pydantic fields: `battery_capacity_kwh`, `self_consumption_pct`
- Test classes: `TestBatterySimulation`; test methods: `test_zero_capacity_passthrough`

**Frontend (JavaScript) — camelCase for variables/functions, kebab-case for files:**
- Files: `battery-forms.js`, `battery-charts.js`, `tabs.js`
- Functions: `loadBatteryDefaults()`, `updateSocChart()`, `switchTab(tabId)`
- DOM IDs: `battery-capacity`, `soc-chart`, `tab-battery` (kebab-case in HTML)
- JS references to DOM: `document.getElementById('battery-capacity')`

**API fields: always snake_case.** Pydantic serialises to snake_case; JS reads snake_case directly — do not convert to camelCase on the frontend.

---

### API Patterns

**Request:** JSON body, all fields snake_case. Battery fields optional — omit entirely when not using battery tab.

**Response:** Direct Pydantic model serialisation — no wrapper envelope. Battery fields present only when battery params were sent:
```json
{
  "annual_energy_kwh": 4987.2,
  "battery_hourly_soc": [2.1, 1.8, ...],
  "self_consumption_pct": 74.3
}
```

**Errors:** FastAPI 422 with `detail` array of `{field, message}` objects. Frontend displays these inline next to the relevant input. Never show raw Pydantic error text.

**All-or-none battery validation:** If any battery field is provided, all required battery fields must be present. Return 422 with a clear message if partial.

---

### Frontend Module Patterns

**ES6 named exports only — no default exports:**
```js
// good
export function loadBatteryDefaults() { ... }
export function readBatteryForm() { ... }

// bad
export default { loadBatteryDefaults, readBatteryForm }
```

**`app.js` imports everything; modules do NOT import each other** (except `battery-forms.js` and `forms.js` may both import `api.js`). No circular dependencies.

**Chart lifecycle — update in place, never destroy/recreate:**
```js
// good
chart.data.datasets[0].data = newValues;
chart.update();

// bad — destroys and recreates on every simulate
chart.destroy();
new Chart(...);
```
Exception: first call (chart not yet initialised) creates the instance and stores reference in module scope.

**Loading state pattern — always disable Simulate and show spinner during fetch:**
```js
simulateBtn.disabled = true;
simulateBtn.textContent = 'Simulating…';
try { ... } finally {
  simulateBtn.disabled = false;
  simulateBtn.textContent = 'Simulate';
}
```

---

### Tab Pattern

Tab panels use `hidden` attribute (not CSS `display`). Active tab button gets class `tab-active`.
```js
// tabs.js — canonical implementation
export function switchTab(tabId) {
  document.querySelectorAll('.tab-panel').forEach(p => p.hidden = true);
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('tab-active'));
  document.getElementById(`panel-${tabId}`).hidden = false;
  document.querySelector(`[data-tab="${tabId}"]`).classList.add('tab-active');
}
```

---

### Backend Patterns

**Calculator functions are pure** — no side effects, no I/O, no global state.

**Battery module follows the same shape as `calculator.py`:**
- One top-level `simulate_battery(solar_output, battery_input)` function
- Sub-functions per step: `calculate_hourly_soc()`, `calculate_self_consumption()`
- All tested in `tests/test_battery.py`

**Test pattern mirrors `test_calculator.py`:**
- Class per function: `class TestCalculateHourlySoc`
- Physical sanity checks (SoC never negative, never exceeds capacity)
- Edge cases: zero capacity, zero load, 100% self-consumption

---

---

## Project Structure & Boundaries

### Complete Project Directory Structure

```
bmad-solar-panels/
├── README.md                          # existing
├── docker-compose.yml                 # existing — orchestrates backend + frontend
│
├── backend/
│   ├── Dockerfile                     # existing — uvicorn-based image
│   ├── pyproject.toml                 # existing — UV deps + ruff + pytest config; add httpx
│   ├── uv.lock                        # existing
│   ├── .coveragerc                    # existing — coverage gate config
│   │
│   ├── app/
│   │   ├── __init__.py                # existing
│   │   ├── constants.py               # existing — shared constants (AMBIENT_TEMP_MEAN_C, etc.)
│   │   ├── solar_position.py          # existing — NOAA: julian_day, sunrise_sunset, hourly_sun_position
│   │   ├── irradiance.py              # existing — Kasten-Young → Erbs → isotropic transposition
│   │   ├── calculator.py              # existing — orchestration: simulate(), calculate_daily_profile()
│   │   ├── battery.py                 # NEW — hourly energy balance: simulate_battery()
│   │   ├── models.py                  # EXTEND — SolarInput + SolarOutput: add optional battery fields
│   │   ├── validation.py              # existing — field-level validators
│   │   └── main.py                    # EXTEND — /simulate route: wire battery.py when battery params present
│   │
│   └── tests/
│       ├── __init__.py                # existing
│       ├── conftest.py                # existing — shared fixtures: default_solar_input, turin_location, etc.
│       ├── test_solar_position.py     # existing — 95% coverage
│       ├── test_irradiance.py         # existing
│       ├── test_calculator.py         # existing
│       ├── test_main.py               # existing — FastAPI TestClient integration tests
│       └── test_battery.py            # NEW — TestBatterySimulation, TestCalculateHourlySoc, edge cases
│
└── frontend/
    ├── Dockerfile                     # existing — nginx static file server
    ├── index.html                     # REWRITE — add 3-tab layout + battery form section
    ├── style.css                      # EXTEND — tab styles + battery section styles
    ├── app.js                         # REFACTOR — entry point only: init tabs, wire modules on DOMContentLoaded
    ├── api.js                         # NEW — simulateSolar(payload) → POST /simulate; error normalisation
    ├── charts.js                      # NEW — daily line chart + yearly bar chart (solar tab)
    ├── forms.js                       # NEW — solar form: load defaults, read values, show/clear errors
    ├── tabs.js                        # NEW — switchTab(tabId): toggle hidden + tab-active class
    ├── battery-forms.js               # NEW — battery form: read values, show/clear errors; imports api.js
    └── battery-charts.js              # NEW — hourly SoC line chart (battery tab)
```

---

### Architectural Boundaries

**API Boundary — single POST `/simulate`:**
- Entry: `backend/app/main.py`
- Request validated by Pydantic: `SolarInput` in `models.py`
- Response serialised by Pydantic: `SolarOutput` in `models.py`
- Battery fields optional — omit entirely for solar-only calls; all-or-none validation on partial battery input (422)
- `validation.py` owns field-range constraints; `main.py` owns the all-or-none battery check

**Component Boundaries — frontend module isolation:**
- `app.js` is the sole orchestrator; imports all other modules
- No circular dependencies — `api.js` may be imported by `forms.js` and `battery-forms.js` only
- `api.js` is the only file allowed to call `fetch()`
- Chart instances live in `charts.js` / `battery-charts.js` module scope; updated in-place, never recreated

**Data Boundaries:**
- No persistence — all data is ephemeral per-request
- Request → Response is the only data flow: JSON body in, JSON body out
- Frontend reads snake_case API fields directly — no camelCase conversion

---

### Requirements → Structure Mapping

| Requirement | File(s) |
|---|---|
| FR-1 Solar generation simulation | `calculator.py`, `models.py` |
| FR-2 Sunrise/sunset | `solar_position.py` |
| FR-3 Daily hourly graph | `charts.js` (frontend), `calculator.py` (backend) |
| FR-4 Yearly graph | `charts.js` (frontend), `calculator.py` (backend) |
| FR-5 Result cards | `app.js` + `forms.js` (DOM updates) |
| FR-6 Interactive parameter form | `forms.js`, `battery-forms.js`, `index.html` |
| FR-7 Placeholder defaults | `forms.js` (loads on DOMContentLoaded) |
| FR-8 Irradiance model | `irradiance.py`, `solar_position.py` |
| Battery simulation (new) | `battery.py`, `models.py`, `battery-forms.js`, `battery-charts.js` |
| 3-tab UI layout | `tabs.js`, `index.html`, `style.css` |
| Cost analysis placeholder | `index.html` (static panel only) |

---

### Integration Points

**Frontend → Backend:**
```
user clicks Simulate
  → forms.js / battery-forms.js reads form values
  → app.js builds payload
  → api.js POST /simulate
  → app.js dispatches results to charts.js + battery-charts.js + DOM card updates
```

**Backend module chain:**
```
main.py (route)
  → calculator.simulate()      → solar_position, irradiance, constants
  → battery.simulate_battery() → called only when battery params present
  → returns SolarOutput (battery fields populated when battery ran)
```

**External integrations:** None (no weather API, no auth, no persistence).

---

### Epic → Story Mapping

**Epic 1 — Frontend Refactor** (pre-condition for battery UI):
- Story 1.1: `index.html` → 3-tab layout + tab switching (`tabs.js`)
- Story 1.2: Extract `api.js` from `app.js`
- Story 1.3: Extract `forms.js` + `charts.js`; `app.js` becomes entry point only

**Epic 2 — Battery Simulation:**
- Story 2.1: `battery.py` + extend `models.py` + extend `main.py` (backend)
- Story 2.2: `battery-forms.js` + `battery-charts.js` + `index.html` battery section (frontend)
- Story 2.3: `test_battery.py` backend tests (>80% coverage gate)

---

### All AI Agents MUST:
- Use snake_case for all Pydantic fields and Python identifiers
- Use kebab-case for HTML IDs and CSS classes; camelCase for JS variables/functions
- Never add new pip or npm dependencies without noting them explicitly in the story
- Keep battery calculation logic in `battery.py` — not in `calculator.py` or `main.py`
- Never convert API response fields to camelCase — read them as snake_case
- Update charts in-place; never destroy/recreate on each simulate call
- Run `pytest --cov=app` before marking any backend story done; keep coverage >80%

---

### Cross-Cutting Concerns Identified

- **API contract evolution** — battery simulation adds new input params and output fields; must decide extend vs new endpoint
- **Module boundaries** — frontend split must not break existing behaviour; refactor is pre-condition for cleanly adding battery UI
- **Test coverage continuity** — new modules need tests; coverage gate must hold
- **Docker** — new Python deps (e.g. numeric libs) trigger image rebuild

---

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All technology choices are compatible. Vanilla JS ES6 modules require no build tooling — nginx serves them directly. FastAPI + Pydantic v2 on Python 3.11 is stable. Chart.js loaded via CDN — no npm required. Docker Compose orchestration unchanged. No version conflicts.

**Pattern Consistency:**
Naming conventions are internally consistent: snake_case for all Python/API identifiers, camelCase for JS variables and functions, kebab-case for HTML IDs and JS filenames. The "no camelCase conversion" rule bridges the two layers cleanly. Chart update-in-place and loading-state button patterns are consistently specified across solar and battery modules.

**Structure Alignment:**
`app.js`-as-sole-orchestrator enforces no circular imports by design. `api.js`-only-fetch rule maps to a single file boundary. Battery logic isolation in `battery.py` is structurally clear and enforced by the "All AI Agents MUST" rules.

---

### Requirements Coverage ✅

| Requirement | Covered by | Status |
|---|---|---|
| FR-1 Solar generation | `calculator.py`, `models.py` | ✅ |
| FR-2 Sunrise/sunset | `solar_position.py` | ✅ |
| FR-3 Daily hourly graph | `charts.js` + `calculator.py` | ✅ |
| FR-4 Yearly graph | `charts.js` + `calculator.py` | ✅ |
| FR-5 Result cards | `app.js` + `forms.js` | ✅ |
| FR-6 Interactive form | `forms.js`, `index.html` | ✅ |
| FR-7 Placeholder defaults | `forms.js` | ✅ |
| FR-8 Irradiance model | `irradiance.py`, `solar_position.py` | ✅ |
| Battery simulation | `battery.py`, `models.py`, `battery-forms.js`, `battery-charts.js` | ✅ |
| Tab UI (3 tabs) | `tabs.js`, `index.html`, `style.css` | ✅ |
| Cost analysis placeholder | `index.html` static panel | ✅ |

**NFR Coverage:**
- Simulate <500ms: FastAPI with no I/O — met
- Page load <2s: nginx-served static files — met
- Accuracy ±10%: model validated at ±6% for Turin reference — met
- Coverage >80%: gate enforced in `.coveragerc`, currently 95% — met
- No persistence, no auth: confirmed no database layer, no auth middleware

---

### Gap Analysis Results

**Critical Gaps:** None.

**Important (note for story authors):**
1. `httpx==0.24.1` must be added to `pyproject.toml` — currently installed in Docker only; pinning prevents breakage on image rebuild.
2. Frontend Jest testing appears in NFRs (80% target) but no story currently covers it — add as sub-task in Epic 2.
3. `seasonal_ambient_temperature()` SH inversion is a known bug (cos is an even function; sign flip has no effect). Not blocking for battery stories but worth a dedicated fix story.

**Minor:**
- `docs/` directory not mapped to any story — screenshots/reference material, no action required.

---

### Architecture Completeness Checklist

**Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

---

### Architecture Readiness Assessment

**Overall Status: READY FOR IMPLEMENTATION**
**Confidence Level: High**

**Key Strengths:**
- Single-endpoint backwards-compatible API extension eliminates client-side coordination risk
- Module isolation enforced by structure — circular imports impossible by design
- All patterns have canonical code examples — implementation agents have no ambiguity
- Battery model is physics-simple and fully specced; no new external dependencies

**Areas for Future Enhancement:**
- SH temperature model bug fix (`seasonal_ambient_temperature`)
- Frontend Jest coverage stories
- `httpx` pinned in `pyproject.toml`
- Real weather API integration (post-MVP, already deferred in PRD)

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure and module boundaries
- Refer to this document for all architectural questions

**First Implementation Priority:**
Epic 1 frontend refactor is the pre-condition — begin with `bmad-create-epics-and-stories` to generate detailed stories for both epics, then `bmad-sprint-planning` to populate `sprint-status.yaml`.
