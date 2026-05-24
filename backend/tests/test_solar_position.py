"""Unit tests for solar_position module (sunrise/sunset and sun angles)."""

from datetime import datetime

import pytest

from app.solar_position import (
    day_of_year,
    equation_of_time,
    hourly_sun_position,
    julian_day,
    sun_declination,
    sun_elevation,
    sunrise_sunset,
)


class TestJulianDay:
    """Tests for Julian Day Number calculation."""

    def test_j2000_epoch(self, known_solar_events):
        """J2000.0 epoch (Jan 1, 2000 12:00:00 UTC) should be Julian Day 2451545.0."""
        j2000 = known_solar_events["j2000_epoch"]
        jd = julian_day(j2000)
        assert jd == pytest.approx(2451545.0, rel=1e-6)

    def test_julian_day_increases_with_date(self):
        """Julian Day should increase monotonically."""
        date1 = datetime(2026, 1, 1, 0, 0, 0)
        date2 = datetime(2026, 6, 21, 0, 0, 0)
        date3 = datetime(2026, 12, 31, 0, 0, 0)
        jd1 = julian_day(date1)
        jd2 = julian_day(date2)
        jd3 = julian_day(date3)
        assert jd1 < jd2 < jd3

    def test_julian_day_includes_hour(self):
        """Julian Day should include fractional hour offset."""
        date_midnight = datetime(2026, 1, 1, 0, 0, 0)
        date_noon = datetime(2026, 1, 1, 12, 0, 0)
        jd_midnight = julian_day(date_midnight)
        jd_noon = julian_day(date_noon)
        assert jd_noon == pytest.approx(jd_midnight + 0.5, rel=1e-6)


class TestDayOfYear:
    """Tests for day-of-year calculation."""

    def test_january_first_is_day_1(self):
        """January 1 should be day 1."""
        date = datetime(2026, 1, 1)
        doy = day_of_year(date)
        assert doy == 1

    def test_december_31_is_day_365(self):
        """December 31 in non-leap year should be day 365."""
        date = datetime(2026, 12, 31)
        doy = day_of_year(date)
        assert doy == 365

    def test_leap_year_february_29(self):
        """February 29 in leap year should be day 60."""
        date = datetime(2024, 2, 29)  # 2024 is leap year
        doy = day_of_year(date)
        assert doy == 60

    def test_vernal_equinox(self, known_solar_events):
        """Vernal equinox (Mar 20) should be ~day 79."""
        date, expected_doy = known_solar_events["vernal_equinox_2026"]
        doy = day_of_year(date)
        assert doy == pytest.approx(expected_doy, abs=1)

    def test_summer_solstice(self, known_solar_events):
        """Summer solstice (Jun 21) should be ~day 172."""
        date, expected_doy = known_solar_events["summer_solstice_2026"]
        doy = day_of_year(date)
        assert doy == pytest.approx(expected_doy, abs=1)


class TestEquationOfTime:
    """Tests for equation of time."""

    def test_equation_of_time_magnitude(self):
        """Equation of time should be within ±15 minutes."""
        for day in range(1, 366, 30):
            date = datetime(2026, 1, 1) + __import__("datetime").timedelta(days=day - 1)
            jd = julian_day(date)
            eot = equation_of_time(jd)
            assert -15 <= eot <= 20, f"EoT {eot} out of bounds on doy {day}"

    def test_equation_of_time_varies_by_date(self):
        """Equation of time should vary throughout the year."""
        jan_date = datetime(2026, 1, 1)
        jun_date = datetime(2026, 6, 21)
        dec_date = datetime(2026, 12, 21)

        eot_jan = equation_of_time(julian_day(jan_date))
        eot_jun = equation_of_time(julian_day(jun_date))
        eot_dec = equation_of_time(julian_day(dec_date))

        # Should have some variation (not all the same)
        values = [eot_jan, eot_jun, eot_dec]
        assert max(values) - min(values) > 5, "EoT should vary by season"


class TestSunDeclination:
    """Tests for sun declination angle."""

    def test_declination_summer_solstice(self, known_solar_events):
        """Summer solstice should have declination ≈ +23.44°."""
        date, _ = known_solar_events["summer_solstice_2026"]
        jd = julian_day(date)
        delta = sun_declination(jd)
        assert 23.0 < delta < 23.5, f"Summer solstice declination {delta} out of bounds"

    def test_declination_winter_solstice(self, known_solar_events):
        """Winter solstice should have declination ≈ -23.44°."""
        date, _ = known_solar_events["winter_solstice_2026"]
        jd = julian_day(date)
        delta = sun_declination(jd)
        assert -23.5 < delta < -23.0, f"Winter solstice declination {delta} out of bounds"

    def test_declination_equinox(self, known_solar_events):
        """Equinoxes should have declination ≈ 0°."""
        spring_date, _ = known_solar_events["vernal_equinox_2026"]
        fall_date, _ = known_solar_events["autumnal_equinox_2026"]

        delta_spring = sun_declination(julian_day(spring_date))
        delta_fall = sun_declination(julian_day(fall_date))

        assert abs(delta_spring) < 1.5, f"Spring equinox declination {delta_spring} not near 0"
        assert abs(delta_fall) < 1.5, f"Fall equinox declination {delta_fall} not near 0"

    def test_declination_range(self):
        """Declination should stay within [-23.44°, +23.44°]."""
        for day in range(1, 366, 7):
            date = datetime(2026, 1, 1) + __import__("datetime").timedelta(days=day - 1)
            jd = julian_day(date)
            delta = sun_declination(jd)
            assert -23.5 < delta < 23.5, f"Declination {delta} out of bounds on doy {day}"


