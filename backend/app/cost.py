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
    lifespan_years: int
) -> dict:
    """
    Calculate 25-year return on investment for solar system.

    Financial Model:
    - Year N generation = Year 1 generation × (1 - degradation%)^(N-1)
    - Annual savings = generation × (electricity_price + feedin_tariff)
    - Cumulative savings = sum of all annual savings up to year N
    - Break-even = first year where cumulative ≥ system_cost

    Args:
        annual_generation_kwh: First year energy production in kWh
        system_cost_eur: Total system cost in euros
        electricity_price: Price per kWh for self-consumed electricity (€/kWh)
        feedin_tariff: Revenue per kWh for exported energy (€/kWh)
        degradation_percent: Annual degradation rate (0-100%)
        lifespan_years: Analysis period (typically 25 years)

    Returns:
        dict with:
            - year_1_savings: Annual savings in year 1 (€)
            - breakeven_year: Year when cumulative savings ≥ system_cost (int or null)
            - cumulative_savings: List of cumulative savings for each year (€)
            - total_25year_savings: Sum of all annual savings (€)
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

    return {
        "year_1_savings": year_1_savings,
        "breakeven_year": breakeven_year,
        "cumulative_savings": cumulative_savings,
        "total_25year_savings": total_cumulative
    }
