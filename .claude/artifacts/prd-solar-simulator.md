---
title: Solar Panel Simulator - Product Requirements Document
status: final
created: 2026-05-21
updated: 2026-05-22
---

# Solar Panel Simulator PRD

## 1. Overview

**Product Name:** Solar Panel Simulator

**Purpose:** Interactive web application that models solar panel energy production based on user-specified system parameters. Users adjust inputs, simulate, and view visualization of estimated daily and yearly energy output. User may also configure energy consumption and battery capacity storage to simulate and visualize solar energy use. Lastly, by configuring network energy price, feed in tariffs, and equipment cost, the user may estimate and review charts for break-even period for the installation of the solar system.

**Primary Use Case:** Enable homeowners, students, installers, and enthusiasts to quickly model solar system performance and experiment with configuration changes.

**Success Criteria:**
- Calculations match PVGIS/NREL within ±10% for identical inputs
- Graphs update responsively (<1s) after parameter changes
- App renders with sensible defaults; users can simulate without manual input
- User can estimate breakeven period for the installation of an arbitrary solar system in 

---

## 2. Feature Requirements

### 2.1 Solar Generation Simulation (FR-1)
**Description:** Calculate total energy output (kWh) for a solar installation over a user-specified duration.

**Input Parameters:**
- Panel count (integer ≥ 1)
- Panel area per unit (m², float ≥ 0.1)
- Panel efficiency (%, float 5–25)
- Tilt angle (°, float 0–90)
- Azimuth (°, float 0–360; 0° = north, 90° = east, 180° = south, 270° = west)
- Latitude (float, range −90 to +90)
- Longitude (float, range −180 to +180)
- Simulation date (YYYY-MM-DD)
- Simulation duration (days or months; [ASSUMPTION] days preferred for MVP)

**Calculation Method:**
```
Daily Energy (kWh) = Total Panel Area × Panel Efficiency × Daily Irradiance × System Losses

Where:
- Total Panel Area = panel count × panel area per unit
- Panel Efficiency (adjusted for temperature) = Base Efficiency × (1 − 0.004 × (Module Temp − 25°C))
- Daily Irradiance = incident solar radiation on tilted surface (from hourly irradiance model; see FR-8)
- System Losses = Inverter Efficiency × Wiring Factor × Soiling Factor
  Fixed losses: Inverter 97%, Wiring 99%, Soiling 98% → 0.942 combined factor
  Temperature derating: 0.4%/°C above 25°C reference
  Module temperature = Ambient Temp + (Irradiance × 0.03 °C per W/m²)
```

**Output:**
- Total energy for duration (kWh)
- Average daily energy (kWh/day)
- Peak generation hour (kW)

### 2.2 Sunrise and Sunset Calculation (FR-2)
**Description:** Determine civil daylight hours for the given location and date.

**Method:**
- Calculate sunrise/sunset times using latitude, longitude, and Julian date
- Uses NOAA solar position algorithm: Julian centuries from J2000 epoch, geometric mean longitude, mean anomaly, equation of time, and solar declination
- Civil twilight threshold: sun 6° below horizon (NOAA standard)

**Output:**
- Sunrise time (HH:MM UTC)
- Sunset time (HH:MM UTC)
- Civil daylight hours (decimal hours)

### 2.3 Daily Generation Graph (FR-3)
**Description:** Hourly energy production curve for a representative day within the simulation period.

**Behavior:**
- Display generation curve from sunrise to sunset (0 before sunrise, 0 after sunset)
- X-axis: Hour of day (0–23)
- Y-axis: Power output (kW)
- [ASSUMPTION] Uses first day of simulation period as representative day

**Curve Calculation:**
- For each hour: compute sun elevation/azimuth via NOAA algorithm, calculate tilted-plane irradiance (see FR-8), apply module temperature derating, multiply by total panel area × efficiency × system losses

### 2.4 Yearly Generation Graph (FR-4)
**Description:** Monthly total energy production across the simulation duration.

**Behavior:**
- Bar chart showing total kWh per month
- X-axis: Month
- Y-axis: Energy (kWh)
- [ASSUMPTION] Assumes 30-day months for simplicity if duration spans partial months

### 2.5 Summary Result Cards (FR-5)
**Description:** Key metrics displayed above graphs.

**Cards:**
- **Annual Energy Production:** Total kWh over simulation period
- **Average Daily Generation:** Mean kWh/day
- **Peak Hour Generation:** Maximum kW in any single hour
- **System Capacity:** Total peak kW = (Panel Count × Panel Area × Panel Efficiency × 1000 W/m² irradiance) / 1000

### 2.6 Interactive Parameter Input (FR-6)
**Description:** Form where users adjust simulation parameters and trigger recalculation.

