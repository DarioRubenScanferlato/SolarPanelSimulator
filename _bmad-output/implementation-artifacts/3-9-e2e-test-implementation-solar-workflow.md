---
storyKey: 3-9-e2e-test-implementation-solar-workflow
storyId: "3.9"
title: E2E Test Implementation (Solar Workflow)
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-9: E2E Test Implementation (Solar Workflow)

## Story

As a qa engineer,
I want E2E test patterns for solar simulation workflow, validation errors, and tab switching,
So that complete user journeys are validated end-to-end.

**Requirements Covered:** NFR-3, NFR-SEC-1

---

## Acceptance Criteria

**Given** I run E2E tests for the solar simulation workflow
**When** the test executes
**Then** the test loads the page, verifies defaults are loaded, fills form with custom values, clicks Simulate, waits for results, verifies result cards are populated, verifies charts are visible

**Given** I run E2E tests for validation error handling
**When** I enter invalid values (latitude=95)
**Then** the test verifies error message appears next to input

**Given** I run E2E tests for tab switching with state persistence
**When** I fill the solar form, switch tabs, and switch back
**Then** the test verifies solar form values are preserved (not cleared)

---

## Tasks & Subtasks

- [ ] Create test for solar simulation workflow (default inputs)
  - [ ] File: `frontend/e2e/solar-simulation-workflow.spec.ts`
  - [ ] Test name: "Solar simulation with default values"
  - [ ] Steps:
    - [ ] Navigate to page
    - [ ] Verify Solar Simulation tab is active
    - [ ] Verify form is visible
    - [ ] Verify default values loaded (latitude 45.0703, longitude 7.6869, etc.)
    - [ ] Click Simulate button
    - [ ] Wait for results to load (timeout 10s)
    - [ ] Verify result cards display: annual energy, daily average, peak hour, system capacity
    - [ ] Verify daily chart is visible (canvas element)
    - [ ] Verify yearly chart is visible (canvas element)
    - [ ] Verify result values are numeric and reasonable

- [ ] Create test for solar simulation workflow (custom inputs)
  - [ ] Test name: "Solar simulation with custom values"
  - [ ] Steps:
    - [ ] Navigate to page
    - [ ] Clear form fields and enter custom values:
      - [ ] latitude: 40.0
      - [ ] longitude: 10.0
      - [ ] panels: 5
      - [ ] area: 1.5
      - [ ] efficiency: 18
      - [ ] tilt: 25
      - [ ] azimuth: 190
      - [ ] date: (last month, same day if exists)
      - [ ] duration: 30
    - [ ] Click Simulate button
    - [ ] Wait for results
    - [ ] Verify result cards updated with new values
    - [ ] Verify chart data updated
    - [ ] Verify values differ from default simulation

- [ ] Create test for form validation errors
  - [ ] Test name: "Form validation error display"
  - [ ] Steps:
    - [ ] Navigate to page
    - [ ] Clear latitude field, enter: 95 (invalid, out of range)
    - [ ] Click Simulate
    - [ ] Wait for error response (422)
    - [ ] Verify error message appears inline next to latitude field
    - [ ] Verify error message text is clear (e.g., "Latitude must be between -90 and 90")
    - [ ] Clear latitude, enter: -95 (invalid, negative)
    - [ ] Click Simulate
    - [ ] Verify error appears for negative latitude
    - [ ] Verify errors persist until corrected
    - [ ] Enter valid latitude: 45.0
    - [ ] Click Simulate
    - [ ] Verify error clears and simulation succeeds

- [ ] Create test for multiple validation errors
  - [ ] Test name: "Multiple validation errors displayed"
  - [ ] Steps:
    - [ ] Enter invalid latitude: 95
    - [ ] Enter invalid longitude: 200
    - [ ] Enter invalid panels: -1
    - [ ] Click Simulate
    - [ ] Verify all three error messages appear
    - [ ] Verify each error is next to correct field

- [ ] Create test for tab switching with state preservation
  - [ ] Test name: "Tab switching preserves form state"
  - [ ] Steps:
    - [ ] Navigate to page
    - [ ] Fill Solar form with custom values (change defaults)
    - [ ] Click Battery Simulation tab
    - [ ] Verify Battery tab is active
    - [ ] Verify Battery form is visible
    - [ ] Click Solar Simulation tab
    - [ ] Verify Solar Simulation tab is active
    - [ ] Verify Solar form values are preserved (same custom values as before)
    - [ ] Verify form data was not cleared or reset

