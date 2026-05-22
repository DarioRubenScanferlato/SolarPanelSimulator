---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9]
lastStep: 9
status: 'complete'
completedAt: '2026-05-22'
updatedAt: '2026-05-22'
updateReason: 'Security Architecture addition — environment management, CORS hardening, rate limiting, error masking'
inputDocuments:
  - .claude/artifacts/prd-solar-simulator.md
  - .claude/artifacts/product-brief-solar-simulator.md
  - _bmad-output/project-context.md
  - Security Review Report (2026-05-22)
workflowType: 'architecture'
project_name: 'bmad-solar-panels'
user_name: 'Dario'
date: '2026-05-22'
securityArchitectureVersion: '1.0'
---

# Architecture Decision Document — Solar Panel Simulator

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (current — 8 FRs):**
- FR-1 to FR-8: simulation pipeline, sunrise/sunset, daily/yearly charts, result cards, parameter form, defaults, 8-step irradiance model
- Validated within ±6% of PVGIS for Turin 4 kWp reference case

**Planned extensions (driving this architecture session):**
- Battery simulation: capture/discharge cycle modelling on top of existing generation output
- Frontend modularisation: split app.js into charts.js, api.js, forms.js (and potentially battery-specific modules)

**Non-Functional Requirements:**
- Graph update <1s; page load <2s; simulate <500ms
- Calculation accuracy ±10% PVGIS
- No persistence, no authentication, no real-time streaming
- Backend test coverage >80%; frontend Jest coverage target 80%+

**Scale & Complexity:**
- Primary domain: full-stack web, calculation-heavy Python backend
- Complexity level: low-medium (POC/demo scope)
- Estimated architectural components: 3 backend modules (calc engine + battery module + API layer), 4–5 frontend modules

### Technical Constraints & Dependencies

- Vanilla JS only — no framework (React, Vue, etc.) by project decision
- Python FastAPI + Pydantic for backend validation and response schemas
- Chart.js for visualisations
- Docker Compose orchestration — new deps require image rebuild
- pytest + pytest-cov (backend); Jest (frontend, in progress)

## Technology Foundation

### Primary Technology Domain

Full-stack web application — extending an existing codebase (brownfield). No new project initialisation required.

### Existing Stack (locked — do not change)

**Frontend:**
- Vanilla JavaScript (ES6 modules) — no framework by design decision
- HTML5 / plain CSS
- Chart.js for data visualisation
- Fetch API for backend communication

**Backend:**
- Python 3.11 + FastAPI
- Pydantic v2 for request/response validation
- pytest + pytest-cov (>80% coverage gate)
- UV for dependency management

**Infrastructure:**
- Docker Compose (frontend served via nginx or static file server; backend via uvicorn)
- Ruff linter + prek git hooks

### Target Module Structure (post-refactor)

**Backend (`backend/app/`):**
- `solar_position.py` — NOAA algorithm (existing)
- `irradiance.py` — Kasten-Young + Laue + Erbs + transposition (existing)
- `calculator.py` — orchestration + temperature derating (existing)
- `battery.py` — battery simulation module (new)
- `main.py` — FastAPI routes (extend for battery)
- `models.py` — Pydantic schemas (extend for battery)

**Frontend (`frontend/`):**
- `index.html` — single page shell
- `app.js` — entry point + initialisation only (refactored)
- `api.js` — fetch calls and error handling (new module)
- `charts.js` — Chart.js lifecycle: daily, yearly, battery charts (new module)
- `forms.js` — form state, defaults, validation display (new module)
- `battery.js` — battery input section + results display (new module)

**Note:** Frontend refactor (app.js → modules) is a pre-condition for battery UI and should be its own story completed before battery simulation is built.

---

## Core Architectural Decisions

### Decision Priority Analysis

**Critical (block implementation):**
- API contract extension strategy
- Battery physics model scope
- UI layout pattern (tabs)

**Important (shape architecture):**
- Frontend module system
- Battery chart placement

**Deferred (post-MVP):**
- Cost analysis implementation (placeholder tab only)
- Real weather API integration

---

### API & Communication Patterns

**Decision: Extend `/simulate` with optional battery fields**
- `SolarInput` gains optional battery parameters (`battery_capacity_kwh`, `battery_charge_efficiency`, `battery_discharge_efficiency`, `daily_load_kwh`, `initial_soc_pct`). All default to `None`.
- `SolarOutput` gains optional battery result fields (`battery_hourly_soc`, `self_consumption_pct`, `grid_export_kwh`, `grid_import_kwh`). Present only when battery inputs are provided.
- Backwards compatible: existing frontend calls without battery fields continue to work.
- Rationale: single endpoint, simpler client, consistent with POC scope.

**Error handling:** 422 if battery params are partially provided (all-or-none validation).

---

### Battery Simulation Model

**Decision: Simple hourly energy balance**

Inputs (all optional on `SolarInput`):

| Field | Type | Description |
|---|---|---|
| `battery_capacity_kwh` | float ≥ 0.5 | Usable battery capacity |
| `battery_charge_efficiency` | float 0.5–1.0 | Charge efficiency (default 0.95) |
| `battery_discharge_efficiency` | float 0.5–1.0 | Discharge efficiency (default 0.95) |
| `daily_load_kwh` | float ≥ 0 | Flat daily household load, distributed across 07:00–23:00 |
| `initial_soc_pct` | float 0–100 | Starting state of charge (default 50%) |

Simulation loop (per hour):
```
net = generation[h] - load[h]
if net > 0:  # surplus → charge battery
    soc[h] = min(capacity, soc[h-1] + net × charge_eff)
    grid_export[h] = net - (soc[h] - soc[h-1]) / charge_eff
else:  # deficit → discharge battery
    discharge = min(-net, soc[h-1] × discharge_eff)
    soc[h] = soc[h-1] - discharge / discharge_eff
    grid_import[h] = max(0, -net - discharge)
```

Outputs added to `SolarOutput`:
- `battery_hourly_soc`: `List[float]` — 24 hourly SoC values (kWh)
- `self_consumption_pct`: `float` — % of generation consumed directly or via battery
- `grid_export_kwh`: `float` — daily total exported to grid
- `grid_import_kwh`: `float` — daily total imported from grid

Backend module: `backend/app/battery.py`

---

### Frontend Architecture

**Decision: ES6 native modules via `<script type="module">`**
No bundler, no build step. Each file is a standard ES6 module imported directly by the browser.

**Decision: Tab-based UI layout (3 tabs)**

| Tab | Label | Status | Content |
|---|---|---|---|
| 1 | Solar Simulation | Active (existing) | Solar parameter form + result cards + daily chart + yearly chart |
| 2 | Battery Simulation | New | Battery parameter form + SoC chart + battery result cards |
| 3 | Cost Analysis | Placeholder | Static "coming soon" panel |

Tab switching: pure CSS/JS, no router. Active tab class toggled on click.

**Frontend module breakdown:**

| File | Responsibility |
|---|---|
| `app.js` | Entry point: initialise tabs, wire up modules, bootstrap on DOMContentLoaded |
| `api.js` | `simulateSolar(payload)` → POST /simulate; error normalisation |
| `forms.js` | Load defaults, read solar form values, show/clear field errors |
| `charts.js` | Create/update daily line chart + yearly bar chart (solar tab) |
| `battery-forms.js` | Read battery form values, show/clear battery field errors |
| `battery-charts.js` | Create/update hourly SoC line chart (battery tab) |
| `tabs.js` | Tab switching: show/hide panels, manage active state |

