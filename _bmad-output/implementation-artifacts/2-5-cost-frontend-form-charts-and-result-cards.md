---
storyKey: 2-5-cost-frontend-form-charts-and-result-cards
storyId: "2.5"
title: Cost Frontend — Form, Charts, and Result Cards
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: backlog
createdAt: '2026-05-23'
startedAt: null
completedAt: null
---

# Story 2-5: Cost Frontend — Form, Charts, and Result Cards

## Story

As a homeowner or solar enthusiast,
I want a Cost Analysis tab with a financial parameters form, cumulative ROI chart, year-over-year savings chart, and result cards,
So that I can understand the long-term financial viability of my solar installation.

**Requirements Covered:** FR-10 (Cost Analysis UI), ARCH-3, ARCH-4, ARCH-5, Tab Data Inheritance

---

## Acceptance Criteria

**Given** the Cost Analysis tab,
**When** I view it,
**Then** the form contains labelled inputs for: System Cost (€), Electricity Price (€/kWh), Feed-in Tariff (€/kWh), System Lifespan (years), Annual Degradation (%/year), and a "Simulate" button

**Given** the Cost Analysis tab loads for the first time,
**When** the form renders,
**Then** it displays an inheritance notice: "Using generation from Solar tab: X kWh/year (calculated at [timestamp])"

**Given** the Cost Analysis tab loads for the first time,
**When** the form renders,
**Then** it pre-fills with Italian defaults: system cost = €1,800/kW × capacity_kw, electricity price = €0.32/kWh, feed-in tariff = €0.12/kWh, lifespan = 25 years, degradation = 0.5%/year

**Given** valid inputs in both Solar and Cost forms,
**When** I click Simulate on the Cost tab,
**Then** `simulateSolar()` is called with a payload containing all solar fields plus all five cost fields

**Given** a successful cost analysis response,
**When** the results arrive,
**Then** result cards display: Year 1 Annual Savings (€), Break-even Year (or "No payback within 25 years"), 25-Year Total Savings (€) — all formatted to 2 decimal places

**Given** a successful cost analysis response,
**When** the results arrive,
**Then** a line chart renders showing cumulative savings over 25 years with a horizontal baseline at system cost and intersection point marked at break-even year

**Given** a successful cost analysis response,
**When** the results arrive,
**Then** a bar chart renders showing annual savings per year (1–25), with values declining due to panel degradation

---

## Tasks & Subtasks

- [ ] Create `frontend/cost-forms.js` module (ES6 native module)
  - [ ] Export `initCostForm(annual_kwh, system_capacity_kw)` function
  - [ ] Render cost form HTML with inputs:
    - [ ] System Cost (€): calculate default = 1800 × system_capacity_kw
    - [ ] Electricity Price (€/kWh): default 0.32
    - [ ] Feed-in Tariff (€/kWh): default 0.12
    - [ ] System Lifespan (years): default 25
    - [ ] Annual Degradation (%/year): default 0.5
  - [ ] Display inheritance notice: "Using generation from Solar tab: {annual_kwh} kWh/year (calculated at {timestamp})"
  - [ ] Export `getCostInput()` function returning current form values
  - [ ] Export `showFieldError(field, message)` function
  - [ ] Export `clearErrors()` function

- [ ] Create `frontend/cost-charts.js` module (ES6 native module)
  - [ ] Export `initCumulativeROIChart(container_id)` function
    - [ ] Line chart with cumulative savings over 25 years
    - [ ] Horizontal line at system cost (break-even baseline)
    - [ ] Mark intersection point at break-even year with annotation
  - [ ] Export `updateCumulativeROIChart(cumulative_savings, system_cost, breakeven_year)` function
  - [ ] Export `initAnnualSavingsChart(container_id)` function
    - [ ] Bar chart showing annual savings per year (declining with degradation)
  - [ ] Export `updateAnnualSavingsChart(annual_savings_list)` function
  - [ ] Ensure chart.update() used (no recreate)

- [ ] Update `frontend/app.js` to orchestrate Cost tab Simulate
  - [ ] In initializeApp(), call cost-forms.initCostForm(annual_kwh, capacity_kw) with solar data
  - [ ] In initializeApp(), initialize both cost charts
  - [ ] Add Cost tab Simulate button listener
    - [ ] Get solar form values
    - [ ] Get cost form values
    - [ ] Merge into single payload with all solar + all cost fields
    - [ ] Call api.simulateSolar(payload)
  - [ ] In response handler:
    - [ ] Update cumulative ROI chart
    - [ ] Update annual savings chart
    - [ ] Update result cards (Year 1 Savings, Break-even Year, 25-Year Total)
    - [ ] Format currency to 2 decimals, format break-even year or "No payback within 25 years"
  - [ ] In error handler:
    - [ ] Display field-level 422 errors inline

- [ ] Create cost result cards section in HTML (if not exists)
  - [ ] #cost-year-1-savings-card
  - [ ] #cost-breakeven-year-card
  - [ ] #cost-total-25year-savings-card

- [ ] Create Jest tests for cost frontend
  - [ ] Test: initCostForm() renders with Italian defaults
  - [ ] Test: getCostInput() returns correct structure
  - [ ] Test: Chart update functions preserve existing chart (no recreate)
  - [ ] Test: Result cards display formatted currency

- [ ] Verify integration: Cost tab Simulate → charts + cards update

---

## Dev Notes

**Tab Data Inheritance:**
Cost form receives annual_kwh and system_capacity_kw from solar simulation. It calculates default system_cost = €1,800/kW from capacity. These are independent calculations; Cost tab doesn't re-run solar simulation.

**Chart Details:**
- Cumulative ROI chart: X=years (1–25), Y=€ savings; line shows cumulative curve, horizontal baseline at system cost
- Annual Savings chart: X=years (1–25), Y=€/year; bar chart shows declining values (degradation effect)

**Currency Formatting:**
- System Cost, annual/cumulative savings: 2 decimal places (€X,XXX.XX)
- Break-even year: integer year number, or "No payback within 25 years" if null

---

## Dev Agent Record

### Implementation Plan
1. Create cost-forms.js and cost-charts.js modules
2. Update app.js to orchestrate Cost tab Simulate
3. Create cost result cards in HTML
4. Create Jest tests
5. Verify full integration

### Debug Log
(To be filled by dev agent)

### Completion Notes
(To be filled by dev agent)

---

## File List

**New Files:**
- frontend/cost-forms.js
- frontend/cost-charts.js
- frontend/__tests__/cost-frontend.test.js

**Modified Files:**
- frontend/app.js
- frontend/index.html

**Deleted Files:**
(none)

---

## Change Log

- 2026-05-23: Story 2-5 created — Cost Analysis tab UI with forms and charts

---

## Status

**Current:** backlog
**Depends On:** Story 2-4 (backend)
**Story Created:** 2026-05-23

