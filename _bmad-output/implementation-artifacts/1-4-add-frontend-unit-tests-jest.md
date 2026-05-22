---
stepsCompleted: []
status: 'ready-for-dev'
createdAt: '2026-05-22'
story_key: '1-4-add-frontend-unit-tests-jest'
epic_num: 1
story_num: 4
---

# Story 1.4: Add Frontend Unit Tests with Jest

**Epic:** Frontend Modularisation  
**Story ID:** 1.4  
**Story Key:** 1-4-add-frontend-unit-tests-jest  
**Status:** ready-for-dev  

---

## Story Requirements

### User Story Statement

As a developer,
I want comprehensive unit tests for all frontend ES6 modules using Jest,
So that module behavior is verified, regressions are caught early, and Epic 2 battery features can be developed with confidence.

### Acceptance Criteria (BDD Format)

**AC-1: Jest configured and tests run successfully**
```
Given Jest is configured in package.json
When npm test is run
Then all tests execute and pass
And coverage report shows per-file breakdown
```

**AC-2: api.js module fully tested**
```
Given api.js exports simulateSolar(payload)
When tests run for success, 422 error, and network error cases
Then simulateSolar returns correct response objects and manages button state
And button DOM state changes verified (disabled, text content)
```

**AC-3: forms.js module fully tested**
```
Given forms.js exports form handling functions
When tests run for loadDefaults, readSolarForm, showFieldError, clearErrors, updateResultCards
Then each function correctly reads/writes DOM and transforms data
And DEFAULTS object has correct Turin values
```

**AC-4: charts.js module fully tested**
```
Given charts.js exports chart init and update functions
When tests run for initDailyChart, initYearlyChart, updateDailyChart, updateYearlyChart
Then charts are initialized correctly
And chart.update() is called when data updates (not destroy/recreate)
```

**AC-5: tabs.js module fully tested**
```
Given tabs.js exports switchTab(tabId)
When tests run for tab switching logic
Then correct panels shown/hidden and active class applied
```

**AC-6: app.js integration tested**
```
Given app.js orchestrates all modules
When integration tests run for DOMContentLoaded, handleSubmit, displayResults flows
Then module interactions verified and no regressions in simulate flow
```

**AC-7: Minimum 80% code coverage for frontend modules**
```
Given all tests run
When coverage report generated
Then statements: ≥80%, branches: ≥75%, functions: ≥80%, lines: ≥80%
```

---

## Developer Context & Guardrails

### Architecture Compliance

**Critical Testing Rules:**
- ✅ Jest setup with jsdom for DOM testing
- ✅ Mock Chart.js globally (no real Canvas)
- ✅ Mock fetch API for api.js tests
- ✅ Test module exports and function signatures
- ✅ Verify no circular dependencies between modules
- ✅ Integration tests verify app.js orchestration only, not module internals

### Module Test Scope

**api.js Tests:**
- simulateSolar(payload) with success response (200)
- simulateSolar(payload) with validation error (422)
- simulateSolar(payload) with network error
- Button state changes: disabled=true, text='Simulating…'
- Button state restore: disabled=false, text='Simulate'
- Response structure matches API contract

**forms.js Tests:**
- loadDefaults() sets all form field values from DEFAULTS
- readSolarForm() collects form data and converts to snake_case payload
- showFieldError(fieldId, message) displays error in correct location
- clearFieldError(fieldName) clears error from field
- clearErrors() clears all field errors
- showFormError(message) displays global error message
- updateResultCards(data) updates card text with correct values
- Error elements have .show class when visible

**charts.js Tests:**
- initDailyChart(canvas) creates Chart instance with correct config
- initYearlyChart(canvas) creates Chart instance with correct config
- updateDailyChart(data) sets chart.data.datasets[0].data and calls chart.update()
- updateYearlyChart(data) sets chart.data.datasets[0].data and calls chart.update()
- No destroy() or new Chart() called in update functions
- Chart instances persist across multiple updates

