---
storyKey: 2-6-battery-integrated-cost-analysis-and-testing
storyId: "2.6"
title: Battery-Integrated Cost Analysis and Testing
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: ready-for-dev
createdAt: '2026-05-23'
startedAt: null
completedAt: null
---

# Story 2-6: Battery-Integrated Cost Analysis and Testing

## Story

As a developer,
I want the cost analysis to account for battery behavior (self-consumption vs grid import/export) when calculating financial projections,
So that ROI calculations are accurate when a battery is part of the system and users understand the true financial impact of battery storage.

**Requirements Covered:** FR-10 (Cost Analysis with Battery), ARCH-1, ARCH-2

---

## Acceptance Criteria

**Given** battery simulation results are available (self_consumption_pct, grid_export_kwh, grid_import_kwh),
**When** cost analysis is invoked with both solar and battery fields,
**Then** annual savings calculation uses:
- Self-consumed energy: `annual_generation × self_consumption_pct / 100` at `electricity_price` rate
- Grid-exported energy: `annual_generation × (100 - self_consumption_pct) / 100` at `feedin_tariff` rate
- Grid-imported energy: NOT directly added to cost (already represented in daily load not met by solar+battery)

**Given** the new battery-aware ROI calculation is implemented,
**When** compared to the simplified calculation (all generation × (electricity_price + feedin_tariff)),
**Then** the battery-integrated model shows reduced savings due to lower feedin_tariff for exported excess energy

**Given** cost analysis is requested WITHOUT battery fields (solar-only system),
**When** the API response is generated,
**Then** the simplified calculation is used (backwards compatible): `annual_savings = annual_generation × (electricity_price + feedin_tariff)`

**Given** cost analysis is requested WITH battery fields,
**When** the financial model calculates year N savings with degradation,
**Then** degradation is applied to annual_generation BEFORE applying self-consumption split (generation degrades, self-consumption % remains constant per day)

**Given** I run unit tests for battery-integrated cost calculation,
**When** tests complete,
**Then** coverage report shows ≥80% for cost.py with battery path tested

**And** test patterns cover:
- Solar-only cost (backwards compatibility)
- Battery-integrated cost with high self-consumption (e.g., 80%)
- Battery-integrated cost with low self-consumption (e.g., 20%)
- Edge cases: zero battery, very large battery, seasonal variation in self-consumption
- Degradation applied correctly in battery-integrated path
- Break-even calculation with and without battery impact

**Given** I run integration tests for the /simulate endpoint,
**When** I send requests with battery + cost fields together,
**Then** the response includes cost fields calculated using battery-aware model

**Given** I use the Cost Analysis tab with battery results loaded,
**When** I view the financial projections with battery vs solar-only comparison,
**Then** charts and result cards show the impact of battery storage on 25-year ROI

---

## Architecture Notes

**Critical Design Decision:** The cost calculation has two paths:

1. **Solar-Only Path** (backwards compatible):
   - Used when cost fields present but NO battery fields
   - Formula: `annual_savings = annual_generation × (electricity_price + feedin_tariff)`
   - Simplified assumption: all generation is either consumed at home or exported at full feedin_tariff

2. **Battery-Integrated Path** (new):
   - Used when BOTH battery AND cost fields present
   - Requires battery simulation to be run first (provides self_consumption_pct)
   - Formula: 
     - `self_consumed_energy = annual_generation × self_consumption_pct / 100`
     - `exported_energy = annual_generation × (100 - self_consumption_pct) / 100`
     - `annual_savings = (self_consumed_energy × electricity_price) + (exported_energy × feedin_tariff)`
   - Degrades `annual_generation` first, then applies self_consumption split to each degraded year

**Why This Matters:** The simplified model assumes all generated energy is equally valuable — either consumed at home or exported to grid. In reality, with a battery:
- Energy directly consumed at home avoids grid import at full electricity_price ✓
- Energy exported to grid is worth feedin_tariff (typically lower) ✗
- Battery shifts generation from peak export hours to peak demand hours, increasing self-consumption %
- Therefore, adding a battery increases annual savings more than the simplified model suggests

**Current Limitation (Accepted):** The battery simulation runs on a single representative day (first day of period). For a full-accuracy cost analysis, we would need to simulate the full 365-day period. This story assumes self_consumption_pct from the single day is representative for the entire year. Future enhancement: Story 2-X could implement full-period battery simulation.

---

## Tasks & Subtasks