**Inputs:**
- Location: Latitude input, Longitude input (number fields)
- System: Panel Count, Panel Area, Panel Efficiency, Tilt Angle, Azimuth (number/range fields)
- Time: Date picker, Duration selector
- Validation enforced server-side (Pydantic) and reflected to the client as field-level 422 errors; ranges per Section 4

**Submit Button:**
- Labeled "Simulate"
- Triggers calculation and graph updates

### 2.7 Placeholder Defaults (FR-7)
**Description:** Pre-filled sensible values on page load so users can simulate immediately.

**Defaults:**
- Location: Turin, Italy (Lat: 45.0703, Long: 7.6869)
- Panel Count: 10
- Panel Area: 2.0 m²
- Panel Efficiency: 20%
- Tilt Angle: 35°
- Azimuth: 180° (south-facing)
- Simulation Date: Today
- Duration: 365 days

### 2.8 Heuristic Irradiance Model (FR-8)
**Description:** Physics-based clear-sky irradiance model with seasonal cloud attenuation; no external weather API calls.

**Calculation pipeline (per hour):**

1. **Extraterrestrial irradiance** — Spencer (1971) eccentricity correction applied to solar constant (1361 W/m²) to account for Earth–Sun distance variation (~±3.3% perihelion to aphelion).

2. **Air mass** — Kasten & Young (1989) formula, valid down to near-horizon elevations:
   ```
   AM = 1 / (cos(z) + 0.50572 × (96.07995 − z)^−1.6364)
   ```
   where z = zenith angle. Returns ∞ when sun is below horizon.

3. **Clear-sky DNI** — Laue/Meinel atmospheric transmittance:
   ```
   DNI_clear = E0 × 0.7^(AM^0.678)
   ```

4. **Clear-sky GHI** — Direct horizontal component plus ~13% diffuse approximation:
   ```
   GHI_clear = DNI_clear × sin(elevation) × 1.13
   ```

5. **Seasonal cloud factor** — Heuristic attenuation (no external API):
   ```
   cloud_factor = 0.65 + amplitude × cos(2π × (doy − 172) / 365 × sign(latitude))
   amplitude = 0.15 + min(|latitude|, 60°) / 60° × 0.10
   ```
   Northern hemisphere peaks around summer solstice (doy 172); southern hemisphere is inverted. Factor bounded [0.05, 1.0].

6. **GHI after clouds:** `GHI = GHI_clear × cloud_factor`

7. **GHI decomposition** — Erbs et al. (1982) diffuse fraction correlation:
   Clearness index `kt = GHI / GHI_clear` drives a piecewise polynomial that splits GHI into DNI and DHI.

8. **Tilted-plane irradiance** — Isotropic-sky transposition model:
   ```
   G_tilt = DNI × cos(θ) + DHI × (1 + cos(tilt)) / 2 + GHI × albedo × (1 − cos(tilt)) / 2
   ```
   where θ = angle of incidence on the tilted surface, albedo = 0.20.

**Validated output:** Turin, Italy (45.07°N) with 4 kWp south-facing 35° system yields ~5000 kWh/year (PVGIS reference: ~5300 kWh; within ±6%).

---

## 3. Non-Functional Requirements

| Requirement | Specification |
|---|---|
| **Response Time** | Graph update <1 second after input change |
| **Calculation Accuracy** | Within ±10% of PVGIS for same inputs |
| **Browser Support** | Modern browsers (Chrome, Firefox, Safari, Edge) |
| **Mobile Responsiveness** | [ASSUMPTION] Desktop-first for MVP; mobile nice-to-have |
| **Performance** | Load page in <2s, simulate in <500ms |
| **Data Persistence** | None required (MVP); no database |
| **Accessibility** | [ASSUMPTION] WCAG 2.1 AA for MVP scope TBD |

---

## 4. User Inputs & Validation

| Input | Type | Range/Format | Required | Validation |
|---|---|---|---|---|
| Latitude | Float | −90 to +90 | Yes | Numeric, within range |
| Longitude | Float | −180 to +180 | Yes | Numeric, within range |
| Panel Count | Integer | ≥ 1 | Yes | Positive integer |
| Panel Area | Float | ≥ 0.1 m² | Yes | Positive float |
| Panel Efficiency | Float | 5–25 % | Yes | 5 ≤ value ≤ 25 |
| Tilt Angle | Float | 0–90 ° | Yes | 0 ≤ value ≤ 90 |
| Azimuth | Float | 0–360 ° | Yes | 0 ≤ value ≤ 360 |
| Simulation Date | Date | YYYY-MM-DD | Yes | Valid date |
| Duration | Integer | ≥ 1 day | Yes | Positive integer |

Validation occurs server-side (Pydantic on POST /simulate); the API returns field-level 422 errors. The frontend displays these inline.

---

## 5. Outputs & Display

