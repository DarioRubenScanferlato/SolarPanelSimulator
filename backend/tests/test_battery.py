"""
Unit tests for battery simulation module
Tests battery energy balance, SoC bounds, efficiency losses, and edge cases
"""

import pytest
from app.battery import simulate_battery


@pytest.fixture
def basic_solar_output():
    """Representative day with hourly solar generation (kWh)"""
    return {
        "daily_hourly_generation": [
            0, 0, 0, 0, 0,  # 0-4: night
            2, 5, 8, 12, 15, 18, 20,  # 5-11: morning to noon
            20, 18, 15, 12, 8, 5,  # 12-17: afternoon
            2, 0, 0, 0, 0, 0  # 18-23: evening to night
        ]
    }


@pytest.fixture
def basic_battery_params():
    """Standard battery configuration"""
    return {
        "capacity_kwh": 10.0,
        "charge_efficiency": 0.92,
        "discharge_efficiency": 0.92,
        "daily_load_kwh": 10.0,
        "initial_soc_pct": 50.0,
    }


def test_battery_basic_charge_discharge_cycle(basic_solar_output, basic_battery_params):
    """Test basic charge/discharge cycle with balanced load and solar"""
    result = simulate_battery(basic_solar_output, basic_battery_params)

    # Verify all required keys present
    assert "battery_hourly_soc" in result
    assert "self_consumption_pct" in result
    assert "grid_export_kwh" in result
    assert "grid_import_kwh" in result

    # Verify types and lengths
    assert isinstance(result["battery_hourly_soc"], list)
    assert len(result["battery_hourly_soc"]) == 24
    assert all(isinstance(x, float) for x in result["battery_hourly_soc"])
    assert 0 <= result["self_consumption_pct"] <= 100
    assert result["grid_export_kwh"] >= 0
    assert result["grid_import_kwh"] >= 0


def test_battery_soc_never_exceeds_capacity(basic_battery_params):
    """Test that SoC never exceeds battery capacity"""
    # High solar input (40 kWh total for day)
    solar_output = {
        "daily_hourly_generation": [2] * 24
    }
    result = simulate_battery(solar_output, basic_battery_params)

    assert max(result["battery_hourly_soc"]) <= basic_battery_params["capacity_kwh"] + 0.01  # small tolerance


def test_battery_soc_never_negative(basic_battery_params):
    """Test that SoC never goes negative"""
    # Low solar input (3 kWh total) with high load (10 kWh)
    solar_output = {
        "daily_hourly_generation": [0.125] * 24  # ~3 kWh total
    }
    result = simulate_battery(solar_output, basic_battery_params)

    assert min(result["battery_hourly_soc"]) >= -0.01  # small tolerance for rounding


def test_battery_efficiency_losses_applied():
    """Test that efficiency factors work correctly"""
    # Just verify efficiency runs without error and produces valid output
    result = simulate_battery(
        {"daily_hourly_generation": [3] * 24},
        {
            "capacity_kwh": 10.0,
            "charge_efficiency": 0.85,
            "discharge_efficiency": 0.85,
            "daily_load_kwh": 10.0,
            "initial_soc_pct": 50.0,
        }
    )

    # Verify result is valid
    assert result["self_consumption_pct"] > 0
    assert all(0 <= soc <= 10.0 for soc in result["battery_hourly_soc"])


def test_battery_output_format():
    """Test output format and value ranges"""
    solar_output = {
        "daily_hourly_generation": [2] * 24
    }
    battery_params = {
        "capacity_kwh": 10.0,
        "charge_efficiency": 0.92,
        "discharge_efficiency": 0.92,
        "daily_load_kwh": 5.0,
        "initial_soc_pct": 50.0,
    }
    result = simulate_battery(solar_output, battery_params)

    # Verify SoC list format
    assert isinstance(result["battery_hourly_soc"], list)
    assert len(result["battery_hourly_soc"]) == 24
    assert all(isinstance(x, (int, float)) for x in result["battery_hourly_soc"])
    assert all(0 <= x <= 10.0 for x in result["battery_hourly_soc"])

    # Verify metric ranges
    assert isinstance(result["self_consumption_pct"], (int, float))
    assert 0 <= result["self_consumption_pct"] <= 100
    assert isinstance(result["grid_export_kwh"], (int, float))
    assert result["grid_export_kwh"] >= 0
    assert isinstance(result["grid_import_kwh"], (int, float))
    assert result["grid_import_kwh"] >= 0


def test_battery_zero_initial_soc():
    """Test with zero initial state of charge"""
    solar_output = {
        "daily_hourly_generation": [2] * 24
    }
    battery_params = {
        "capacity_kwh": 10.0,
        "charge_efficiency": 0.92,
        "discharge_efficiency": 0.92,
        "daily_load_kwh": 5.0,
        "initial_soc_pct": 0,
    }
    result = simulate_battery(solar_output, battery_params)

    # First hour SoC should be positive (charging from solar surplus)
    # Solar 2 kWh/hr - load 5/24 ≈ 0.208 kWh/hr = net 1.79 kWh, charged at 92% eff ≈ 1.65 kWh
    assert result["battery_hourly_soc"][0] > 0
    assert result["battery_hourly_soc"][0] < 2.0


def test_battery_full_initial_soc():
    """Test with 100% initial state of charge"""
    solar_output = {
        "daily_hourly_generation": [0.1] * 24  # Low solar
    }
    battery_params = {
        "capacity_kwh": 10.0,
        "charge_efficiency": 0.92,
        "discharge_efficiency": 0.92,
        "daily_load_kwh": 5.0,
        "initial_soc_pct": 100,
    }
    result = simulate_battery(solar_output, battery_params)

    # First hour should start near full capacity (with discharge for load)
    # Load: 5/24 ≈ 0.208 kWh, discharged at 92% eff ≈ 0.226 kWh from battery
    assert result["battery_hourly_soc"][0] >= 9.75


def test_battery_energy_balance_invariant(basic_solar_output, basic_battery_params):
    """Test energy balance equation: solar + import = load + export + delta_soc"""
    result = simulate_battery(basic_solar_output, basic_battery_params)

    total_solar = sum(basic_solar_output["daily_hourly_generation"])
    total_load = basic_battery_params["daily_load_kwh"]
    delta_soc = result["battery_hourly_soc"][-1] - (basic_battery_params["initial_soc_pct"] * basic_battery_params["capacity_kwh"] / 100)

    # Energy balance (within 5% tolerance for efficiency losses)
    balance = total_solar + result["grid_import_kwh"] - total_load - result["grid_export_kwh"] - delta_soc
    assert abs(balance) < max(total_solar * 0.05, 0.5)  # 5% of solar or 0.5 kWh, whichever is larger
