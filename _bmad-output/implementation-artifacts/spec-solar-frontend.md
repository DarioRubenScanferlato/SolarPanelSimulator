---
title: 'Solar Panel Simulator Frontend - Vanilla JS UI'
type: 'feature'
created: '2026-05-21'
status: 'done'
baseline_commit: 'NO_VCS'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The backend API is complete and running, but users have no interface to interact with it. They need a responsive web UI to input solar parameters and visualize results.

**Approach:** Build a vanilla JavaScript single-page app (no frameworks) with HTML form inputs, dynamic graph rendering via Chart.js, and real-time API integration. Load with placeholder defaults; update all charts on "Simulate" button click.

## Boundaries & Constraints

**Always:**
- Vanilla JavaScript only (no React, Vue, Svelte)
- Chart.js for graphs (CDN or bundled)
- Plain CSS (no Tailwind, Bootstrap)
- Fetch API for HTTP requests to `http://localhost:8000/simulate`
- Input validation matches backend (Pydantic schema)
- All numeric outputs formatted to appropriate decimals
- Responsive design (mobile-friendly)
- Placeholder defaults: San Francisco (37.77, -122.41), 10 panels, 2m² each, 20% efficiency, 35° tilt, 180° azimuth

**Ask First:**
- CSS framework preference (plain, or minimal utility library)?
- Should app work offline or always require backend connection?

**Never:**
- No build tools (Webpack, Vite, etc.) — plain HTML + JS + CSS
- No npm dependencies except Chart.js (CDN preferred)
- No server-side rendering
- Do not add authentication or user accounts
- No data persistence (localStorage, database)

</frozen-after-approval>

## Code Map

- `frontend/index.html` -- Single HTML page with form and chart containers
- `frontend/style.css` -- Styling for form, cards, and charts
- `frontend/app.js` -- Vanilla JS: form handling, API calls, chart rendering
- `frontend/Dockerfile` -- Simple HTTP server for static files (nginx or python)
- `frontend/.gitkeep` -- (placeholder, remove when index.html added)

## Tasks & Acceptance

**Execution:**
- [x] `frontend/index.html` -- Input form (8 fields), simulate button, 4 result cards, 2 chart containers with Chart.js -- Semantic HTML, accessible labels
- [x] `frontend/style.css` -- Form styling, card layout, responsive grid, gradient backgrounds, mobile-first -- Readability and UX
- [x] `frontend/app.js` -- API client, form state management, Chart.js initialization, real-time updates -- Fetch API with error handling
- [x] `frontend/Dockerfile` -- Python http.server on port 3000 -- Simple, lightweight deployment

**Acceptance Criteria:**
- Given user lands on page, when page loads, then form is pre-filled with placeholder defaults and daily/monthly charts are rendered with zero data
- Given user enters valid inputs and clicks Simulate, when API responds, then summary cards update and both graphs refresh with new data within <500ms
- Given user enters invalid input (e.g., latitude > 90), when clicking Simulate, then input validation prevents request and displays error message
- Given user is on mobile, when viewport is <768px, then form and charts stack vertically without horizontal scrolling

## Design Notes

### Form Layout
```
[Latitude] [Longitude]
[Panel Count] [Panel Area (m²)]
[Efficiency (%)] [Tilt (°)]
[Azimuth (°)] [Start Date]
[Duration (days)] [Simulate Button]
```

### Result Display
- Summary cards: 4 boxes showing annual kWh, daily avg, peak kW, capacity
- Daily graph: Line chart, 24 hours, kW per hour
- Yearly graph: Bar chart, 12 months, kWh per month

### Error Handling
- Network errors: "Failed to connect to backend"
- Validation errors: Field-level error messages from backend (422 response)
- Calculation errors: "Simulation failed — check inputs"

## Verification

**Manual checks:**
- Page loads with Chart.js loaded (check DevTools Network)
- Form fields have correct input types (number, date, etc.)
- Placeholder values visible in form on page load
- Click Simulate → API call visible in Network tab
- Charts render and update without page reload
- Responsive on mobile (iPhone/iPad viewport)
- No console errors in DevTools

## Suggested Review Order

**API Integration & Data Flow**

- Fetch API call to backend, error handling for validation and network failures
  [`frontend/app.js:104`](../../../frontend/app.js#L104)

- Form data serialization and payload construction matching backend schema
  [`frontend/app.js:85`](../../../frontend/app.js#L85)

**Chart Rendering**

- Chart.js initialization with default empty data and responsive sizing
  [`frontend/app.js:40`](../../../frontend/app.js#L40)

- Dynamic chart updates on API response with formatted tooltips
  [`frontend/app.js:128`](../../../frontend/app.js#L128)

**User Interface**

- Input form with 9 fields, default placeholder values on load
  [`frontend/index.html:15`](../../../frontend/index.html#L15)

- Result cards and chart containers (hidden until simulation completes)
  [`frontend/index.html:80`](../../../frontend/index.html#L80)

- Responsive CSS grid layout with gradient styling
  [`frontend/style.css:1`](../../../frontend/style.css#L1)

**Error Handling & UX**

- Field-level error display for validation failures from backend
  [`frontend/app.js:156`](../../../frontend/app.js#L156)

- Loading spinner and disabled button state during API request
  [`frontend/index.html:91`](../../../frontend/index.html#L91)

**Deployment**

- Python http.server Dockerfile for simple static file serving on port 3000
  [`frontend/Dockerfile:1`](../../../frontend/Dockerfile#L1)
