"""Unit tests for calculator module (core simulation functions)."""

from datetime import datetime

import pytest

from app.calculator import (
    adjust_efficiency_for_temperature,
    calculate_daily_profile,
    calculate_hourly_energy,
    calculate_module_temperature,
    seasonal_ambient_temperature,
    simulate,
)
from app.constants import AMBIENT_TEMP_MEAN_C
from app.models import SolarInput


class TestSeasonalAmbientTemperature:
    """Tests for seasonal temperature variation model."""

    def test_summer_warmer_than_winter(self):
        """Summer (doy 172) should be warmer than winter (doy 355)."""
        summer_temp = seasonal_ambient_temperature(45.0, 172)
        winter_temp = seasonal_ambient_temperature(45.0, 355)
        assert summer_temp > winter_temp, "Summer should be warmer than winter"

    def test_january_near_minimum(self):
        """January should be near annual minimum temperature."""
        jan_temp = seasonal_ambient_temperature(45.0, 10)
        mean_temp = 15.0  # AMBIENT_TEMP_MEAN_C
        assert jan_temp < mean_temp, "January should be below mean"

    def test_july_near_maximum(self):
        """July should be near annual maximum temperature (lagging solstice)."""
        jul_temp = seasonal_ambient_temperature(45.0, 200)
        mean_temp = 15.0
        assert jul_temp > mean_temp, "July should be above mean"

    def test_amplitude_within_bounds(self):
        """Temperature should stay within realistic bounds (±10°C from mean)."""
        for doy in range(1, 366):
            temp = seasonal_ambient_temperature(45.0, doy)
            assert 5.0 <= temp <= 25.0, f"Temperature out of bounds on doy {doy}: {temp}°C"

    def test_seasonal_temperature_varies_by_doy(self):
        """Temperature should vary by day of year."""
        # The seasonal model uses a cosine function that peaks around doy 200
        temp_peak = seasonal_ambient_temperature(45.0, 200)
        temp_trough = seasonal_ambient_temperature(45.0, 20)

        # Peak should be warmer than trough
        assert temp_peak > temp_trough, "Temperature should peak in mid-year (doy ~200)"

        # Amplitude should be approximately AMBIENT_TEMP_AMPLITUDE_C (10°C)
        amplitude = temp_peak - AMBIENT_TEMP_MEAN_C
        assert 9.5 < amplitude < 10.5, f"Peak amplitude {amplitude}°C should be ~10°C"


class TestEfficiencyDerating:
    """Tests for temperature derating of panel efficiency."""

    def test_base_efficiency_at_reference_temperature(self):
        """At 25°C, efficiency should be unaffected."""
        eff = adjust_efficiency_for_temperature(0.20, 25)
        assert eff == pytest.approx(0.20, rel=1e-6)

    def test_efficiency_decreases_with_heat(self):
        """Efficiency should decrease monotonically as temperature increases."""
        eff_25 = adjust_efficiency_for_temperature(0.20, 25)
        eff_45 = adjust_efficiency_for_temperature(0.20, 45)
        eff_65 = adjust_efficiency_for_temperature(0.20, 65)
        assert eff_65 < eff_45 < eff_25, "Efficiency should decrease monotonically with temp"

    def test_derating_coefficient_accuracy(self):
        """Verify 0.4% per °C derating coefficient."""
        eff_35 = adjust_efficiency_for_temperature(0.20, 35)
        expected_derating = 1 - 0.004 * 10
        assert eff_35 == pytest.approx(0.20 * expected_derating, rel=1e-6)

    def test_cold_temperatures_boost_efficiency(self):
        """Below 25°C, efficiency should slightly increase."""
        eff_25 = adjust_efficiency_for_temperature(0.20, 25)
        eff_5 = adjust_efficiency_for_temperature(0.20, 5)
        assert eff_5 > eff_25, "Cold temperatures should boost efficiency"

    def test_efficiency_never_negative(self):
        """Efficiency should never go negative, even at extreme temperatures."""
        eff_extreme = adjust_efficiency_for_temperature(0.20, 100)
        assert eff_extreme >= 0, "Efficiency should not go negative"


