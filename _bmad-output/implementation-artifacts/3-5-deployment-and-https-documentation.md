---
storyKey: 3-5-deployment-and-https-documentation
storyId: "3.5"
title: Deployment & HTTPS Documentation
epicId: 3
epicTitle: Quality, Reliability & Security
status: ready-for-dev
createdAt: '2026-05-22'
startedAt: null
completedAt: null
---

# Story 3-5: Deployment & HTTPS Documentation

## Story

As a devops engineer,
I want documented HTTPS/TLS setup with nginx and Let's Encrypt,
So that production deployment can be secured with valid certificates.

**Requirements Covered:** FR-SEC-1, FR-SEC-2, FR-SEC-4, FR-SEC-5

---

## Acceptance Criteria

**Given** I am preparing for production deployment
**When** I read the deployment documentation
**Then** I find clear instructions for: setting up nginx reverse proxy, configuring Let's Encrypt certificates, creating docker-compose.prod.yml, setting up HTTP → HTTPS redirect

**And** a DEPLOYMENT.md file exists with complete setup instructions

**And** a SECURITY.md file exists with security checklist for pre-production launch

---

## Tasks & Subtasks

- [ ] Create DEPLOYMENT.md documentation
  - [ ] Section 1: Prerequisites (server, domain, ports 80/443 open, Docker/docker-compose installed)
  - [ ] Section 2: DNS Setup (point domain to server IP)
  - [ ] Section 3: Let's Encrypt Certificate Setup
    - [ ] Install certbot
    - [ ] Generate wildcard certificate (or single-domain)
    - [ ] Setup auto-renewal via cron
  - [ ] Section 4: nginx Configuration
    - [ ] Create nginx.conf with SSL/TLS settings
    - [ ] Setup reverse proxy: frontend at / → :3000, backend at /api → :8000
    - [ ] HTTP → HTTPS redirect
    - [ ] Security headers (via nginx or backend)
    - [ ] Gzip compression
  - [ ] Section 5: docker-compose.prod.yml
    - [ ] Production service definitions (ENV=production for backend)
    - [ ] Volume mounts for Let's Encrypt certificates
    - [ ] Network configuration
    - [ ] Resource limits (memory, CPU)
  - [ ] Section 6: Deployment Steps
    - [ ] Build images
    - [ ] Configure environment variables
    - [ ] Start services via docker-compose
    - [ ] Verify HTTPS working
  - [ ] Section 7: Monitoring & Maintenance
    - [ ] Log access (nginx)
    - [ ] Health checks
    - [ ] Certificate renewal verification

- [ ] Create SECURITY.md checklist
  - [ ] Pre-deployment security checklist items:
    - [ ] Environment variables properly set (no development defaults)
    - [ ] Secrets not committed to repository
    - [ ] CORS restricted to production domain only
    - [ ] Rate limiting enabled
    - [ ] Error masking enabled (ENV=production)
    - [ ] Security headers present (X-Content-Type-Options, X-Frame-Options, etc.)
    - [ ] HTTPS/TLS certificate valid
    - [ ] Certificate renewal automated
  - [ ] Runtime security items:
    - [ ] Regular log review
    - [ ] Rate limit monitoring
    - [ ] Error monitoring and alerting
  - [ ] Post-deployment validation
    - [ ] Run security header tests (curl -I https://yourdomain.com)
    - [ ] Verify HTTPS redirect working
    - [ ] Run automated accessibility audit
    - [ ] Load test with realistic traffic patterns

- [ ] Create docker-compose.prod.yml
  - [ ] Define backend service
    - [ ] Image built from production Dockerfile
    - [ ] Environment: ENV=production, ALLOWED_ORIGINS, RATE_LIMIT_PER_MINUTE=30
    - [ ] Restart policy: always
    - [ ] Resource limits
    - [ ] Health check
  - [ ] Define frontend service
    - [ ] Image built from production build
    - [ ] Environment: API_URL=https://yourdomain.com/api
    - [ ] Restart policy: always
    - [ ] Resource limits
  - [ ] Define nginx service
    - [ ] Image: nginx:latest
    - [ ] Ports: 80 and 443
    - [ ] Volumes: nginx.conf, certificates
    - [ ] Depends on: backend and frontend services
  - [ ] Volumes for certificates and logs
  - [ ] Network configuration for service-to-service communication

- [ ] Create example nginx.conf
  - [ ] HTTP server block that redirects to HTTPS
  - [ ] HTTPS server block with TLS settings
  - [ ] SSL certificate and key paths
  - [ ] upstream definitions for backend and frontend
  - [ ] Proxy settings (timeouts, headers)
  - [ ] Gzip compression
  - [ ] Example location blocks for / and /api

- [ ] Update main README
  - [ ] Add link to DEPLOYMENT.md
  - [ ] Add link to SECURITY.md
  - [ ] Add quick-start deployment command

- [ ] Verify documentation completeness
  - [ ] Follow DEPLOYMENT.md steps and verify all work as documented
  - [ ] Check SECURITY.md checklist covers all pre-deployment items
  - [ ] Review for clarity and completeness by non-author reader
  - [ ] Verify no hardcoded values or secrets in example files

---

## Dev Notes

**Architecture Context:**
Production deployment requires multiple layers of security:
1. Network layer: HTTPS/TLS with valid certificates
2. Reverse proxy layer: nginx handling SSL termination, routing, security headers
3. Application layer: environment-based config, error masking, rate limiting (Stories 3-1 through 3-4)

This story documents the infrastructure pieces that support Stories 3-1 through 3-4 in production.

**Key Patterns:**
- HTTPS should be enforced (HTTP → HTTPS redirect)
- Certificates should be auto-renewed (certbot with cron)
- Environment variables should be kept in docker-compose.prod.yml or external secret manager
- Logging should be centralized for security monitoring
- Health checks should be in place for automated failover

**Dependencies:**
- nginx (reverse proxy)
- certbot and Let's Encrypt (TLS certificates)
- docker-compose (orchestration)
- No code changes required for this story

**Related Stories:**
- Story 3-1 (Backend environment setup) — provides config needed for production
- Story 3-2 (Frontend environment setup) — provides config needed for production
- Story 3-3 (CORS Hardening) — configured per environment
- Story 3-4 (Error Masking) — configured per environment

**Files Created:**
- `DEPLOYMENT.md` — complete deployment guide
- `SECURITY.md` — security checklist
- `docker-compose.prod.yml` — production orchestration
- `nginx.conf.example` — nginx configuration template

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
- DEPLOYMENT.md
- SECURITY.md
- docker-compose.prod.yml
- nginx.conf.example

**Modified Files:**
- README.md (add links to deployment docs)

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
