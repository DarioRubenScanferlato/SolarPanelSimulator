---
storyKey: 2-4-cost-backend-roi-module-api-extension
storyId: "2.4"
title: Cost Backend — ROI Module, API Extension
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-23'
startedAt: null
completedAt: null
---

# Story 2-4: Cost Backend — ROI Module, API Extension

## Story

As a developer,
I want `cost.py` implementing the 25-year ROI calculation with panel degradation, `models.py` extended with optional cost fields, and `/simulate` wired to invoke cost analysis when those fields are present,
So that the API supports cost analysis with full backwards compatibility.

**Requirements Covered:** FR-10 (Cost Analysis & Payback), ARCH-1, ARCH-2

---

## Acceptance Criteria

**Given** `cost.py` exports `calculate_25year_roi(annual_generation_kwh, system_cost_eur, electricity_price, feedin_tariff, degradation_percent, lifespan_years)`,
**When** called with valid inputs,
**Then** it returns a dict with `year_1_savings` (float €), `breakeven_year` (int or null), `cumulative_savings` (list of 25 floats), `total_25year_savings` (float €)

**Given** `SolarInput` extended with optional fields: `system_cost_eur`, `electricity_price_eur_per_kwh`, `feedin_tariff_eur_per_kwh`, `lifespan_years`, `annual_degradation_percent` (all defaulting to sensible values),
**When** POST `/simulate` is called with all cost fields populated,
**Then** the response includes `cost_year_1_savings`, `cost_breakeven_year`, `cost_cumulative_savings`, `cost_total_25year_savings`

**Given** a POST `/simulate` request with no cost fields,
**When** the response is received,
**Then** it contains only solar and battery fields (if present) — identical to previous response format (backwards compatible)

**Given** the 25-year projection calculation,
**When** degradation is applied (default 0.5%/year),
**Then** Year 25 generation ≈ 12% lower than Year 1 (clamped to [0.88, 1.0] of initial)

**Given** break-even calculation,
**When** cumulative savings reach or exceed system cost,
**Then** `breakeven_year` is set to the first year where cumulative ≥ cost; if no break-even within lifespan, `breakeven_year` is null

**Given** Italian defaults for cost fields,
**When** the values are not provided by the user,
**Then** system defaults: system_cost = €1,800/kW, electricity_price = €0.32/kWh, feedin_tariff = €0.12/kWh, lifespan = 25 years, degradation = 0.5%/year

---

## Tasks & Subtasks

- [ ] Create `backend/app/cost.py` module with `calculate_25year_roi()` function
  - [ ] Function signature: `calculate_25year_roi(annual_generation_kwh: float, system_cost_eur: float, electricity_price: float, feedin_tariff: float, degradation_percent: float, lifespan_years: int) -> dict`
  - [ ] For each year in range(1, lifespan_years + 1):
    - [ ] Apply degradation: capacity_factor = (1 - degradation_percent/100) ^ (year - 1)
    - [ ] Annual generation = annual_generation_kwh × capacity_factor
    - [ ] Electricity savings = annual_generation × electricity_price
    - [ ] Feed-in revenue = annual_generation × feedin_tariff
    - [ ] Annual savings = electricity_savings + feedin_revenue
    - [ ] Cumulative savings = previous_cumulative + annual_savings
    - [ ] If breakeven_year not yet found and cumulative ≥ system_cost: breakeven_year = year
  - [ ] Calculate totals:
    - [ ] `year_1_savings`: (annual_generation_kwh × electricity_price) + (annual_generation_kwh × feedin_tariff)
    - [ ] `total_25year_savings`: sum of all annual savings
    - [ ] `cumulative_savings`: list of 25 cumulative values (or lifespan_years values)
    - [ ] `breakeven_year`: first year where cumulative ≥ system_cost, or null if no payback
  - [ ] Return dict: {year_1_savings, breakeven_year, cumulative_savings, total_25year_savings}

