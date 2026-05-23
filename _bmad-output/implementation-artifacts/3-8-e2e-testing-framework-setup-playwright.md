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

- [x] Install Playwright testing framework
  - [x] Install @playwright/test@^1.40.0 as dev dependency: `npm install --save-dev @playwright/test@^1.40.0`
  - [x] Verify installation in package.json (shows @playwright/test: ^1.60.0)
  - [x] Verify node_modules contains Playwright (installed successfully)

- [x] Create playwright.config.ts
  - [x] Configure testDir: './frontend/e2e' (directory for E2E tests)
  - [x] Configure baseURL: 'http://localhost:3000' (frontend URL)
  - [x] Configure webServer section with dev server startup
  - [x] Configure browser targets: chromium, firefox, webkit
  - [x] Set headless: true (headless operation)
  - [x] Configure timeout: 10000ms action timeout, 120s webserver timeout
  - [x] Configure retries: 1 for local, 2 for CI
  - [x] Configure use section: baseURL, trace, actionTimeout

- [x] Create frontend/e2e directory structure
  - [x] Create `frontend/e2e/` directory (contains E2E tests)
  - [x] Create `frontend/e2e/example.spec.ts` with 5 example tests

- [x] Add npm scripts
  - [x] Add "test:e2e" script: `playwright test`
  - [x] Add "test:e2e:headed" script: `playwright test --headed` (for debugging)
  - [x] Add "test:e2e:ui" script: `playwright test --ui` (interactive mode)
  - [x] Add "test:e2e:debug" script: `playwright test --debug` (debug mode)

- [x] Create example E2E test file
  - [x] File: `frontend/e2e/example.spec.ts`
  - [x] Test: page loads successfully
  - [x] Test: Solar Simulation tab is visible
  - [x] Test: form inputs are present
  - [x] Test: defaults are loaded on page load
  - [x] Test: Battery and Cost Analysis tabs visible

- [x] Create .gitignore rules for Playwright
  - [x] Add test-results/ directory
  - [x] Add playwright-report/ directory
  - [x] Add playwright/.cache/ directory

- [x] Document Playwright usage
  - [x] Add section to README about E2E testing
  - [x] Document how to run tests: `npm run test:e2e`
  - [x] Document debug options: `--headed`, `--ui`, `--debug`
  - [x] Link to Playwright documentation

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

1. Install Playwright: `npm install --save-dev @playwright/test^1.40.0`
2. Create playwright.config.ts with testDir, baseURL, webServer, browser targets
3. Create frontend/e2e directory and example.spec.ts
4. Add npm scripts to package.json
5. Update .gitignore with Playwright artifacts
6. Update README with E2E testing documentation

### Debug Log

All tasks completed successfully. No blockers encountered.

### Completion Notes

✅ Installed @playwright/test (version 1.60.0 — compatible with ^1.40.0)
✅ Created playwright.config.ts with:
  - testDir: ./frontend/e2e
  - baseURL: http://localhost:3000
  - webServer: npm run dev on port 3000
  - Browser targets: chromium, firefox, webkit
  - Headless mode enabled, retries configured, trace artifacts
✅ Created frontend/e2e/example.spec.ts with 5 passing example tests
✅ Added npm scripts: test:e2e, test:e2e:headed, test:e2e:ui, test:e2e:debug
✅ Updated .gitignore with test-results/, playwright-report/, playwright/.cache/
✅ Updated README with E2E testing section and all available commands

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
- 2026-05-23: Playwright framework setup complete — config, example tests, npm scripts, documentation

---

## Status

**Current:** review
**Completion:** complete
**Final:** Ready for code review
