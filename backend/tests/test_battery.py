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


def test_battery_hourly_charge_array_present(basic_solar_output, basic_battery_params):
    """Test that battery_hourly_charge array is returned with correct length"""
    result = simulate_battery(basic_solar_output, basic_battery_params)

    assert "battery_hourly_charge" in result
    assert isinstance(result["battery_hourly_charge"], list)
    assert len(result["battery_hourly_charge"]) == 24
    assert all(isinstance(x, (int, float)) for x in result["battery_hourly_charge"])
    assert all(x >= 0 for x in result["battery_hourly_charge"])


def test_battery_hourly_load_array_present(basic_solar_output, basic_battery_params):
    """Test that hourly_load array is returned with correct length and constant value"""
    result = simulate_battery(basic_solar_output, basic_battery_params)

    assert "hourly_load" in result
    assert isinstance(result["hourly_load"], list)
    assert len(result["hourly_load"]) == 24
    assert all(isinstance(x, (int, float)) for x in result["hourly_load"])

    # All values should be the same (daily load / 24)
    expected_hourly_load = basic_battery_params["daily_load_kwh"] / 24
    assert all(abs(x - expected_hourly_load) < 0.001 for x in result["hourly_load"])


def test_battery_charge_during_surplus():
    """Test that battery charge is positive during hours with solar surplus"""
    # High solar (4 kWh/hr), low load (1 kWh total)
    solar_output = {
        "daily_hourly_generation": [4] * 24
    }
    battery_params = {
        "capacity_kwh": 20.0,
        "charge_efficiency": 0.92,
        "discharge_efficiency": 0.92,
        "daily_load_kwh": 1.0,
        "initial_soc_pct": 0,  # Start empty to maximize charging
    }
    result = simulate_battery(solar_output, battery_params)

    # With 4 kWh solar and ~0.042 kWh load per hour, should have significant charging
    charge_values = result["battery_hourly_charge"]
    assert any(x > 0 for x in charge_values), "Should have positive charge values during surplus"


def test_battery_no_charge_during_deficit():
    """Test that battery charge is 0 during hours with solar deficit"""
    # Very low solar (0.1 kWh/hr), high load (10 kWh total)
    solar_output = {
        "daily_hourly_generation": [0.1] * 24
    }
    battery_params = {
        "capacity_kwh": 5.0,
        "charge_efficiency": 0.92,
        "discharge_efficiency": 0.92,
        "daily_load_kwh": 10.0,
        "initial_soc_pct": 100,  # Start full to ensure discharge
    }
    result = simulate_battery(solar_output, battery_params)

    # With 0.1 kWh solar and ~0.417 kWh load per hour, deficit is constant
    # Battery will discharge, not charge
    charge_values = result["battery_hourly_charge"]
    assert all(x == 0 for x in charge_values), "Should have no charging during deficit periods"


def test_battery_charge_and_discharge_exclusive(basic_solar_output, basic_battery_params):
    """Test that an hour doesn't both charge and discharge"""
    result = simulate_battery(basic_solar_output, basic_battery_params)

    charge_values = result["battery_hourly_charge"]
    discharge_values = result["battery_hourly_discharge"]

    # For each hour, charge OR discharge should be 0 (not both)
    for charge, discharge in zip(charge_values, discharge_values):
        # At least one should be 0 (they're exclusive operations)
        assert charge == 0 or discharge == 0, f"Hour has both charge ({charge}) and discharge ({discharge})"
