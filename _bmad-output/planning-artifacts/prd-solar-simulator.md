---
title: Solar Panel Simulator - Product Requirements Document
status: final
created: 2026-05-21
updated: 2026-05-23
finalized: 2026-05-23
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

### 2.9 Battery Simulation (FR-9)
**Description:** Model household energy balance with a battery storage system and appliance-based consumption estimation.

**Input Parameters:**

**Appliance Selection (predefined list with defaults):**
- Refrigerator: 150W × 24h/day
- Air Conditioning/Heat: 3000W × 8h/day (default; user adjustable)
- Washing Machine: 2000W × 1.5h/day
- Dishwasher: 1800W × 1h/day
- Water Heater: 4000W × 2h/day
- Lighting: 300W × 8h/day
- Television: 150W × 5h/day
- Microwave: 1000W × 0.5h/day
- [ASSUMPTION] Users can toggle appliances on/off and adjust daily usage hours; custom appliances deferred to post-MVP

**Daily Consumption Calculation:**
```
Daily Consumption (kWh) = Sum of (Appliance Power (kW) × Daily Usage Hours) for all selected appliances
```

**Battery Specifications:**
- Capacity (kWh): float ≥ 1
- Charge/Discharge Efficiency (%): float 80–99 (default: 92%)
- Max Charge Rate (kW): float > 0 (default: 5 kW)
- Max Discharge Rate (kW): float > 0 (default: 5 kW)

**Daily Energy Balance Calculation (per day):**
```
Available Solar Energy = Daily generation from FR-1 (kWh)
Required Consumption = Sum of selected appliances (kWh)
Surplus/Deficit = Available Solar Energy - Required Consumption

If Surplus > 0:
  - Charge battery up to capacity, applying charge efficiency
  - Export excess to grid
Else (Deficit > 0):
  - Discharge battery to meet deficit, applying discharge efficiency
  - Import remaining from grid

Battery State of Charge = Previous SoC + Charge – Discharge (clamped to [0, Capacity])
```

**Output Visualizations:**
- **Daily SoC Curve**: Line chart showing state of charge hour-by-hour for a representative day (sunrise to sunset)
- **Monthly Energy Balance**: Stacked bar chart showing surplus (green) and deficit (red) per month
- **Grid Interaction Summary Card**: Monthly average import/export (kWh)

### 2.10 Cost Analysis & Payback (FR-10)
**Description:** Calculate financial viability of solar installation including system cost, electricity savings, and feed-in tariff revenue.

**Input Parameters:**
- **System Cost (€)**: Total installed cost (default: €1,800/kW × system capacity)
- **Electricity Price (€/kWh)**: Residential grid tariff (default: €0.32/kWh — Italian residential average)
- **Feed-in Tariff (€/kWh)**: Revenue for exported solar energy (default: €0.12/kWh — Italian scambio sul posto)
- **System Lifespan (years)**: Analysis period (default: 25 years)
- **Annual Degradation (%/year)**: Panel efficiency loss over time (default: 0.5%/year)

**Calculation (per year):**
```
Year N (1 ≤ N ≤ Lifespan):
  Capacity = Initial Capacity × (1 − Degradation%)^(N−1)
  Annual Generation = Daily Generation × 365 × Capacity Factor Adjustment
  
  Consumption Covered by Solar = min(Annual Generation, Annual Consumption)
  Electricity Savings = Consumption Covered × Electricity Price
  
  Excess Generation = Annual Generation − Consumption Covered
  Feed-in Revenue = Excess Generation × Feed-in Tariff
  
  Annual Savings = Electricity Savings + Feed-in Revenue
  Cumulative Savings (Year N) = Sum of Annual Savings from Year 1 to N
  
  Break-even Year = First year where Cumulative Savings ≥ System Cost
```

**Output Visualizations:**
- **Annual Savings Card**: €/year (Year 1)
- **Cumulative ROI Chart**: Line chart showing cumulative savings vs. system cost over 25 years
- **Break-even Year Card**: Year N when payback occurs (or "No payback within 25 years")
- **Year-over-Year Savings**: Bar chart showing annual savings per year (declining with degradation)

