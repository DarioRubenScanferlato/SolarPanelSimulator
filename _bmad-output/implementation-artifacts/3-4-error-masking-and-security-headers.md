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

- [ ] Implement environment-aware error handling in main.py
  - [ ] Read ENV setting from os.getenv() (configured in Story 3-1)
  - [ ] Create custom exception handler for unhandled exceptions
  - [ ] In development: return full traceback in response body
  - [ ] In production: return generic error message "Simulation failed. Please try again."
  - [ ] Verify exception handler is invoked for all unhandled exceptions

- [ ] Add security headers to all responses
  - [ ] Create middleware or response hook to add security headers
  - [ ] Add X-Content-Type-Options: nosniff (prevents MIME sniffing)
  - [ ] Add X-Frame-Options: DENY (prevents clickjacking)
  - [ ] Add X-XSS-Protection: 1; mode=block (XSS filter)
  - [ ] Add Strict-Transport-Security: max-age=31536000 (HSTS, 1 year)

- [ ] Test error masking in development environment
  - [ ] Set ENV=development
  - [ ] Trigger an error in /simulate (e.g., invalid input causing exception)
  - [ ] Verify response includes full stack trace
  - [ ] Verify error is visible for debugging

- [ ] Test error masking in production environment
  - [ ] Set ENV=production
  - [ ] Trigger the same error in /simulate
  - [ ] Verify response shows generic message "Simulation failed. Please try again."
  - [ ] Verify stack trace is NOT present in response body
  - [ ] Verify stack trace is logged server-side for ops review

- [ ] Test security headers in all responses
  - [ ] Make requests to /simulate endpoint
  - [ ] Verify X-Content-Type-Options: nosniff is present
  - [ ] Verify X-Frame-Options: DENY is present
  - [ ] Verify X-XSS-Protection: 1; mode=block is present
  - [ ] Verify Strict-Transport-Security: max-age=31536000 is present
  - [ ] Verify headers are present on both success and error responses

- [ ] Verify no regressions
  - [ ] Run existing backend tests: `pytest --cov=app`
  - [ ] Ensure all tests pass with new error handling
  - [ ] Verify coverage remains ≥80%
  - [ ] Test end-to-end simulation workflow with valid inputs

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

(To be filled in during implementation)

### Debug Log

(To be filled in during implementation)

### Completion Notes

(To be filled in during implementation)

---

## File List

**New Files:**
(none)

**Modified Files:**
- backend/app/main.py

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