**Dependency graph (no circular imports):**
```
app.js
  ├── tabs.js
  ├── forms.js         → api.js → (fetch)
  ├── charts.js
  ├── battery-forms.js → api.js
  └── battery-charts.js
```

---

### Infrastructure & Deployment

No changes to Docker Compose or deployment. `battery.py` is added inside the existing backend image — no new services, ports, or dependencies beyond the Python standard library.

---

## Security Architecture

### Overview

Security is integrated at three levels: **configuration & environment isolation**, **runtime protection**, and **deployment hardening**. All improvements maintain zero-dependency overhead and preserve the project's lightweight footprint.

---

### 1. Environment Management System

**Decision: Three-environment strategy with .env files and environment-aware configuration**

All sensitive and environment-specific values are moved from hardcoded strings to configuration loaded at startup.

**Backend (Python) — `python-dotenv`:**

Create `backend/.env.example` (committed to repo, no secrets):
```
# Environment
ENV=development

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# API Server
BACKEND_URL=http://localhost:8000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
```

Create `backend/.env.local` (NOT committed, local development):
```
ENV=development
ALLOWED_ORIGINS=http://localhost:3000
BACKEND_URL=http://localhost:8000
RATE_LIMIT_PER_MINUTE=10
```

Create `backend/.env.production` (deployment, NOT committed):
```
ENV=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
BACKEND_URL=https://api.yourdomain.com
RATE_LIMIT_PER_MINUTE=30
```

**Implementation in `main.py`:**
```python
from dotenv import load_dotenv
import os

# Load .env file (local development) or use env vars (production/Docker)
load_dotenv()

ENV = os.getenv("ENV", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
```

**Frontend (JavaScript) — `.env.local` and build-time replacement:**

Create `frontend/.env.example`:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

Create `frontend/.env.local`:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

