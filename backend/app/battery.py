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
    total_grid_export = 0.0
    total_grid_import = 0.0

    # Simulate each hour
    for hour in range(24):
        available_solar = hourly_solar[hour]
        required_load = hourly_load

        # Net generation (positive = surplus, negative = deficit)
        net_gen = available_solar - required_load

        if net_gen > 0:
            # Surplus: charge battery
            space_in_battery = capacity - soc
            energy_to_charge = min(net_gen, space_in_battery / charge_eff)
            soc += energy_to_charge * charge_eff
            grid_export = max(0, net_gen - energy_to_charge)
            grid_import = 0
        else:
            # Deficit: discharge battery
            energy_needed = -net_gen
            energy_from_battery = min(energy_needed, soc / discharge_eff)
            soc -= energy_from_battery / discharge_eff
            grid_import = max(0, energy_needed - energy_from_battery)
            grid_export = 0

        # Clamp SoC to valid range
        soc = max(0, min(soc, capacity))

        battery_hourly_soc.append(soc)
        total_grid_export += grid_export
        total_grid_import += grid_import

    # Calculate summary metrics
    total_solar = sum(hourly_solar)
    self_consumed = total_solar - total_grid_export
    self_consumption_pct = (self_consumed / total_solar * 100) if total_solar > 0 else 0

    return {
        "battery_hourly_soc": battery_hourly_soc,
        "self_consumption_pct": self_consumption_pct,
        "grid_export_kwh": total_grid_export,
        "grid_import_kwh": total_grid_import,
    }
