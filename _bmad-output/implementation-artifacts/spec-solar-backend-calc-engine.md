---
title: 'Solar Panel Simulator Backend - Calculation Engine'
type: 'feature'
created: '2026-05-21'
status: 'done'
baseline_commit: 'NO_VCS'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The Solar Panel Simulator needs a calculation engine to model solar energy production from user-defined system parameters (location, panel specs, tilt angle, date, duration). Without this, the app has no core functionality.

**Approach:** Build a FastAPI backend service (Python) that exposes a `/simulate` endpoint. The endpoint ingests solar system parameters and outputs daily/yearly energy metrics and hourly generation curves. Use heuristic weather modeling and standard PV calculations to achieve ±10% accuracy vs PVGIS. Deploy via Docker Compose alongside frontend (separate task).

## Boundaries & Constraints

**Always:**
- All calculations client-side; no backend API or external calls
- Accuracy target: ±10% vs PVGIS baseline for identical inputs
- Temperature derating: 0.4%/°C for silicon PV
- System losses fixed: 0.942 factor (97% inverter, 1% wiring, 2% soiling)
- Sunrise/sunset: NOAA solar position algorithm (civil daylight)
- Heuristic GHI: Ångström clearness-index model with seasonal variation
- Module temperature: Ambient + (Irradiance × 0.03°C per W/m²)
- Input validation: all constraints enforced (latitude ±90, longitude ±180, efficiency 5–25%, tilt 0–90°, azimuth 0–360°)
- Output precision: annual/daily kWh to 1–2 decimals, peak kW to 2 decimals, hourly array values to 3 decimals

**Ask First:**
- Should degradation be modeled in MVP, or is fixed 20% efficiency assumed? (PRD says fixed, but clarify if needed)
- Should monthly totals assume 30-day months, or use actual calendar? (PRD silent; 30-day assumed)
- Spectral effects (AM mass) — include basic model or skip for MVP?

**Never:**
- No external weather API calls (PVGIS, NREL, OpenWeather)
- No battery simulation
- No cloud cover variation or real-time forecasts
- No multi-year degradation curves
- No tracking system orientation optimization

</frozen-after-approval>

## Code Map

- `backend/app/main.py` -- FastAPI application and `/simulate` endpoint
- `backend/app/calculator.py` -- Main calculation engine; orchestrates irradiance, temperature, and energy calculations
- `backend/app/solar_position.py` -- Sunrise/sunset and sun position (NOAA algorithm)
- `backend/app/irradiance.py` -- GHI estimation (Ångström model) and tilted-plane irradiance
- `backend/app/models.py` -- Pydantic request/response models for validation and serialization
- `backend/app/constants.py` -- Physical constants, loss factors, coefficients
- `backend/app/validation.py` -- Input validation logic
- `backend/tests/test_calculator.py` -- Unit tests for each calculation step
- `backend/Dockerfile` -- Docker image for FastAPI service
- `backend/docker-compose.yml` -- Local dev compose (backend only)
- `docker-compose.yml` -- Root-level compose orchestrating backend and frontend

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/models.py` -- Define Pydantic request/response schemas (SolarInput, SolarOutput) -- API contract clarity and validation
- [x] `backend/app/constants.py` -- Hard-code physical constants (solar constant, temperature coefficients, loss factors) -- Single source of truth
- [x] `backend/app/solar_position.py` -- Implement NOAA solar position algorithm for sunrise/sunset and sun elevation angle -- Reusable core for irradiance calculations
- [x] `backend/app/irradiance.py` -- Implement Ångström GHI model and tilted-plane irradiance projection -- Accuracy foundation
- [x] `backend/app/validation.py` -- Input validation logic with clear error messages -- Robust API boundary
- [x] `backend/app/calculator.py` -- Orchestrate hourly energy calculations across duration, apply temperature derating, aggregate daily/monthly/annual totals -- Core calculation API
- [x] `backend/app/main.py` -- FastAPI app setup and `/simulate` POST endpoint that accepts SolarInput and returns SolarOutput -- User-facing API
- [x] `backend/Dockerfile` -- Python 3.11+, FastAPI dependencies, expose port 8000 -- Container deployment
- [x] `backend/docker-compose.yml` -- Service definition for backend, port mapping 8000:8000 -- Local dev orchestration
- [x] `docker-compose.yml` -- Root-level orchestration for backend and frontend -- Monorepo coordination
- [x] `backend/tests/test_calculator.py` -- Unit test each calculation step and validate against reference values from PVGIS/NREL -- Verify ±10% accuracy

**Acceptance Criteria:**
- Given a test case (location, panel specs, date), when calculating daily energy, then result matches PVGIS within ±10% for 5 diverse locations (equator, mid-latitude, high-latitude, hot climate, cool climate)
- Given sunrise/sunset calculation, when comparing to NOAA tables, then result matches to within ±2 minutes for any location/date
- Given an hourly irradiance curve, when summing to daily total, then total matches daily calculation within ±0.5%
- Given all inputs valid, when running calculation, then no errors thrown; all outputs present and within expected ranges
- Given invalid inputs (e.g., latitude 100, efficiency 200%), when validating, then graceful error with clear message

## Design Notes

### FastAPI Endpoint Design
```python
POST /simulate
Request: {
  "latitude": 37.77,
  "longitude": -122.41,
  "panel_count": 10,
  "panel_area_m2": 2.0,
  "panel_efficiency": 20,
  "tilt_angle_deg": 35,
  "azimuth_deg": 180,
  "start_date": "2026-05-21",
  "duration_days": 365
}

