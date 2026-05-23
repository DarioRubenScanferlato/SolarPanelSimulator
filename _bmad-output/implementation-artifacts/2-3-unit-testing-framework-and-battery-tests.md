---
storyKey: 2-3-unit-testing-framework-and-battery-tests
storyId: "2.3"
title: Unit Testing Framework & Battery Tests
epicId: 2
epicTitle: Battery Storage Simulation
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 2-3: Unit Testing Framework & Battery Tests

## Story

As a developer,
I want comprehensive unit tests for the battery module,
So that battery simulation logic is thoroughly tested and edge cases are covered.

**Requirements Covered:** NFR-3, NFR-SEC-1

---

## Acceptance Criteria

**Given** I run pytest with coverage for the battery module
**When** the tests complete
**Then** coverage report shows ≥80% for battery.py

**And** all tests in test_battery.py pass

**And** test patterns cover edge cases: zero capacity passthrough, SoC never negative, SoC never exceeds capacity, efficiency losses

**And** pytest is run with: pytest --cov=app --cov-fail-under=80

---

## Tasks & Subtasks

- [ ] Create test_battery.py with TestSimulateBattery class
  - [ ] Test zero capacity battery returns generation values unchanged
  - [ ] Test full capacity never exceeded across all 24 hours
  - [ ] Test SoC never negative at any hour
  - [ ] Test grid export only when solar surplus exceeds battery charge headroom
  - [ ] Test grid import only when load exceeds available generation plus battery
  - [ ] Test round-trip efficiency (charge then discharge loses energy)

- [ ] Create TestCalculateHourlySoc class
  - [ ] Test charge efficiency reduces net energy stored (stored < surplus)
  - [ ] Test discharge efficiency limits draw (drawn < deficit)
  - [ ] Test SoC bounded [0, capacity] for every hour index 0–23
  - [ ] Test edge case: zero efficiency values

- [ ] Create TestSelfConsumption class
  - [ ] Test 100% self-consumption when daily load ≤ total generation and battery capacity sufficient
  - [ ] Test 0% self-consumption when daily_load_kwh=0
  - [ ] Test partial self-consumption with insufficient generation
  - [ ] Test calculation accounts for efficiency losses

- [ ] Create TestEnergyBalanceInvariant
  - [ ] Test energy balance holds: grid_import_kwh + self_consumed_kwh == daily_load_kwh (within 1e-6 tolerance)
  - [ ] Test across multiple input scenarios with different capacities and loads
  - [ ] Test with edge case values (very small loads, very large capacities)

- [ ] Create test fixtures for common inputs
  - [ ] Fixture: default battery params (capacity=10, charge_eff=95%, discharge_eff=95%, etc.)
  - [ ] Fixture: solar generation data (24-hour values)
  - [ ] Fixture: various battery scenarios (small, medium, large capacity)

- [ ] Verify test coverage
  - [ ] Run pytest --cov=app --cov-fail-under=80
  - [ ] Verify battery.py has ≥80% line coverage
  - [ ] Verify overall app/ coverage remains ≥80%
  - [ ] Generate coverage report for review

- [ ] Run full test suite for regressions
  - [ ] Run pytest --cov=app on all test files
  - [ ] Verify test_solar_position passes (no regressions)
  - [ ] Verify test_irradiance passes (no regressions)
  - [ ] Verify test_calculator passes (no regressions)
  - [ ] Verify test_main passes (no regressions)
  - [ ] Verify all new test_battery tests pass

- [ ] Document test patterns in docstrings
  - [ ] Add docstring to TestSimulateBattery explaining physics validation
  - [ ] Add docstring to TestEnergyBalanceInvariant explaining conservation principle
  - [ ] Add comments for complex test calculations

---

## Dev Notes

**Architecture Context:**
Battery testing validates two critical aspects:
1. Physics correctness: energy conservation, efficiency losses, SoC bounds
2. API contract: input/output format, edge case handling

The energy balance invariant (grid_import + self_consumption == load) is the foundation for all tests. Every test scenario should satisfy this invariant within floating-point tolerance (1e-6).

**Key Patterns:**
- Use pytest fixtures for common test inputs (DRY principle)
- Test both happy paths and edge cases (zero capacity, full capacity, no load, no generation)
- Use parametrized tests for testing across multiple input scenarios
- Verify energy conservation (balance invariant) in every test
- Test efficiency losses explicitly (charge/discharge reduce available energy)

**Test Coverage Targets:**
- battery.py: ≥80% line coverage
- app/: ≥80% overall coverage
- All edge cases mentioned in acceptance criteria covered

**Dependencies:**
- pytest (already installed)
- pytest-cov (already installed)
- No new test dependencies required
- battery.py (Story 2-1) must exist before this story can be implemented

**Related Stories:**
- Story 2-1 (Battery Backend) — battery.py must exist before tests
- Story 2-2 (Battery Frontend) — UI implementation alongside backend
- Story 2-3 (Battery Backend Tests, epics.md) — this story supersedes/consolidates 2-3

**Files Modified/Created:**
- `backend/tests/test_battery.py` — NEW, comprehensive battery tests

---

## Dev Agent Record

### Implementation Plan

(To be filled in during implementation)

### Debug Log

(To be filled in during implementation)

### Completion Notes

(To be filled in during implementation)

---

## File List

**New Files:**
- backend/tests/test_battery.py

**Modified Files:**
(none)

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-22: Story created from Epic 3 specification
- 2026-05-23: Moved from Epic 3 (story 3-6) to Epic 2 as story 2-3, consolidating with original 2-3

---

## Status

**Current:** ready-for-dev
**Completion:** pending
**Final:** Awaiting implementation