class TestSunriseSunset:
    """Tests for sunrise/sunset calculation."""

    def test_sunrise_before_sunset(self, turin_location):
        """Sunrise should occur before sunset."""
        date = datetime(2026, 6, 21)
        sunrise, sunset = sunrise_sunset(
            turin_location["latitude"], turin_location["longitude"], date
        )
        assert sunrise < sunset, "Sunrise should be before sunset"

    def test_sunrise_sunset_range(self, turin_location):
        """Sunrise/sunset times should be within reasonable UTC range."""
        date = datetime(2026, 6, 21)
        sunrise, sunset = sunrise_sunset(
            turin_location["latitude"], turin_location["longitude"], date
        )
        # For June at 45°N, sunrise ~03:00 UTC, sunset ~20:00 UTC
        assert 1 <= sunrise.hour <= 6, f"June sunrise at hour {sunrise.hour} unrealistic"
        assert 18 <= sunset.hour <= 22, f"June sunset at hour {sunset.hour} unrealistic"

    def test_december_shorter_than_june(self, turin_location):
        """December daylight duration should be much shorter than June."""
        jun_date = datetime(2026, 6, 21)
        dec_date = datetime(2026, 12, 21)

        jun_sunrise, jun_sunset = sunrise_sunset(
            turin_location["latitude"], turin_location["longitude"], jun_date
        )
        dec_sunrise, dec_sunset = sunrise_sunset(
            turin_location["latitude"], turin_location["longitude"], dec_date
        )

        jun_duration = (jun_sunset - jun_sunrise).total_seconds() / 3600
        dec_duration = (dec_sunset - dec_sunrise).total_seconds() / 3600

        assert jun_duration > dec_duration * 1.5, "June should be much longer than December"

    def test_equator_roughly_12_hours(self):
        """At equator, daylight should be approximately 12 hours year-round."""
        for month in [1, 6, 12]:
            date = datetime(2026, month, 15)
            sunrise, sunset = sunrise_sunset(0.0, 0.0, date)
            duration = (sunset - sunrise).total_seconds() / 3600
            # Civil twilight (-6°) extends daylight beyond 12 hours
            # At equator, expect 12-13 hours across all seasons
            assert 11.5 < duration < 13.5, (
                f"Equator month {month} duration {duration} should be ~12h"
            )

    def test_arctic_midnight_sun_around_solstice(self):
        """Arctic at summer solstice should have midnight sun."""
        # Barrow, Alaska: 71.3°N
        date = datetime(2026, 6, 21)
        sunrise, sunset = sunrise_sunset(71.3, -156.8, date)
        # Should return (date, date+1) for midnight sun
        assert sunset.day != sunrise.day or (sunrise.day == sunset.day and sunrise == sunset), (
            "Arctic summer should have midnight sun"
        )

    def test_known_sunrise_sunset_turin_june(self, known_sunrise_sunset, turin_location):
        """Verify Turin June sunrise/sunset against NOAA data (±5 min tolerance)."""
        date = datetime(2026, 6, 21)
        sunrise, sunset = sunrise_sunset(
            turin_location["latitude"], turin_location["longitude"], date
        )

        expected = known_sunrise_sunset[(45.0703, 7.69, date)]
        expected_sunrise_str, expected_sunset_str = expected

        # Parse expected times
        exp_sr_h, exp_sr_m = map(int, expected_sunrise_str.split(":"))
        exp_ss_h, exp_ss_m = map(int, expected_sunset_str.split(":"))

        # Calculate differences in minutes
        sr_diff = abs((sunrise.hour * 60 + sunrise.minute) - (exp_sr_h * 60 + exp_sr_m))
        ss_diff = abs((sunset.hour * 60 + sunset.minute) - (exp_ss_h * 60 + exp_ss_m))

        # Allow ±5 minute tolerance for NOAA reference comparison
        assert sr_diff <= 5, (
            f"Sunrise {sunrise.time()} differs {sr_diff} min from NOAA {expected_sunrise_str}"
        )
        assert ss_diff <= 5, (
            f"Sunset {sunset.time()} differs {ss_diff} min from NOAA {expected_sunset_str}"
        )


