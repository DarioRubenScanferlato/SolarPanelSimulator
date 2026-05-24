"""
Cost analysis module — 25-year ROI calculation with degradation
Calculates system payback period and cumulative financial savings
"""


def calculate_25year_roi(
    annual_generation_kwh: float,
    system_cost_eur: float,
    electricity_price: float,
    feedin_tariff: float,
    degradation_percent: float,
    lifespan_years: int,
    battery_params: dict = None
) -> dict:
    """
    Calculate 25-year return on investment for solar system.

    Supports two financial models:
    1. Solar-only (simplified): all generation valued at (electricity_price + feedin_tariff)
    2. Battery-integrated (new): splits generation into self-consumed (valued at electricity_price)
       and exported (valued at feedin_tariff) based on self_consumption_pct from battery simulation

    Financial Model (Solar-Only Path — backwards compatible):
    - Year N generation = Year 1 generation × (1 - degradation%)^(N-1)
    - Annual savings = generation × (electricity_price + feedin_tariff)
    - Cumulative savings = sum of all annual savings up to year N
    - Break-even = first year where cumulative ≥ system_cost

    Financial Model (Battery-Integrated Path — new):
    - Year N degraded_generation = Year 1 generation × (1 - degradation%)^(N-1)
    - self_consumed = degraded_generation × self_consumption_pct / 100
    - exported = degraded_generation × (100 - self_consumption_pct) / 100
    - annual_savings = (self_consumed × electricity_price) + (exported × feedin_tariff)
    - Cumulative savings = sum of all annual savings up to year N
    - Break-even = first year where cumulative ≥ system_cost

    Args:
        annual_generation_kwh: First year energy production in kWh
        system_cost_eur: Total system cost in euros
        electricity_price: Price per kWh for self-consumed electricity (€/kWh)
        feedin_tariff: Revenue per kWh for exported energy (€/kWh)
        degradation_percent: Annual degradation rate (0-100%)
        lifespan_years: Analysis period (typically 25 years)
        battery_params: Optional dict with battery simulation results:
            - self_consumption_pct: Percentage of generation self-consumed (0-100)
            If None, uses solar-only path; if provided, uses battery-integrated path

    Returns:
        dict with:
            - year_1_savings: Annual savings in year 1 (€)
            - breakeven_year: Year when cumulative savings ≥ system_cost (int or null)
            - cumulative_savings: List of cumulative savings for each year (€)
            - total_25year_savings: Sum of all annual savings (€)
            - monthly_savings: List of monthly savings for year 1 (12 values, € evenly distributed)
            - monthly_cost_allocation: List of monthly system cost allocation (12 values, € evenly distributed)
    """
    # Determine which calculation path to use
    if battery_params is None:
        # Solar-only path (backwards compatible)
        return _calculate_solar_only_roi(
            annual_generation_kwh,
            system_cost_eur,
            electricity_price,
            feedin_tariff,
            degradation_percent,
            lifespan_years
        )
    else:
        # Battery-integrated path (new)
        return _calculate_battery_integrated_roi(
            annual_generation_kwh,
            system_cost_eur,
            electricity_price,
            feedin_tariff,
            degradation_percent,
            lifespan_years,
            battery_params
        )


def _calculate_solar_only_roi(
    annual_generation_kwh: float,
    system_cost_eur: float,
    electricity_price: float,
    feedin_tariff: float,
    degradation_percent: float,
    lifespan_years: int
) -> dict:
    """
    Solar-only cost calculation (simplified model, backwards compatible).
    Assumes all generation is either consumed at home or exported to grid at full tariff.
    """
    # Year 1 savings
    annual_revenue_per_kwh = electricity_price + feedin_tariff
    year_1_savings = annual_generation_kwh * annual_revenue_per_kwh

    cumulative_savings = []
    total_cumulative = 0
    breakeven_year = None

    # Calculate for each year
    for year in range(1, lifespan_years + 1):
        # Apply degradation: generation diminishes each year
        capacity_factor = (1 - degradation_percent / 100) ** (year - 1)
        annual_generation = annual_generation_kwh * capacity_factor

        # Annual savings (electricity savings + feed-in revenue)
        annual_savings = annual_generation * annual_revenue_per_kwh

        # Cumulative savings
        total_cumulative += annual_savings
        cumulative_savings.append(total_cumulative)

        # Check for break-even
        if breakeven_year is None and total_cumulative >= system_cost_eur:
            breakeven_year = year

    # Calculate monthly breakdown for year 1
    monthly_savings = [year_1_savings / 12] * 12
    monthly_cost_allocation = [system_cost_eur / (lifespan_years * 12)] * 12

    return {
        "year_1_savings": year_1_savings,
        "breakeven_year": breakeven_year,
        "cumulative_savings": cumulative_savings,
        "total_25year_savings": total_cumulative,
        "monthly_savings": monthly_savings,
        "monthly_cost_allocation": monthly_cost_allocation
    }


def _calculate_battery_integrated_roi(
    annual_generation_kwh: float,
    system_cost_eur: float,
    electricity_price: float,
    feedin_tariff: float,
    degradation_percent: float,
    lifespan_years: int,
    battery_params: dict
) -> dict:
    """
    Battery-integrated cost calculation (new model).
    Splits generation into self-consumed (valued at electricity_price) and
    exported (valued at feedin_tariff) based on battery simulation results.
    """
    self_consumption_pct = battery_params.get("self_consumption_pct", 0)

    # Year 1 savings (calculate before loop for return value)
    year_1_self_consumed = annual_generation_kwh * self_consumption_pct / 100
    year_1_exported = annual_generation_kwh * (100 - self_consumption_pct) / 100
    year_1_savings = (year_1_self_consumed * electricity_price) + (year_1_exported * feedin_tariff)

    cumulative_savings = []
    total_cumulative = 0
    breakeven_year = None

    # Calculate for each year
    for year in range(1, lifespan_years + 1):
        # Apply degradation: generation diminishes each year
        capacity_factor = (1 - degradation_percent / 100) ** (year - 1)
        degraded_generation = annual_generation_kwh * capacity_factor

        # Split into self-consumed and exported
        self_consumed = degraded_generation * self_consumption_pct / 100
        exported = degraded_generation * (100 - self_consumption_pct) / 100

        # Annual savings (self-consumed at electricity_price, exported at feedin_tariff)
        annual_savings = (self_consumed * electricity_price) + (exported * feedin_tariff)

        # Cumulative savings
        total_cumulative += annual_savings
        cumulative_savings.append(total_cumulative)

        # Check for break-even
        if breakeven_year is None and total_cumulative >= system_cost_eur:
            breakeven_year = year

    # Calculate monthly breakdown for year 1
    monthly_savings = [year_1_savings / 12] * 12
    monthly_cost_allocation = [system_cost_eur / (lifespan_years * 12)] * 12

    return {
        "year_1_savings": year_1_savings,
        "breakeven_year": breakeven_year,
        "cumulative_savings": cumulative_savings,
        "total_25year_savings": total_cumulative,
        "monthly_savings": monthly_savings,
        "monthly_cost_allocation": monthly_cost_allocation
    }
