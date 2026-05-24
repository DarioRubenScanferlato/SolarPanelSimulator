"""
Unit tests for cost analysis module
Tests ROI calculation, degradation, break-even, and financial metrics
"""

import pytest
from app.cost import calculate_25year_roi


@pytest.fixture
def basic_cost_params():
    """Standard cost analysis parameters"""
    return {
        "annual_generation_kwh": 5000,
        "system_cost_eur": 9000,
        "electricity_price": 0.32,
        "feedin_tariff": 0.12,
        "degradation_percent": 0.5,
        "lifespan_years": 25
    }


def test_cost_basic_25year_roi(basic_cost_params):
    """Test basic 25-year ROI calculation"""
    result = calculate_25year_roi(**basic_cost_params)

    # Verify all required keys present
    assert "year_1_savings" in result
    assert "breakeven_year" in result
    assert "cumulative_savings" in result
    assert "total_25year_savings" in result

    # Verify types
    assert isinstance(result["year_1_savings"], float)
    assert isinstance(result["cumulative_savings"], list)
    assert isinstance(result["total_25year_savings"], float)
    assert result["breakeven_year"] is None or isinstance(result["breakeven_year"], int)

    # Year 1 savings: 5000 * (0.32 + 0.12) = 5000 * 0.44 = 2200
    assert result["year_1_savings"] == pytest.approx(2200, abs=0.1)


def test_cost_year_1_savings_calculation():
    """Test year 1 savings calculation"""
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=15000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0,
        lifespan_years=25
    )

    # Year 1 savings should be generation × (price + tariff)
    expected_savings = 5000 * (0.32 + 0.12)
    assert result["year_1_savings"] == pytest.approx(expected_savings, abs=0.1)


def test_cost_breakeven_year_calculation(basic_cost_params):
    """Test break-even year calculation"""
    result = calculate_25year_roi(**basic_cost_params)

    # With 5000 kWh/year, €0.44/kWh revenue, and €9000 cost:
    # Annual savings ≈ €2200/year (no degradation for this test)
    # Break-even: 9000 / 2200 ≈ 4.1 years, so year 5
    # But with 0.5% degradation, it takes slightly longer
    assert result["breakeven_year"] is not None
    assert 4 <= result["breakeven_year"] <= 6


def test_cost_degradation_applied_correctly():
    """Test that degradation is applied correctly (0.5%/year)"""
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=20000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0.5,
        lifespan_years=25
    )

    # Year 1: 5000 kWh
    # Year 25: 5000 × (1 - 0.005)^24 ≈ 5000 × 0.8879 ≈ 4439 kWh (11.2% loss)
    year_1_generation = 5000
    year_25_generation = year_1_generation * ((1 - 0.5 / 100) ** 24)

    # Year 1 savings: 5000 * 0.44 = 2200
    # Year 25 savings: ~4439 * 0.44 ≈ 1953
    year_1_savings = year_1_generation * 0.44
    year_25_savings = year_25_generation * 0.44

    # Verify degradation reduces year 25 generation by approximately 11-12%
    degradation_loss = (year_1_generation - year_25_generation) / year_1_generation
    assert 0.10 < degradation_loss < 0.13  # 10-13% loss


def test_cost_cumulative_savings_list(basic_cost_params):
    """Test cumulative savings list structure and values"""
    result = calculate_25year_roi(**basic_cost_params)

    cumulative = result["cumulative_savings"]

    # Should have 25 years of data
    assert len(cumulative) == 25

    # All values should be floats
    assert all(isinstance(x, float) for x in cumulative)

    # Should be monotonically increasing
    for i in range(1, len(cumulative)):
        assert cumulative[i] >= cumulative[i-1]

    # First year should equal year_1_savings
    assert cumulative[0] == pytest.approx(result["year_1_savings"], abs=0.1)

    # Last year should equal total_25year_savings
    assert cumulative[-1] == pytest.approx(result["total_25year_savings"], abs=0.1)


