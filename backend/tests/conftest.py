"""Pytest configuration and shared fixtures for backend tests."""

import pytest
from datetime import datetime
from app.models import SolarInput


@pytest.fixture
def turin_location():
    """Standard test location (Turin, Italy) with known solar data."""
    return {"latitude": 45.0703, "longitude": 7.6869}


@pytest.fixture
def default_solar_input(turin_location):
    """Default simulation parameters matching frontend and real-world test case."""
    return SolarInput(
        latitude=turin_location["latitude"],
        longitude=turin_location["longitude"],
        panel_count=10,
        panel_area_m2=2.0,
        panel_efficiency=20,
        tilt_angle_deg=35,
        azimuth_deg=180,
        start_date="2026-06-21",
        duration_days=1,
    )


@pytest.fixture
def june_solstice_input(turin_location):
    """June solstice test case (summer, long days, high sun)."""
    return SolarInput(
        latitude=turin_location["latitude"],
        longitude=turin_location["longitude"],
        panel_count=10,
        panel_area_m2=2.0,
        panel_efficiency=20,
        tilt_angle_deg=35,
        azimuth_deg=180,
        start_date="2026-06-21",
        duration_days=1,
    )


@pytest.fixture
def december_solstice_input(turin_location):
    """December solstice test case (winter, short days, low sun)."""
    return SolarInput(
        latitude=turin_location["latitude"],
        longitude=turin_location["longitude"],
        panel_count=10,
        panel_area_m2=2.0,
        panel_efficiency=20,
        tilt_angle_deg=35,
        azimuth_deg=180,
        start_date="2026-12-21",
        duration_days=1,
    )


@pytest.fixture
def known_solar_events():
    """Known solar events for validation (Julian Day and seasonal dates)."""
    return {
        "j2000_epoch": datetime(2000, 1, 1, 12, 0, 0),  # Julian Day 2451545.0
        "vernal_equinox_2026": (datetime(2026, 3, 20), 79),  # doy ~79
        "summer_solstice_2026": (datetime(2026, 6, 21), 172),  # doy ~172
        "autumnal_equinox_2026": (datetime(2026, 9, 23), 266),  # doy ~266
        "winter_solstice_2026": (datetime(2026, 12, 21), 355),  # doy ~355
    }


@pytest.fixture
def known_sun_positions():
    """Known sun positions from NOAA/PVGIS for validation.

    Format: (latitude, longitude, date, hour_utc) -> (elevation_expected, azimuth_expected)
    """
    return {
        # Turin (45.07°N, 7.69°E) - Summer Solstice (June 21) at solar noon UTC
        (45.0703, 7.69, datetime(2026, 6, 21), 12): {"elevation": (68.0, 70.0), "azimuth": (175.0, 185.0)},
        # Turin - Winter Solstice (Dec 21) at solar noon UTC
        (45.0703, 7.69, datetime(2026, 12, 21), 12): {"elevation": (21.0, 23.0), "azimuth": (175.0, 185.0)},
        # Turin - Equinox (Mar 20) at solar noon UTC
        (45.0703, 7.69, datetime(2026, 3, 20), 12): {"elevation": (44.5, 45.5), "azimuth": (175.0, 185.0)},
    }


@pytest.fixture
def known_sunrise_sunset():
    """Known sunrise/sunset times from NOAA for validation (UTC, civil twilight -6°).

    Format: (latitude, longitude, date) -> (sunrise_utc_hhmm, sunset_utc_hhmm)
    """
    return {
        # Turin (45.07°N, 7.69°E) - June 21 (summer, long day)
        (45.0703, 7.69, datetime(2026, 6, 21)): ("03:00", "20:00"),
        # Turin - December 21 (winter, short day)
        (45.0703, 7.69, datetime(2026, 12, 21)): ("06:20", "16:30"),
        # Turin - March 20 (equinox)
        (45.0703, 7.69, datetime(2026, 3, 20)): ("04:50", "18:45"),
    }


@pytest.fixture
def known_annual_production():
    """Known annual production values for validation (PVGIS reference data).

    Format: (latitude, longitude, tilt, azimuth, capacity_kw) -> annual_kwh
    """
    return {
        # Turin, 4 kWp (10 panels × 2m² × 20%), 35° tilt, south-facing
        (45.0703, 7.69, 35, 180, 4.0): (4800, 5200),  # Range: ~5000 kWh expected
    }


@pytest.fixture
def test_locations():
    """Test locations across different latitudes and hemispheres."""
    return {
        "turin": {"lat": 45.0703, "lon": 7.6869},  # Northern mid-latitude
        "equator": {"lat": 0.0, "lon": 0.0},  # Equator
        "south_africa": {"lat": -33.9, "lon": 18.4},  # Southern hemisphere
        "arctic": {"lat": 70.0, "lon": 25.0},  # High northern latitude (polar regions)
        "antarctic": {"lat": -70.0, "lon": 0.0},  # High southern latitude
    }
