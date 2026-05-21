"""
Solar Panel Simulator - Solar Position Calculations
NOAA solar position algorithm for sunrise/sunset and sun position
"""

import math
from datetime import datetime, timedelta

from app.constants import CIVIL_TWILIGHT_ANGLE


def julian_day(date: datetime) -> float:
    """Calculate Julian Day Number for a given date."""
    a = (14 - date.month) // 12
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3
    jdn = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn + (date.hour - 12) / 24.0


def day_of_year(date: datetime) -> int:
    """Get day of year (1-366)."""
    return date.timetuple().tm_yday


def equation_of_time(julian_day_num: float) -> float:
    """
    Equation of time in minutes (positive = sundial ahead of clock).
    NOAA solar position algorithm.
    """
    t = (julian_day_num - 2451545.0) / 36525.0  # Julian centuries since J2000

    # Geometric mean longitude of sun (deg)
    l0 = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360

    # Mean anomaly of sun (deg)
    m = 357.52911 + t * (35999.05029 - t * 0.0001537)
    m_rad = math.radians(m)

    # Eccentricity of Earth's orbit
    e = 0.016708634 - t * (0.000042037 + t * 0.0000001267)

    # Mean obliquity of the ecliptic (deg, arcseconds form)
    epsilon0 = 23.0 + (26.0 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60.0) / 60.0

    # Corrected obliquity (small nutation term)
    omega = 125.04 - 1934.136 * t
    epsilon = epsilon0 + 0.00256 * math.cos(math.radians(omega))

    y = math.tan(math.radians(epsilon / 2.0)) ** 2

    eot_rad = (
        y * math.sin(2.0 * math.radians(l0))
        - 2.0 * e * math.sin(m_rad)
        + 4.0 * e * y * math.sin(m_rad) * math.cos(2.0 * math.radians(l0))
        - 0.5 * y * y * math.sin(4.0 * math.radians(l0))
        - 1.25 * e * e * math.sin(2.0 * m_rad)
    )

    return math.degrees(eot_rad) * 4.0  # Minutes


def sun_declination(julian_day_num: float) -> float:
    """Calculate sun's declination angle in degrees."""
    jd = julian_day_num - 2451545.0
    jc = jd / 36525.0

    # Mean longitude of ascending node of lunar orbit
    omega = 125.04452 - jc * 1934.136461

    # Mean longitude of sun
    l0 = 280.46646 + jc * (36000.76983 + jc * 0.0003032)

    # Mean anomaly of sun
    m = 357.52911 + jc * (35999.05029 - jc * 0.0001536)
    m_rad = math.radians(m)

    # Equation of center
    c = (
        (1.914602 - jc * (0.004817 + jc * 0.000014)) * math.sin(m_rad)
        + (0.019993 - jc * 0.000101) * math.sin(2 * m_rad)
        + 0.000029 * math.sin(3 * m_rad)
    )

    # True longitude
    sun_lon = l0 + c

    # Apparent longitude
    lambda_sun = sun_lon - 0.00569 - 0.00478 * math.sin(math.radians(omega))

    # Obliquity of ecliptic
    epsilon = 23.439291 - jc * 0.0130042 - jc * jc * 0.00000164 + jc * jc * jc * 0.000000504

    # Declination
    delta = math.degrees(
        math.asin(math.sin(math.radians(epsilon)) * math.sin(math.radians(lambda_sun)))
    )
    return delta


def sunrise_sunset(latitude: float, longitude: float, date: datetime) -> tuple:
    """
    Calculate sunrise and sunset times (civil twilight, sun -6° below horizon).
    Returns: (sunrise_time, sunset_time) as datetime objects in UTC.

    For polar night returns (date, date); for midnight sun returns
    (date, date + 1 day).
    """
    jd = julian_day(date)
    delta = sun_declination(jd)

    lat_rad = math.radians(latitude)
    delta_rad = math.radians(delta)
    sin_altitude_threshold = math.sin(math.radians(CIVIL_TWILIGHT_ANGLE))

    denom = math.cos(lat_rad) * math.cos(delta_rad)
    if abs(denom) < 1e-9:
        return (date, date)

    cos_h0 = (sin_altitude_threshold - math.sin(lat_rad) * math.sin(delta_rad)) / denom

    if cos_h0 > 1.0:
        return (date, date)  # Polar night
    if cos_h0 < -1.0:
        return (date, date + timedelta(days=1))  # Midnight sun

    h0_deg = math.degrees(math.acos(cos_h0))

    # Solar noon in UTC hours: LST = UTC + longitude/15 + EoT/60
    eot_minutes = equation_of_time(jd)
    solar_noon_utc = 12.0 - longitude / 15.0 - eot_minutes / 60.0

    sunrise_hour = solar_noon_utc - h0_deg / 15.0
    sunset_hour = solar_noon_utc + h0_deg / 15.0

    sunrise = date + timedelta(hours=sunrise_hour)
    sunset = date + timedelta(hours=sunset_hour)
    return (sunrise, sunset)


def sun_elevation(latitude: float, longitude: float, date: datetime) -> float:
    """Calculate sun elevation angle in degrees at solar noon."""
    jd = julian_day(date)
    declination = sun_declination(jd)

    # Hour angle at solar noon (0)
    h = 0

    # Elevation angle
    sin_elevation = math.sin(math.radians(latitude)) * math.sin(
        math.radians(declination)
    ) + math.cos(math.radians(latitude)) * math.cos(math.radians(declination)) * math.cos(
        math.radians(h)
    )

    elevation = math.degrees(math.asin(sin_elevation))
    return elevation


def hourly_sun_position(latitude: float, longitude: float, date: datetime, hour: int) -> tuple:
    """
    Calculate sun elevation and azimuth at the given UTC hour.
    Azimuth convention: 0=N, 90=E, 180=S, 270=W.
    Returns: (elevation_degrees, azimuth_degrees)
    """
    jd = julian_day(date)
    declination = sun_declination(jd)
    eot = equation_of_time(jd)

    # Local solar time: LST = UTC + longitude/15 + EoT/60
    solar_time = hour + longitude / 15.0 + eot / 60.0
    h = (solar_time - 12.0) * 15.0  # Hour angle: negative=morning, positive=afternoon

    lat_rad = math.radians(latitude)
    decl_rad = math.radians(declination)
    h_rad = math.radians(h)

    sin_elevation = math.sin(lat_rad) * math.sin(decl_rad) + math.cos(lat_rad) * math.cos(
        decl_rad
    ) * math.cos(h_rad)
    sin_elevation = max(-1.0, min(1.0, sin_elevation))
    elevation = math.degrees(math.asin(sin_elevation))

    cos_elev = math.cos(math.radians(elevation))
    if abs(cos_elev) < 1e-9 or abs(math.cos(lat_rad)) < 1e-9:
        return (elevation, 180.0)

    cos_azimuth = (math.sin(decl_rad) - math.sin(lat_rad) * sin_elevation) / (
        math.cos(lat_rad) * cos_elev
    )
    cos_azimuth = max(-1.0, min(1.0, cos_azimuth))
    azimuth = math.degrees(math.acos(cos_azimuth))

    # acos gives 0-180. Sun is west of meridian after solar noon (h > 0).
    if h > 0:
        azimuth = 360.0 - azimuth

    return (elevation, azimuth)