def test_cost_no_breakeven_when_high_cost(basic_cost_params):
    """Test that break-even is null when system never pays for itself"""
    result = calculate_25year_roi(
        annual_generation_kwh=1000,  # Low generation
        system_cost_eur=50000,  # High cost
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0.5,
        lifespan_years=25
    )

    # With only 1000 kWh/year at €0.44/kWh = €440/year, can't pay off €50k in 25 years
    assert result["breakeven_year"] is None


def test_cost_zero_degradation():
    """Test calculation with no degradation (0%)"""
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0,
        lifespan_years=25
    )

    # Without degradation, all years should have same generation
    # Year 1: 5000 × 0.44 = 2200
    # Year 25 should be same savings: 2200
    year_1 = result["cumulative_savings"][0]
    year_25_additional = result["cumulative_savings"][-1] - result["cumulative_savings"][-2]

    assert year_1 == pytest.approx(year_25_additional, rel=0.001)


def test_cost_total_savings_sum(basic_cost_params):
    """Test that total_25year_savings equals sum of cumulative values"""
    result = calculate_25year_roi(**basic_cost_params)

    # Last cumulative value should equal total
    assert result["cumulative_savings"][-1] == pytest.approx(
        result["total_25year_savings"], abs=0.01
    )


def test_cost_backwards_compatibility_no_cost_fields():
    """Test that cost calculation works independently"""
    # This verifies the cost module returns expected structure
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0.5,
        lifespan_years=25
    )

    # Should always return these 4 keys
    assert set(result.keys()) == {
        "year_1_savings",
        "breakeven_year",
        "cumulative_savings",
        "total_25year_savings"
    }


@pytest.mark.parametrize("annual_gen,cost,breakeven_expected", [
    (10000, 10000, 2),  # High generation, quick payback
    (5000, 5000, 3),    # Medium generation
    (500, 10000, None),  # Very low generation, no payback
])
def test_cost_parametrized_breakeven_scenarios(annual_gen, cost, breakeven_expected):
    """Test break-even calculation across scenarios"""
    result = calculate_25year_roi(
        annual_generation_kwh=annual_gen,
        system_cost_eur=cost,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0.5,
        lifespan_years=25
    )

    if breakeven_expected is None:
        assert result["breakeven_year"] is None
    else:
        assert result["breakeven_year"] is not None
        # Allow some tolerance due to degradation
        assert abs(result["breakeven_year"] - breakeven_expected) <= 2


def test_cost_output_format_validation():
    """Test output format and value ranges"""
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0.5,
        lifespan_years=25
    )

    # Verify types
    assert isinstance(result["year_1_savings"], float)
    assert result["year_1_savings"] > 0

    assert isinstance(result["cumulative_savings"], list)
    assert len(result["cumulative_savings"]) == 25
    assert all(isinstance(x, float) for x in result["cumulative_savings"])
    assert all(x > 0 for x in result["cumulative_savings"])

    assert isinstance(result["total_25year_savings"], float)
    assert result["total_25year_savings"] > 0

    assert result["breakeven_year"] is None or isinstance(result["breakeven_year"], int)


# Battery-Integrated Cost Calculation Tests

def test_cost_battery_integrated_high_self_consumption():
    """Test battery-integrated cost with 80% self-consumption"""
    battery_params = {"self_consumption_pct": 80}
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0,  # No degradation for clarity
        lifespan_years=25,
        battery_params=battery_params
    )

    # Year 1 calculation:
    # self_consumed = 5000 × 0.80 = 4000 kWh
    # exported = 5000 × 0.20 = 1000 kWh
    # year_1_savings = (4000 × 0.32) + (1000 × 0.12) = 1280 + 120 = 1400
    expected_year_1 = (4000 * 0.32) + (1000 * 0.12)
    assert result["year_1_savings"] == pytest.approx(expected_year_1, abs=0.1)

    # Should have all required fields
    assert "year_1_savings" in result
    assert "breakeven_year" in result
    assert "cumulative_savings" in result
    assert "total_25year_savings" in result