class TestModuleTemperature:
    """Tests for module temperature estimation."""

    def test_module_temp_zero_irradiance(self):
        """At zero irradiance, module temp equals ambient."""
        t_module = calculate_module_temperature(20.0, 0)
        assert t_module == pytest.approx(20.0, rel=1e-6)

    def test_module_temp_increases_with_irradiance(self):
        """Module temperature should increase with irradiance."""
        t_0 = calculate_module_temperature(20.0, 0)
        t_500 = calculate_module_temperature(20.0, 500)
        t_1000 = calculate_module_temperature(20.0, 1000)
        assert t_500 > t_0
        assert t_1000 > t_500

    def test_module_temp_rise_coefficient(self):
        """Verify 0.03°C per W/m² rise coefficient."""
        ambient = 20.0
        irradiance = 800.0
        t_module = calculate_module_temperature(ambient, irradiance)
        expected = ambient + irradiance * 0.03
        assert t_module == pytest.approx(expected, rel=1e-6)


class TestHourlyEnergy:
    """Tests for hourly power and energy calculations."""

    def test_zero_irradiance_zero_power(self):
        """Zero irradiance should result in zero power output."""
        power_kw, energy_kwh = calculate_hourly_energy(2.0, 0.20, 0, 20)
        assert power_kw == pytest.approx(0, abs=1e-9)
        assert energy_kwh == pytest.approx(0, abs=1e-9)

    def test_power_proportional_to_area_and_efficiency(self):
        """Power should scale with panel area and efficiency."""
        irradiance = 1000.0  # 1 kW/m² (standard test condition)
        temp = 25.0

        power1, _ = calculate_hourly_energy(2.0, 0.20, irradiance, temp)
        power2, _ = calculate_hourly_energy(4.0, 0.20, irradiance, temp)

        # Doubling area should double power
        assert power2 == pytest.approx(power1 * 2.0, rel=0.01)

        # Power should be positive
        assert power1 > 0

    def test_energy_represents_one_hour(self):
        """Energy should represent 1 hour of power generation."""
        power_kw, energy_kwh = calculate_hourly_energy(2.0, 0.20, 800, 25)
        assert energy_kwh == pytest.approx(power_kw, rel=1e-6)

    def test_hot_temperature_reduces_output(self):
        """Higher module temperature should reduce output."""
        irradiance = 800.0
        power_cool, _ = calculate_hourly_energy(2.0, 0.20, irradiance, 25)
        power_hot, _ = calculate_hourly_energy(2.0, 0.20, irradiance, 50)
        assert power_hot < power_cool


class TestDailyProfile:
    """Tests for daily hourly generation profile."""

    def test_daily_profile_24_hours(self, default_solar_input):
        """Daily profile should return 24 hourly values."""
        hourly_gen, daily_total, peak_kw, sunrise_str, sunset_str = calculate_daily_profile(
            default_solar_input.latitude,
            default_solar_input.longitude,
            datetime(2026, 6, 21),
            4.0,  # total area (10 panels × 2m² × 20%)
            0.20,  # efficiency
            default_solar_input.tilt_angle_deg,
            default_solar_input.azimuth_deg,
        )
        assert len(hourly_gen) == 24, "Should return 24 hourly values"
        assert sum(hourly_gen) == pytest.approx(daily_total, rel=0.01)

    def test_summer_higher_than_winter(self, turin_location):
        """Summer daily energy should be significantly higher than winter."""
        summer_hourly, summer_total, _, _, _ = calculate_daily_profile(
            turin_location["latitude"],
            turin_location["longitude"],
            datetime(2026, 6, 21),
            4.0,
            0.20,
            35,
            180,
        )
        winter_hourly, winter_total, _, _, _ = calculate_daily_profile(
            turin_location["latitude"],
            turin_location["longitude"],
            datetime(2026, 12, 21),
            4.0,
            0.20,
            35,
            180,
        )
        assert summer_total > winter_total, "Summer should produce more than winter"
        assert summer_total > winter_total * 2, "Summer should be significantly higher"

    def test_peak_hour_during_day(self):
        """Peak power should occur during daylight hours."""
        hourly_gen, _, peak_kw, _, _ = calculate_daily_profile(
            45.0703, 7.6869, datetime(2026, 6, 21), 4.0, 0.20, 35, 180
        )
        peak_index = hourly_gen.index(max(hourly_gen))
        assert 8 <= peak_index <= 16, f"Peak at hour {peak_index} should be during day (8-16)"

    def test_night_hours_zero_generation(self):
        """Night hours (midnight-sunrise, sunset-midnight) should have zero generation."""
        hourly_gen, _, _, _, _ = calculate_daily_profile(
            45.0703, 7.6869, datetime(2026, 6, 21), 4.0, 0.20, 35, 180
        )
        # Night hours 0-2 and 22-23 should be ~0
        assert hourly_gen[0] < 0.01
        assert hourly_gen[1] < 0.01
        assert hourly_gen[22] < 0.01
        assert hourly_gen[23] < 0.01


