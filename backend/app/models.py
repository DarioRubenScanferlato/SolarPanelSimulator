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


class ValidationError(BaseModel):
    field: str
    message: str
