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

- [ ] Create TestSimulateEndpointIntegration class
  - [ ] Test valid solar request returns 200 with complete response
    - [ ] Verify all solar output fields present (hourly_output, monthly_output, etc.)
    - [ ] Verify field types and ranges
  - [ ] Test valid request with battery fields returns 200 with battery response
    - [ ] Verify battery_hourly_soc present
    - [ ] Verify self_consumption_pct in range [0, 100]
    - [ ] Verify grid_import_kwh and grid_export_kwh ≥ 0
  - [ ] Test legacy request (no battery fields) returns 200 without battery fields (backwards compatible)
  - [ ] Test response time <500ms for typical request

- [ ] Create TestInputValidation class
  - [ ] Test latitude out of range (-90 to 90) returns 422
  - [ ] Test longitude out of range (-180 to 180) returns 422
  - [ ] Test invalid panels count (<1) returns 422
  - [ ] Test invalid area (<0) returns 422
  - [ ] Test invalid efficiency (<0 or >100) returns 422
  - [ ] Test invalid tilt angle (<0 or >90) returns 422
  - [ ] Test invalid azimuth (<0 or >360) returns 422
  - [ ] Test invalid date (future date beyond reasonable forecast) returns 422
  - [ ] Test invalid duration (<1 day) returns 422
  - [ ] Test partial battery fields (some but not all) returns 422 with clear message
  - [ ] Verify error response includes detail array with field-level errors

- [ ] Create TestRateLimiting class
  - [ ] Test single request succeeds (within limit)
  - [ ] Test make 10 requests to /simulate in 60 seconds — all succeed
  - [ ] Test 11th request in same 60-second window receives 429 Too Many Requests
  - [ ] Verify 429 response includes rate limit information
  - [ ] Test after 60 seconds, next request succeeds (limit resets)
  - [ ] Test rate limiting is IP-based (different IPs have separate limits)

- [ ] Create TestSecurityHeaders class
  - [ ] Test X-Content-Type-Options: nosniff present on success response
  - [ ] Test X-Content-Type-Options: nosniff present on error response
  - [ ] Test X-Frame-Options: DENY present on all responses
  - [ ] Test X-XSS-Protection: 1; mode=block present on all responses
  - [ ] Test Strict-Transport-Security: max-age=31536000 present on all responses
  - [ ] Verify security headers on /simulate endpoint
  - [ ] Verify security headers on /health endpoint (if exists)

- [ ] Create TestErrorHandling class
  - [ ] Test development error response includes stack trace (when ENV=development)
  - [ ] Test production error response is generic (when ENV=production)
  - [ ] Test 404 error for invalid endpoint
  - [ ] Test 405 error for invalid HTTP method (GET to /simulate)

- [ ] Create TestCORSBehavior class
  - [ ] Test OPTIONS preflight request succeeds
  - [ ] Test preflight response includes Access-Control-Allow-Origin
  - [ ] Test preflight response includes Access-Control-Allow-Methods: POST, GET
  - [ ] Test preflight response includes Access-Control-Allow-Headers: Content-Type
  - [ ] Test CORS request from allowed origin succeeds
  - [ ] Test CORS request from blocked origin fails (no CORS headers in response)

- [ ] Create test fixtures
  - [ ] Fixture: FastAPI TestClient for /simulate endpoint
  - [ ] Fixture: valid solar input payload
  - [ ] Fixture: valid battery input payload
  - [ ] Fixture: invalid inputs for parameterized tests
  - [ ] Fixture: environment setup (ENV=development vs. production)

- [ ] Verify test coverage
  - [ ] Run pytest --cov=app --cov-fail-under=80
  - [ ] Verify overall app/ coverage remains ≥80%
  - [ ] Verify integration tests cover main.py endpoints
  - [ ] Generate coverage report for review

- [ ] Run full test suite
  - [ ] Run all unit tests (test_battery, test_calculator, etc.)
  - [ ] Run all integration tests (test_main_integration)
  - [ ] Verify zero regressions in existing tests
  - [ ] Verify coverage remains ≥80%

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

(To be filled in during implementation)

### Debug Log

(To be filled in during implementation)

### Completion Notes

(To be filled in during implementation)

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

---

## Status

**Current:** ready-for-dev
**Completion:** pending
**Final:** Awaiting implementation
