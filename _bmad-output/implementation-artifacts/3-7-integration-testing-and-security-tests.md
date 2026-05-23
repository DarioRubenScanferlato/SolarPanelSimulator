---
storyKey: 3-7-integration-testing-and-security-tests
storyId: "3.7"
title: Integration Testing & Security Tests
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-7: Integration Testing & Security Tests

## Story

As a qa engineer,
I want integration tests for /simulate endpoint including rate limiting and security headers,
So that API contracts and security configurations are validated.

**Requirements Covered:** NFR-3, NFR-SEC-1

---

## Acceptance Criteria

**Given** I run integration tests with FastAPI TestClient
**When** I send a valid request to /simulate
**Then** the response is 200 with all expected fields

**Given** I send an invalid request (e.g., latitude=95)
**When** the request is processed
**Then** the response is 422 with field-level validation errors

**Given** I send requests to /simulate at a rate exceeding the limit
**When** the limit is exceeded
**Then** subsequent requests receive 429 Too Many Requests

**Given** I check security headers in the response
**When** the response is returned
**Then** X-Content-Type-Options, X-Frame-Options, X-XSS-Protection are present with correct values

---

## Tasks & Subtasks

- [x] Create TestSimulateEndpointIntegration class
  - [x] Test valid solar request returns 200 with complete response
    - [x] Verify all solar output fields present (daily_hourly_generation, monthly_energy_kwh, etc.)
    - [x] Verify field types and ranges (24 hourly values, 12 monthly values)
  - [x] Test legacy request (no battery fields) returns 200 without battery fields (backwards compatible)
  - [x] Test response time <500ms for typical request

- [x] Create TestInputValidation class
  - [x] Test latitude out of range (-90 to 90) returns 422
  - [x] Test longitude out of range (-180 to 180) returns 422
  - [x] Test invalid panels count (<1) returns 422
  - [x] Test invalid area (<0) returns 422
  - [x] Test invalid efficiency (<0 or >100) returns 422
  - [x] Test invalid tilt angle (<0 or >90) returns 422
  - [x] Test invalid azimuth (<0 or >360) returns 422
  - [x] Test invalid duration (<1 day) returns 422
  - [x] Test partial battery fields ignored for now (will enforce all-or-none in Story 2-1)
  - [x] Verify error response includes detail array with field-level errors

- [x] Create TestRateLimiting class
  - [x] Test single request succeeds (within limit)
  - [x] Test 10 requests to /simulate in 60 seconds — all succeed
  - [x] Test 11th request in same 60-second window receives 429 Too Many Requests
  - [x] Test rate limiting is per-IP

- [x] Create TestSecurityHeaders class
  - [x] Test X-Content-Type-Options: nosniff present on success response
  - [x] Test X-Content-Type-Options: nosniff present on error response
  - [x] Test X-Frame-Options: DENY present on all responses
  - [x] Test X-XSS-Protection: 1; mode=block present on all responses
  - [x] Test Strict-Transport-Security: max-age=31536000 present on all responses
  - [x] Verify security headers on /health endpoint

- [x] Create TestErrorHandling class
  - [x] Test development error response includes stack trace (when ENV=development)
  - [x] Test production error response is generic (when ENV=production)
  - [x] Test 404 error for invalid endpoint
  - [x] Test 405 error for invalid HTTP method (GET to /simulate)

- [x] Create TestCORSBehavior class
  - [x] Test CORS request from allowed origin includes correct headers
  - [x] Test CORS request from blocked origin excludes CORS headers

- [x] Create test fixtures
  - [x] Fixture: FastAPI TestClient for /simulate endpoint
  - [x] Fixture: valid solar input payload
  - [x] Fixture: valid battery input payload (for future battery tests)
  - [x] Fixture: invalid inputs for parameterized tests
  - [x] Fixture: environment setup (ENV=development vs. production)

- [x] Verify test coverage
  - [x] Run pytest --cov=app --cov-fail-under=80
  - [x] Overall app/ coverage: 94% (threshold met)
  - [x] Integration tests cover main.py endpoints thoroughly
  - [x] All 31 integration tests pass

- [x] Run full test suite
  - [x] Run all unit tests (test_battery, test_calculator, etc.)
  - [x] Run all integration tests (test_main_integration)
  - [x] All 178 tests pass with zero regressions
  - [x] Coverage remains 94% (well above 80% threshold)

---

## Dev Notes

**Architecture Context:**
Integration tests validate the entire /simulate endpoint including:
1. Input validation (Pydantic models catch invalid data)
2. Rate limiting (slowapi middleware enforces limits)
3. Security headers (middleware adds headers to responses)
4. CORS behavior (FastAPI CORSMiddleware applies rules)
5. Error handling (custom exception handlers apply logic)

These tests are "integration" because they test the full stack from HTTP request to response, exercising all middleware and validation layers.

**Key Patterns:**
- Use FastAPI TestClient for server-side integration tests (no network calls)
- Test both success and error paths
- Verify security headers on all response types
- Test rate limiting with controlled timing
- Test edge cases and invalid inputs
- Use fixtures for common test data
- Parameterize tests across multiple input scenarios

**Dependencies:**
- pytest (already installed)
- FastAPI TestClient (comes with FastAPI)
- pytest-cov (already installed)
- No new test dependencies required

**Related Stories:**
- Story 3-1 (Environment Management) — provides config for testing
- Story 3-3 (CORS Hardening) — includes rate limiting tests
- Story 3-4 (Error Masking) — includes error handling tests
- Story 3-6 (Unit Testing) — unit-level battery tests

**Files Modified/Created:**
- `backend/tests/test_main_integration.py` — NEW, integration tests for /simulate endpoint

---

## Dev Agent Record

### Implementation Plan

Created comprehensive integration test suite in `test_main_integration.py` with:
- 6 test classes (TestSimulateEndpointIntegration, TestInputValidation, TestRateLimiting, TestSecurityHeaders, TestErrorHandling, TestCORSBehavior)
- 31 integration tests validating HTTP layer, middleware, and endpoint behavior
- Parametrized tests for input validation edge cases
- Fixtures for payloads, clients, and environment setup
- Full coverage of acceptance criteria

### Debug Log

Minor adjustments made:
- Fixed field names to match actual SolarOutput model (daily_hourly_generation, monthly_energy_kwh, average_daily_kwh)
- Adjusted battery tests to reflect that battery simulation not yet implemented (Story 2-1)
- Fixed CORS preflight tests since /simulate only supports POST, not OPTIONS
- All tests pass after adjustments

### Completion Notes

✅ Created `backend/tests/test_main_integration.py` with 31 comprehensive integration tests
✅ All acceptance criteria validated:
  - Valid requests return 200 with correct field structure and types
  - Invalid inputs return 422 with field-level errors
  - Rate limiting enforces 10 requests/minute limit
  - Security headers present on all responses (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, STS)
  - Error handling differs between dev (with traceback) and production (generic)
  - CORS validation prevents unauthorized origins
✅ Test coverage: 94% (threshold: 80%)
✅ All 178 tests pass (31 integration + 147 existing unit tests)
✅ Zero regressions

---

## File List

**New Files:**
- backend/tests/test_main_integration.py

**Modified Files:**
(none)

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-22: Story created from Epic 3 specification
- 2026-05-23: Implementation complete — 31 integration tests, 94% coverage, all 178 tests pass

---

## Status

**Current:** review
**Completion:** complete
**Final:** Ready for code review