**Implementation in `api.js`:**
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function simulateSolar(payload) {
    const response = await fetch(`${API_BASE_URL}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    // ... rest of function
}
```

**Docker integration:**

Update `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -U pip uv && uv sync
# Copy production env or create default
COPY .env.production .env
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Update `docker-compose.yml`:
```yaml
services:
  backend:
    build: ./backend
    environment:
      - ENV=docker
      - ALLOWED_ORIGINS=http://frontend:3000,http://localhost:3000
    ports:
      - "8000:8000"
```

**Dependencies to add:**
- `python-dotenv==1.0.0` in `pyproject.toml` dev dependencies

---

### 2. CORS Configuration Hardening

**Decision: Environment-based CORS with explicit method and header allowlists**

Replace hardcoded CORS config in `main.py`:

**Before (vulnerable):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # ❌ Too permissive
    allow_headers=["*"],  # ❌ Too permissive
)
```

**After (hardened):**
```python
from fastapi.middleware.cors import CORSMiddleware
import os

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
is_production = os.getenv("ENV") == "production"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,  # Set True only if authentication is added
    allow_methods=["POST", "GET"],  # Explicit methods only
    allow_headers=["Content-Type"],  # Explicit headers only
    allow_origin_regex=None if not is_production else None,  # No wildcard regex
    max_age=600,  # Cache preflight for 10 minutes
)
```

**Environment examples:**

| Environment | ALLOWED_ORIGINS | Notes |
|---|---|---|
| Development | `http://localhost:3000,http://127.0.0.1:3000` | Local development |
| Docker Compose | `http://frontend:3000,http://localhost:3000` | Container networking |
| Production | `https://yourdomain.com,https://www.yourdomain.com` | HTTPS only |

---

### 3. Rate Limiting on `/simulate` Endpoint

**Decision: Per-IP rate limiting using `slowapi` library**

Prevents DOS and runaway client requests.

**Implementation:**

Add to `pyproject.toml`:
```toml
dependencies = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "pydantic==2.5.0",
    "slowapi==0.1.9",  # NEW
    "python-dotenv==1.0.0",  # NEW
]
```

Update `backend/app/main.py`:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

@app.post("/simulate", response_model=SolarOutput, tags=["simulation"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def simulate_solar_system(request: Request, input_data: SolarInput):
    """Simulate solar panel energy production (rate-limited per IP)."""
    validation_errors = validate_input(input_data)
    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail=[{"field": e.field, "message": e.message} for e in validation_errors],
        )
    try:
        result = simulate(input_data)
        return result
    except Exception as e:
        error_msg = str(e) if os.getenv("ENV") != "production" else "Simulation failed"
        raise HTTPException(status_code=500, detail=error_msg)
```

**Rate limit by environment:**

| Environment | Limit | Purpose |
|---|---|---|
| Development | 10/min | Accommodate rapid iteration |
| Docker Compose | 20/min | Local testing |
| Production | 30/min | Reasonable daily-use ceiling; generous for education/demo |

---

### 4. Error Handling Masking for Production

**Decision: Expose internal errors in development, mask in production**

Prevents information leakage while maintaining debuggability.

**Implementation in `main.py`:**

```python
import os

IS_PRODUCTION = os.getenv("ENV") == "production"

@app.post("/simulate", response_model=SolarOutput, tags=["simulation"])
async def simulate_solar_system(input_data: SolarInput):
    """Simulate solar panel energy production."""
    validation_errors = validate_input(input_data)
    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail=[{"field": e.field, "message": e.message} for e in validation_errors],
        )
    try:
        result = simulate(input_data)
        return result
    except Exception as e:
        # Log the full error server-side for debugging
        import logging
        logging.error(f"Simulation error: {str(e)}", exc_info=True)
        
        # Return masked error to client in production
        if IS_PRODUCTION:
            detail = "Simulation failed. Please try again."
        else:
            detail = f"Simulation error: {str(e)}"
        
        raise HTTPException(status_code=500, detail=detail)
```

**Logging setup (optional but recommended):**

Add to `pyproject.toml`:
```toml
dependencies = [
    ...
    "python-json-logger==2.0.7",  # Structured logging
]
```

Create `backend/app/logging_config.py`:
```python
import logging
import os
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    if os.getenv("ENV") == "production":
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)

setup_logging()
```

---

### 5. Security Headers Middleware

**Decision: Add HTTP security headers to all responses**

Mitigates XSS, clickjacking, and other browser-based attacks.

**Implementation in `main.py`:**

```python
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Header explanations:**

| Header | Value | Purpose |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Enable XSS protection |
| `Strict-Transport-Security` | `max-age=31536000` | Force HTTPS (enable after TLS setup) |

---

### 6. HTTPS/TLS Setup (Production)

**Decision: Use Let's Encrypt + nginx reverse proxy for HTTPS**

This is deployment-specific, not code changes, but critical for production.

**Architecture (production):**

```
[User Browser]
         ↓ HTTPS (443)
    [nginx Reverse Proxy] ← TLS termination, Let's Encrypt cert
         ↓ HTTP (8000, internal only)
    [FastAPI Backend]
```

**Docker Compose update for production (`docker-compose.prod.yml`):**

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro  # Mount SSL certificates
    depends_on:
      - backend
    environment:
      - VIRTUAL_HOST=yourdomain.com

  backend:
    build: ./backend
    environment:
      - ENV=production
      - ALLOWED_ORIGINS=https://yourdomain.com
    expose:
      - "8000"
    # No ports exposed — nginx proxies internally
```

**nginx.conf (HTTPS reverse proxy):**

```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;  # Redirect HTTP → HTTPS
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Certificate setup (Let's Encrypt via Certbot):**

```bash
docker run --rm -it \
  -v /path/to/certs:/etc/letsencrypt \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d yourdomain.com -d www.yourdomain.com
```

---

### Security Checklist for Implementation

**Before Production Launch:**

- [ ] `.env.example` committed; `.env.local` and `.env.production` in `.gitignore`
- [ ] CORS configured from `ALLOWED_ORIGINS` env var
- [ ] API URLs moved to `REACT_APP_API_URL` (frontend) and `BACKEND_URL` (backend)
- [ ] Rate limiting active on `/simulate` endpoint
- [ ] Error messages masked in production
- [ ] Security headers middleware added to all responses
- [ ] HTTPS configured with valid TLS certificates
- [ ] `Strict-Transport-Security` header enabled
- [ ] Dependencies added: `slowapi`, `python-dotenv`, optionally `python-json-logger`
- [ ] Docker Compose updated with environment injection
- [ ] No hardcoded secrets in any committed file
- [ ] `npm audit` and `pip-audit` pass

---

### Security Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  User Browser (HTTPS)                                       │
│  - Fetches from REACT_APP_API_URL env var                   │
│  - No hardcoded URLs                                         │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS (TLS)
┌────────────────▼────────────────────────────────────────────┐
│  nginx Reverse Proxy                                         │
│  - TLS termination (Let's Encrypt)                           │
│  - HTTP → HTTPS redirect                                     │
│  - Rate limiting via nginx (optional layer)                  │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP (internal only)
┌────────────────▼────────────────────────────────────────────┐
│  FastAPI Backend                                             │
│  ├─ Environment Config (python-dotenv)                       │
│  │  ├─ ALLOWED_ORIGINS (CORS)                               │
│  │  ├─ RATE_LIMIT_PER_MINUTE                                │
│  │  └─ ENV (development|production)                         │
│  ├─ CORS Middleware (explicit methods/headers)              │
│  ├─ Rate Limiting Middleware (slowapi)                      │
│  ├─ Security Headers Middleware                             │
│  └─ Error Handling (masked in production)                   │
│                                                              │
│  POST /simulate                                              │
│  ├─ Rate limit: 10/min (dev), 30/min (prod)                │
│  ├─ Validate input (Pydantic)                               │
│  ├─ Execute simulation                                       │
│  └─ Mask errors in production                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Testing Architecture

### Overview

Testing spans three layers: **unit tests** (module behavior), **integration tests** (API contracts), and **E2E tests** (user workflows). All tests are isolated, deterministic, and require zero external dependencies.

---

### 1. Unit Testing Strategy

**Backend (pytest):**

Coverage target: **≥80% per module** (currently 95% across all backend modules).

**Existing coverage:**
- `solar_position.py`: 95%
- `irradiance.py`: 95%
- `calculator.py`: 90%
- `models.py`: 100%
- `validation.py`: 100%

**New modules must maintain 80%+:**
- `battery.py`: target 90%+ (physics-heavy, requires comprehensive edge cases)
- Any new modules added

**Test patterns:**

```python
# test_battery.py
import pytest
from app.battery import simulate_battery, calculate_hourly_soc

class TestCalculateHourlySoc:
    """Test hourly state-of-charge calculation."""
    
    @pytest.fixture
    def base_params(self):
        return {
            "capacity_kwh": 10.0,
            "charge_efficiency": 0.95,
            "discharge_efficiency": 0.95,
            "daily_load_kwh": 5.0,
            "initial_soc_pct": 50.0
        }
    
    def test_zero_capacity_passthrough(self):
        """Battery with zero capacity should pass all generation to grid."""
        generation = [1.0, 2.0, 1.5]
        result = calculate_hourly_soc(
            generation, capacity_kwh=0, charge_eff=0.95, discharge_eff=0.95, 
            load=[1.0, 1.0, 1.0], initial_soc=0
        )
        # Assert no charging possible; all generation exported
        assert all(soc == 0 for soc in result['soc'])
    
    def test_soc_never_negative(self, base_params):
        """SoC must never go negative (discharge limited by available capacity)."""
        high_load = [10.0] * 24  # Exceeds capacity
        generation = [0.5] * 24  # Minimal generation
        result = calculate_hourly_soc(
            generation, load=high_load, **base_params
        )
        assert all(soc >= 0 for soc in result['soc'])
    
    def test_soc_never_exceeds_capacity(self, base_params):
        """SoC must never exceed battery capacity."""
        high_generation = [10.0] * 24  # Abundant
        zero_load = [0.0] * 24
        result = calculate_hourly_soc(
            high_generation, load=zero_load, **base_params
        )
        assert all(soc <= base_params['capacity_kwh'] for soc in result['soc'])
    
    def test_efficiency_losses(self):
        """Charge/discharge efficiency should reduce round-trip energy."""
        generation = [2.0] * 24
        load = [0.5] * 24  # Charge: 1.5 * 0.95 = 1.425, Discharge: 1.425 * 0.95 = 1.35
        result = calculate_hourly_soc(
            generation, load=load, capacity_kwh=10, 
            charge_eff=0.95, discharge_eff=0.95, initial_soc=5
        )
        # Verify losses accumulate
        # (Detailed assertion depends on simulation logic)
```

**Frontend (Jest):**

Coverage target: **≥80% per module** (currently: api.js 100%, forms.js 100%, charts.js 100%, tabs.js 100%).

Test isolation via jsdom + mocks:
- `Canvas` mock prevents rendering errors
- `Chart.js` mock prevents real chart instantiation
- `fetch` global mock for API testing

```javascript
// __tests__/battery-forms.test.js
describe('battery-forms.js', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <form id="batteryForm">
        <input id="battery-capacity" name="battery_capacity_kwh" value="">
        <input id="daily-load" name="daily_load_kwh" value="">
        <span class="error"></span>
      </form>
    `;
  });

  test('readBatteryForm collects form values', () => {
    const { readBatteryForm } = require('../battery-forms.js');
    document.getElementById('battery-capacity').value = 10;
    document.getElementById('daily-load').value = 5;
    
    const data = readBatteryForm();
    
    expect(data.battery_capacity_kwh).toBe(10);
    expect(data.daily_load_kwh).toBe(5);
  });
  
  test('showBatteryFieldError displays error with show class', () => {
    const { showBatteryFieldError } = require('../battery-forms.js');
    
    showBatteryFieldError('battery-capacity', 'Capacity must be > 0');
    
    const errorSpan = document.querySelector('.error');
    expect(errorSpan.textContent).toBe('Capacity must be > 0');
    expect(errorSpan.classList.contains('show')).toBe(true);
  });
});
```

**Test Commands:**

```bash
# Backend
pytest --cov=app --cov-report=html  # Unit + integration
pytest tests/test_battery.py -v     # Single module
pytest -k "TestBattery" -v          # Test class