- [ ] Refactor `backend/app/cost.py` to support battery-integrated calculations (AC: #1, #2, #3)
  - [ ] Modify `calculate_25year_roi()` function signature to include optional `battery_params` (self_consumption_pct, grid_export_kwh, grid_import_kwh)
  - [ ] Detect if battery_params present:
    - [ ] If battery_params provided → use battery-integrated path
    - [ ] If battery_params not provided → use solar-only path (backwards compatible)
  - [ ] Implement solar-only path (existing logic, no change)
  - [ ] Implement battery-integrated path:
    - [ ] For each year 1–25:
      - [ ] degraded_generation = annual_generation_kwh × (1 - degradation_percent/100)^(year-1)
      - [ ] self_consumed = degraded_generation × self_consumption_pct / 100
      - [ ] exported = degraded_generation × (100 - self_consumption_pct) / 100
      - [ ] annual_savings = (self_consumed × electricity_price) + (exported × feedin_tariff)
      - [ ] cumulative_savings = previous_cumulative + annual_savings
      - [ ] if cumulative >= system_cost and breakeven_year not found: breakeven_year = year
  - [ ] Return dict with same structure as solar-only path
  - [ ] Add code comments explaining both calculation paths

- [ ] Update `backend/app/calculator.py` to pass battery results to cost module (AC: #4)
  - [ ] In `simulate()` function, after battery simulation completes:
    - [ ] If battery_output exists and cost fields present:
      - [ ] Extract self_consumption_pct from battery_output
      - [ ] Extract grid_export_kwh from battery_output (for future analytics, not used in cost calc yet)
      - [ ] Extract grid_import_kwh from battery_output (for future analytics, not used in cost calc yet)
      - [ ] Create battery_params dict
      - [ ] Pass to `cost.calculate_25year_roi(..., battery_params=battery_params)`
    - [ ] If battery_output does NOT exist but cost fields present:
      - [ ] Call cost calculation with battery_params=None (uses solar-only path)

- [ ] Create comprehensive unit tests in `backend/tests/test_cost.py` (AC: #5, #6)
  - [ ] Test: Solar-only cost calculation (backwards compatibility)
    - [ ] Given: 5000 kWh/year, no battery_params
    - [ ] Expected: year_1_savings ≈ €2,200 ((5000 × 0.32) + (5000 × 0.12))
  - [ ] Test: Battery-integrated cost with 80% self-consumption
    - [ ] Given: 5000 kWh/year, self_consumption_pct = 80
    - [ ] Calculated: self_consumed = 4000 kWh, exported = 1000 kWh
    - [ ] Expected: year_1_savings ≈ €1,400 ((4000 × 0.32) + (1000 × 0.12)) = €1,280 + €120
  - [ ] Test: Battery-integrated cost with 20% self-consumption
    - [ ] Given: 5000 kWh/year, self_consumption_pct = 20
    - [ ] Calculated: self_consumed = 1000 kWh, exported = 4000 kWh
    - [ ] Expected: year_1_savings ≈ €800 ((1000 × 0.32) + (4000 × 0.12)) = €320 + €480
  - [ ] Test: Battery-integrated cost with zero battery (100% export)
    - [ ] Given: 5000 kWh/year, self_consumption_pct = 0
    - [ ] Expected: same as solar-only (all generation exported at feedin_tariff, no home consumption benefit)
  - [ ] Test: Degradation applied in battery-integrated path
    - [ ] Given: year 1 generation = 5000 kWh, self_consumption_pct = 80
    - [ ] Expected: year 25 self_consumed ≈ 5000 × 0.88 × 0.80 = 3520 kWh (generation degrades, then self-consumption % applied)
  - [ ] Test: Break-even calculation with battery impact
    - [ ] Given: battery reduces year_1_savings (due to lower feedin_tariff on exports)
    - [ ] Expected: breakeven_year is later than solar-only scenario
  - [ ] Test: Edge case — very large battery (100% self-consumption)
    - [ ] Given: self_consumption_pct = 100
    - [ ] Expected: all generation valued at electricity_price (no export revenue)
  - [ ] Run: `pytest --cov=app --cov-fail-under=80`

- [ ] Create integration tests for /simulate endpoint with battery + cost (AC: #7)
  - [ ] Test: POST /simulate with solar + battery + cost fields
    - [ ] Expected: response includes cost fields using battery-aware calculation
  - [ ] Test: POST /simulate with solar + cost fields (no battery)
    - [ ] Expected: response includes cost fields using solar-only calculation (backwards compatible)
  - [ ] Test: POST /simulate with solar + battery fields (no cost)
    - [ ] Expected: response includes battery fields, no cost fields (null)
  - [ ] Test: Verify field-level error handling (missing fields, invalid values)

- [ ] Verify full test suite passes with no regressions (AC: #7)
  - [ ] Run: `pytest --cov=app --cov-fail-under=80`
  - [ ] Expected: all tests pass, coverage ≥80%, no regressions in battery or existing tests

---

## Dev Notes

**Architecture Context:**

Story 2-6 extends the cost analysis from Story 2-4 to account for battery behavior. The key insight: when a battery is present, not all generated energy is equally valuable:
- Energy consumed at home avoids grid import cost (electricity_price) ✓
- Energy exported to grid earns feedin_tariff (typically much lower) ✗
- Battery shifts generation timing to increase self-consumption % (improves financial case)

This story assumes self_consumption_pct from a single representative day can be extrapolated to the full year (acceptable for MVP; future enhancement would run full 365-day battery simulation).

**Financial Model Details:**

Current (Story 2-4) simplified model:
```
annual_savings = annual_generation × (electricity_price + feedin_tariff)
              = 5000 × (0.32 + 0.12)
              = 5000 × 0.44
              = €2,200 / year
```

New (Story 2-6) battery-integrated model:
```
self_consumed = annual_generation × self_consumption_pct / 100
exported = annual_generation × (100 - self_consumption_pct) / 100
annual_savings = (self_consumed × electricity_price) + (exported × feedin_tariff)

Example (80% self-consumption):
self_consumed = 5000 × 0.80 = 4000 kWh
exported = 5000 × 0.20 = 1000 kWh
annual_savings = (4000 × 0.32) + (1000 × 0.12) = €1,280 + €120 = €1,400 / year
```

Notice: €1,400 < €2,200. This is correct — the battery improves self-consumption (say, from 30% without battery to 80% with battery), but we're comparing the cost calculation model, not the before/after battery benefit. The battery benefit is captured in the change in self_consumption_pct.

**Previous Story Intelligence:**

Story 2-4 (Cost Backend) implemented the financial model using simplified calculation (all generation × both rates). This story extends it without breaking backwards compatibility:
- Solar-only requests (no battery) → use simplified path
- Solar + battery requests → use battery-integrated path
- Existing tests for solar-only continue to pass

**Design Pattern:** The cost module maintains its pure-function design (ARCH-2). Battery results are passed in as parameters; cost.py does not depend on or call battery.py.

**File Relationships:**
- `cost.py` (UPDATE) — add battery_params parameter, implement two calculation paths
- `calculator.py` (UPDATE) — extract battery self_consumption_pct and pass to cost module
- `models.py` (NO CHANGE) — SolarOutput already includes battery fields
- `test_cost.py` (UPDATE) — add battery integration tests

**Testing Standards:**
- Unit tests cover both calculation paths (solar-only and battery-integrated)
- Edge cases: zero battery, 100% self-consumption, degradation interaction
- Integration tests verify /simulate endpoint routes battery results correctly
- Coverage target: ≥80% for cost.py (existing gate from Story 2-4)

---

## Dev Agent Record

### Implementation Plan

1. Extend cost.py with battery_params support (two calculation paths)
2. Update calculator.py to extract and pass battery self_consumption_pct
3. Create unit tests for both solar-only and battery-integrated paths
4. Create integration tests for /simulate endpoint with battery + cost
5. Run full test suite, verify ≥80% coverage, zero regressions

### Debug Log

[To be updated during implementation]

### Completion Notes

[To be updated during implementation]

---

## File List

**Modified Files:**
- backend/app/cost.py — Extend with battery_params, implement two calculation paths
- backend/app/calculator.py — Extract battery results and pass to cost module
- backend/tests/test_cost.py — Add battery integration tests

**Deleted Files:**
None

---

## References

- Story 2-1: Battery Backend simulation outputs `self_consumption_pct`, `grid_export_kwh`, `grid_import_kwh`
- Story 2-4: Cost Backend initial implementation using simplified calculation
- PRD: FR-10 (Cost Analysis & Payback) and FR-9 (Battery simulation with grid import/export)
- Architecture: ARCH-1 (all-or-nothing validation), ARCH-2 (isolated modules)
