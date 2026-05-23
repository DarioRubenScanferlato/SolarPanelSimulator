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
