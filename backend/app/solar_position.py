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
    """Calculate equation of time in minutes (Spencer 1971)."""
    jd = julian_day_num - 2451545.0
    jc = jd / 36525.0

    # Mean longitude of sun
    l0 = 280.46646 + jc * (36000.76983 + jc * 0.0003032)
    l0 = l0 % 360

    # Mean anomaly of sun
    m = 357.52911 + jc * (35999.05029 - jc * 0.0001536)
    m_rad = math.radians(m)

    # Sun equation of center
    c = ((1.914602 - jc * (0.004817 + jc * 0.000014)) * math.sin(m_rad) +
         (0.019993 - jc * 0.000101) * math.sin(2 * m_rad) +
         0.000029 * math.sin(3 * m_rad))

    # True longitude
    sun_lon = l0 + c

    # Apparent longitude (with aberration)
    omega = 125.04 - jc * 1934.136
    lambda_sun = sun_lon - 0.00569 - 0.00478 * math.sin(math.radians(omega))

    # Equation of time
    epsilon = 23.439291 - jc * 0.0130042
    y = math.tan(math.radians(epsilon / 2))
    y = y * y

    eot = (y * math.sin(2 * math.radians(l0)) -
           2 * math.sin(math.radians(m)) * y * math.cos(2 * math.radians(l0)) +
           4 * math.sin(math.radians(m)) * y * math.cos(2 * math.radians(l0)) -
           0.5 * y * y * math.sin(4 * math.radians(l0)) -
           1.25 * math.sin(2 * math.radians(m)))

    return math.degrees(eot) * 4  # Convert to minutes


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
    c = ((1.914602 - jc * (0.004817 + jc * 0.000014)) * math.sin(m_rad) +
         (0.019993 - jc * 0.000101) * math.sin(2 * m_rad) +
         0.000029 * math.sin(3 * m_rad))

    # True longitude
    sun_lon = l0 + c

    # Apparent longitude
    lambda_sun = sun_lon - 0.00569 - 0.00478 * math.sin(math.radians(omega))

    # Obliquity of ecliptic
    epsilon = 23.439291 - jc * 0.0130042 - jc * jc * 0.00000164 + jc * jc * jc * 0.000000504

    # Declination
    delta = math.degrees(math.asin(math.sin(math.radians(epsilon)) * math.sin(math.radians(lambda_sun))))
    return delta


def sunrise_sunset(latitude: float, longitude: float, date: datetime) -> tuple:
    """
    Calculate sunrise and sunset times (civil twilight).
    Returns: (sunrise_time, sunset_time) as datetime objects in UTC.
    """
    jd = julian_day(date)
    n = jd - 2451545.0 - 0.0009
    n = math.floor(n + 0.5) - 0.5

    # Solar noon
    j_noon = n + 0.0009 + longitude / 360.0

    # Declination and equation of time
    m = (357.52910 + 35999.05030 * j_noon / 36525.0) % 360
    c = ((1.9142 - 0.004817 * j_noon / 36525.0) * math.sin(math.radians(m)) +
         0.019993 * math.sin(2 * math.radians(m)) + 0.00029 * math.sin(3 * math.radians(m)))
    lambda_sun = (280.4664 + 36000.7698 * j_noon / 36525.0 + c) % 360

    jde = j_noon + 0.1570 - (0.004817 + 0.000041 * j_noon / 36525.0) * math.sin(2 * math.radians(m))
    epsilon = 23.4393 - 0.0130 * jde / 36525.0
    delta = math.degrees(math.asin(math.sin(math.radians(epsilon)) * math.sin(math.radians(lambda_sun))))

    # Hour angle for civil twilight
    h0 = math.cos(math.radians(CIVIL_TWILIGHT_ANGLE)) / (math.cos(math.radians(latitude)) * math.cos(math.radians(delta))) - math.tan(math.radians(latitude)) * math.tan(math.radians(delta))
    # Clamp h0 to valid acos range [-1, 1]
    h0 = max(-1, min(1, h0))
    h0 = math.degrees(math.acos(h0))

    # Sunrise and sunset in hours
    eot = equation_of_time(jd) / 60.0
    sunrise_hour = (12 - h0 / 15 - longitude / 15 - eot / 60) / 24
    sunset_hour = (12 + h0 / 15 - longitude / 15 - eot / 60) / 24

    # Convert to datetime
    sunrise = date + timedelta(days=sunrise_hour)
    sunset = date + timedelta(days=sunset_hour)

    return (sunrise, sunset)


def sun_elevation(latitude: float, longitude: float, date: datetime) -> float:
    """Calculate sun elevation angle in degrees at solar noon."""
    jd = julian_day(date)
    declination = sun_declination(jd)
    eot = equation_of_time(jd)

    # Solar noon
    solar_noon_hours = 12 - longitude / 15 - eot / 60

    # Hour angle at solar noon (0)
    h = 0

    # Elevation angle
    sin_elevation = (math.sin(math.radians(latitude)) * math.sin(math.radians(declination)) +
                     math.cos(math.radians(latitude)) * math.cos(math.radians(declination)) * math.cos(math.radians(h)))

    elevation = math.degrees(math.asin(sin_elevation))
    return elevation


def hourly_sun_position(latitude: float, longitude: float, date: datetime, hour: int) -> tuple:
    """
    Calculate sun elevation and azimuth for a specific hour.
    Returns: (elevation_degrees, azimuth_degrees)
    """
    jd = julian_day(date)
    declination = sun_declination(jd)
    eot = equation_of_time(jd)

    # Solar time for given hour
    solar_time = hour - longitude / 15 + eot / 60

    # Hour angle
    h = (solar_time - 12) * 15

    # Elevation angle
    sin_elevation = (math.sin(math.radians(latitude)) * math.sin(math.radians(declination)) +
                     math.cos(math.radians(latitude)) * math.cos(math.radians(declination)) * math.cos(math.radians(h)))

    elevation = math.degrees(math.asin(sin_elevation))

    # Azimuth angle
    cos_azimuth = (math.sin(math.radians(declination)) - math.sin(math.radians(latitude)) * sin_elevation) / (math.cos(math.radians(latitude)) * math.cos(math.radians(elevation) if elevation > -90 else -89.99))

    if elevation > -90:
        azimuth = math.degrees(math.acos(cos_azimuth))
        if solar_time < 12:
            azimuth = 360 - azimuth
    else:
        azimuth = 180

    return (elevation, azimuth)