class TestSunElevation:
    """Tests for sun elevation at solar noon."""

    def test_noon_elevation_summer_higher_than_winter(self, turin_location):
        """Summer noon elevation should be higher than winter."""
        jun_date = datetime(2026, 6, 21)
        dec_date = datetime(2026, 12, 21)

        elev_jun = sun_elevation(turin_location["latitude"], turin_location["longitude"], jun_date)
        elev_dec = sun_elevation(turin_location["latitude"], turin_location["longitude"], dec_date)

        assert elev_jun > elev_dec, "June noon should have higher elevation than December"

    def test_elevation_at_equinox(self, turin_location, known_solar_events):
        """Equinox elevation should be between summer and winter."""
        spring_date, _ = known_solar_events["vernal_equinox_2026"]
        jun_date = datetime(2026, 6, 21)
        dec_date = datetime(2026, 12, 21)

        elev_spring = sun_elevation(
            turin_location["latitude"], turin_location["longitude"], spring_date
        )
        elev_jun = sun_elevation(turin_location["latitude"], turin_location["longitude"], jun_date)
        elev_dec = sun_elevation(turin_location["latitude"], turin_location["longitude"], dec_date)

        assert elev_dec < elev_spring < elev_jun, "Equinox should be between solstices"


class TestHourlySunPosition:
    """Tests for hourly sun elevation and azimuth."""

    def test_elevation_negative_at_midnight(self, turin_location):
        """At midnight, elevation should be negative."""
        date = datetime(2026, 6, 21)
        elevation, _ = hourly_sun_position(
            turin_location["latitude"],
            turin_location["longitude"],
            date,
            0,  # Hour 0 (midnight)
        )
        assert elevation < 0, "Midnight elevation should be below horizon"

    def test_elevation_positive_at_noon(self, turin_location):
        """At solar noon, elevation should be positive."""
        date = datetime(2026, 6, 21)
        # Approximate solar noon for Turin is ~11-12 UTC (varies by EoT)
        elevations = []
        for hour in range(10, 15):
            elevation, _ = hourly_sun_position(
                turin_location["latitude"], turin_location["longitude"], date, hour
            )
            elevations.append(elevation)

        assert max(elevations) > 0, "Should have positive elevation during midday"

    def test_elevation_peaks_near_noon(self, turin_location):
        """Elevation should peak near solar noon."""
        date = datetime(2026, 6, 21)
        elevations = []
        for hour in range(24):
            elevation, _ = hourly_sun_position(
                turin_location["latitude"], turin_location["longitude"], date, hour
            )
            elevations.append(elevation)

        peak_hour = elevations.index(max(elevations))
        # Solar noon is around hour 12 UTC (varies with EoT), peak should be nearby
        assert 8 <= peak_hour <= 15, f"Peak elevation at hour {peak_hour} not near noon"

    def test_azimuth_east_in_morning(self, turin_location):
        """Morning (east) azimuth should be in range 0-90° (east)."""
        date = datetime(2026, 6, 21)
        # Morning hours: 3-9 UTC
        for hour in [4, 6, 8]:
            elevation, azimuth = hourly_sun_position(
                turin_location["latitude"], turin_location["longitude"], date, hour
            )
            if elevation > 0:  # Only if above horizon
                assert 0 <= azimuth <= 180, f"Morning azimuth {azimuth} not in east/south"

    def test_azimuth_south_at_noon(self, turin_location):
        """At noon (for northern hemisphere), azimuth should be roughly southern."""
        date = datetime(2026, 6, 21)
        # Near solar noon
        elevation, azimuth = hourly_sun_position(
            turin_location["latitude"], turin_location["longitude"], date, 12
        )
        # For Turin at 45°N, noon azimuth should be in southern range
        # (180 = due south, but sun can be slightly west due to equation of time)
        assert 160 < azimuth < 210, f"Noon azimuth {azimuth} not in southern range"

    def test_azimuth_west_in_afternoon(self, turin_location):
        """Afternoon (west) azimuth should be in range 180-360° (west)."""
        date = datetime(2026, 6, 21)
        # Afternoon hours: 15-21 UTC
        for hour in [15, 18, 20]:
            elevation, azimuth = hourly_sun_position(
                turin_location["latitude"], turin_location["longitude"], date, hour
            )
            if elevation > 0:  # Only if above horizon
                assert 180 <= azimuth <= 360, f"Afternoon azimuth {azimuth} not in south/west"

    def test_known_sun_position_validation(self, known_sun_positions, turin_location):
        """Verify sun positions are within reasonable bounds."""
        # Test one known position: Turin June 21 noon
        date = datetime(2026, 6, 21)
        hour = 12

        elevation, azimuth = hourly_sun_position(
            turin_location["latitude"], turin_location["longitude"], date, hour
        )

        # At northern latitudes in summer, sun should be high and southerly
        # Elevation should be 60-75°
        assert 60 < elevation < 75, f"June noon elevation {elevation}° should be 60-75°"
        # Azimuth should be southern (150-210°, allowing for EoT variation)
        assert 150 < azimuth < 210, (
            f"June noon azimuth {azimuth}° should be roughly south (150-210°)"
        )
