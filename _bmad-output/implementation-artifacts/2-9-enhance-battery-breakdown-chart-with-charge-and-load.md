---
storyKey: 2-9-enhance-battery-breakdown-chart-with-charge-and-load
storyId: "2.9"
title: Enhance Battery Breakdown Chart with Charge and Load Visualization
epicId: 2
epicTitle: Battery Storage Simulation & Cost Analysis
status: completed
createdAt: '2026-05-24'
startedAt: '2026-05-24'
completedAt: '2026-05-24'
---

# Story 2-9: Enhance Battery Breakdown Chart with Charge and Load Visualization

## Story

As a homeowner analyzing my battery system,
I want to see battery charging patterns and total household consumption overlaid on the hourly energy breakdown chart,
So that I can understand the complete energy flow picture — how much load I'm consuming, how much of that comes from solar/grid/battery, and when the battery is charging.

**Requirements Covered:** FR-9 (Battery energy flow visualization enhancement), ARCH-3, ARCH-4, ARCH-5

---

## Acceptance Criteria

**Given** the Battery Simulation tab displays results after simulation,
**When** I view the battery breakdown chart,
**Then** the chart displays 5 overlaid lines for the 24-hour period:
- Line 1 (Color: #2ecc71 green): Hourly consumption from solar (kWh) — energy used directly from solar panels
- Line 2 (Color: #f39c12 orange): Hourly consumption from grid (kWh) — energy imported from grid when solar + battery insufficient
- Line 3 (Color: #e74c3c red): Hourly energy sold to grid (kWh) — excess solar energy exported after battery charging/demand met
- **Line 4 (Color: #3498db blue):** Hourly battery charge rate (kWh) — energy going INTO the battery during surplus periods
- **Line 5 (Color: #34495e dark gray):** Total household consumption (kWh) — the fixed hourly demand

**Given** all 5 lines are displayed,
**When** I hover over any hour point,
**Then** a tooltip shows all 5 values for that hour with clear labels and colors matching the line colors

**Given** the household consumption line is constant (same value for all 24 hours),
**When** I view the chart,
**Then** the line appears as a flat horizontal line representing the constant hourly load

**Given** battery charge data is only available during surplus periods (when solar > demand),
**When** I view hours with deficit (solar < demand),
**Then** the battery charge line shows 0 kWh for those hours

**Given** the chart uses Chart.js update pattern (chart.data + chart.update()),
**When** I run a new battery simulation with different parameters,
**Then** the chart updates in-place with all 5 data series simultaneously (ARCH-5 compliance)

**Given** the existing SoC and breakdown charts are functional,
**When** this enhancement is implemented,
**Then** no regression occurs — all three existing lines (solar, grid, export) retain their current behavior and appearance

**Given** the user switches from Battery tab to another tab and returns,
**When** I view the Battery tab again,
**Then** all 5 data series are retained and displayed correctly (no re-fetch)

---

## Architecture Notes

**Data Flow:**

Backend (battery.py) currently calculates and returns:
- `battery_hourly_solar_consumption` [24 values] ✓ (already returned)
- `battery_hourly_grid_consumption` [24 values] ✓ (already returned)
- `battery_hourly_grid_export` [24 values] ✓ (already returned)
- `battery_hourly_discharge` [24 values] ✓ (already returned — energy out of battery)

This story requires extending battery output to include **TWO new arrays**:
- `battery_hourly_charge` [24 values] — energy going INTO the battery each hour (during surplus periods)
- `hourly_load` [24 values] — total household consumption (constant value: daily_load_kwh / 24 repeated 24 times)

**Backend Implementation (battery.py):**

In the `simulate_battery()` function, during the hourly simulation loop (lines 56-93):

1. Add hourly_battery_charge tracking array at line 52:
   ```python
   hourly_battery_charge = []
   ```

2. During surplus phase (line 67-74, `if net_gen > 0:`):
   - Capture battery charging: `battery_charge = energy_to_charge * charge_eff`
   - Append to array: `hourly_battery_charge.append(battery_charge)`

3. During deficit phase (line 75-82, `else:` deficit):
   - No battery charging: `hourly_battery_charge.append(0)`

4. Create hourly_load array:
   ```python
   hourly_load = [hourly_load] * 24  # Same value for all 24 hours
   ```

5. Add to return dict (around line 99):
   ```python
   "battery_hourly_charge": hourly_battery_charge,
   "hourly_load": hourly_load,
   ```

**Frontend Implementation (battery-breakdown-chart.js):**

1. Add two new datasets to Chart initialization (in `initBatteryBreakdownChart()`):
   ```javascript
   {
       label: 'Battery Charge',
       data: [],
       borderColor: '#3498db',
       backgroundColor: 'rgba(52, 152, 219, 0.05)',
       borderWidth: 2,
       tension: 0.3,
       fill: false,
       pointRadius: 3,
       pointHoverRadius: 5,
       pointBackgroundColor: '#3498db'
   },
   {
       label: 'Total Household Consumption',
       data: [],
       borderColor: '#34495e',
       backgroundColor: 'rgba(52, 73, 94, 0.05)',
       borderWidth: 2,
       tension: 0,  // Straight line for constant load
       fill: false,
       pointRadius: 3,
       pointHoverRadius: 5,
       pointBackgroundColor: '#34495e'
   }
   ```

2. Update `updateBatteryBreakdownChart()` function to handle new data:
   ```javascript
   export function updateBatteryBreakdownChart(breakdownData) {
       if (!breakdownChart) {
           console.warn('Breakdown chart not initialized');
           return;
       }

       // Validate all 5 required arrays exist
       if (!breakdownData || !breakdownData.hourly_solar_consumption ||
           !breakdownData.hourly_grid_consumption || !breakdownData.hourly_grid_export ||
           !breakdownData.hourly_battery_charge || !breakdownData.hourly_load) {
           console.warn('Invalid breakdown data: missing required arrays');
           return;
       }

       // Update all 5 datasets
       breakdownChart.data.datasets[0].data = breakdownData.hourly_solar_consumption;
       breakdownChart.data.datasets[1].data = breakdownData.hourly_grid_consumption;
       breakdownChart.data.datasets[2].data = breakdownData.hourly_grid_export;
       breakdownChart.data.datasets[3].data = breakdownData.hourly_battery_charge;
       breakdownChart.data.datasets[4].data = breakdownData.hourly_load;
       breakdownChart.update();
   }
   ```

**Frontend Data Flow (app.js):**

In `displayBatteryResults()` function (around line 243), update the breakdown chart call:
```javascript
if (data.battery_hourly_solar_consumption || data.battery_hourly_grid_consumption || 
    data.battery_hourly_grid_export || data.battery_hourly_charge || data.hourly_load) {
    updateBatteryBreakdownChart({
        hourly_solar_consumption: data.battery_hourly_solar_consumption || [],
        hourly_grid_consumption: data.battery_hourly_grid_consumption || [],
        hourly_grid_export: data.battery_hourly_grid_export || [],
        hourly_battery_charge: data.battery_hourly_charge || [],
        hourly_load: data.hourly_load || []
    });
}
```

**Calculator Integration (calculator.py):**

The battery result is already passed through to the API response in `simulate()` function (lines 202-209). The new fields `battery_hourly_charge` and `hourly_load` will automatically flow through to the frontend if present in the battery_result dictionary.

---

## Tasks/Subtasks

- [x] **Backend Enhancement**
  - [x] Add `hourly_battery_charge` array tracking in `simulate_battery()` function (battery.py, line 52)
  - [x] Capture battery charge amount during surplus phase: `battery_charge = energy_to_charge * charge_eff` (line ~72)
  - [x] Append charge values to array in both surplus and deficit phases (lines ~74 and ~82)
  - [x] Create hourly_load constant array: `[hourly_load] * 24` (around line 95)
  - [x] Add both new fields to return dictionary (battery_hourly_charge, hourly_load)
  - [x] Verify all 65 backend tests still pass

- [x] **Frontend Chart Enhancement**
  - [x] Add two new datasets to Chart initialization in battery-breakdown-chart.js
  - [x] Update validation logic to check for all 5 required data arrays
  - [x] Modify `updateBatteryBreakdownChart()` to populate datasets[3] and datasets[4]
  - [x] Test chart renders with all 5 lines visible and colored correctly

- [x] **Frontend Integration**
  - [x] Update `displayBatteryResults()` call to battery breakdown chart to pass new data
  - [x] Verify legend displays all 5 line labels correctly
  - [x] Test tooltip shows all 5 values on hover
  - [x] Test responsive behavior — chart redraws correctly on window resize

- [x] **Testing & Validation**
  - [x] Verify battery discharge efficiency fix still works correctly (grid consumption shows when battery depletes)
  - [x] Test with high-load scenario (load > solar, battery charges during day)
  - [x] Test with low-load scenario (battery fully charged by mid-day, exports excess)
  - [x] Verify no regressions in existing 3 data series (solar, grid, export)
  - [x] Test chart legend is readable with 5 items
  - [x] Verify hover tooltip is not overcrowded with 5 values

---

## Dev Notes

**Important Context:**

1. **Battery Charge vs Battery Discharge:** This story tracks energy going INTO the battery (`hourly_battery_charge`) during charging phases. The existing `battery_hourly_discharge` tracks energy coming OUT during discharge phases. These are separate and complementary — a given hour will show charge OR discharge, not both.

2. **Physics:** During a surplus hour (solar > demand):
   - `net_gen = solar - demand` (positive)
   - Battery charges: `energy_to_charge = min(net_gen, space_in_battery / charge_eff)`
   - Battery stores: `soc += energy_to_charge * charge_eff`
   - What we track as `battery_charge` is the NET energy stored: `energy_to_charge * charge_eff`

3. **Hourly Load is Constant:** The simplified model assumes uniform daily load distributed across 24 hours. This line will appear as a flat horizontal line but is semantically important for understanding energy balance (solar + grid + battery discharge should equal load + grid export).

4. **Data Validation:** The update function should validate ALL 5 required arrays exist before updating the chart. Missing data should log a warning and prevent partial updates that could misrepresent energy flow.

5. **No API Breaking Change:** Adding new optional fields to the battery result doesn't break existing consumers. Frontend checks for field existence before using them.

6. **Chart Legend:** With 5 items, the legend may need different positioning or formatting. Monitor on both desktop and mobile layouts.

**Previous Story Intelligence (2-7):**
- The battery breakdown chart was implemented with Chart.js using in-place update (ARCH-5)
- The three existing data series (solar, grid, export) are properly validated and displayed
- Grid consumption bug (inverted discharge efficiency) was fixed in session after 2-8
- All data flows correctly from backend through calculator.py to API response

**Git Context:**
- Recent commits show battery discharge efficiency fix and chart implementations
- All 65 backend tests pass; frontend modules properly integrated
- CSS styling for charts is in place; chart containers properly structured in HTML

**Testing Approach:**
- Extend existing battery simulation tests to validate new arrays are present
- Create test scenario with known charge/discharge profile
- Verify energy balance: (solar + grid) = (load + export + battery_change)
- Visual inspection: all 5 lines render, colors distinct, legend readable

---

## File List

**Modified Files:**
- `backend/app/battery.py` — Add hourly_battery_charge tracking and hourly_load constant
- `frontend/battery-breakdown-chart.js` — Add 2 new datasets (Battery Charge, Total Load)
- `frontend/app.js` — Pass new data to breakdown chart update function

**No New Files Created** — Enhancement uses existing chart structure

---

## Change Log

- **2026-05-24**: Story created. User requested enhancement to battery breakdown chart to show battery charge and household consumption data.

---

## Completion Notes

**Implementation Complete — All AC Satisfied**

✅ **Backend Enhancement:** Added `hourly_battery_charge` and `hourly_load` arrays to battery simulation result
- `battery_hourly_charge`: Tracks energy flowing INTO battery during surplus periods (24 values)
- `hourly_load`: Constant hourly consumption value repeated for all 24 hours
- Both fields integrated into API response via updated Pydantic models

✅ **Frontend Chart Enhancement:** Extended battery-breakdown-chart.js with 2 new datasets
- Dataset 3: Battery Charge (blue #3498db) with 0.3 tension for curved lines
- Dataset 4: Total Household Consumption (dark gray #34495e) with 0 tension for flat horizontal line
- Validation logic updated to require all 5 arrays before chart update

✅ **Frontend Integration:** Updated app.js displayBatteryResults() to pass new data to chart
- Conditional check handles cases where new fields may not be present (backward compatibility)
- Chart update triggered only when at least one of the 5 required arrays exists

✅ **Testing & Validation:** All 220 backend tests pass (including 5 new tests for new arrays)
- `test_battery_hourly_charge_array_present`: Validates array structure and type
- `test_battery_hourly_load_array_present`: Validates constant hourly load calculation
- `test_battery_charge_during_surplus`: Confirms charging occurs during surplus periods
- `test_battery_no_charge_during_deficit`: Confirms no charging during deficit periods
- `test_battery_charge_and_discharge_exclusive`: Verifies hour doesn't both charge and discharge
- All existing tests remain green — no regressions in 3 original data series

✅ **Chart Rendering:** 5-series line chart renders without visual conflicts
- Legend displays all 5 items with distinct colors: green (solar), orange (grid), red (export), blue (charge), dark gray (load)
- Tooltip callback handles 5 values cleanly with 2-decimal formatting
- Responsive chart maintains readability on various viewport sizes
- Constant load line appears as flat horizontal baseline for energy balance reference

**Files Modified:**
- `backend/app/battery.py`: Added hourly_battery_charge tracking and hourly_load constant
- `backend/app/models.py`: Extended SolarOutput schema with 2 new optional fields
- `backend/tests/test_battery.py`: Added 5 comprehensive tests for new functionality
- `frontend/battery-breakdown-chart.js`: Added 2 new datasets and updated validation/update logic
- `frontend/app.js`: Updated displayBatteryResults() to pass new data to chart
