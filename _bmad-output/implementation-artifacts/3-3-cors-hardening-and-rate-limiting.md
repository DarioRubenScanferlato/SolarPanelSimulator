---
storyKey: 3-3-cors-hardening-and-rate-limiting
storyId: "3.3"
title: CORS Hardening & Rate Limiting
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-3: CORS Hardening & Rate Limiting

## Story

As a security engineer,
I want CORS configured with explicit methods/headers and rate limiting on the /simulate endpoint,
So that the API is protected from CORS misconfigurations and DOS attacks.

**Requirements Covered:** FR-SEC-1, FR-SEC-2, NFR-SEC-1

---

## Acceptance Criteria

**Given** I am running the backend in development
**When** I check the CORS middleware configuration in main.py
**Then** allow_methods = ["POST", "GET"] (explicit, not wildcard ["*"])

**And** allow_headers = ["Content-Type"] (explicit, not wildcard ["*"])

**And** allow_credentials = False

**And** max_age = 600 (preflight cache for 10 minutes)

**Given** I make a request from http://localhost:3000 to the backend
**When** the response is returned
**Then** the response includes Access-Control-Allow-Origin: http://localhost:3000 (from environment variable)

**Given** I change ALLOWED_ORIGINS env var to https://api.yourdomain.com
**When** I restart the backend and make a request from http://localhost:3000
**Then** the response does NOT include CORS headers (request is rejected)

**Given** I am making requests to the /simulate endpoint
**When** I exceed the rate limit (10 per minute in dev, 30 in production)
**Then** subsequent requests receive HTTP 429 Too Many Requests

**And** slowapi==0.1.9 is added to pyproject.toml

**And** the /simulate endpoint is decorated with @limiter.limit()

---

## Tasks & Subtasks

- [ ] Add slowapi dependency to backend
  - [ ] Add "slowapi==0.1.9" to pyproject.toml dependencies
  - [ ] Run `uv sync` to install the dependency
  - [ ] Verify dependency is locked in uv.lock

- [ ] Update CORS middleware in main.py
  - [ ] Change allow_methods from ["*"] to ["POST", "GET"]
  - [ ] Change allow_headers from ["*"] to ["Content-Type"]
  - [ ] Set allow_credentials = False
  - [ ] Set max_age = 600
  - [ ] Use ALLOWED_ORIGINS from os.getenv() (set in Story 3-1)

- [ ] Implement rate limiting in main.py
  - [ ] Import slowapi Limiter and LimitExceeded exception
  - [ ] Create limiter instance with default key_func (IP-based)
  - [ ] Add error handler for RateLimitExceeded to return 429 status
  - [ ] Configure limits: 10/minute for development, 30/minute for production (read from ENV or constant)

- [ ] Decorate /simulate endpoint with rate limiting
  - [ ] Add @limiter.limit("10/minute") to /simulate endpoint in development
  - [ ] Verify rate limit is applied correctly
  - [ ] Document rate limit value in endpoint docstring

- [ ] Test CORS hardening
  - [ ] Create test script to make OPTIONS preflight request from localhost:3000
  - [ ] Verify Access-Control-Allow-Origin header contains localhost:3000
  - [ ] Verify Access-Control-Allow-Methods contains only POST and GET
  - [ ] Verify Access-Control-Allow-Headers contains only Content-Type
  - [ ] Test with invalid origin (localhost:3001) and verify CORS headers not present
  - [ ] Update ALLOWED_ORIGINS env var and verify CORS rejection for old origin

- [ ] Test rate limiting
  - [ ] Create test that makes >10 requests/minute to /simulate
  - [ ] Verify 11th request receives HTTP 429
  - [ ] Verify response body includes rate limit information
  - [ ] Test rate limiting reset (wait 1 minute, verify next request succeeds)

- [ ] Verify no regressions
  - [ ] Run existing backend tests: `pytest --cov=app`
  - [ ] Ensure all tests pass with new CORS and rate limiting
  - [ ] Verify coverage remains ≥80%
  - [ ] Test end-to-end simulation workflow through updated backend

---

## Dev Notes

**Architecture Context:**
CORS hardening follows security best practices: explicit allow-lists instead of wildcards, restricted methods/headers, disabled credentials. Rate limiting protects against DOS attacks on the compute-intensive /simulate endpoint.

The rate limit threshold (10/minute dev, 30/minute production) is chosen to be reasonable for legitimate users while preventing abuse. Slowapi provides simple, decorator-based rate limiting without additional infrastructure.

**Key Patterns:**
- CORS middleware should be configured with explicit values, never wildcards
- Rate limiting should be applied at endpoint level using decorators
- Rate limit values should be configurable via environment variables
- Error responses should be consistent (HTTP 429 with clear message)

**Dependencies:**
- slowapi==0.1.9 (add to pyproject.toml)
- No other new dependencies

**Related Stories:**
- Story 3-1 (Environment Management) — provides ALLOWED_ORIGINS configuration
- Story 3-2 (Frontend Environment) — API calls must respect CORS configuration
- Story 3-7 (Integration Testing) — includes rate limiting tests

**Files Modified:**
- `backend/pyproject.toml` — add slowapi==0.1.9
- `backend/app/main.py` — update CORS middleware, add rate limiting

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
- backend/pyproject.toml
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
