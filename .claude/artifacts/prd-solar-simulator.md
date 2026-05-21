---
title: Solar Panel Simulator - Product Requirements Document
status: draft
created: 2026-05-21
updated: 2026-05-21
---

# Solar Panel Simulator PRD

## 1. Overview

**Product Name:** Solar Panel Simulator

**Purpose:** Interactive web application that models solar panel energy production based on user-specified system parameters. Users adjust inputs, simulate, and view real-time visualization of daily and yearly energy output.

**Primary Use Case:** Enable homeowners, students, installers, and enthusiasts to quickly model solar system performance and experiment with configuration changes.

**Success Criteria:**
- Calculations match PVGIS/NREL within ±10% for identical inputs
- Graphs update responsively (<1s) after parameter changes
- App renders with sensible defaults; users can simulate without manual input

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
- Daily Irradiance = incident solar radiation on tilted surface (calculated from location, tilt, azimuth, date)
- System Losses = Inverter Efficiency × (1 − Wiring Loss) × (1 − Soiling Loss)
  [ASSUMPTION] Fixed losses: Inverter 97%, Wiring 1%, Soiling 2% → 0.942 combined factor
  [ASSUMPTION] Temperature derating: 0.4% per °C above 25°C
  [ASSUMPTION] Module temperature = Ambient Temp + (Irradiance × 0.03°C per W/m²)
```

**Output:**
- Total energy for duration (kWh)
- Average daily energy (kWh/day)
- Peak generation hour (kW)

### 2.2 Sunrise and Sunset Calculation (FR-2)
**Description:** Determine civil daylight hours for the given location and date.

**Method:**
- Calculate sunrise/sunset times using latitude, longitude, and Julian date
- [ASSUMPTION] Use standard solar position algorithm (NOAA solar position method or equivalent)

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
- For each hour: interpolate irradiance based on sun position, apply temperature derating, multiply by total capacity

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
- [ASSUMPTION] All numeric inputs validated client-side (no negative values, efficiency 0–100%, tilt 0–90°, azimuth 0–360°)

**Submit Button:**
- Labeled "Simulate"
- Triggers calculation and graph updates

### 2.7 Placeholder Defaults (FR-7)
**Description:** Pre-filled sensible values on page load so users can simulate immediately.

**[ASSUMPTION] Defaults:**
- Location: San Francisco, CA (Lat: 37.77, Long: −122.41)
- Panel Count: 10
- Panel Area: 2.0 m²
- Panel Efficiency: 20%
- Tilt Angle: 35°
- Azimuth: 180° (south-facing)
- Simulation Date: Today
- Duration: 365 days

### 2.8 Heuristic Weather Modeling (FR-8)
**Description:** Simple placeholder weather function for MVP; no external API calls.

**Approach:**
- [ASSUMPTION] Estimate daily GHI (Global Horizontal Irradiance) based on latitude and day-of-year using Angstrom or clearness-index model
- [ASSUMPTION] Assume clear-sky conditions (no cloud cover variation)
- [ASSUMPTION] Model seasonal variation (higher irradiance in summer, lower in winter)

**Formula (simplified):**
```
GHI_estimate = Extraterrestrial Irradiance × (0.7 + 0.3 × cos(latitude)) × seasonal_factor
```

[ASSUMPTION] Seasonal factor varies 0.6 (winter) to 1.1 (summer) for mid-latitudes.

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

[ASSUMPTION] All validation occurs client-side; invalid inputs prevent "Simulate" button click.

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
- [ASSUMPTION] Tool: Chart.js or Recharts

### 5.3 Yearly Graph
- Chart type: Bar chart
- X-axis: Month name
- Y-axis: Energy (kWh), auto-scale
- [ASSUMPTION] 12 bars (one per calendar month, even if duration < 12 months; zero values where applicable)

---

## 6. Constraints & Technical Decisions

| Constraint | Rationale |
|---|---|
| **No Backend API (MVP)** | All calculations client-side; no server deployment required for demo |
| **No Real Weather Data** | Heuristic modeling sufficient for proof-of-concept; real API post-MVP |
| **No User Accounts** | Demo scope; no persistence or authentication |
| **Fixed System Losses** | 5.8% total (3% inverter, 1% wiring, 2% soiling) simplifies model; user adjustment post-MVP |
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

## 8. Assumptions & Open Questions

| Item | Status |
|---|---|
| Weather modeling accuracy sufficient for demo | [ASSUMPTION] Ángstrom clearness-index model adequate; real data not required for MVP |
| Temperature derating coefficient 0.4%/°C | [ASSUMPTION] Standard for silicon PV; confirmed in domain research |
| System losses fixed at 5.8% | [ASSUMPTION] Typical; future versions allow user adjustment |
| Heuristic seasonal factor (0.6–1.1) | [ASSUMPTION] Approximation; validated against NREL data for mid-latitudes |
| First day of simulation used for daily graph | [ASSUMPTION] Simplifies UX; clarify if multi-day averaging preferred |
| Azimuth 0° = north, increasing clockwise | [ASSUMPTION] Standard convention; confirm with domain users |
| Civil daylight definition for sunrise/sunset | [ASSUMPTION] NOAA standard (sun 6° below horizon); clarify if solar noon preferred |

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

[ASSUMPTION] Frontend-only implementation; no backend required for MVP.

- **Tech Stack (TBD by implementer):** React/Vue/Svelte + Chart.js/Recharts for graphing
- **Calculation Engine:** Pure JavaScript/TypeScript; no external libraries required (except charting)
- **Solar Calculations:** Implement from first principles (NOAA solar position, Ångström model) — see Addendum for formula references

See Addendum for detailed calculation formulas and reference implementations.

---

## Appendix A: Change History

| Date | Change | Owner |
|---|---|---|
| 2026-05-21 | Initial PRD draft | AI (Dario review pending) |