# Frontend
npm test                            # All Jest tests
npm test -- --coverage             # Coverage report
npm test -- api.test.js            # Single file
npm test -- --watch                # Watch mode
```

---

### 2. Integration Testing Strategy

**Backend API Integration Tests (`test_main.py`):**

Test full request/response cycle via FastAPI TestClient.

```python
# test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSimulateEndpoint:
    """Test /simulate endpoint with rate limiting, validation, errors."""
    
    def test_successful_solar_simulation(self):
        """Valid solar input returns SolarOutput with all fields."""
        payload = {
            "latitude": 45.0703,
            "longitude": 7.6869,
            "panel_count": 10,
            "panel_area_m2": 2.0,
            "panel_efficiency": 20,
            "tilt_angle_deg": 35,
            "azimuth_deg": 180,
            "start_date": "2026-05-22",
            "duration_days": 365
        }
        response = client.post("/simulate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "annual_energy_kwh" in data
        assert "daily_hourly_generation" in data
        assert len(data["daily_hourly_generation"]) == 24
    
    def test_validation_error_returns_422(self):
        """Invalid latitude returns 422 with field-level errors."""
        payload = {
            "latitude": 95,  # Invalid: > 90
            "longitude": 7.6869,
            # ... rest of fields
        }
        response = client.post("/simulate", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert any(e["field"] == "latitude" for e in data["detail"])
    
    def test_rate_limiting(self):
        """Requests exceeding rate limit return 429."""
        payload = { ... }  # Valid
        
        # Make requests up to limit
        for i in range(11):  # Assuming 10/minute limit
            response = client.post("/simulate", json=payload)
            if i < 10:
                assert response.status_code == 200
            else:
                assert response.status_code == 429  # Too Many Requests
    
    def test_cors_headers_present(self):
        """CORS headers included in all responses."""
        response = client.get("/health")
        
        assert "access-control-allow-origin" in response.headers.lower()
        assert "access-control-allow-methods" in response.headers.lower()
    
    def test_security_headers_present(self):
        """Security headers included in all responses."""
        response = client.get("/health")
        
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert "X-XSS-Protection" in response.headers
```

**Frontend Integration Tests (Selenium/Playwright for browser flow, separate from Jest):**

Covered in E2E section below.

---

### 3. End-to-End Testing with Playwright

**Purpose:** Verify complete user workflows in a real browser without mocks.

**Setup:**

Add to `frontend/package.json`:
```json
{
  "devDependencies": {
    "@playwright/test": "^1.40.0"
  }
}
```

Install: `npm install --save-dev @playwright/test`

**Playwright Configuration (`frontend/playwright.config.ts`):**

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
});
```

**E2E Test Patterns (`frontend/e2e/solar-simulation.spec.ts`):**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Solar Simulation E2E', () => {
  test('User can load page, fill form, simulate, and view results', async ({ page }) => {
    // Navigate
    await page.goto('/');
    
    // Wait for page to load
    await expect(page.locator('#simulatorForm')).toBeVisible();
    
    // Verify defaults are loaded
    const latitudeInput = page.locator('#latitude');
    await expect(latitudeInput).toHaveValue('45.0703');
    
    // Modify form
    await page.locator('#panelCount').fill('15');
    await page.locator('#efficiency').fill('22');
    
    // Mock backend response
    await page.route('**/simulate', route => {
      route.abort('blockedbyapp'); // or mock response
    });
    
    // Submit form
    const simulateBtn = page.locator('#simulateBtn');
    await simulateBtn.click();
    
    // Verify loading state
    await expect(simulateBtn).toBeDisabled();
    await expect(simulateBtn).toContainText('Simulating');
    
    // Wait for results
    await page.waitForSelector('#resultsSection:not([style*="display: none"])');
    
    // Verify result cards are populated
    await expect(page.locator('#annualEnergy')).not.toHaveText('0');
    
    // Verify charts exist
    await expect(page.locator('#dailyChart')).toBeVisible();
    await expect(page.locator('#yearlyChart')).toBeVisible();
    
    // Verify button is restored
    await expect(simulateBtn).toBeEnabled();
    await expect(simulateBtn).toContainText('Simulate');
  });

  test('User receives validation error on invalid input', async ({ page }) => {
    await page.goto('/');
    
    await page.locator('#latitude').fill('95');  // Invalid
    await page.locator('#simulateBtn').click();
    
    // Verify error displayed
    const latitudeError = page.locator('#latitude').locator('+ .error');
    await expect(latitudeError).toContainText('Latitude must be between');
  });

  test('Tab switching maintains form state', async ({ page }) => {
    await page.goto('/');
    
    // Fill solar form
    await page.locator('#panelCount').fill('12');
    
    // Switch to battery tab
    await page.locator('[data-tab="battery"]').click();
    
    // Verify battery tab visible
    await expect(page.locator('#panel-battery')).not.toHaveAttribute('hidden');
    
    // Switch back to solar
    await page.locator('[data-tab="solar"]').click();
    
    // Verify form value persisted
    await expect(page.locator('#panelCount')).toHaveValue('12');
  });
});
```

**E2E Test Commands:**

```bash
npm run test:e2e              # Run all E2E tests
npm run test:e2e --headed    # Visual browser
npm run test:e2e --debug     # Debug mode
npx playwright codegen http://localhost:3000  # Record test
```

---

### 4. Test Coverage Gates

**Backend (`pyproject.toml`):**

```toml
[tool.coverage.run]
source = ["app"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
fail_under = 80
```

**Frontend (`jest.config.js`):**

```javascript
coverageThreshold: {
  global: {
    statements: 70,
    branches: 50,
    functions: 70,
    lines: 70
  }
}
```

**CI/CD Check:**

Both test suites must pass with coverage before PR merge:
```bash
# Backend
pytest --cov=app --cov-fail-under=80

# Frontend
npm test -- --coverage
```

---

## Accessibility Architecture

### Overview

WCAG 2.1 Level AA compliance required. Accessibility is tested via:
1. **Automated scanning** (axe-core, Lighthouse)
2. **Manual testing** (keyboard navigation, screen reader)
3. **CI integration** (failed accessibility = failed PR)

---

### 1. Semantic HTML & ARIA

**Principles:**

- Use semantic HTML: `<button>`, `<form>`, `<label>`, `<fieldset>`, `<nav>`, `<main>`, `<section>`, `<article>`
- Never use `<div>` with `click` handler — use `<button>` or `<a>`
- All form inputs must have `<label>` with matching `for` attribute
- Tab structure uses semantic `<nav>` and `<button>` elements

**Current State (good):**

```html
<!-- Good: semantic elements, proper structure -->
<nav class="tab-nav" role="tablist">
  <button class="tab-btn tab-active" data-tab="solar" role="tab" aria-selected="true">
    Solar Simulation
  </button>
  <button class="tab-btn" data-tab="battery" role="tab" aria-selected="false">
    Battery Simulation
  </button>
</nav>

<main>
  <form id="simulatorForm">
    <fieldset>
      <legend>Solar Panel Parameters</legend>
      <div class="form-group">
        <label for="latitude">Latitude</label>
        <input id="latitude" name="latitude" type="number" min="-90" max="90" required>
        <span class="error" role="alert"></span>
      </div>
    </fieldset>
  </form>
</main>
```

**Accessibility improvements needed:**

- [ ] Add `role="tablist"` to tab nav, `role="tab"` to buttons
- [ ] Add `aria-selected` to tab buttons (toggle on click)
- [ ] Add `aria-label` to icon-only buttons (if any)
- [ ] Add `role="alert"` to error messages (for screen readers)
- [ ] Ensure form labels have `for` attribute matching input `id`
- [ ] Add `aria-live="polite"` to results section (announces updates)
- [ ] Charts: add `role="img"` and `aria-label` with text description

**Chart Accessibility:**

```html
<!-- Chart with aria-label describing the visualization -->
<div role="img" aria-label="Daily solar generation by hour: peak at 13:00 with 2.5 kW, sunrise at 03:18, sunset at 19:33">
  <canvas id="dailyChart"></canvas>
</div>
```

---

### 2. Keyboard Navigation

**Requirements:**

- All interactive elements must be keyboard accessible
- Tab order follows logical reading order (top to bottom, left to right)
- No keyboard traps (user can always escape)
- Focus must be visible (outline or highlight)

**Testing (manual):**

```
Tab through page:
  1. Tab focuses "Solar" tab button
  2. Tab focuses "Battery" tab button
  3. Tab focuses "Cost Analysis" tab button
  4. Tab focuses first form input (latitude)
  5. ... cycle through all form inputs
  6. Tab focuses "Simulate" button
  7. Tab cycles back to first element

Arrow keys (for tab navigation):
  Left/Right arrow switches active tab
  Enter/Space activates tab or submits form
```

**Implementation in `tabs.js`:**

```javascript
export function setupTabKeyboard() {
  document.querySelectorAll('[role="tab"]').forEach((tab, index) => {
    tab.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
        const prev = tabs[(index - 1 + tabs.length) % tabs.length];
        prev.focus();
        switchTab(prev.getAttribute('data-tab'));
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
        const next = tabs[(index + 1) % tabs.length];
        next.focus();
        switchTab(next.getAttribute('data-tab'));
      }
    });
  });
}
```

---

### 3. Color Contrast & Visual Design

**WCAG AA Requirements:**

- **Normal text:** ≥4.5:1 contrast ratio
- **Large text** (18pt+ or 14pt bold): ≥3:1 contrast ratio
- **Interactive elements:** ≥3:1 against adjacent colors

**Current Style Review:**

```css
/* Good: sufficient contrast */
.tab-btn {
  color: #333;          /* Dark text */
  background: #f5f5f5;  /* Light background */
  /* Ratio: ~7:1, exceeds 4.5:1 */
}