- [ ] Extend `backend/app/models.py` SolarInput with optional cost fields
  - [ ] Add to `SolarInput` class:
    - [ ] `system_cost_eur: float | None = None` (Field ge=0 if provided)
    - [ ] `electricity_price_eur_per_kwh: float | None = None` (Field ge=0 if provided)
    - [ ] `feedin_tariff_eur_per_kwh: float | None = None` (Field ge=0 if provided)
    - [ ] `lifespan_years: int | None = None` (Field ge=1 if provided)
    - [ ] `annual_degradation_percent: float | None = None` (Field ge=0, le=100 if provided)

- [ ] Extend `backend/app/models.py` SolarOutput with cost fields
  - [ ] Add to `SolarOutput` class:
    - [ ] `cost_year_1_savings: float | None = None` (€)
    - [ ] `cost_breakeven_year: int | None = None` (year or null)
    - [ ] `cost_cumulative_savings: List[float] | None = None` (25-element list if cost present)
    - [ ] `cost_total_25year_savings: float | None = None` (€)

- [ ] Update `backend/app/validation.py` to validate cost fields
  - [ ] Add validator: `validate_cost_fields(input_data: SolarInput)`
  - [ ] Check: if ANY of the 5 cost fields are provided, ALL 5 must be provided
  - [ ] Return validation error if partial: "All cost fields must be provided together or not at all"
  - [ ] Add sensible Italian defaults when all fields provided:
    - [ ] `system_cost_eur`: default to €1,800 × system_capacity_kw (requires system_capacity from solar input)
    - [ ] `electricity_price_eur_per_kwh`: default 0.32
    - [ ] `feedin_tariff_eur_per_kwh`: default 0.12
    - [ ] `lifespan_years`: default 25
    - [ ] `annual_degradation_percent`: default 0.5

- [ ] Update `backend/app/main.py` /simulate endpoint
  - [ ] Before calling `simulate()`, call `validate_cost_fields(input_data)` to check for partial cost input
  - [ ] Pass full `input_data` (with cost fields) to `simulate()`

- [ ] Update `backend/app/calculator.py` `simulate()` function to invoke cost module
  - [ ] After calculating battery output (if present), check if `input_data.system_cost_eur` is not None
  - [ ] If cost fields present:
    - [ ] Prepare annual_generation_kwh from solar_output.annual_energy_kwh
    - [ ] Prepare cost_params dict from input_data
    - [ ] Call `cost.calculate_25year_roi(...)`
    - [ ] Merge cost results into `output` dict with `cost_` prefixes
  - [ ] Return complete SolarOutput (with or without cost fields depending on input)

- [ ] Create `backend/tests/test_cost.py` unit tests
  - [ ] Test: Basic 25-year ROI calculation
    - [ ] Given: 5000 kWh/year, €9,000 system cost (1.8€/kW × 5kW), €0.32/kWh, €0.12/kWh
    - [ ] Expected: year_1_savings ≈ €2,200 ((5000 × 0.32) + (5000 × 0.12))
  - [ ] Test: Break-even calculation
    - [ ] Given: year_1_savings = €2,200, system_cost = €9,000, no degradation
    - [ ] Expected: breakeven_year = 5 (9000 / 2200 ≈ 4.1 years, so year 5)
  - [ ] Test: Degradation applied correctly (0.5%/year)
    - [ ] Given: year 1 generation = 5000 kWh
    - [ ] Expected: year 25 generation ≈ 5000 × 0.88 = 4400 kWh (12% loss)
  - [ ] Test: Cumulative savings list matches calculation
    - [ ] Given: valid inputs
    - [ ] Expected: cumulative_savings[0] = year_1_savings, cumulative_savings[24] = total_25year_savings
  - [ ] Test: Null break-even year when no payback within lifespan
    - [ ] Given: high system cost, low savings
    - [ ] Expected: breakeven_year = null
  - [ ] Test: Backwards compatibility — API call without cost fields
    - [ ] Given: POST /simulate with only solar fields
    - [ ] Expected: response includes only solar fields, no cost fields (null)
  - [ ] Test: Validation rejects partial cost input
    - [ ] Given: POST /simulate with 3 of 5 cost fields
    - [ ] Expected: HTTP 422 with validation error message
  - [ ] Run: `pytest --cov=app --cov-fail-under=80` → cost.py coverage ≥80%