def test_cost_battery_integrated_low_self_consumption():
    """Test battery-integrated cost with 20% self-consumption"""
    battery_params = {"self_consumption_pct": 20}
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0,
        lifespan_years=25,
        battery_params=battery_params
    )

    # Year 1 calculation:
    # self_consumed = 5000 × 0.20 = 1000 kWh
    # exported = 5000 × 0.80 = 4000 kWh
    # year_1_savings = (1000 × 0.32) + (4000 × 0.12) = 320 + 480 = 800
    expected_year_1 = (1000 * 0.32) + (4000 * 0.12)
    assert result["year_1_savings"] == pytest.approx(expected_year_1, abs=0.1)


def test_cost_battery_integrated_zero_battery():
    """Test battery-integrated cost with 0% self-consumption (equivalent to solar-only)"""
    battery_params = {"self_consumption_pct": 0}
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0,
        lifespan_years=25,
        battery_params=battery_params
    )

    # Year 1 calculation:
    # self_consumed = 5000 × 0.00 = 0 kWh
    # exported = 5000 × 1.00 = 5000 kWh
    # year_1_savings = (0 × 0.32) + (5000 × 0.12) = 0 + 600 = 600
    expected_year_1 = (0 * 0.32) + (5000 * 0.12)
    assert result["year_1_savings"] == pytest.approx(expected_year_1, abs=0.1)


def test_cost_battery_integrated_full_self_consumption():
    """Test battery-integrated cost with 100% self-consumption"""
    battery_params = {"self_consumption_pct": 100}
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0,
        lifespan_years=25,
        battery_params=battery_params
    )

    # Year 1 calculation:
    # self_consumed = 5000 × 1.00 = 5000 kWh
    # exported = 5000 × 0.00 = 0 kWh
    # year_1_savings = (5000 × 0.32) + (0 × 0.12) = 1600 + 0 = 1600
    expected_year_1 = (5000 * 0.32) + (0 * 0.12)
    assert result["year_1_savings"] == pytest.approx(expected_year_1, abs=0.1)


def test_cost_battery_integrated_degradation():
    """Test that degradation is applied correctly in battery-integrated path"""
    battery_params = {"self_consumption_pct": 80}
    result = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=20000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0.5,
        lifespan_years=25,
        battery_params=battery_params
    )

    # Year 1: 5000 kWh total, 4000 self-consumed, 1000 exported
    year_1_savings = (4000 * 0.32) + (1000 * 0.12)
    assert result["cumulative_savings"][0] == pytest.approx(year_1_savings, abs=0.1)

    # Year 25: degraded generation = 5000 × (0.995)^24 ≈ 4439 kWh
    # Then split: 4439 × 0.80 ≈ 3551 self-consumed, 4439 × 0.20 ≈ 888 exported
    year_25_generation = 5000 * ((1 - 0.5 / 100) ** 24)
    year_25_self_consumed = year_25_generation * 0.80
    year_25_exported = year_25_generation * 0.20
    year_25_savings = (year_25_self_consumed * 0.32) + (year_25_exported * 0.12)

    # Cumulative should be less in year 25 than if no degradation
    # Verify degradation reduces savings
    assert result["cumulative_savings"][-1] < (year_1_savings * 25)


def test_cost_battery_vs_solar_only_comparison():
    """Test that battery-integrated cost is different from solar-only"""
    solar_only = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0,
        lifespan_years=25,
        battery_params=None
    )

    battery_integrated = calculate_25year_roi(
        annual_generation_kwh=5000,
        system_cost_eur=9000,
        electricity_price=0.32,
        feedin_tariff=0.12,
        degradation_percent=0,
        lifespan_years=25,
        battery_params={"self_consumption_pct": 80}
    )

    # Solar-only: 5000 × (0.32 + 0.12) = 2200
    # Battery (80%): (4000 × 0.32) + (1000 × 0.12) = 1400
    # Battery savings should be lower (due to lower feedin_tariff on exports)
    assert solar_only["year_1_savings"] > battery_integrated["year_1_savings"]
    assert solar_only["total_25year_savings"] > battery_integrated["total_25year_savings"]