.tab-btn.tab-active {
  color: white;
  background: #667eea;  /* Purple */
  /* Verify ratio: white (#fff) on #667eea = ~4.7:1, meets AA */
}

/* Bad: insufficient contrast */
.error {
  color: #ff6b6b;       /* Red on white = ~3.1:1, fails AA for normal text */
}

/* Good: sufficient contrast */
.error {
  color: #d32f2f;       /* Darker red on white = ~4.8:1, passes AA */
}
```

**Tools:**

- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Lighthouse in Chrome DevTools (audit tab)

---

### 4. Screen Reader Compatibility

**Testing with NVDA (free, Windows) or VoiceOver (Mac/iOS):**

**Checklist:**

- [ ] Form labels announced correctly
- [ ] Error messages announced with alert role
- [ ] Chart descriptions announced via aria-label
- [ ] Tab buttons announce current/selected state
- [ ] Results section announces updates with aria-live
- [ ] Button purposes are clear from text alone (no icon-only buttons)

**Example ARIA roles for Solar Simulator:**

```html
<form id="simulatorForm" aria-label="Solar simulation parameters">
  <fieldset>
    <legend>System Configuration</legend>
    <div class="form-group">
      <label for="panelCount">Number of Panels</label>
      <input id="panelCount" name="panelCount" type="number" min="1" required>
      <span class="error" role="alert"></span>
    </div>
  </fieldset>
</form>

<div id="resultsSection" aria-live="polite" aria-label="Simulation results">
  <div id="annualEnergy" role="status">0 kWh</div>
  <!-- Results update announcement via aria-live -->
</div>
```

---

### 5. Automated Accessibility Testing

**Setup with `jest-axe` (frontend):**

Add to `package.json`:
```json
{
  "devDependencies": {
    "jest-axe": "^8.0.0",
    "axe-core": "^4.8.0"
  }
}
```

**Test pattern:**

```javascript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  test('solar form has no accessibility violations', async () => {
    document.body.innerHTML = `
      <form id="simulatorForm">
        <label for="latitude">Latitude</label>
        <input id="latitude" type="number">
      </form>
    `;
    
    const results = await axe(document.body);
    expect(results).toHaveNoViolations();
  });
});
```

**Playwright accessibility testing:**

```typescript
test('page has no accessibility violations', async ({ page }) => {
  await page.goto('/');
  const violations = await page.evaluate(() => {
    // Uses axe-core if injected
    return checkAccessibility();
  });
  expect(violations).toEqual([]);
});
```

**CI Integration:**

```yaml
# .github/workflows/ci.yml
- name: Run accessibility tests
  run: |
    npm test -- --testPathPattern=a11y
    npx axe-core http://localhost:3000
```

---

### 6. Accessibility Checklist

**Before Shipping Any UI Change:**

- [ ] All interactive elements are semantic (`<button>`, `<a>`, `<input>`)
- [ ] All form inputs have `<label>` with `for` attribute
- [ ] Tab order is logical (test with Tab key)
- [ ] Focus is visible (outline or underline)
- [ ] Error messages have `role="alert"`
- [ ] Charts/images have `aria-label` descriptions
- [ ] Color contrast ≥4.5:1 for normal text
- [ ] No keyboard traps
- [ ] Screen reader tested (NVDA, VoiceOver, or JAWS)
- [ ] axe-core scan passes
- [ ] Lighthouse accessibility score ≥90

---

## Environment Management Architecture (Detailed)

### 1. Configuration Hierarchy

**Priority order (highest to lowest):**

1. Runtime environment variables (Docker/CI/CD)
2. `.env.{ENV}` file (git-ignored, environment-specific)
3. `.env.example` defaults (committed, for reference)
4. Fallback hardcoded defaults in code

**Example resolution:**

```python
# backend/main.py
import os
from dotenv import load_dotenv

# Load from .env file if present (development)
load_dotenv()

