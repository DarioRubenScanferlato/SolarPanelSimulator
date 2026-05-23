---
storyKey: 2-6-cost-analysis-testing-and-validation
storyId: "2.6"
title: Cost Analysis Testing & Validation
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: backlog
createdAt: '2026-05-23'
startedAt: null
completedAt: null
---

# Story 2-6: Cost Analysis Testing & Validation

## Story

As a developer,
I want comprehensive unit tests for the cost analysis module including financial edge cases and degradation scenarios,
So that the ROI calculations are validated and trustworthy for users.

**Requirements Covered:** NFR-3 (≥80% test coverage), Cost Module Validation

---

## Acceptance Criteria

**Given** I run pytest with coverage for the cost module
**When** the tests complete
**Then** coverage report shows ≥80% for cost.py

**And** all tests in test_cost.py pass

**And** test patterns cover: Year 1 savings, break-even year calculation, degradation effects, cumulative calculation, null break-even edge case

**And** pytest is run with: pytest --cov=app --cov-fail-under=80

---

## Tasks & Subtasks

- [ ] Create comprehensive unit test suite in `backend/tests/test_cost.py`
  - [ ] Create pytest fixtures for common cost scenarios
  - [ ] Test: Year 1 savings calculation
    - [ ] Given: 5000 kWh/year, €0.32/kWh electricity, €0.12/kWh feed-in
    - [ ] Expected: year_1_savings ≈ 5000 × (0.32 + 0.12) = €2,200
  - [ ] Test: Break-even year calculation
    - [ ] Given: €2,200 year 1 savings, €9,000 system cost, no degradation
    - [ ] Expected: breakeven_year = 5 (cumulative at year 4 is €8,800 < €9,000, year 5 is €11,000 ≥ €9,000)
  - [ ] Test: Degradation applied (0.5%/year)
    - [ ] Given: 5000 kWh year 1, 0.5% degradation
    - [ ] Expected: year 25 ≈ 5000 × (1 - 0.005)^24 ≈ 4400 kWh (12% loss)
  - [ ] Test: Cumulative savings list integrity
    - [ ] Expected: cumulative_savings[0] = year_1_savings, cumulative_savings[-1] = total_25year_savings
  - [ ] Test: Null break-even year when no payback
    - [ ] Given: high system cost (€50,000), low savings (€500/year)
    - [ ] Expected: breakeven_year = null (no payback within 25 years)
  - [ ] Test: Cumulative savings never negative
    - [ ] Expected: all cumulative_savings values ≥ 0
  - [ ] Parametrized tests: 10+ scenarios with varied degradation, lifespans, costs

- [ ] Run test suite with coverage
  - [ ] Command: `pytest --cov=app --cov-fail-under=80 backend/tests/test_cost.py`
  - [ ] Expected: all tests PASS, cost.py coverage ≥80%

- [ ] Verify no regressions in full test suite
  - [ ] Command: `pytest --cov=app --cov-fail-under=80 backend/tests/`
  - [ ] Expected: all tests PASS, coverage ≥80%

- [ ] Document cost module edge cases and assumptions in dev notes
  - [ ] Break-even can be year 1 if annual savings ≥ system cost
  - [ ] Break-even is null if no payback within lifespan
  - [ ] Cumulative savings always non-negative (no negative years)
  - [ ] Degradation applied as compounding (not linear)

---

## Dev Notes

**Testing Strategy:**

This story validates cost.py from Story 2.4. Key invariants to verify:
- Year 1 savings calculated as (annual_generation × (electricity_price + feedin_tariff))
- Cumulative savings monotonically increasing or flat (never decreases)
- Break-even year is first year where cumulative ≥ system_cost
- Degradation compounds: year N generation = year 1 × (1 - deg%)^(N-1)
- Total 25-year savings = sum of all annual savings

Use parametrized tests to cover diverse scenarios (high/low costs, degradation rates, lifespans).

---

## Dev Agent Record

### Implementation Plan
1. Create test_cost.py with fixtures and 10+ unit tests
2. Verify ≥80% coverage for cost.py
3. Ensure no regressions to full test suite

### Debug Log
(To be filled by dev agent)

### Completion Notes
(To be filled by dev agent)

---

## File List

**New Files:**
- backend/tests/test_cost.py

**Modified Files:**
(none)

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-23: Story 2-6 created — comprehensive unit tests for cost analysis module

---

## Status

**Current:** backlog
**Depends On:** Story 2-4 (backend)
**Story Created:** 2026-05-23

