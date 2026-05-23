"""
Solar Panel Simulator - Input Validation
Validate user inputs against constraints
"""

from datetime import datetime

from app.constants import (
    AZIMUTH_MAX,
    AZIMUTH_MIN,
    DURATION_DAYS_MIN,
    LATITUDE_MAX,
    LATITUDE_MIN,
    LONGITUDE_MAX,
    LONGITUDE_MIN,
    PANEL_AREA_MIN,
    PANEL_COUNT_MIN,
    PANEL_EFFICIENCY_MAX,
    PANEL_EFFICIENCY_MIN,
    TILT_ANGLE_MAX,
    TILT_ANGLE_MIN,
)
from app.models import SolarInput, ValidationError


def validate_input(input_data: SolarInput) -> list[ValidationError]:
    """
    Validate all input fields.
    Returns list of ValidationError objects (empty if valid).
    """
    errors = []

    # Latitude
    if not (LATITUDE_MIN <= input_data.latitude <= LATITUDE_MAX):
        errors.append(
            ValidationError(
                field="latitude",
                message=f"Latitude must be between {LATITUDE_MIN} and {LATITUDE_MAX}",
            )
        )

    # Longitude
    if not (LONGITUDE_MIN <= input_data.longitude <= LONGITUDE_MAX):
        errors.append(
            ValidationError(
                field="longitude",
                message=f"Longitude must be between {LONGITUDE_MIN} and {LONGITUDE_MAX}",
            )
        )

    # Panel count
    if input_data.panel_count < PANEL_COUNT_MIN:
        errors.append(
            ValidationError(
                field="panel_count", message=f"Panel count must be at least {PANEL_COUNT_MIN}"
            )
        )

    # Panel area
    if input_data.panel_area_m2 < PANEL_AREA_MIN:
        errors.append(
            ValidationError(
                field="panel_area_m2", message=f"Panel area must be at least {PANEL_AREA_MIN} m²"
            )
        )

    # Panel efficiency
    if not (PANEL_EFFICIENCY_MIN <= input_data.panel_efficiency <= PANEL_EFFICIENCY_MAX):
        errors.append(
            ValidationError(
                field="panel_efficiency",
                message=f"Panel efficiency must be between {PANEL_EFFICIENCY_MIN}% and {PANEL_EFFICIENCY_MAX}%",
            )
        )

    # Tilt angle
    if not (TILT_ANGLE_MIN <= input_data.tilt_angle_deg <= TILT_ANGLE_MAX):
        errors.append(
            ValidationError(
                field="tilt_angle_deg",
                message=f"Tilt angle must be between {TILT_ANGLE_MIN}° and {TILT_ANGLE_MAX}°",
            )
        )

    # Azimuth
    if not (AZIMUTH_MIN <= input_data.azimuth_deg <= AZIMUTH_MAX):
        errors.append(
            ValidationError(
                field="azimuth_deg",
                message=f"Azimuth must be between {AZIMUTH_MIN}° and {AZIMUTH_MAX}°",
            )
        )

    # Duration
    if input_data.duration_days < DURATION_DAYS_MIN:
        errors.append(
            ValidationError(
                field="duration_days", message=f"Duration must be at least {DURATION_DAYS_MIN} day"
            )
        )

    # Start date (must be valid and not too far in past/future)
    try:
        start = datetime.strptime(input_data.start_date, "%Y-%m-%d")
        now = datetime.now()
        if (now - start).days > 365:
            errors.append(
                ValidationError(
                    field="start_date",
                    message="Start date must not be more than 1 year in the past",
                )
            )
    except ValueError:
        errors.append(
            ValidationError(field="start_date", message="Invalid date format (use YYYY-MM-DD)")
        )

    # Battery field validation (all-or-nothing: either all present or all None)
    battery_fields = [
        input_data.battery_capacity_kwh,
        input_data.battery_charge_efficiency,
        input_data.battery_discharge_efficiency,
        input_data.daily_load_kwh,
        input_data.initial_soc_pct,
    ]
    battery_provided = [f is not None for f in battery_fields]

    if any(battery_provided) and not all(battery_provided):
        errors.append(
            ValidationError(
                field="battery",
                message="All battery fields must be provided together or not at all",
            )
        )

    return errors