**tabs.js Tests:**
- switchTab(tabId) shows correct panel by removing [hidden]
- switchTab(tabId) adds .tab-active class to correct button
- Switching tabs multiple times maintains correct state

**app.js Integration Tests:**
- DOMContentLoaded initializes all modules correctly
- handleSubmit flow: clear errors → readSolarForm → simulateSolar → displayResults
- Error handling: 422 errors display inline, network errors show global message
- displayResults: calls updateResultCards, updateDailyChart, updateYearlyChart
- No direct Chart constructor calls from app.js

### Current Frontend State

**Story 1.3 Completion Summary:**
- 5 ES6 modules created: tabs.js, api.js, forms.js, charts.js, app.js
- Total: 336 lines of modular code
- No external dependencies (Chart.js via CDN, fetch native)
- All functionality working end-to-end

**Test Files to Create:**
- `frontend/__tests__/api.test.js`
- `frontend/__tests__/forms.test.js`
- `frontend/__tests__/charts.test.js`
- `frontend/__tests__/tabs.test.js`
- `frontend/__tests__/app.test.js` (integration)

### Implementation Strategy

**Phase 1: Jest Setup**
1. Create `frontend/package.json` with Jest and testing dependencies
   - jest (test framework)
   - @testing-library/dom (DOM testing utilities)
   - jsdom (DOM implementation for Node)
2. Create `frontend/jest.config.js` with:
   - testEnvironment: 'jsdom'
   - setupFilesAfterEnv for global mocks
   - testMatch pattern for test files
   - collectCoverageFrom for coverage reporting
3. Create `frontend/__tests__/setup.js` to mock Chart.js and fetch

**Phase 2: Write Module Tests**
1. api.test.js (15-20 tests)
   - Mock fetch, button DOM
   - Test success, 422, network error cases
   - Verify button state changes

2. forms.test.js (12-15 tests)
   - Mock DOM, form elements, error spans
   - Test all exported functions
   - Verify DEFAULTS values
   - Test data transformation (camelCase → snake_case)

3. charts.test.js (8-10 tests)
   - Mock Chart.js constructor
   - Test init functions create instances
   - Test update functions call chart.update()
   - Verify no destroy calls

4. tabs.test.js (4-6 tests)
   - Mock tab buttons and panels
   - Test switchTab for each tab
   - Verify hidden attribute and active class

5. app.test.js (6-8 tests)
   - Integration tests for DOMContentLoaded
   - Test handleSubmit flow
   - Test error handling paths
   - Verify module interactions

**Phase 3: Verify Coverage**
1. Run `npm test -- --coverage`
2. Check each module meets ≥80% statement coverage
3. Identify and test uncovered branches

### Technical Requirements

**Dependencies:**
```json
{
  "devDependencies": {
    "jest": "^29.7.0",
    "@testing-library/dom": "^9.3.4",
    "jsdom": "^22.1.0"
  }
}
```

**Jest Configuration:**
- testEnvironment: 'jsdom' (browser-like DOM)
- setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
- collectCoverageFrom: ['*.js', '!jest.config.js']
- testMatch: ['**/__tests__/**/*.test.js']
- coverageThreshold:
  - statements: 80
  - branches: 75
  - functions: 80
  - lines: 80

**Mock Strategy:**
- Chart.js: Mock constructor and instance methods
- fetch API: Jest mock function with configurable responses
- DOM elements: Create in beforeEach, clean in afterEach
- Button element: Mock getElementById, disabled property, textContent

**Test Pattern (Example):**
```javascript
// api.test.js
import { simulateSolar } from '../api.js';

describe('api.js', () => {
  beforeEach(() => {
    // Mock button DOM
    document.body.innerHTML = '<button id="simulateBtn">Simulate</button>';
    // Mock fetch
    global.fetch = jest.fn();
  });

  test('simulateSolar returns success response', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ annual_energy_kwh: 5000 })
    });
    
    const result = await simulateSolar({ /* payload */ });
    expect(result.annual_energy_kwh).toBe(5000);
  });

  test('button disabled during request', async () => {
    const btn = document.getElementById('simulateBtn');
    // ... call simulateSolar and verify button state
  });
});
```