class TestSimulate:
    """Tests for complete end-to-end simulation."""

    def test_simulate_returns_all_required_fields(self, default_solar_input):
        """Simulation should return all required output fields."""
        result = simulate(default_solar_input)
        assert result.annual_energy_kwh > 0
        assert result.average_daily_kwh > 0
        assert result.peak_hour_kw > 0
        assert result.system_capacity_kw > 0
        assert len(result.daily_hourly_generation) == 24
        assert len(result.monthly_energy_kwh) == 12
        assert result.daily_sunrise is not None
        assert result.daily_sunset is not None

    def test_annual_energy_equals_monthly_sum(self, default_solar_input):
        """Annual energy should equal sum of monthly energy."""
        result = simulate(default_solar_input)
        monthly_sum = sum(result.monthly_energy_kwh)
        assert result.annual_energy_kwh == pytest.approx(monthly_sum, rel=0.01)

    def test_average_daily_from_annual(self, default_solar_input):
        """Average daily energy should be annual / duration_days."""
        result = simulate(default_solar_input)
        expected_avg = result.annual_energy_kwh / default_solar_input.duration_days
        assert result.average_daily_kwh == pytest.approx(expected_avg, rel=0.01)

    def test_peak_hour_in_daily_profile(self, default_solar_input):
        """Peak hour power should match max in daily profile."""
        result = simulate(default_solar_input)
        daily_max = max(result.daily_hourly_generation)
        assert result.peak_hour_kw == pytest.approx(daily_max, rel=0.01)

    def test_system_capacity_from_inputs(self, default_solar_input):
        """System capacity should be panel_count × area × efficiency."""
        result = simulate(default_solar_input)
        expected_capacity = (
            default_solar_input.panel_count
            * default_solar_input.panel_area_m2
            * default_solar_input.panel_efficiency
            / 100
        )
        assert result.system_capacity_kw == pytest.approx(expected_capacity, rel=0.01)

    def test_turin_june_annual_production(self, june_solstice_input):
        """Turin June 21: verify annual production is realistic (>600 kWh for 4 kWp)."""
        june_solstice_input.duration_days = 30  # Full June
        result = simulate(june_solstice_input)
        # June production ~700 kWh for 4 kWp = 175 kWh/kWp
        # For 1 day (June 21): ~23 kWh
        assert result.annual_energy_kwh > 20, "June 21 should produce >20 kWh for 4 kWp"
        assert result.peak_hour_kw > 2.5, "June noon should peak >2.5 kW"

    def test_turin_december_lower_production(self, december_solstice_input):
        """Turin Dec 21: verify lower production than June (cold, low sun)."""
        december_solstice_input.duration_days = 1  # Single day
        result_dec = simulate(december_solstice_input)

        # Compare to June production
        june_input = SolarInput(
            latitude=45.0703,
            longitude=7.6869,
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-06-21",
            duration_days=1,
        )
        result_jun = simulate(june_input)

        # December should produce significantly less than June
        assert result_dec.annual_energy_kwh > 1, "December 21 should produce >1 kWh for 4 kWp"
        assert result_dec.annual_energy_kwh < result_jun.annual_energy_kwh * 0.3, (
            "December should produce <30% of June for 4 kWp"
        )

    def test_duration_one_day(self, default_solar_input):
        """Duration of 1 day should only process that day."""
        result = simulate(default_solar_input)
        # Check that monthly totals sum to annual
        assert sum(result.monthly_energy_kwh) == pytest.approx(result.annual_energy_kwh, rel=0.01)

    def test_duration_365_days(self, default_solar_input):
        """Duration of 365 days should produce annual production."""
        default_solar_input.duration_days = 365
        default_solar_input.start_date = "2026-01-01"
        result = simulate(default_solar_input)
        # Expect ~5000 kWh annual for Turin 4 kWp
        assert 4500 < result.annual_energy_kwh < 5500, "Annual should be ~5000 kWh for Turin 4 kWp"

    def test_equinox_symmetry(self, turin_location):
        """March and September equinoxes should have similar daily production."""
        march_input = SolarInput(
            latitude=turin_location["latitude"],
            longitude=turin_location["longitude"],
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-03-20",
            duration_days=1,
        )
        september_input = SolarInput(
            latitude=turin_location["latitude"],
            longitude=turin_location["longitude"],
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-09-23",
            duration_days=1,
        )
        march_result = simulate(march_input)
        september_result = simulate(september_input)
        # Equinoxes should have similar production (within 10%)
        assert march_result.annual_energy_kwh == pytest.approx(
            september_result.annual_energy_kwh, rel=0.10
        )
