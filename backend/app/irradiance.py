"""
Solar Panel Simulator - Irradiance Calculations
GHI estimation and tilted-plane irradiance
"""

import math
from datetime import datetime
from app.constants import (
    SOLAR_CONSTANT_WM2,
    ANGSTROM_A,
    ANGSTROM_B,
    SEASONAL_MIN,
    SEASONAL_MAX,
)
from app.solar_position import day_of_year, hourly_sun_position


def clearness_index(doy: int) -> float:
    """
    Calculate clearness index based on day of year.
    Varies from SEASONAL_MIN (winter) to SEASONAL_MAX (summer).
    """
    angle = 2 * math.pi * (doy - 1) / 365
    index = SEASONAL_MIN + (SEASONAL_MAX - SEASONAL_MIN) * (1 - math.cos(angle)) / 2
    return index  # Seasonal variation without artificial cap


def extraterrestrial_irradiance(doy: int) -> float:
    """
    Calculate extraterrestrial irradiance (normal incidence).
    Based on solar constant and Earth-Sun distance variation.
    """
    b = 2 * math.pi * (doy - 1) / 365
    r = 1.00011 + 0.034221 * math.cos(b) + 0.00128 * math.sin(b) + 0.000719 * math.cos(2 * b) + 0.000077 * math.sin(2 * b)
    return SOLAR_CONSTANT_WM2 * r


def ghi_estimate(latitude: float, doy: int, hour: int) -> float:
    """
    Estimate Global Horizontal Irradiance using Ångström model.
    GHI = (a + b * daylight_fraction) * ExtraterrestrialIrradiance * seasonal_factor
    """
    # Daylight fraction (simplified)
    daylight_fraction = max(0, math.sin(2 * math.pi * (doy - 1) / 365 + math.radians(latitude) / 5))

    # Extraterrestrial irradiance
    i0 = extraterrestrial_irradiance(doy)

    # Clearness index (seasonal variation)
    kt = clearness_index(doy)

    # Simple hour-based reduction (no sun = 0)
    if hour < 6 or hour > 18:
        ghi = 0
    else:
        # Approximate irradiance by hour (cosine variation around solar noon)
        hour_angle = (hour - 12) * 15
        cos_factor = max(0, math.cos(math.radians(hour_angle)) * 1.2)  # Simplified
        ghi = i0 * kt * cos_factor

    return ghi


def dni_estimate(ghi: float, zenith: float) -> float:
    """
    Estimate Direct Normal Irradiance from GHI and solar zenith angle.
    Simplified relationship: DNI ≈ GHI / cos(zenith)
    """
    zenith_rad = math.radians(zenith)
    if zenith < 90 and math.cos(zenith_rad) > 0:
        return ghi / math.cos(zenith_rad)
    return 0


def dhi_estimate(ghi: float, dni: float, zenith: float) -> float:
    """
    Estimate Diffuse Horizontal Irradiance.
    DHI = GHI - DNI * cos(zenith)
    """
    zenith_rad = math.radians(zenith)
    dni_h = max(0, dni * math.cos(zenith_rad))
    dhi = ghi - dni_h
    return max(0, dhi)


def tilted_irradiance(ghi: float, dhi: float, dni: float, elevation: float,
                      tilt: float, azimuth: float, surface_azimuth: float) -> float:
    """
    Calculate irradiance on a tilted surface using transposition model.
    elevation: sun elevation angle (degrees)
    tilt: panel tilt angle (degrees)
    azimuth: sun azimuth angle (degrees)
    surface_azimuth: panel azimuth angle (degrees)
    """
    # Angle of incidence
    sun_elev_rad = math.radians(elevation)
    sun_azim_rad = math.radians(azimuth)
    tilt_rad = math.radians(tilt)
    surface_azim_rad = math.radians(surface_azimuth)

    # Zenith angle
    zenith = 90 - elevation

    # Angle of incidence on tilted surface
    cos_theta = (math.sin(sun_elev_rad) * math.cos(tilt_rad) +
                 math.cos(sun_elev_rad) * math.sin(tilt_rad) * math.cos(sun_azim_rad - surface_azim_rad))

    # Beam irradiance on tilted surface
    rb = cos_theta / math.cos(math.radians(zenith)) if math.cos(math.radians(zenith)) > 0 else 0
    rb = max(0, rb)

    # Beam component
    beam_tilted = dni * rb if elevation > 0 else 0

    # Diffuse (isotropic sky model)
    rd = (1 + math.cos(tilt_rad)) / 2
    diffuse_tilted = dhi * rd

    # Ground reflection (assuming 0.2 albedo)
    rr = (1 - math.cos(tilt_rad)) / 2
    reflected = ghi * 0.2 * rr

    # Total irradiance on tilted surface
    total = beam_tilted + diffuse_tilted + reflected
    return max(0, total)


def hourly_irradiance(latitude: float, longitude: float, date: datetime, hour: int,
                      tilt: float, azimuth: float) -> float:
    """
    Calculate hourly irradiance on a tilted panel.
    Returns total irradiance in W/m².
    """
    doy = day_of_year(date)

    # Sun position
    elevation, sun_azimuth = hourly_sun_position(latitude, longitude, date, hour)

    # Irradiance components
    ghi = ghi_estimate(latitude, doy, hour)
    zenith = 90 - elevation
    dni = dni_estimate(ghi, zenith)
    dhi = dhi_estimate(ghi, dni, zenith)

    # Tilted irradiance
    if elevation > 0:
        irradiance = tilted_irradiance(ghi, dhi, dni, elevation, tilt, sun_azimuth, azimuth)
    else:
        irradiance = 0

    return irradiance