### Files to Create / Modify

**NEW FILES:**
- `frontend/package.json` — npm configuration with Jest dependencies
- `frontend/jest.config.js` — Jest configuration
- `frontend/jest.setup.js` — Global test setup (mocks)
- `frontend/__tests__/api.test.js` — api.js tests (15-20 tests)
- `frontend/__tests__/forms.test.js` — forms.js tests (12-15 tests)
- `frontend/__tests__/charts.test.js` — charts.js tests (8-10 tests)
- `frontend/__tests__/tabs.test.js` — tabs.js tests (4-6 tests)
- `frontend/__tests__/app.test.js` — app.js integration tests (6-8 tests)

**MODIFIED FILES:**
- None (tests don't modify existing code)

**UNCHANGED FILES:**
- All frontend .js, .html, .css files remain unchanged
- Backend files unchanged

### Key Constraints & Decisions

**No Code Changes:**
- Tests verify existing modules, don't modify them
- If bugs found, create separate bug fix commits

**Mock Boundaries:**
- Chart.js fully mocked (no real Canvas rendering)
- fetch fully mocked (no real HTTP requests)
- DOM fully mocked (no real browser)
- Modules imported as-is (no instrumentation)

**Test Organization:**
- One test file per module
- Group related tests with describe blocks
- Clear test names: describe what is tested and expected outcome
- beforeEach/afterEach for setup/cleanup

**Coverage Goals:**
- Minimum 80% statement coverage overall
- All exported functions tested
- Main branches (success/error paths) covered
- Integration test verifies module interactions

---

## Dev Notes: Code Patterns & Learnings

### Module Testing Patterns

**Mock Setup Pattern:**
```javascript
beforeEach(() => {
  // Reset all mocks
  jest.clearAllMocks();
  
  // Create fresh DOM
  document.body.innerHTML = `<div id="root">...</div>`;
  
  // Mock globals
  global.fetch = jest.fn();
});

afterEach(() => {
  // Cleanup
  document.body.innerHTML = '';
});
```

**Async Testing Pattern:**
```javascript
test('async function returns expected value', async () => {
  // Setup mocks
  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ /* response */ })
  });

  // Call function
  const result = await someAsyncFunction();

  // Assert
  expect(result).toEqual({ /* expected */ });
});
```

**DOM State Verification Pattern:**
```javascript
test('DOM state changes', () => {
  const element = document.getElementById('element-id');
  
  // Call function that modifies DOM
  someFunction();
  
  // Verify state
  expect(element.disabled).toBe(true);
  expect(element.textContent).toBe('Expected Text');
  expect(element.classList.contains('active')).toBe(true);
});
```

### Learnings from Stories 1.1-1.3

**Module Structure:**
- Each module is independent (no circular dependencies)
- Modules communicate through function calls from app.js
- Module-level variables (chart instances, DOM references) are initialized per call
- Pure functions preferred where possible

**Test Data:**
- Use DEFAULTS values from forms.js in tests
- API response structure from calculator backend
- Pydantic error format with detail array

**Jest-jsdom Considerations:**
- jsdom provides browser-like DOM but not full browser features
- Canvas API not available (Chart.js needs mock)
- fetch not available (need Jest mock)
- Custom elements need manual setup in tests

---

## Tasks & Subtasks

- [ ] **Task 1: Set up Jest and package.json**
  - [ ] Create frontend/package.json with Jest and testing dependencies
  - [ ] Create frontend/jest.config.js with jsdom configuration
  - [ ] Create frontend/jest.setup.js for global mocks (Chart, fetch)
  - [ ] Add npm test script to package.json
  - [ ] Verify npm test runs without errors

- [ ] **Task 2: Write api.js tests**
  - [ ] Create __tests__/api.test.js file
  - [ ] Mock fetch API and button DOM
  - [ ] Test simulateSolar with 200 success response
  - [ ] Test simulateSolar with 422 validation error
  - [ ] Test simulateSolar with network error
  - [ ] Test button disabled/enabled state transitions
  - [ ] Test button text changes during simulation
  - [ ] Verify ≥80% coverage for api.js

- [ ] **Task 3: Write forms.js tests**
  - [ ] Create __tests__/forms.test.js file
  - [ ] Mock form DOM elements
  - [ ] Test loadDefaults() sets all field values
  - [ ] Test readSolarForm() collects and converts data
  - [ ] Test showFieldError() displays error message
  - [ ] Test clearFieldError() removes error
  - [ ] Test clearErrors() clears all errors
  - [ ] Test showFormError() shows global error
  - [ ] Test updateResultCards() updates card values
  - [ ] Verify DEFAULTS object has correct Turin values
  - [ ] Verify ≥80% coverage for forms.js

- [ ] **Task 4: Write charts.js tests**
  - [ ] Create __tests__/charts.test.js file
  - [ ] Mock Chart.js constructor
  - [ ] Test initDailyChart() creates chart instance
  - [ ] Test initYearlyChart() creates chart instance
  - [ ] Test updateDailyChart() updates data and calls chart.update()
  - [ ] Test updateYearlyChart() updates data and calls chart.update()
  - [ ] Verify chart.update() called, not destroy()
  - [ ] Verify ≥80% coverage for charts.js

- [ ] **Task 5: Write tabs.js tests**
  - [ ] Create __tests__/tabs.test.js file
  - [ ] Mock tab buttons and panels
  - [ ] Test switchTab('solar') shows solar panel
  - [ ] Test switchTab('battery') shows battery panel
  - [ ] Test switchTab('cost') shows cost panel
  - [ ] Test tab button active class applied correctly
  - [ ] Verify ≥80% coverage for tabs.js

- [ ] **Task 6: Write app.js integration tests**
  - [ ] Create __tests__/app.test.js file
  - [ ] Mock all dependencies (api, forms, charts, tabs)
  - [ ] Test DOMContentLoaded initializes modules
  - [ ] Test handleSubmit flow (clear → read → call api → display)
  - [ ] Test error handling for 422 errors
  - [ ] Test error handling for network errors
  - [ ] Test displayResults updates cards and charts
  - [ ] Verify ≥80% coverage for app.js

- [ ] **Task 7: Verify coverage and run full test suite**
  - [ ] Run npm test -- --coverage
  - [ ] Verify overall coverage ≥80%
  - [ ] Check each module has ≥80% statement coverage
  - [ ] Identify any uncovered branches
  - [ ] All tests pass without errors
  - [ ] Coverage report shows per-file breakdown

---

## Dev Agent Record

### Implementation Plan

_To be filled in by dev agent during implementation_

### Debug Log

_To be filled in during implementation if issues arise_

### Completion Notes

_To be filled in when story is marked complete_

---

## File List

### NEW FILES
- `frontend/package.json` — npm configuration with Jest
- `frontend/jest.config.js` — Jest configuration
- `frontend/jest.setup.js` — Global test setup
- `frontend/__tests__/api.test.js` — api.js unit tests
- `frontend/__tests__/forms.test.js` — forms.js unit tests
- `frontend/__tests__/charts.test.js` — charts.js unit tests
- `frontend/__tests__/tabs.test.js` — tabs.js unit tests
- `frontend/__tests__/app.test.js` — app.js integration tests

### MODIFIED FILES
- None (tests don't modify existing code)

### UNCHANGED FILES
- All frontend .js, .html, .css files
- All backend files

---

## Change Log

- **2026-05-22** — Story file created with comprehensive Jest testing context
  - Planned Jest setup with jsdom for DOM testing
  - Defined test scope for all 5 frontend modules
  - Created test patterns and mock strategies
  - Identified 50+ tests to write across all modules
  - Set coverage threshold: ≥80% per module

---

## Status

**Current:** ready-for-dev  
**Next:** Implement Jest setup and write 50+ unit tests

**Blockers:** None  
**Dependencies:** Story 1.3 (modules complete) — done ✓  
**Blocks:** Epic 2 (Battery Simulation) — unit tests validate before new features

