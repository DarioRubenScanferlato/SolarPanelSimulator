"""
Solar Panel Simulator - Pydantic Models
Request/response schemas and validation
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator


class SolarInput(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    panel_count: int = Field(..., ge=1, description="Number of solar panels")
    panel_area_m2: float = Field(..., ge=0.1, description="Panel area in square meters")
    panel_efficiency: float = Field(..., ge=5, le=25, description="Panel efficiency as percentage")
    tilt_angle_deg: float = Field(..., ge=0, le=90, description="Tilt angle in degrees")
    azimuth_deg: float = Field(
        ..., ge=0, le=360, description="Azimuth in degrees (0=N, 90=E, 180=S, 270=W)"
    )
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    duration_days: int = Field(..., ge=1, description="Simulation duration in days")
    battery_capacity_kwh: float | None = Field(None, ge=1, description="Battery capacity in kWh (optional, all-or-none with other battery fields)")
    battery_charge_efficiency: float | None = Field(None, ge=80, le=99, description="Charge efficiency as percentage (optional)")
    battery_discharge_efficiency: float | None = Field(None, ge=80, le=99, description="Discharge efficiency as percentage (optional)")
    daily_load_kwh: float | None = Field(None, ge=0.1, description="Daily household load in kWh (optional)")
    initial_soc_pct: float | None = Field(None, ge=0, le=100, description="Initial battery state of charge as percentage (optional)")
    system_cost_eur: float | None = Field(None, ge=0, description="Total system cost in euros (optional, all-or-none with other cost fields)")
    electricity_price_eur_per_kwh: float | None = Field(None, ge=0, description="Electricity price in €/kWh (optional)")
    feedin_tariff_eur_per_kwh: float | None = Field(None, ge=0, description="Feed-in tariff in €/kWh (optional)")
    lifespan_years: int | None = Field(None, ge=1, description="System lifespan in years (optional)")
    annual_degradation_percent: float | None = Field(None, ge=0, le=100, description="Annual degradation as percentage (optional)")

    @field_validator("start_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class SolarOutput(BaseModel):
    annual_energy_kwh: float = Field(..., description="Total annual energy production in kWh")
    average_daily_kwh: float = Field(..., description="Average daily energy in kWh")
    peak_hour_kw: float = Field(..., description="Peak hourly generation in kW")
    system_capacity_kw: float = Field(..., description="Total system capacity in kW")
    daily_hourly_generation: List[float] = Field(
        ..., description="Hourly generation for first day (24 values)"
    )
    daily_sunrise: str = Field(..., description="Sunrise time in HH:MM format")
    daily_sunset: str = Field(..., description="Sunset time in HH:MM format")
    monthly_energy_kwh: List[float] = Field(..., description="Monthly totals (12 values)")
    calculation_date: datetime = Field(..., description="UTC timestamp of calculation")
    battery_hourly_soc: List[float] | None = Field(None, description="Battery hourly state of charge in kWh (24 values if battery present)")
    battery_hourly_solar_consumption: List[float] | None = Field(None, description="Hourly energy consumed directly from solar in kWh (24 values if battery present)")
    battery_hourly_grid_consumption: List[float] | None = Field(None, description="Hourly energy imported from grid in kWh (24 values if battery present)")
    battery_hourly_grid_export: List[float] | None = Field(None, description="Hourly energy exported to grid in kWh (24 values if battery present)")
    battery_hourly_charge: List[float] | None = Field(None, description="Hourly energy going into battery in kWh (24 values if battery present)")
    hourly_load: List[float] | None = Field(None, description="Total hourly household consumption in kWh (24 values if battery present)")
    self_consumption_pct: float | None = Field(None, description="Percentage of solar used locally (0-100)")
    grid_export_kwh: float | None = Field(None, description="Total energy exported to grid in kWh")
    grid_import_kwh: float | None = Field(None, description="Total energy imported from grid in kWh")
    battery_monthly_solar_consumption: List[float] | None = Field(None, description="Monthly solar consumption totals in kWh (up to 12 values if battery and duration >= 24h)")
    battery_monthly_grid_consumption: List[float] | None = Field(None, description="Monthly grid consumption totals in kWh (up to 12 values if battery and duration >= 24h)")
    battery_monthly_battery_discharge: List[float] | None = Field(None, description="Monthly battery discharge totals in kWh (up to 12 values if battery and duration >= 24h)")
    cost_system_cost_eur: float | None = Field(None, description="System cost in euros (echoed from input for frontend validation)")
    cost_year_1_savings: float | None = Field(None, description="First year financial savings in euros")
    cost_breakeven_year: int | None = Field(None, description="Year when system pays for itself (or null if no payback)")
    cost_cumulative_savings: List[float] | None = Field(None, description="Cumulative savings for each year (25 values if cost present)")
    cost_total_25year_savings: float | None = Field(None, description="Total financial savings over 25 years in euros")
    cost_monthly_savings: List[float] | None = Field(None, description="Monthly savings breakdown for year 1 (12 values if cost present)")
    cost_monthly_cost_allocation: List[float] | None = Field(None, description="Monthly system cost allocation (12 values if cost present)")


class ValidationError(BaseModel):
    field: str
    message: str
