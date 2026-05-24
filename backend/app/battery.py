"""
Battery simulation module - hourly energy balance modeling
Calculates battery state of charge, self-consumption, and grid metrics
"""


def simulate_battery(solar_output: dict, battery_params: dict) -> dict:
    """
    Simulate hourly battery energy balance for a day.

    Physics Model:
    - For each hour, calculate net generation = solar generation - load
    - If net > 0 (surplus): charge battery up to capacity (with charge efficiency loss)
    - If net < 0 (deficit): discharge battery to cover deficit (with discharge efficiency loss)
    - SoC always clamped to [0, capacity]
    - Excess solar exports to grid; unmet load imports from grid

    Args:
        solar_output: dict with 'daily_hourly_generation' (list of 24 floats, kWh)
        battery_params: dict with keys:
            - capacity_kwh: battery capacity (float, kWh)
            - charge_efficiency: charging efficiency (float, 0.8-0.99)
            - discharge_efficiency: discharging efficiency (float, 0.8-0.99)
            - daily_load_kwh: daily household load (float, kWh)
            - initial_soc_pct: initial state of charge (float, 0-100%)

    Returns:
        dict with:
            - battery_hourly_soc: list of 24 SoC values (kWh)
            - self_consumption_pct: percentage of solar used locally (0-100)
            - grid_export_kwh: total solar exported to grid (kWh)
            - grid_import_kwh: total energy imported from grid (kWh)
    """
    # Extract inputs
    hourly_solar = solar_output["daily_hourly_generation"]
    capacity = battery_params["capacity_kwh"]
    charge_eff = battery_params["charge_efficiency"]
    discharge_eff = battery_params["discharge_efficiency"]
    daily_load = battery_params["daily_load_kwh"]
    initial_soc_pct = battery_params["initial_soc_pct"]

    # Hourly load (uniform distribution across 24 hours)
    hourly_load = daily_load / 24

    # Initialize state
    soc = (initial_soc_pct / 100) * capacity  # Initial SoC in kWh
    battery_hourly_soc = []
    hourly_solar_consumption = []
    hourly_grid_consumption = []
    hourly_grid_export = []
    hourly_battery_discharge = []
    total_grid_export = 0.0
    total_grid_import = 0.0

    # Simulate each hour
    for hour in range(24):
        available_solar = hourly_solar[hour]
        required_load = hourly_load

        # Track solar consumption: energy directly from solar used for load
        solar_to_load = min(available_solar, required_load)
        hourly_solar_consumption.append(solar_to_load)

        # Net generation (positive = surplus, negative = deficit)
        net_gen = available_solar - required_load

        if net_gen > 0:
            # Surplus: charge battery
            space_in_battery = capacity - soc
            energy_to_charge = min(net_gen, space_in_battery / charge_eff)
            soc += energy_to_charge * charge_eff
            grid_export = max(0, net_gen - energy_to_charge)
            grid_import = 0
            battery_discharge = 0
        else:
            # Deficit: discharge battery
            energy_needed = -net_gen
            energy_from_battery = min(energy_needed, soc * discharge_eff)
            soc -= energy_from_battery / discharge_eff
            grid_import = max(0, energy_needed - energy_from_battery)
            grid_export = 0
            battery_discharge = energy_from_battery

        # Clamp SoC to valid range
        soc = max(0, min(soc, capacity))

        battery_hourly_soc.append(soc)
        hourly_grid_consumption.append(grid_import)
        hourly_grid_export.append(grid_export)
        hourly_battery_discharge.append(battery_discharge)
        total_grid_export += grid_export
        total_grid_import += grid_import

    # Calculate summary metrics
    total_solar = sum(hourly_solar)
    self_consumed = total_solar - total_grid_export
    self_consumption_pct = (self_consumed / total_solar * 100) if total_solar > 0 else 0

    return {
        "battery_hourly_soc": battery_hourly_soc,
        "battery_hourly_solar_consumption": hourly_solar_consumption,
        "battery_hourly_grid_consumption": hourly_grid_consumption,
        "battery_hourly_grid_export": hourly_grid_export,
        "battery_hourly_discharge": hourly_battery_discharge,
        "self_consumption_pct": self_consumption_pct,
        "grid_export_kwh": total_grid_export,
        "grid_import_kwh": total_grid_import,
    }


def aggregate_to_yearly(
    daily_hourly_breakdown: dict,
    start_date_str: str,
    duration_days: int
) -> dict:
    """
    Aggregate hourly breakdown data to monthly values.

    Assumes a single representative day's hourly breakdown is extrapolated to a full year
    or partial period. For each month covered by the simulation, daily totals are multiplied
    by the number of days in that month.

    Args:
        daily_hourly_breakdown: dict with hourly arrays:
            - 'hourly_solar_consumption': [24 floats]
            - 'hourly_grid_consumption': [24 floats]
            - 'hourly_grid_export': [24 floats]
        start_date_str: start date string in format "YYYY-MM-DD"
        duration_days: simulation duration in days

    Returns:
        dict with:
            - 'monthly_solar_consumption': list of up to 12 monthly totals (kWh)
            - 'monthly_grid_consumption': list of up to 12 monthly totals (kWh)
            - 'monthly_battery_discharge': list of up to 12 monthly totals (kWh)
    """
    from datetime import datetime, timedelta

    # Parse start date
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = start_date + timedelta(days=duration_days - 1)

    # Sum hourly arrays to daily totals
    daily_solar = sum(daily_hourly_breakdown.get("hourly_solar_consumption", []))
    daily_grid = sum(daily_hourly_breakdown.get("hourly_grid_consumption", []))
    daily_battery = sum(daily_hourly_breakdown.get("hourly_battery_discharge", []))

    # Initialize 12-month arrays
    monthly_solar = [0.0] * 12
    monthly_grid = [0.0] * 12
    monthly_battery = [0.0] * 12

    # For each month in the simulation period, calculate the number of days
    # and accumulate the daily totals
    current_date = start_date
    while current_date <= end_date:
        month_idx = current_date.month - 1
        year = current_date.year
        month = current_date.month

        # Find the last day of this month
        if month == 12:
            next_month_start = datetime(year + 1, 1, 1)
        else:
            next_month_start = datetime(year, month + 1, 1)

        # Calculate days in this month that fall within the simulation period
        month_start = current_date.replace(day=1)
        if month_start < start_date:
            month_start = start_date

        if next_month_start - timedelta(days=1) > end_date:
            month_end = end_date
        else:
            month_end = next_month_start - timedelta(days=1)

        days_in_month = (month_end - month_start).days + 1

        # Accumulate monthly totals
        monthly_solar[month_idx] += daily_solar * days_in_month
        monthly_grid[month_idx] += daily_grid * days_in_month
        monthly_battery[month_idx] += daily_battery * days_in_month

        # Move to next month
        if month == 12:
            current_date = datetime(year + 1, 1, 1)
        else:
            current_date = datetime(year, month + 1, 1)

    # Remove trailing zero months (months after simulation end)
    last_nonzero = 0
    for i in range(11, -1, -1):
        if monthly_solar[i] > 0 or monthly_grid[i] > 0 or monthly_battery[i] > 0:
            last_nonzero = i + 1
            break

    return {
        "monthly_solar_consumption": monthly_solar[:last_nonzero] if last_nonzero > 0 else [],
        "monthly_grid_consumption": monthly_grid[:last_nonzero] if last_nonzero > 0 else [],
        "monthly_battery_discharge": monthly_battery[:last_nonzero] if last_nonzero > 0 else [],
    }
