"""
Solar Panel Simulator - Unit Tests
Test calculation accuracy and edge cases
"""

import pytest
from datetime import datetime
from app.models import SolarInput
from app.calculator import simulate, calculate_hourly_energy, adjust_efficiency_for_temperature
from app.solar_position import sunrise_sunset, day_of_year
from app.validation import validate_input


class TestEfficiencyDerating:
    """Test temperature derating of panel efficiency."""

    def test_base_temperature(self):
        """Efficiency should be unaffected at 25°C."""
        efficiency = adjust_efficiency_for_temperature(0.20, 25)
        assert efficiency == pytest.approx(0.20, rel=1e-3)

    def test_high_temperature(self):
        """Efficiency should decrease at higher temperatures."""
        efficiency_25 = adjust_efficiency_for_temperature(0.20, 25)
        efficiency_45 = adjust_efficiency_for_temperature(0.20, 45)
        assert efficiency_45 < efficiency_25

    def test_derating_coefficient(self):
        """Verify 0.4% per °C derating."""
        efficiency = adjust_efficiency_for_temperature(0.20, 35)
        expected = 0.20 * (1 - 0.004 * 10)
        assert efficiency == pytest.approx(expected, rel=1e-3)


class TestValidation:
    """Test input validation."""

    def test_valid_input(self):
        """Valid input should produce no errors."""
        input_data = SolarInput(
            latitude=37.77,
            longitude=-122.41,
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-05-21",
            duration_days=365
        )
        errors = validate_input(input_data)
        assert len(errors) == 0

    def test_invalid_latitude(self):
        """Latitude out of range should fail."""
        input_data = SolarInput(
            latitude=100,
            longitude=-122.41,
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-05-21",
            duration_days=365
        )
        errors = validate_input(input_data)
        assert any(e.field == "latitude" for e in errors)

    def test_invalid_efficiency(self):
        """Efficiency out of range should fail."""
        input_data = SolarInput(
            latitude=37.77,
            longitude=-122.41,
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=30,  # > 25%
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-05-21",
            duration_days=365
        )
        errors = validate_input(input_data)
        assert any(e.field == "panel_efficiency" for e in errors)

    def test_zero_panels(self):
        """Zero panels should fail."""
        input_data = SolarInput(
            latitude=37.77,
            longitude=-122.41,
            panel_count=0,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-05-21",
            duration_days=365
        )
        errors = validate_input(input_data)
        assert any(e.field == "panel_count" for e in errors)


class TestSunriseSunset:
    """Test sunrise/sunset calculations."""

    def test_sunrise_before_sunset(self):
        """Sunrise should always be before sunset."""
        date = datetime(2026, 6, 21)  # Summer solstice
        sunrise, sunset = sunrise_sunset(37.77, -122.41, date)
        assert sunrise < sunset

    def test_longer_day_summer(self):
        """Summer day should be longer than winter day."""
        summer = datetime(2026, 6, 21)
        winter = datetime(2026, 12, 21)
        sunrise_s, sunset_s = sunrise_sunset(37.77, -122.41, summer)
        sunrise_w, sunset_w = sunrise_sunset(37.77, -122.41, winter)
        summer_length = (sunset_s - sunrise_s).total_seconds() / 3600
        winter_length = (sunset_w - sunrise_w).total_seconds() / 3600
        assert summer_length > winter_length


class TestSimulation:
    """Test complete simulation."""

    def test_san_francisco_annual(self):
        """Test annual simulation for San Francisco."""
        input_data = SolarInput(
            latitude=37.77,
            longitude=-122.41,
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-05-21",
            duration_days=365
        )

        result = simulate(input_data)

        # Sanity checks
        assert result.annual_energy_kwh > 0
        assert result.average_daily_kwh > 0
        assert result.peak_hour_kw > 0
        assert result.system_capacity_kw == pytest.approx(4.0, rel=0.01)  # 10 * 2 * 0.20
        assert len(result.daily_hourly_generation) == 24
        assert len(result.monthly_energy_kwh) == 12
        assert sum(result.monthly_energy_kwh) == pytest.approx(result.annual_energy_kwh, rel=0.01)

    def test_single_day_simulation(self):
        """Test single-day simulation."""
        input_data = SolarInput(
            latitude=37.77,
            longitude=-122.41,
            panel_count=1,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-06-21",  # Summer solstice
            duration_days=1
        )

        result = simulate(input_data)

        # Single day should have meaningful output
        assert result.daily_hourly_generation[12] > result.daily_hourly_generation[8]  # Noon > morning
        assert result.daily_hourly_generation[0] == 0  # Midnight = 0
        assert all(x >= 0 for x in result.daily_hourly_generation)

    def test_equator_simulation(self):
        """Test simulation near equator."""
        input_data = SolarInput(
            latitude=0,
            longitude=0,
            panel_count=5,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=0,
            azimuth_deg=180,
            start_date="2026-03-20",  # Spring equinox
            duration_days=30
        )

        result = simulate(input_data)

        # Equator should have consistent daily output
        assert result.annual_energy_kwh > 0
        assert result.average_daily_kwh > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