---

## 3. Tab Structure & Navigation

The application presents three simulation tabs with inherited data flow:

1. **Solar Simulation (FR-1 through FR-8)** — Default tab; energy generation calculation
2. **Battery Simulation (FR-9)** — Energy balance with appliance consumption and battery storage
3. **Cost Analysis (FR-10)** — Financial payback and ROI modeling

**Data Flow:**
- Solar tab is the entry point; user configures location, system specs, and runs simulation
- Battery tab **inherits** location, system capacity, and daily generation from Solar tab; user adds appliance selection and battery specs
- Cost tab **inherits** location, system capacity, and annual generation from Solar tab; user adds financial parameters (cost, tariffs, lifespan)
- Each tab can be revisited independently; changes in Solar tab propagate to Battery and Cost tabs

**Within Each Tab:**
- Solar: Single form + simulate button → graphs update
- Battery: Appliance checklist + battery specs form → inherits solar generation → graphs update
- Cost: Financial parameters form → inherits solar generation → graphs update

---

## 4. Non-Functional Requirements

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

## 5. User Inputs & Validation

### 5.1 Solar Simulation Inputs

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

### 5.2 Battery Simulation Inputs

| Input | Type | Range/Format | Required | Validation |
|---|---|---|---|---|
| Appliances | Checklist | Predefined list + hours/day | Yes | Integer hours 0–24 per appliance |
| Battery Capacity | Float | ≥ 1 kWh | Yes | Positive float |
| Charge Efficiency | Float | 80–99 % | Yes | 80 ≤ value ≤ 99 |
| Discharge Efficiency | Float | 80–99 % | Yes | 80 ≤ value ≤ 99 |
| Max Charge Rate | Float | > 0 kW | Yes | Positive float |
| Max Discharge Rate | Float | > 0 kW | Yes | Positive float |

### 5.3 Cost Analysis Inputs

| Input | Type | Range/Format | Required | Validation |
|---|---|---|---|---|
| System Cost | Float | ≥ 0 € | Yes | Non-negative float |
| Electricity Price | Float | ≥ 0 €/kWh | Yes | Non-negative float |
| Feed-in Tariff | Float | ≥ 0 €/kWh | Yes | Non-negative float |
| System Lifespan | Integer | ≥ 5 years | Yes | Integer ≥ 5 |
| Annual Degradation | Float | 0–2 %/year | Yes | 0 ≤ value ≤ 2 |

---

## 6. Outputs & Display

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

### 6.2 Battery Simulation Outputs

**Summary Cards:**
- **Daily Consumption (kWh):** Sum of selected appliances
- **Battery Capacity (kWh):** User-specified capacity
- **Grid Interaction (avg/month kWh):** Import/export summary

**Daily SoC Curve:**
- Chart type: Line chart
- X-axis: Hour (0–23)
- Y-axis: State of Charge (%), 0–100%
- Data points: 24 hourly values showing battery charge level

**Monthly Energy Balance:**
- Chart type: Stacked bar chart
- X-axis: Month
- Y-axis: Energy (kWh)
- Surplus (green): Energy exported to grid
- Deficit (red): Energy imported from grid

### 6.3 Cost Analysis Outputs

**Summary Cards:**
- **Annual Savings (Year 1, €):** Electricity savings + feed-in revenue
- **Break-even Year:** Year when cumulative savings ≥ system cost (or "No payback within 25 years")
- **25-Year Total Savings (€):** Cumulative savings over full lifespan

**Cumulative ROI Chart:**
- Chart type: Line chart overlaid on system cost baseline
- X-axis: Year (1–25)
- Y-axis: Cumulative Savings (€)
- Line: Cumulative savings trajectory
- Baseline: Horizontal line at system cost
- Break-even point: Intersection of cumulative savings line and baseline

**Year-over-Year Savings:**
- Chart type: Bar chart
- X-axis: Year
- Y-axis: Annual Savings (€)
- Values declining with panel degradation over time

---

## 7. Constraints & Technical Decisions