- [ ] Create test for simulation with battery tab
  - [ ] Test name: "Tab switch does not affect simulation results"
  - [ ] Steps:
    - [ ] Navigate to page
    - [ ] Run solar simulation (click Simulate)
    - [ ] Verify results displayed in Solar tab
    - [ ] Click Battery Simulation tab
    - [ ] Click Solar Simulation tab
    - [ ] Verify solar results still displayed (not cleared)

- [ ] Create test for Simulate button state during request
  - [ ] Test name: "Simulate button disabled during request"
  - [ ] Steps:
    - [ ] Navigate to page
    - [ ] Click Simulate button
    - [ ] While request is in flight (within first 100ms):
      - [ ] Verify button is disabled
      - [ ] Verify button text is "Simulating…"
    - [ ] Wait for response
    - [ ] Verify button is re-enabled
    - [ ] Verify button text is "Simulate"

- [ ] Create test for page responsiveness
  - [ ] Test name: "Page loads within performance budget"
  - [ ] Steps:
    - [ ] Measure page load time (DOMContentLoaded or ready state)
    - [ ] Verify page loads in <2 seconds
    - [ ] Measure simulation response time
    - [ ] Verify results appear in <1 second after Simulate click
    - [ ] Verify charts render within <500ms

- [ ] Create shared test utilities
  - [ ] File: `frontend/e2e/helpers.ts`
  - [ ] Helper: fillSolarForm(page, values) — fills form with custom values
  - [ ] Helper: verifySolarResults(page) — checks result cards are populated
  - [ ] Helper: verifyChartsVisible(page) — checks chart canvases are present
  - [ ] Helper: getErrorMessage(page, fieldId) — retrieves error text for field
  - [ ] Helper: defaultSolarValues — returns Turin default values

- [ ] Add tests to npm scripts
  - [ ] Verify npm run test:e2e runs all E2E tests
  - [ ] Verify tests run in sequence (not parallel) to avoid port conflicts

- [ ] Test cross-browser behavior
  - [ ] Run tests on Chromium (default)
  - [ ] Run tests on Firefox (if configured)
  - [ ] Run tests on WebKit (if configured)
  - [ ] Verify all tests pass on all browsers

- [ ] Add continuous failure handling
  - [ ] Verify tests retry once on failure (per playwright config)
  - [ ] Verify flaky tests are identified and documented
  - [ ] Add appropriate waits and timeouts to prevent flakiness

---

## Dev Notes

**Architecture Context:**
E2E tests validate complete user workflows from page load through simulation and results display. These tests exercise:
1. Frontend form handling
2. API communication
3. Error display and recovery
4. Tab navigation and state persistence
5. Chart rendering
6. Performance (load time, simulation speed)

Tests should be maintainable and use shared utilities (helpers) to avoid repetition.

**Key Patterns:**
- Use helpers for common actions (fill form, verify results, etc.)
- Use explicit waits (waitForSelector) instead of sleeps
- Test both happy paths and error paths
- Verify visual elements (charts, result cards) are present
- Test state persistence across tab switches
- Use reasonable timeouts (10s for page load, 5s for API response)
- Avoid hardcoding selectors; extract to data attributes or helpers

**Playwright Best Practices:**
- Use waitForLoadState() to wait for page ready
- Use page.locator() with data attributes for robust selectors
- Use page.fill() for form inputs (auto-clears before typing)
- Use page.click() for buttons
- Use expect() assertions from @playwright/test for clear failures
- Test both success and error scenarios
- Use beforeEach() to initialize page state

**Dependencies:**
- Playwright (installed in Story 3-8)
- Helper utilities (create in this story)

**Related Stories:**
- Story 3-8 (E2E Framework Setup) — Playwright configured
- Story 1-1 (Tab Layout) — tab switching tested
- Story 1-2 (API Module) — API contract tested

**Files Modified/Created:**
- `frontend/e2e/solar-simulation-workflow.spec.ts` — NEW, workflow tests
- `frontend/e2e/helpers.ts` — NEW, test utilities

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
- frontend/e2e/solar-simulation-workflow.spec.ts
- frontend/e2e/helpers.ts

**Modified Files:**
(none)

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-22: Story created from Epic 3 specification

---

**Current:** review
**Completion:** complete
**Final:** Ready for code review
