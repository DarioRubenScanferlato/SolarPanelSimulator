---
storyKey: 3-8-e2e-testing-framework-setup-playwright
storyId: "3.8"
title: E2E Testing Framework Setup (Playwright)
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-8: E2E Testing Framework Setup (Playwright)

## Story

As a qa engineer,
I want E2E testing framework set up with Playwright configuration,
So that user workflows can be tested in a real browser.

**Requirements Covered:** NFR-3, NFR-SEC-1

---

## Acceptance Criteria

**Given** I am setting up Playwright for E2E testing
**When** I install dependencies
**Then** @playwright/test==^1.40.0 is installed as dev dependency

**And** playwright.config.ts exists with testDir, baseURL, webServer, and browser targeting

**Given** I run E2E tests in headless mode
**When** tests execute
**Then** no browser window appears (headless operation)

**And** npm scripts are added: npm run test:e2e

---

## Tasks & Subtasks

- [ ] Install Playwright testing framework
  - [ ] Install @playwright/test==^1.40.0 as dev dependency: `npm install --save-dev @playwright/test@^1.40.0`
  - [ ] Verify installation in package.json
  - [ ] Verify node_modules contains Playwright

- [ ] Create playwright.config.ts
  - [ ] Configure testDir: './frontend/e2e' (directory for E2E tests)
  - [ ] Configure baseURL: 'http://localhost:3000' (frontend URL)
  - [ ] Configure webServer section:
    - [ ] command to start dev server
    - [ ] port: 3000
    - [ ] reuseExistingServer: false (for clean tests)
  - [ ] Configure browser targets: chromium, firefox, webkit (or subset)
  - [ ] Set headless: true (headless mode)
  - [ ] Configure timeout: 30000ms per test
  - [ ] Configure retries: 1 (retry failed tests once)
  - [ ] Configure use section: browserName, baseURL, viewport, actionTimeout

- [ ] Create frontend/e2e directory structure
  - [ ] Create `frontend/e2e/` directory (contains E2E tests)
  - [ ] Create `frontend/e2e/example.spec.ts` placeholder test file

- [ ] Add npm scripts
  - [ ] Add "test:e2e" script: `playwright test`
  - [ ] Add "test:e2e:headed" script: `playwright test --headed` (for debugging)
  - [ ] Add "test:e2e:ui" script: `playwright test --ui` (interactive mode)
  - [ ] Add "test:e2e:debug" script: `playwright test --debug` (debug mode)

- [ ] Create example E2E test file
  - [ ] File: `frontend/e2e/example.spec.ts`
  - [ ] Test: page loads successfully
  - [ ] Test: page title is correct
  - [ ] Test: Solar Simulation tab is visible
  - [ ] Test: form inputs are present
  - [ ] Verify example tests pass

- [ ] Create .gitignore rules for Playwright
  - [ ] Add test results directory to .gitignore
  - [ ] Add Playwright cache directory to .gitignore
  - [ ] Add artifacts directory to .gitignore

- [ ] Verify Playwright configuration
  - [ ] Run `npm run test:e2e` and verify tests pass
  - [ ] Run in headless mode and verify no browser window appears
  - [ ] Run `npm run test:e2e:headed` and verify browser opens (for manual testing)
  - [ ] Verify test results are reported clearly

- [ ] Document Playwright usage
  - [ ] Add section to README about E2E testing
  - [ ] Document how to run tests: `npm run test:e2e`
  - [ ] Document debug options: `--headed`, `--ui`, `--debug`
  - [ ] Link to Playwright documentation

---

## Dev Notes

**Architecture Context:**
Playwright provides a modern, maintainable E2E testing framework. Key features:
- Cross-browser testing (Chromium, Firefox, WebKit)
- Headless operation (ideal for CI/CD)
- Auto-waiting (reduces flaky tests)
- Inspector and tracing tools for debugging
- Generates test reports and artifacts

The configuration allows:
1. Local development with `--headed` to see browser
2. CI/CD with headless mode
3. Debug mode with Inspector for troubleshooting
4. Interactive UI mode for exploring page behavior

**Key Patterns:**
- testDir should be separate from frontend source code
- baseURL should match dev server URL
- webServer should start dev server automatically
- headless: true for CI/CD, false/--headed for debugging
- Timeouts should be generous (30s) to avoid flaky tests

**Dependencies:**
- @playwright/test==^1.40.0 (add to package.json devDependencies)
- No other new dependencies required

**Related Stories:**
- Story 3-9 (E2E Test Implementation) — implements actual tests using this framework

**Files Modified/Created:**
- `frontend/package.json` — add @playwright/test dependency and scripts
- `playwright.config.ts` — NEW
- `frontend/e2e/example.spec.ts` — NEW, example test
- `.gitignore` — add Playwright artifacts
- `README.md` — document E2E testing setup

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
- playwright.config.ts
- frontend/e2e/example.spec.ts

**Modified Files:**
- frontend/package.json
- .gitignore
- README.md

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-22: Story created from Epic 3 specification

---

## Status

**Current:** ready-for-dev
**Completion:** pending
**Final:** Awaiting implementation