| Constraint | Rationale |
|---|---|
| **No Real Weather Data** | Heuristic modeling sufficient for proof-of-concept; real API post-MVP |
| **No User Accounts** | Demo scope; no persistence or authentication |
| **Fixed System Losses** | 5.8% total (3% inverter, 1% wiring, 2% soiling) → 0.942 combined factor; user adjustment post-MVP |
| **No Cloud Cover Variation** | Clear-sky assumption; real forecast integration post-MVP |
| **No Tracking Systems** | Fixed tilt angle only; no dual-axis or single-axis tracking |
| **No Shading Analysis** | Assumes unshaded installation |

---

## 8. Out of Scope (MVP)

- Real weather API integration (PVGIS, NREL, OpenWeather) — heuristic model used instead
- Scenario comparison / side-by-side views
- Export (PDF, CSV)
- Mobile-optimized UI
- User accounts / saved simulations
- Utility bill integration
- Multi-language support
- Custom appliance definitions (predefined list only for MVP)
- Seasonal feed-in tariff variation (flat rate only)

**Future (Post-MVP):**
- Real weather API integration with historical data
- Custom appliance database
- Advanced battery profiles (temperature derating, cycling limits)
- Grid tariff optimization
- Scenario export and comparison
- Mobile app
- Machine learning-based consumption prediction

---

## 9. Decisions & Resolved Assumptions

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
| Battery charge/discharge efficiency | Default 92%; typical for lithium-ion residential batteries; range 80–99% allows variety of chemistries |
| Panel degradation | 0.5%/year — standard for modern crystalline silicon; industry average over 25 years ~12% total loss |
| Feed-in tariff (Italy) | Default €0.12/kWh — Italian scambio sul posto / ritiro dedicato average; user adjustable |
| Electricity price (Italy) | Default €0.32/kWh — Italian residential tariff (2026 estimate) |
| System cost default | €1,800/kW × system capacity — typical residential installation cost in Italy |
| System lifespan | 25 years default — industry standard warranty period for panels |
| Appliance defaults (Italy) | Based on typical Italian household consumption patterns; user selectable |

---

## 10. Success Metrics & Acceptance Criteria

### 10.1 Solar Simulation Acceptance
- [ ] Daily energy calculation matches PVGIS within ±10% for 10 test cases (varied lat/long/tilt)
- [ ] Graphs render without errors for all valid input combinations
- [ ] Placeholder defaults load on page refresh
- [ ] "Simulate" button disabled until all required inputs filled

### 10.2 Battery Simulation Acceptance
- [ ] Appliance consumption matches user selection (sum of selected appliances)
- [ ] Battery SoC never exceeds capacity or goes below 0%
- [ ] Daily SoC curve shows realistic charge/discharge cycles
- [ ] Monthly energy balance correctly displays surplus and deficit

### 10.3 Cost Analysis Acceptance
- [ ] Break-even year calculated correctly (cumulative savings ≥ system cost)
- [ ] Degradation applied correctly (output Year 25 ≈ 12% lower than Year 1)
- [ ] Feed-in tariff and electricity price applied to correct energy flows
- [ ] ROI chart shows intersection with system cost baseline at break-even year

### 10.4 Performance Acceptance
- [ ] Graph updates <1 second after input change
- [ ] Page loads in <2 seconds (cold start)
- [ ] All three tabs load independently without blocking

### 10.5 UX Acceptance
- [ ] User can run all three simulations without reading documentation
- [ ] Input validation error messages clear and actionable
- [ ] Graphs labeled with units and legend; axis ranges appropriate
- [ ] Tab switching preserves prior inputs within each tab

---

## 11. Design & Architecture Notes

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
| 2026-05-23 | Added FR-9 (Battery Simulation) with appliance-based consumption modeling; added FR-10 (Cost Analysis) with 25-year ROI and degradation modeling; Italian pricing defaults (€0.32/kWh electricity, €0.12/kWh feed-in tariff); moved battery & cost analysis from Out-of-Scope to IN-SCOPE; clarified tab data flow: Battery and Cost tabs inherit location/system specs from Solar tab | Dario / AI |