Response: {
  "annual_energy_kwh": 7234.5,
  "average_daily_kwh": 19.8,
  "peak_hour_kw": 5.2,
  "system_capacity_kw": 4.0,
  "daily_hourly_generation": [0, 0, ..., 0.5, 1.2, ...],
  "daily_sunrise": "05:32",
  "daily_sunset": "20:28",
  "monthly_energy_kwh": [450, 480, ..., 420],
  "calculation_date": "2026-05-21T10:30:00Z"
}
```

CORS enabled for frontend (separate task) on localhost:3000.

### Solar Position (Sunrise/Sunset)
Uses NOAA solar position algorithm (Spencer 1971 / NREL refinement) to compute sun declination, equation of time, and solar noon. Civil twilight is defined as sun 6° below horizon; solar noon is used for tilt orientation.

### Irradiance Model (Ångström)
Estimates Global Horizontal Irradiance (GHI) from latitude and day-of-year using Ångström equation:
```
GHI = (0.7 + 0.3 × daylight_fraction) × ExtraterrestrialIrradiance × seasonal_factor
seasonal_factor = 0.6 + 0.5 × cos(2π × dayOfYear / 365)
```
Tilted-plane irradiance computed from GHI, DNI (estimated), and diffuse components using transposition model.

### Temperature Derating
```
efficiency_adjusted = base_efficiency × (1 − 0.004 × (module_temp − 25))
module_temp = ambient_temp + irradiance × 0.03
```
Assumes linear derating; no nonlinearity for MVP.

### Energy Aggregation
Hourly power calculated as:
```
power(hour) = area × efficiency_adjusted × irradiance(hour) × 0.942  // 0.942 = system losses
energy_day = sum(power(hour) for hour in daylight) / 1000  // kWh
```

## Verification

**Commands:**
- `cd backend && pytest tests/test_calculator.py -v` -- All tests pass
- `docker build -t solar-simulator:latest ./backend` -- Image builds without errors
- `docker-compose up` (from root) -- Backend service starts on port 8000, `/docs` endpoint accessible
- `curl -X POST http://localhost:8000/simulate -H "Content-Type: application/json" -d '{"latitude":37.77,...}'` -- POST request succeeds with valid response

**Manual checks:**
- Compare calculated sunrise/sunset for 5 test dates vs NOAA solar position table: all within ±2 minutes
- Compare daily energy for San Francisco on clear-sky day vs PVGIS: within ±10%
- Verify all hourly irradiance values positive and less than 1360 W/m² (solar constant)
- FastAPI auto-docs at `/docs` shows `/simulate` endpoint with correct schema
- Invalid inputs (e.g., latitude 100) return 422 Unprocessable Entity with clear error message

## Suggested Review Order

**API Endpoint & Request Flow**

- FastAPI app setup with CORS configuration for localhost:3000 frontend
  [`backend/app/main.py:1`](../../../backend/app/main.py#L1)

- `/simulate` POST endpoint accepting SolarInput and returning SolarOutput
  [`backend/app/main.py:31`](../../../backend/app/main.py#L31)

**Core Calculation Engine**

- Main orchestrator: iterates daily across duration, aggregates results
  [`backend/app/calculator.py:105`](../../../backend/app/calculator.py#L105)

- Hourly power and energy calculation with temperature derating applied
  [`backend/app/calculator.py:47`](../../../backend/app/calculator.py#L47)

**Physical Models**

- Solar position (NOAA algorithm) for sunrise/sunset and sun elevation
  [`backend/app/solar_position.py:110`](../../../backend/app/solar_position.py#L110)

- Ångström GHI estimation with seasonal variation and tilted-plane transposition
  [`backend/app/irradiance.py:44`](../../../backend/app/irradiance.py#L44)

- Temperature derating coefficient (0.4%/°C) and module temperature calculation
  [`backend/app/calculator.py:18`](../../../backend/app/calculator.py#L18)

**Data Validation & Schemas**

- Pydantic input/output models with field validators and ranges
  [`backend/app/models.py:1`](../../../backend/app/models.py#L1)

- Input validation logic with field-level error messages
  [`backend/app/validation.py:24`](../../../backend/app/validation.py#L24)

**Configuration & Constants**

- Physical constants, loss factors (inverter 97%, wiring 1%, soiling 2%)
  [`backend/app/constants.py:1`](../../../backend/app/constants.py#L1)

**Testing & Deployment**

- Unit tests covering efficiency derating, validation, sunrise/sunset, simulations
  [`backend/tests/test_calculator.py:1`](../../../backend/tests/test_calculator.py#L1)

- Docker image with Python 3.11, FastAPI, port 8000 exposed
  [`backend/Dockerfile:1`](../../../backend/Dockerfile#L1)

- Root-level docker-compose orchestrating backend and frontend services
  [`docker-compose.yml:1`](../../../docker-compose.yml#L1)
