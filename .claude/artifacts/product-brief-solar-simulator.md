---
title: Solar Panel Simulator - Product Brief
status: draft
created: 2026-05-21
updated: 2026-05-21
---

# Solar Panel Simulator

## Vision

An interactive engineering simulation app that models solar panel energy production. Users adjust system parameters in real time and visualize how changes affect daily and annual energy output. The simulator enables quick "what-if" experimentation and educates users about how solar system design drives performance.

## Primary Goals

1. **Provide realistic solar energy simulation** — Calculate energy production using industry-standard formulas (irradiance, temperature derating, efficiency losses)
2. **Offer interactive engineering visualizations** — Daily and yearly generation graphs that update immediately after parameter changes
3. **Enable "what-if" experimentation** — Users test scenarios (panel count, tilt angle, location) and see instant results
4. **Educate** — Demonstrate the physics of solar systems through interactive visualization

## Target Users

- **Homeowners** — exploring whether solar makes sense for their roof
- **Engineering students** — learning solar system design and performance modeling
- **Renewable energy enthusiasts** — experimenting with system optimization
- **Solar installers** — quick feasibility checking and customer education

## Core Features

### MVP
- **Solar generation simulation** — Calculate energy production based on user inputs using realistic physics (irradiance, temperature effects, efficiency losses)
- **Sunrise and sunset calculation** — Determine daylight hours for the given location and date
- **Interactive graphs** — Daily generation curve and yearly monthly totals, updating on input change
- **Summary cards** — Key results: annual energy (kWh), peak daily generation, etc.
- **Heuristic weather modeling** — Simple placeholder weather function; real weather API integration is post-MVP

### UX Flow
1. User lands on page with pre-filled placeholder values
2. User adjusts inputs (location, panel specs, date, duration)
3. User clicks "Simulate"
4. Graphs and result cards update at bottom of page
5. User iterates with new parameters

## User Inputs

- **Location**: Latitude, longitude
- **System**: Panel count, panel area (m²), panel efficiency (%), tilt angle (°), azimuth (0–360°, where 0° = north)
- **Time**: Current date, simulation duration (days or months)

## Outputs

- **Summary cards**: Annual energy production (kWh), average daily generation (kWh), peak generation (kW)
- **Daily graph**: Generation curve for a representative day (sunrise to sunset, by hour)
- **Yearly graph**: Monthly total generation for the simulation period

## Success Criteria (MVP)

- Calculations match PVGIS or NREL calculator within 10% (for the same inputs)
- Graphs update responsively when inputs change
- App loads with sensible defaults; users can simulate without manual input

## Long-Term Vision (Out of Scope for MVP)

- Battery simulation (storage, discharge, grid interaction)
- Real weather API integration (PVGIS, NREL) instead of heuristic
- Scenario comparison side-by-side
- Export results (PDF, CSV)
- Mobile-responsive design

## Technical Constraints & Decisions

- **Weather modeling (MVP)**: Heuristic estimation based on latitude; real data integration is post-launch
- **Azimuth input**: Slider 0–360° (0° = north, 90° = east, 180° = south, 270° = west)
- **Performance ratio**: Assumed constant 0.85 (typical system losses); user adjustment possible post-MVP
- **Temperature derating**: Modeled using standard 0.4%/°C coefficient for silicon panels

## Assumptions

- Users have or can estimate panel efficiency (available on spec sheets)
- Tilt angle is either fixed (not tracking) or user-specified
- Demo scope: proof-of-concept; no analytics, no user accounts, no persistence required
