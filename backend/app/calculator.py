"""
Solar Panel Simulator - Solar Calculator
Main calculation engine orchestrating all solar simulations
"""

import math
from datetime import datetime, timedelta

from app.constants import (
    AMBIENT_TEMP_AMPLITUDE_C,
    AMBIENT_TEMP_MEAN_C,
    HOURS_PER_DAY,
    MODULE_TEMP_RISE_COEFF,
    MONTHS_PER_YEAR,
    SYSTEM_LOSSES_FACTOR,
    TEMP_DERATING_COEFF,
    TEMP_REFERENCE,
)
from app.irradiance import hourly_irradiance
from app.models import SolarInput, SolarOutput
from app.solar_position import day_of_year, sunrise_sunset


def seasonal_ambient_temperature(latitude: float, doy: int) -> float:
    """
    Heuristic seasonal ambient temperature (°C). Warmer in local summer,
    cooler in local winter. Northern hemisphere peaks around doy 200
    (late July, lagging the solstice); southern hemisphere is inverted.
    """
    sign = 1.0 if latitude >= 0 else -1.0
    angle = 2.0 * math.pi * (doy - 200) / 365.0 * sign
    return AMBIENT_TEMP_MEAN_C + AMBIENT_TEMP_AMPLITUDE_C * math.cos(angle)


def adjust_efficiency_for_temperature(base_efficiency: float, module_temp: float) -> float:
    """
    Adjust PV efficiency based on module temperature.
    efficiency = base_efficiency * (1 - 0.004 * (T_module - 25°C))
    """
    delta_temp = module_temp - TEMP_REFERENCE
    adjustment = 1 - (TEMP_DERATING_COEFF * delta_temp)
    return base_efficiency * max(0, adjustment)


def calculate_module_temperature(ambient_temp: float, irradiance: float) -> float:
    """
    Estimate module temperature from ambient temperature and irradiance.
    T_module = T_ambient + irradiance * 0.03°C per W/m²
    """
    return ambient_temp + (irradiance * MODULE_TEMP_RISE_COEFF)


def calculate_hourly_energy(
    panel_area: float, base_efficiency: float, irradiance: float, ambient_temp: float
) -> tuple[float, float]:
    """
    Calculate power and energy for one hour.
    Returns: (power_kw, energy_kwh)
    """
    # Module temperature
    module_temp = calculate_module_temperature(ambient_temp, irradiance)

    # Adjusted efficiency
    adjusted_efficiency = adjust_efficiency_for_temperature(base_efficiency, module_temp)

    # Power output (W)
    power_w = panel_area * adjusted_efficiency * irradiance * SYSTEM_LOSSES_FACTOR

    # Energy for 1 hour (Wh to kWh)
    energy_kwh = power_w / 1000

    return (power_w / 1000, energy_kwh)  # Return in kW and kWh


def calculate_daily_profile(
    latitude: float,
    longitude: float,
    date: datetime,
    panel_area: float,
    base_efficiency: float,
    tilt_angle: float,
    azimuth: float,
) -> tuple[list[float], float, float, str, str]:
    """
    Calculate hourly generation profile for a single day.
    Returns: (hourly_generation_kw, daily_total_kwh, peak_kw, sunrise_str, sunset_str)
    """
    hourly_generation = []
    daily_total = 0
    peak_power = 0

    # Get sunrise/sunset
    sunrise_time, sunset_time = sunrise_sunset(latitude, longitude, date)

    ambient_temp = seasonal_ambient_temperature(latitude, day_of_year(date))

    for hour in range(HOURS_PER_DAY):
        # Irradiance for this hour
        irradiance = hourly_irradiance(latitude, longitude, date, hour, tilt_angle, azimuth)

        # Hourly energy
        power_kw, energy_kwh = calculate_hourly_energy(
            panel_area, base_efficiency, irradiance, ambient_temp
        )

        hourly_generation.append(power_kw)
        daily_total += energy_kwh
        peak_power = max(peak_power, power_kw)

    # Format times
    sunrise_str = sunrise_time.strftime("%H:%M")
    sunset_str = sunset_time.strftime("%H:%M")

    return (hourly_generation, daily_total, peak_power, sunrise_str, sunset_str)


def simulate(input_data: SolarInput) -> SolarOutput:
    """
    Run complete solar simulation for given parameters.
    """
    # Parse start date
    start_date = datetime.strptime(input_data.start_date, "%Y-%m-%d")

    # Total panel area
    total_area = input_data.panel_count * input_data.panel_area_m2

    # System capacity in kW
    system_capacity_kw = (total_area * input_data.panel_efficiency / 100) * 1000 / 1000

    # Initialize tracking
    annual_energy = 0
    peak_hour_kw = 0
    monthly_totals = [0.0] * MONTHS_PER_YEAR

    # Simulate each day
    current_date = start_date
    first_day_profile = None
    sunrise_first = None
    sunset_first = None

    for day_num in range(input_data.duration_days):
        # Calculate daily profile
        hourly_gen, daily_kwh, peak_kw, sunrise_str, sunset_str = calculate_daily_profile(
            input_data.latitude,
            input_data.longitude,
            current_date,
            total_area,
            input_data.panel_efficiency / 100,
            input_data.tilt_angle_deg,
            input_data.azimuth_deg,
        )

        # Accumulate
        annual_energy += daily_kwh
        peak_hour_kw = max(peak_hour_kw, peak_kw)

        # Store first day profile
        if day_num == 0:
            first_day_profile = hourly_gen
            sunrise_first = sunrise_str
            sunset_first = sunset_str

        # Add to monthly total
        month_idx = current_date.month - 1
        monthly_totals[month_idx] += daily_kwh

        # Move to next day
        current_date += timedelta(days=1)

    # Calculate averages
    average_daily = annual_energy / input_data.duration_days

    # Build response
    return SolarOutput(
        annual_energy_kwh=round(annual_energy, 1),
        average_daily_kwh=round(average_daily, 2),
        peak_hour_kw=round(peak_hour_kw, 2),
        system_capacity_kw=round(system_capacity_kw, 2),
        daily_hourly_generation=[round(x, 3) for x in first_day_profile]
        if first_day_profile
        else [],
        daily_sunrise=sunrise_first,
        daily_sunset=sunset_first,
        monthly_energy_kwh=[round(x, 1) for x in monthly_totals],
        calculation_date=datetime.utcnow(),
    )