- [ ] Verify full test suite passes with no regressions
  - [ ] Run: `pytest --cov=app --cov-fail-under=80`
  - [ ] Expected: all tests pass, coverage ≥80%, no regressions

---

## Dev Notes

**Architecture Context:**

Story 2.4 implements backend cost analysis (ROI module), parallel to 2.1 (battery backend) in development flow. The two modules are independent — cost.py doesn't depend on battery.py. Both extend the /simulate API endpoint with optional fields (all-or-nothing validation).

**ARCH-2 Constraint:** Cost logic MUST be isolated in `cost.py` only, never mixed into `calculator.py` or `main.py`.

**Italian Defaults:** Based on PRD and decision log:
- System Cost: €1,800/kW (scales with system capacity)
- Electricity Price: €0.32/kWh (Italian residential average)
- Feed-in Tariff: €0.12/kWh (Italian scambio sul posto)
- Lifespan: 25 years (standard for solar ROI analysis)
- Degradation: 0.5%/year (industry standard, crystalline panels)

**Financial Model:**
- Year N generation = Year 1 generation × (1 - degradation%)^(N-1)
- Annual savings = generation × (electricity_price + feedin_tariff)
- Cumulative savings = sum of all annual savings up to year N
- Break-even = first year where cumulative ≥ system_cost

**Cost Output Format:**
- `cost_year_1_savings`: Year 1 annual savings (single year, used for card display)
- `cost_cumulative_savings`: List of 25 cumulative totals (one per year), for chart
- `cost_total_25year_savings`: Sum of all annual savings (final cumulative value)
- `cost_breakeven_year`: Year number where payback occurs, or null

**Previous Story Context:** Epic 3 (security/testing) has already hardened the codebase, so cost.py benefits from existing patterns. Story 1.3 (frontend refactor) completed, so frontend is ready for Story 2.5 (cost UI).

**File Relationships:**
- `cost.py` (NEW) — pure function, no dependencies on other app modules
- `models.py` (UPDATE) — add 5 optional fields to SolarInput and 4 to SolarOutput
- `calculator.py` (UPDATE) — call cost.calculate_25year_roi() if cost fields present
- `main.py` (UPDATE) — validate cost fields before passing to simulate()
- `validation.py` (UPDATE) — add all-or-nothing cost field validator
- `pyproject.toml` (NO CHANGE) — httpx already pinned in 2.1

---

## Dev Agent Record

### Implementation Plan

1. Create cost.py with calculate_25year_roi() function
2. Extend models.py with optional cost fields (SolarInput/SolarOutput)
3. Add cost field validation to validation.py (all-or-nothing check)
4. Update main.py /simulate endpoint to validate cost fields
5. Update calculator.py to invoke cost module when cost fields present
6. Create comprehensive unit tests in test_cost.py
7. Run full test suite, verify ≥80% coverage, zero regressions

### Debug Log

(To be filled by dev agent during implementation)

### Completion Notes

(To be filled by dev agent at completion)

---

## File List

**New Files:**
- backend/app/cost.py — Cost analysis ROI calculation module
- backend/tests/test_cost.py — Unit tests for cost module

**Modified Files:**
- backend/app/models.py — Add optional cost fields
- backend/app/validation.py — Add cost field validator
- backend/app/calculator.py — Integrate cost module
- backend/app/main.py — Validate cost fields at /simulate endpoint

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-23: Story 2-4 created from Epic 2 specification
  - Cost analysis ROI module with 25-year payback calculation
  - Panel degradation modeling (0.5%/year default)
  - API extension with optional cost fields (all-or-nothing validation)
  - Italian pricing defaults (€1,800/kW system cost, €0.32/kWh electricity, €0.12/kWh feed-in)
  - Backwards compatibility preserved

---

## Status

**Current:** ready-for-dev
**Completion:** 0% (no tasks started)
**Story Created:** 2026-05-23
**Next:** await dev-story agent execution

