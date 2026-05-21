"""
Solar Panel Simulator - Irradiance Calculations
Clear-sky model (Laue/Meinel transmittance + Kasten-Young air mass),
seasonal cloud factor, Erbs decomposition, and isotropic-sky transposition.
"""

import math
from datetime import datetime

from app.constants import GROUND_ALBEDO, SOLAR_CONSTANT_WM2
from app.solar_position import day_of_year, hourly_sun_position


def extraterrestrial_irradiance(doy: int) -> float:
    """
    Extraterrestrial normal irradiance, corrected for Earth-Sun distance.
    Spencer (1971) eccentricity correction.
    """
    b = 2 * math.pi * (doy - 1) / 365
    e0 = (
        1.00011
        + 0.034221 * math.cos(b)
        + 0.00128 * math.sin(b)
        + 0.000719 * math.cos(2 * b)
        + 0.000077 * math.sin(2 * b)
    )
    return SOLAR_CONSTANT_WM2 * e0


def air_mass(elevation_deg: float) -> float:
    """
    Relative optical air mass (Kasten & Young 1989).
    Works down to elevations near 0° (unlike 1/sin(elev)).
    """
    if elevation_deg <= 0:
        return float("inf")
    z = 90.0 - elevation_deg
    z_rad = math.radians(z)
    return 1.0 / (math.cos(z_rad) + 0.50572 * (96.07995 - z) ** -1.6364)


def clear_sky_dni(elevation_deg: float, doy: int) -> float:
    """
    Clear-sky Direct Normal Irradiance using Laue/Meinel atmospheric
    transmittance: tau = 0.7^(AM^0.678).
    """
    if elevation_deg <= 0:
        return 0.0
    i0 = extraterrestrial_irradiance(doy)
    am = air_mass(elevation_deg)
    tau = 0.7 ** (am**0.678)
    return i0 * tau


def clear_sky_ghi(elevation_deg: float, doy: int) -> float:
    """
    Clear-sky Global Horizontal Irradiance.
    GHI_clear = DNI*sin(elev) + DHI_clear, where DHI_clear is approximated
    as ~13% of beam-on-horizontal under clear conditions.
    """
    if elevation_deg <= 0:
        return 0.0
    dni = clear_sky_dni(elevation_deg, doy)
    sin_elev = math.sin(math.radians(elevation_deg))
    direct_horizontal = dni * sin_elev
    diffuse_horizontal = 0.13 * direct_horizontal
    return direct_horizontal + diffuse_horizontal


def cloud_factor(latitude: float, doy: int) -> float:
    """
    Heuristic seasonal cloud transmittance (0 = fully overcast, 1 = clear).
    Northern hemisphere is cloudiest in winter; southern hemisphere is
    cloudiest during the NH summer. Amplitude grows with |latitude| since
    higher latitudes have stronger seasonal variation in cloudiness.
    """
    sign = 1.0 if latitude >= 0 else -1.0
    # Peak clarity around the summer solstice (doy 172 for NH).
    angle = 2.0 * math.pi * (doy - 172) / 365.0 * sign
    amplitude = 0.15 + min(abs(latitude), 60.0) / 60.0 * 0.10
    base = 0.65
    return max(0.05, min(1.0, base + amplitude * math.cos(angle)))


def decompose_ghi(ghi: float, elevation_deg: float, doy: int) -> tuple[float, float]:
    """
    Split GHI into DNI and DHI using the Erbs et al. (1982) diffuse fraction
    correlation. Returns (dni, dhi) in W/m^2.
    """
    if elevation_deg <= 0 or ghi <= 0:
        return (0.0, 0.0)

    ghi_clear = clear_sky_ghi(elevation_deg, doy)
    if ghi_clear <= 0:
        return (0.0, 0.0)

    kt = min(1.0, max(0.0, ghi / ghi_clear))

    if kt <= 0.22:
        df = 1.0 - 0.09 * kt
    elif kt <= 0.80:
        df = 0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4
    else:
        df = 0.165

    dhi = ghi * df
    direct_horizontal = ghi - dhi
    sin_elev = math.sin(math.radians(elevation_deg))
    dni = direct_horizontal / sin_elev if sin_elev > 0 else 0.0
    return (dni, dhi)


def tilted_irradiance(
    ghi: float,
    dhi: float,
    dni: float,
    elevation_deg: float,
    tilt_deg: float,
    sun_azimuth_deg: float,
    surface_azimuth_deg: float,
) -> float:
    """
    Total irradiance on a tilted surface (isotropic sky transposition).
        Beam      = DNI * cos(theta)
        Diffuse   = DHI * (1 + cos(tilt)) / 2
        Reflected = GHI * albedo * (1 - cos(tilt)) / 2
    """
    tilt_rad = math.radians(tilt_deg)

    diffuse_tilted = dhi * (1.0 + math.cos(tilt_rad)) / 2.0
    reflected = ghi * GROUND_ALBEDO * (1.0 - math.cos(tilt_rad)) / 2.0

    if elevation_deg <= 0:
        return max(0.0, diffuse_tilted + reflected)

    sun_elev_rad = math.radians(elevation_deg)
    sun_az_rad = math.radians(sun_azimuth_deg)
    surf_az_rad = math.radians(surface_azimuth_deg)

    cos_theta = math.sin(sun_elev_rad) * math.cos(tilt_rad) + math.cos(sun_elev_rad) * math.sin(
        tilt_rad
    ) * math.cos(sun_az_rad - surf_az_rad)
    cos_theta = max(0.0, cos_theta)

    beam_tilted = dni * cos_theta
    return beam_tilted + diffuse_tilted + reflected


def hourly_irradiance(
    latitude: float, longitude: float, date: datetime, hour: int, tilt: float, azimuth: float
) -> float:
    """
    Tilted-plane irradiance (W/m^2) for the given hour, derived from a
    clear-sky model attenuated by a seasonal cloud factor.
    """
    doy = day_of_year(date)
    elevation, sun_azimuth = hourly_sun_position(latitude, longitude, date, hour)

    if elevation <= 0:
        return 0.0

    ghi_clear = clear_sky_ghi(elevation, doy)
    cf = cloud_factor(latitude, doy)
    ghi = ghi_clear * cf

    dni, dhi = decompose_ghi(ghi, elevation, doy)
    return tilted_irradiance(ghi, dhi, dni, elevation, tilt, sun_azimuth, azimuth)
