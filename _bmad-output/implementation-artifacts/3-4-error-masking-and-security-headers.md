---
storyKey: 3-4-error-masking-and-security-headers
storyId: "3.4"
title: Error Masking & Security Headers
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-4: Error Masking & Security Headers

## Story

As a security engineer,
I want error messages masked in production and security headers added to all responses,
So that internal implementation details are not leaked and browsers have protection against XSS/clickjacking.

**Requirements Covered:** FR-SEC-1, FR-SEC-2, NFR-SEC-1

---

## Acceptance Criteria

**Given** the backend is running in development (ENV=development)
**When** an unhandled exception occurs in /simulate
**Then** the error response includes the full stack trace (for debugging)

**Given** the backend is running in production (ENV=production)
**When** an unhandled exception occurs in /simulate
**Then** the error response includes generic message "Simulation failed. Please try again."

**And** the full stack trace is NOT sent to the client

**When** any response is returned from the backend
**Then** the response includes: X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block, Strict-Transport-Security: max-age=31536000

---

## Tasks & Subtasks

- [x] Implement environment-aware error handling in main.py
  - [x] Read ENV setting from os.getenv() (configured in Story 3-1)
  - [x] Create custom exception handler for unhandled exceptions
  - [x] In development: return full traceback in response body
  - [x] In production: return generic error message "Simulation failed. Please try again."
  - [x] Verify exception handler is invoked for all unhandled exceptions

- [x] Add security headers to all responses
  - [x] Create middleware or response hook to add security headers
  - [x] Add X-Content-Type-Options: nosniff (prevents MIME sniffing)
  - [x] Add X-Frame-Options: DENY (prevents clickjacking)
  - [x] Add X-XSS-Protection: 1; mode=block (XSS filter)
  - [x] Add Strict-Transport-Security: max-age=31536000 (HSTS, 1 year)

- [x] Test error masking in development environment
  - [x] Set ENV=development
  - [x] Trigger an error in /simulate (e.g., invalid input causing exception)
  - [x] Verify response includes full stack trace
  - [x] Verify error is visible for debugging

- [x] Test error masking in production environment
  - [x] Set ENV=production
  - [x] Trigger the same error in /simulate
  - [x] Verify response shows generic message "Simulation failed. Please try again."
  - [x] Verify stack trace is NOT present in response body
  - [x] Verify stack trace is logged server-side for ops review

- [x] Test security headers in all responses
  - [x] Make requests to /simulate endpoint
  - [x] Verify X-Content-Type-Options: nosniff is present
  - [x] Verify X-Frame-Options: DENY is present
  - [x] Verify X-XSS-Protection: 1; mode=block is present
  - [x] Verify Strict-Transport-Security: max-age=31536000 is present
  - [x] Verify headers are present on both success and error responses

- [x] Verify no regressions
  - [x] Run existing backend tests: `pytest --cov=app`
  - [x] Ensure all tests pass with new error handling
  - [x] Verify coverage remains ≥80%
  - [x] Test end-to-end simulation workflow with valid inputs

---

## Dev Notes

**Architecture Context:**
Error masking is a critical security pattern: production environments should never leak implementation details (stack traces, internal function names, library versions) to clients. Development environments need full traces for debugging.

Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS) are standard defense-in-depth measures:
- X-Content-Type-Options: nosniff prevents browsers from MIME-sniffing (reduces XSS attack surface)
- X-Frame-Options: DENY prevents clickjacking by disallowing framing
- X-XSS-Protection: 1; mode=block enables browser XSS filters (legacy, but still valuable)
- Strict-Transport-Security: max-age=31536000 enforces HTTPS-only communication for 1 year

**Key Patterns:**
- Error handling should be environment-aware (development vs. production)
- Security headers should be added to all responses via middleware
- Stack traces should be logged server-side even in production (for ops support)
- Generic error messages should not expose internal implementation details

**Dependencies:**
- No new dependencies required (uses FastAPI's built-in exception handling)

**Related Stories:**
- Story 3-1 (Environment Management) — provides ENV configuration
- Story 3-5 (Deployment Documentation) — documents security checklist including these headers
- Story 3-7 (Integration Testing) — includes security header validation tests

**Files Modified:**
- `backend/app/main.py` — add exception handler and security headers middleware

---

## Dev Agent Record

### Implementation Plan

Two main additions to `main.py`:
1. `@app.middleware("http") add_security_headers` — placed after `app.add_middleware(CORSMiddleware)` so it becomes the outermost layer (executes last on responses), ensuring all four security headers appear on every response including error responses.
2. `@app.exception_handler(Exception) unhandled_exception_handler` — global safety net for truly unhandled exceptions, env-aware.
3. Updated `/simulate` try/except to log via `logger.error()` and include `traceback.format_exc()` in development responses.

Used `monkeypatch.setattr(main_module, "env", ...)` in tests to switch env without reloading the module.

### Debug Log

(none — implementation straightforward)

### Completion Notes

✅ **Story 3-4: Error Masking & Security Headers COMPLETE**

**Implemented:**
- `add_security_headers` HTTP middleware adds X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Strict-Transport-Security to all responses
- `unhandled_exception_handler` global handler: dev returns exception + traceback, prod returns generic "Internal server error."
- `/simulate` error path: logs traceback with `logger.error()`, dev includes full traceback in response, prod returns "Simulation failed. Please try again."

**Testing:**
- 5 new tests: 3 security header + 2 error masking
- 147 tests pass, 94% coverage (≥80% required)

---

## File List

**New Files:**
(none)

**Modified Files:**
- backend/app/main.py
- backend/tests/test_main.py

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-22: Story created from Epic 3 specification
- 2026-05-23: Implementation complete — security headers middleware and environment-aware error masking

---

## Status

**Current:** review
**Completion:** 2026-05-23
**Final:** All acceptance criteria satisfied, implementation complete, ready for code review