# Get values with fallbacks
ENV = os.getenv("ENV", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
```

**Result:**
- Docker: reads from environment (`docker run -e ENV=production`)
- Development: reads from `.env.local`
- CI/CD: reads from GitHub Secrets (mapped to env vars)

---

### 2. Environment Definitions

| Environment | Purpose | API_BASE_URL | ALLOWED_ORIGINS | RATE_LIMIT | LOG_LEVEL |
|---|---|---|---|---|---|
| **development** | Local dev | `http://localhost:8000` | `http://localhost:3000` | 10/min | DEBUG |
| **testing** | CI/CD tests | `http://localhost:8000` | `http://localhost:3000` | 100/min | INFO |
| **docker** | Docker Compose | `http://backend:8000` | `http://frontend:3000` | 20/min | INFO |
| **staging** | Pre-production | `https://staging-api.yourdomain.com` | `https://staging.yourdomain.com` | 30/min | INFO |
| **production** | Live | `https://api.yourdomain.com` | `https://yourdomain.com` | 30/min | WARN |

---

### 3. Frontend `.env` Setup

**`.env.example` (committed):**

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0
```

**`.env.local` (NOT committed, local dev):**

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

**`.env.production` (NOT committed, for build):**

```
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_ENV=production
REACT_APP_VERSION=1.0.0
```

**Usage in code:**

```javascript
// api.js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function simulateSolar(payload) {
  const response = await fetch(`${API_URL}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  // ...
}
```

---

### 4. Backend `.env` Setup

**`.env.example` (committed):**

```
# Core
ENV=development
BACKEND_URL=http://localhost:8000

# Security
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
RATE_LIMIT_PER_MINUTE=10

# Logging
LOG_LEVEL=DEBUG
```

**`.env.local` (NOT committed, local dev):**

```
ENV=development
BACKEND_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
RATE_LIMIT_PER_MINUTE=10
LOG_LEVEL=DEBUG
```

**`.env.production` (NOT committed, deployment):**

```
ENV=production
BACKEND_URL=https://api.yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
RATE_LIMIT_PER_MINUTE=30
LOG_LEVEL=WARN
```

**Usage in code:**

```python
# main.py
import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
```

---

### 5. Docker & CI/CD Integration

**Docker Compose (development):**

```yaml
services:
  backend:
    build: ./backend
    environment:
      - ENV=docker
      - ALLOWED_ORIGINS=http://frontend:3000,http://localhost:3000
      - RATE_LIMIT_PER_MINUTE=20
    ports:
      - "8000:8000"
```

**GitHub Actions (CI/CD):**

```yaml
env:
  ENV: testing
  ALLOWED_ORIGINS: http://localhost:3000
  RATE_LIMIT_PER_MINUTE: 100

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest --cov=app
      - run: npm test -- --coverage
```

**Kubernetes/Cloud Deployment (production):**

```yaml
# deployment.yaml
env:
  - name: ENV
    value: "production"
  - name: ALLOWED_ORIGINS
    value: "https://yourdomain.com"
  - name: RATE_LIMIT_PER_MINUTE
    valueFrom:
      configMapKeyRef:
        name: api-config
        key: rate-limit
  - name: DATABASE_URL  # Future: if persistence added
    valueFrom:
      secretKeyRef:
        name: api-secrets
        key: database-url
```

---

### 6. Secrets Management (Future)

When authentication or database is added:

**Backend `.env.example` (public template):**

```
ENV=development
ALLOWED_ORIGINS=http://localhost:3000

# Secrets (never commit actual values)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# SECRET_KEY=your-secret-key-here
# API_KEY=external-api-key
```

**Backend `.env.local` (developer-specific, NOT committed):**

```
DATABASE_URL=postgresql://dev:password@localhost:5432/solardb
SECRET_KEY=dev-secret-key-change-in-production
API_KEY=demo-api-key
```

**CI/CD Secret Injection (GitHub Secrets):**

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

**`.gitignore` (critical):**

```
# Environment files
.env
.env.local
.env.*.local
.env.production
```

---

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Backend (Python) — snake_case throughout:**
- Files: `battery.py`, `solar_position.py`
- Functions: `simulate_battery()`, `calculate_hourly_soc()`
- Pydantic fields: `battery_capacity_kwh`, `self_consumption_pct`
- Test classes: `TestBatterySimulation`; test methods: `test_zero_capacity_passthrough`

**Frontend (JavaScript) — camelCase for variables/functions, kebab-case for files:**
- Files: `battery-forms.js`, `battery-charts.js`, `tabs.js`
- Functions: `loadBatteryDefaults()`, `updateSocChart()`, `switchTab(tabId)`
- DOM IDs: `battery-capacity`, `soc-chart`, `tab-battery` (kebab-case in HTML)
- JS references to DOM: `document.getElementById('battery-capacity')`

**API fields: always snake_case.** Pydantic serialises to snake_case; JS reads snake_case directly — do not convert to camelCase on the frontend.

---

### API Patterns

**Request:** JSON body, all fields snake_case. Battery fields optional — omit entirely when not using battery tab.

**Response:** Direct Pydantic model serialisation — no wrapper envelope. Battery fields present only when battery params were sent:
```json
{
  "annual_energy_kwh": 4987.2,
  "battery_hourly_soc": [2.1, 1.8, ...],
  "self_consumption_pct": 74.3
}
```

**Errors:** FastAPI 422 with `detail` array of `{field, message}` objects. Frontend displays these inline next to the relevant input. Never show raw Pydantic error text.

**All-or-none battery validation:** If any battery field is provided, all required battery fields must be present. Return 422 with a clear message if partial.

---

### Frontend Module Patterns

**ES6 named exports only — no default exports:**
```js
// good
export function loadBatteryDefaults() { ... }
export function readBatteryForm() { ... }

// bad
export default { loadBatteryDefaults, readBatteryForm }
```

**`app.js` imports everything; modules do NOT import each other** (except `battery-forms.js` and `forms.js` may both import `api.js`). No circular dependencies.

**Chart lifecycle — update in place, never destroy/recreate:**
```js
// good
chart.data.datasets[0].data = newValues;
chart.update();

// bad — destroys and recreates on every simulate
chart.destroy();
new Chart(...);
```
Exception: first call (chart not yet initialised) creates the instance and stores reference in module scope.

**Loading state pattern — always disable Simulate and show spinner during fetch:**
```js
simulateBtn.disabled = true;
simulateBtn.textContent = 'Simulating…';
try { ... } finally {
  simulateBtn.disabled = false;
  simulateBtn.textContent = 'Simulate';
}
```

---

### Tab Pattern

Tab panels use `hidden` attribute (not CSS `display`). Active tab button gets class `tab-active`.
```js
// tabs.js — canonical implementation
export function switchTab(tabId) {
  document.querySelectorAll('.tab-panel').forEach(p => p.hidden = true);
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('tab-active'));
  document.getElementById(`panel-${tabId}`).hidden = false;
  document.querySelector(`[data-tab="${tabId}"]`).classList.add('tab-active');
}
```

---

### Backend Patterns

**Calculator functions are pure** — no side effects, no I/O, no global state.

**Battery module follows the same shape as `calculator.py`:**
- One top-level `simulate_battery(solar_output, battery_input)` function
- Sub-functions per step: `calculate_hourly_soc()`, `calculate_self_consumption()`
- All tested in `tests/test_battery.py`

**Test pattern mirrors `test_calculator.py`:**
- Class per function: `class TestCalculateHourlySoc`
- Physical sanity checks (SoC never negative, never exceeds capacity)
- Edge cases: zero capacity, zero load, 100% self-consumption

---

---

## Project Structure & Boundaries

### Complete Project Directory Structure

```
bmad-solar-panels/
├── README.md                          # existing
├── docker-compose.yml                 # existing — orchestrates backend + frontend
│
├── backend/
│   ├── Dockerfile                     # existing — uvicorn-based image
│   ├── pyproject.toml                 # existing — UV deps + ruff + pytest config; add httpx
│   ├── uv.lock                        # existing
│   ├── .coveragerc                    # existing — coverage gate config
│   │
│   ├── app/
│   │   ├── __init__.py                # existing
│   │   ├── constants.py               # existing — shared constants (AMBIENT_TEMP_MEAN_C, etc.)
│   │   ├── solar_position.py          # existing — NOAA: julian_day, sunrise_sunset, hourly_sun_position
│   │   ├── irradiance.py              # existing — Kasten-Young → Erbs → isotropic transposition
│   │   ├── calculator.py              # existing — orchestration: simulate(), calculate_daily_profile()
│   │   ├── battery.py                 # NEW — hourly energy balance: simulate_battery()
│   │   ├── models.py                  # EXTEND — SolarInput + SolarOutput: add optional battery fields
│   │   ├── validation.py              # existing — field-level validators
│   │   └── main.py                    # EXTEND — /simulate route: wire battery.py when battery params present
│   │
│   └── tests/
│       ├── __init__.py                # existing
│       ├── conftest.py                # existing — shared fixtures: default_solar_input, turin_location, etc.
│       ├── test_solar_position.py     # existing — 95% coverage
│       ├── test_irradiance.py         # existing
│       ├── test_calculator.py         # existing
│       ├── test_main.py               # existing — FastAPI TestClient integration tests
│       └── test_battery.py            # NEW — TestBatterySimulation, TestCalculateHourlySoc, edge cases
│
└── frontend/
    ├── Dockerfile                     # existing — nginx static file server
    ├── index.html                     # REWRITE — add 3-tab layout + battery form section
    ├── style.css                      # EXTEND — tab styles + battery section styles
    ├── app.js                         # REFACTOR — entry point only: init tabs, wire modules on DOMContentLoaded
    ├── api.js                         # NEW — simulateSolar(payload) → POST /simulate; error normalisation
    ├── charts.js                      # NEW — daily line chart + yearly bar chart (solar tab)
    ├── forms.js                       # NEW — solar form: load defaults, read values, show/clear errors
    ├── tabs.js                        # NEW — switchTab(tabId): toggle hidden + tab-active class
    ├── battery-forms.js               # NEW — battery form: read values, show/clear errors; imports api.js
    └── battery-charts.js              # NEW — hourly SoC line chart (battery tab)
```

---

### Architectural Boundaries

**API Boundary — single POST `/simulate`:**
- Entry: `backend/app/main.py`
- Request validated by Pydantic: `SolarInput` in `models.py`
- Response serialised by Pydantic: `SolarOutput` in `models.py`
- Battery fields optional — omit entirely for solar-only calls; all-or-none validation on partial battery input (422)
- `validation.py` owns field-range constraints; `main.py` owns the all-or-none battery check

**Component Boundaries — frontend module isolation:**
- `app.js` is the sole orchestrator; imports all other modules
- No circular dependencies — `api.js` may be imported by `forms.js` and `battery-forms.js` only
- `api.js` is the only file allowed to call `fetch()`
- Chart instances live in `charts.js` / `battery-charts.js` module scope; updated in-place, never recreated

**Data Boundaries:**
- No persistence — all data is ephemeral per-request
- Request → Response is the only data flow: JSON body in, JSON body out
- Frontend reads snake_case API fields directly — no camelCase conversion

---

### Requirements → Structure Mapping

| Requirement | File(s) |
|---|---|
| FR-1 Solar generation simulation | `calculator.py`, `models.py` |
| FR-2 Sunrise/sunset | `solar_position.py` |
| FR-3 Daily hourly graph | `charts.js` (frontend), `calculator.py` (backend) |
| FR-4 Yearly graph | `charts.js` (frontend), `calculator.py` (backend) |
| FR-5 Result cards | `app.js` + `forms.js` (DOM updates) |
| FR-6 Interactive parameter form | `forms.js`, `battery-forms.js`, `index.html` |
| FR-7 Placeholder defaults | `forms.js` (loads on DOMContentLoaded) |
| FR-8 Irradiance model | `irradiance.py`, `solar_position.py` |
| Battery simulation (new) | `battery.py`, `models.py`, `battery-forms.js`, `battery-charts.js` |
| 3-tab UI layout | `tabs.js`, `index.html`, `style.css` |
| Cost analysis placeholder | `index.html` (static panel only) |

---

### Integration Points

**Frontend → Backend:**
```
user clicks Simulate
  → forms.js / battery-forms.js reads form values
  → app.js builds payload
  → api.js POST /simulate
  → app.js dispatches results to charts.js + battery-charts.js + DOM card updates
```

**Backend module chain:**
```
main.py (route)
  → calculator.simulate()      → solar_position, irradiance, constants
  → battery.simulate_battery() → called only when battery params present
  → returns SolarOutput (battery fields populated when battery ran)
```

**External integrations:** None (no weather API, no auth, no persistence).

---

### Epic → Story Mapping

**Epic 1 — Frontend Refactor** (pre-condition for battery UI):
- Story 1.1: `index.html` → 3-tab layout + tab switching (`tabs.js`)
- Story 1.2: Extract `api.js` from `app.js`
- Story 1.3: Extract `forms.js` + `charts.js`; `app.js` becomes entry point only

**Epic 2 — Battery Simulation:**
- Story 2.1: `battery.py` + extend `models.py` + extend `main.py` (backend)
- Story 2.2: `battery-forms.js` + `battery-charts.js` + `index.html` battery section (frontend)
- Story 2.3: `test_battery.py` backend tests (>80% coverage gate)

---

### All AI Agents MUST:
- Use snake_case for all Pydantic fields and Python identifiers
- Use kebab-case for HTML IDs and CSS classes; camelCase for JS variables/functions
- Never add new pip or npm dependencies without noting them explicitly in the story
- Keep battery calculation logic in `battery.py` — not in `calculator.py` or `main.py`
- Never convert API response fields to camelCase — read them as snake_case
- Update charts in-place; never destroy/recreate on each simulate call
- Run `pytest --cov=app` before marking any backend story done; keep coverage >80%
- **SECURITY:** Never hardcode API URLs, CORS origins, or rate limits — all must use environment variables
- **SECURITY:** Use `os.getenv()` for all configuration; load `.env` file in backend startup
- **SECURITY:** Frontend must use `process.env.REACT_APP_API_URL` for all fetch calls (not `http://localhost:8000`)
- **SECURITY:** Do not expose internal error details in production — check `ENV` variable before returning error text
- **SECURITY:** All new API endpoints must include rate limiting via `@limiter.limit()` decorator
- **SECURITY:** When modifying CORS, use explicit `allow_methods` and `allow_headers` — never use wildcard `["*"]`

---

### Cross-Cutting Concerns Identified

- **API contract evolution** — battery simulation adds new input params and output fields; must decide extend vs new endpoint
- **Module boundaries** — frontend split must not break existing behaviour; refactor is pre-condition for cleanly adding battery UI
- **Test coverage continuity** — new modules need tests; coverage gate must hold
- **Docker** — new Python deps (e.g. numeric libs) trigger image rebuild

---

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All technology choices are compatible. Vanilla JS ES6 modules require no build tooling — nginx serves them directly. FastAPI + Pydantic v2 on Python 3.11 is stable. Chart.js loaded via CDN — no npm required. Docker Compose orchestration unchanged. No version conflicts.

**Pattern Consistency:**
Naming conventions are internally consistent: snake_case for all Python/API identifiers, camelCase for JS variables and functions, kebab-case for HTML IDs and JS filenames. The "no camelCase conversion" rule bridges the two layers cleanly. Chart update-in-place and loading-state button patterns are consistently specified across solar and battery modules.

**Structure Alignment:**
`app.js`-as-sole-orchestrator enforces no circular imports by design. `api.js`-only-fetch rule maps to a single file boundary. Battery logic isolation in `battery.py` is structurally clear and enforced by the "All AI Agents MUST" rules.

---

### Requirements Coverage ✅

| Requirement | Covered by | Status |
|---|---|---|
| FR-1 Solar generation | `calculator.py`, `models.py` | ✅ |
| FR-2 Sunrise/sunset | `solar_position.py` | ✅ |
| FR-3 Daily hourly graph | `charts.js` + `calculator.py` | ✅ |
| FR-4 Yearly graph | `charts.js` + `calculator.py` | ✅ |
| FR-5 Result cards | `app.js` + `forms.js` | ✅ |
| FR-6 Interactive form | `forms.js`, `index.html` | ✅ |
| FR-7 Placeholder defaults | `forms.js` | ✅ |
| FR-8 Irradiance model | `irradiance.py`, `solar_position.py` | ✅ |
| Battery simulation | `battery.py`, `models.py`, `battery-forms.js`, `battery-charts.js` | ✅ |
| Tab UI (3 tabs) | `tabs.js`, `index.html`, `style.css` | ✅ |
| Cost analysis placeholder | `index.html` static panel | ✅ |

**NFR Coverage:**
- Simulate <500ms: FastAPI with no I/O — met
- Page load <2s: nginx-served static files — met
- Accuracy ±10%: model validated at ±6% for Turin reference — met
- Coverage >80%: gate enforced in `.coveragerc`, currently 95% — met
- No persistence, no auth: confirmed no database layer, no auth middleware

---

### Gap Analysis Results

**Critical Gaps (Pre-Production):**
1. Environment management system not yet implemented — required before production. Stories needed:
   - Add `.env` file support and configuration loading (backend + frontend)
   - Update CORS, rate limiting, and error handling to use env vars
   - Add `python-dotenv`, `slowapi` dependencies
   - Update Docker Compose for environment injection

**Important (note for story authors):**
1. `httpx==0.24.1` must be added to `pyproject.toml` — currently installed in Docker only; pinning prevents breakage on image rebuild.
2. Frontend Jest testing appears in NFRs (80% target) — Story 1.4 completed; ready for Epic 2.
3. `seasonal_ambient_temperature()` SH inversion is a known bug (cos is an even function; sign flip has no effect). Not blocking for battery stories but worth a dedicated fix story.
4. HTTPS/TLS setup is deployment-specific — required for production but not code changes; documented in Security Architecture.

**Minor:**
- `docs/` directory not mapped to any story — screenshots/reference material, no action required.

---

### Architecture Completeness Checklist

**Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

---

### Architecture Readiness Assessment

**Overall Status: READY FOR IMPLEMENTATION (with security stories first)**
**Confidence Level: High**

**Key Strengths:**
- Single-endpoint backwards-compatible API extension eliminates client-side coordination risk
- Module isolation enforced by structure — circular imports impossible by design
- All patterns have canonical code examples — implementation agents have no ambiguity
- Battery model is physics-simple and fully specced; low dependency footprint
- **Security architecture fully designed** — environment management, CORS hardening, rate limiting, error masking all specified with code examples

**Immediate Priority (Pre-Production):**
1. **Security Stories** (blocks all other work):
   - Add `.env` file support and environment configuration loading
   - Implement CORS hardening with environment-based allowed_origins
   - Add rate limiting via `slowapi` middleware
   - Mask error messages in production
   - Add security headers middleware
   - Update docker-compose.yml for environment injection

**Areas for Future Enhancement:**
- SH temperature model bug fix (`seasonal_ambient_temperature`)
- Frontend E2E tests with Playwright
- WCAG accessibility audit and remediation
- Real weather API integration (post-MVP, already deferred in PRD)
- HTTPS/TLS setup for production deployment (deployment-specific, not code)

---

## Security Implementation Stories (Priority: IMMEDIATE)

Before proceeding with Epic 2 (Battery Simulation), the following security stories MUST be completed:

### Security Story 1: Environment Management System
- **Objective:** Implement `.env` file support and environment-based configuration loading
- **Backend Changes:**
  - Add `python-dotenv==1.0.0` to `pyproject.toml`
  - Create `backend/.env.example` (committed)
  - Update `main.py` to load environment variables at startup
  - Move `ALLOWED_ORIGINS`, `BACKEND_URL`, `RATE_LIMIT_PER_MINUTE` to env vars
- **Frontend Changes:**
  - Create `frontend/.env.example` (committed)
  - Update `api.js` to use `process.env.REACT_APP_API_URL` instead of hardcoded `http://localhost:8000`
- **Docker:**
  - Update `docker-compose.yml` to inject environment variables
- **Tests:**
  - Add pytest parametrization for different ENV values (development, production)

### Security Story 2: CORS Hardening
- **Objective:** Configure CORS from environment with explicit method/header allowlists
- **Changes:**
  - Replace `allow_origins=["..."]` with `os.getenv("ALLOWED_ORIGINS", "...")`
  - Change `allow_methods=["*"]` to `allow_methods=["POST", "GET"]`
  - Change `allow_headers=["*"]` to `allow_headers=["Content-Type"]`
  - Set `allow_credentials=False` (change to True only if auth is added later)
  - Add `max_age=600` to cache preflight requests
- **Testing:**
  - Test CORS with dev/prod origins in `test_main.py`

### Security Story 3: Rate Limiting & Error Masking
- **Objective:** Add rate limiting to `/simulate` endpoint and mask errors in production
- **Backend Changes:**
  - Add `slowapi==0.1.9` to `pyproject.toml`
  - Import `Limiter` and decorate `/simulate` endpoint with `@limiter.limit()`
  - Add error masking: check `ENV` variable and return generic message in production
  - Add optional structured logging (python-json-logger) for server-side error tracking
- **Configuration:**
  - `RATE_LIMIT_PER_MINUTE` environment variable (default: 10 for dev, 30 for prod)
- **Testing:**
  - Test rate limiting enforcement in `test_main.py`
  - Test error message masking for different ENV values

### Security Story 4: Security Headers Middleware
- **Objective:** Add HTTP security headers to all responses
- **Changes:**
  - Create `SecurityHeadersMiddleware` class
  - Add X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Strict-Transport-Security headers
  - Register middleware in FastAPI app
- **Testing:**
  - Test header presence in response in `test_main.py`

### Security Story 5: Documentation & Deployment Guide
- **Objective:** Create deployment guide with HTTPS/TLS setup
- **Deliverables:**
  - `DEPLOYMENT.md` with nginx configuration for HTTPS
  - `SECURITY.md` with security checklist
  - Docker Compose production configuration (`docker-compose.prod.yml`)
  - Certbot setup instructions for Let's Encrypt

---

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure and module boundaries
- Refer to this document for all architectural questions
- **Security MUST come first** — complete all security stories before resuming Epic 2

**Implementation Sequence:**
1. **Security Stories 1-4** (2-3 story points each, ~1-2 weeks total)
   - Story 1: Environment management (blocking dependency for all others)
   - Stories 2-4: Can be done in parallel after Story 1
   - Story 5: Documentation (can be done concurrently with 2-4)

2. **Then: Epic 2 Battery Simulation**
   - Story 2.1: Backend battery simulation
   - Story 2.2: Frontend battery UI
   - Story 2.3: Battery tests

3. **Then: Quality Initiatives (parallel track)**
   - E2E tests with Playwright
   - WCAG accessibility audit & fixes
   - Additional frontend tests for app.js integration
