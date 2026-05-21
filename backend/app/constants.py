"""
Solar Panel Simulator - Physical Constants
Standard PV and solar radiation constants
"""

# Solar radiation
SOLAR_CONSTANT_WM2 = 1361  # W/m², extraterrestrial irradiance

# Atmospheric / ground parameters
GROUND_ALBEDO = 0.2  # Typical ground reflectance for transposition model

# PV module parameters
TEMP_DERATING_COEFF = 0.004  # per °C (0.4% per °C)
TEMP_REFERENCE = 25  # °C
MODULE_TEMP_RISE_COEFF = 0.03  # °C per W/m² irradiance

# System losses (fixed MVP)
INVERTER_EFFICIENCY = 0.97  # 97%
WIRING_LOSS_FACTOR = 0.99  # 1% loss
SOILING_LOSS_FACTOR = 0.98  # 2% loss
SYSTEM_LOSSES_FACTOR = INVERTER_EFFICIENCY * WIRING_LOSS_FACTOR * SOILING_LOSS_FACTOR  # ~0.942

# Seasonal ambient temperature model (sinusoidal). Provides a realistic
# range for module temperature without per-location climate data.
AMBIENT_TEMP_MEAN_C = 15.0  # Yearly mean
AMBIENT_TEMP_AMPLITUDE_C = 10.0  # Half-range; ±10°C from mean

# Input validation ranges
LATITUDE_MIN = -90
LATITUDE_MAX = 90
LONGITUDE_MIN = -180
LONGITUDE_MAX = 180
PANEL_COUNT_MIN = 1
PANEL_AREA_MIN = 0.1
PANEL_EFFICIENCY_MIN = 5
PANEL_EFFICIENCY_MAX = 25
TILT_ANGLE_MIN = 0
TILT_ANGLE_MAX = 90
AZIMUTH_MIN = 0
AZIMUTH_MAX = 360
DURATION_DAYS_MIN = 1

# Hour parameters
HOURS_PER_DAY = 24
MONTHS_PER_YEAR = 12

# Civil twilight angle (degrees below horizon)
CIVIL_TWILIGHT_ANGLE = -6