### 5.1 Summary Cards
- **Annual Energy (kWh):** Formatted to 1 decimal place
- **Daily Average (kWh/day):** Formatted to 2 decimal places
- **Peak Hour (kW):** Formatted to 2 decimal places

### 5.2 Daily Graph
- Chart type: Line chart
- X-axis: Hour (0–23)
- Y-axis: Power (kW), auto-scale
- Data points: 24 hourly values
- Tool: Chart.js or Recharts

### 5.3 Yearly Graph
- Chart type: Bar chart
- X-axis: Month name
- Y-axis: Energy (kWh), auto-scale
- 12 bars (one per calendar month, even if duration < 12 months; zero values where applicable)

---

## 6. Constraints & Technical Decisions

| Constraint | Rationale |
|---|---|
| **No Real Weather Data** | Heuristic modeling sufficient for proof-of-concept; real API post-MVP |
| **No User Accounts** | Demo scope; no persistence or authentication |
| **Fixed System Losses** | 5.8% total (3% inverter, 1% wiring, 2% soiling) → 0.942 combined factor; user adjustment post-MVP |
| **No Cloud Cover Variation** | Clear-sky assumption; real forecast integration post-MVP |
| **No Tracking Systems** | Fixed tilt angle only; no dual-axis or single-axis tracking |
| **No Shading Analysis** | Assumes unshaded installation |

---

## 7. Out of Scope (MVP)

- Battery simulation
- Real weather API integration (PVGIS, NREL, OpenWeather)
- Scenario comparison / side-by-side views
- Export (PDF, CSV)
- Mobile-optimized UI
- User accounts / saved simulations
- Financing calculations (ROI, payback period)
- Utility bill integration
- Multi-language support

**Future (Post-MVP):**
- Weather API integration
- Battery storage modeling
- Grid interaction modeling
- Scenario export and comparison
- Mobile app

---

## 8. Decisions & Resolved Assumptions

| Item | Decision |
|---|---|
| Irradiance model | Kasten-Young + Laue/Meinel + Erbs + isotropic transposition (see FR-8); validated within ±6% of PVGIS for Turin reference case |
| Temperature derating coefficient | 0.4%/°C — standard for crystalline silicon PV |
| System losses | Fixed: inverter 97%, wiring 99%, soiling 98% → 0.942 combined factor |
| Seasonal cloud factor bounds | Heuristic [0.05, 1.0]; amplitude grows with latitude; NH peaks at summer solstice |
| First day of simulation for daily graph | Confirmed — simplifies UX; multi-day averaging deferred post-MVP |
| Azimuth convention | 0° = north, increasing clockwise (standard compass; 180° = south-facing) |
| Sunrise/sunset definition | Civil twilight: sun 6° below horizon (NOAA standard) |
| Default location | Turin, Italy (45.0703°N, 7.6869°E) — well-documented reference location with PVGIS data |

---

## 9. Success Metrics & Acceptance Criteria

### 9.1 Functional Acceptance
- [ ] Daily energy calculation matches PVGIS within ±10% for 10 test cases (varied lat/long/tilt)
- [ ] Graphs render without errors for all valid input combinations
- [ ] Placeholder defaults load on page refresh
- [ ] "Simulate" button disabled until all required inputs filled

### 9.2 Performance Acceptance
- [ ] Graph updates <1 second after input change
- [ ] Page loads in <2 seconds (cold start)
- [ ] No console errors or warnings

### 9.3 UX Acceptance
- [ ] User can run simulation without reading documentation
- [ ] Input validation error messages clear and actionable
- [ ] Graphs labeled and axis ranges appropriate

---

## 10. Design & Architecture Notes

- **Tech Stack:** Vanilla JavaScript + Chart.js (frontend); Python FastAPI (backend); Docker Compose orchestration
- **Calculation Engine:** Python backend (`solar_position.py`, `irradiance.py`, `calculator.py`)
- **Solar Calculations:** NOAA solar position algorithm + Kasten-Young air mass + Laue/Meinel transmittance + Erbs decomposition + isotropic-sky transposition — see FR-8 for the full pipeline
- **API:** Single POST `/simulate` endpoint; Pydantic validation; returns all output fields in one response
- **No React:** Frontend is plain HTML/CSS/JS to keep the demo dependency-free

---

## Appendix A: Change History

| Date | Change | Owner |
|---|---|---|
| 2026-05-21 | Initial PRD draft | AI (Dario review pending) |
| 2026-05-22 | Updated FR-8 to reflect actual Kasten-Young + Laue/Meinel + Erbs + isotropic-sky pipeline; corrected seasonal factor bounds; resolved all [ASSUMPTION] tags; updated tech stack (Vanilla JS, no React); corrected default location (Turin); fixed system loss breakdown; validated calculations within ±6% of PVGIS | Dario / AI |
