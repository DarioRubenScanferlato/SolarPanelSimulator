"""
Solar Panel Simulator - Physical Constants
Standard PV and solar radiation constants
"""

# Solar radiation
SOLAR_CONSTANT_WM2 = 1361  # W/m², extraterrestrial irradiance
EARTH_ORBIT_ECCENTRICITY = 1.00011  # Earth orbit eccentricity factor

# Atmospheric parameters
ANGSTROM_A = 0.7  # Clear-sky index coefficient a
ANGSTROM_B = 0.3  # Clear-sky index coefficient b
AIR_MASS_REF = 1.5  # Reference air mass for efficiency
CLEARNESS_INDEX_MAX = 0.75  # Max clearness index (clear sky)

# PV module parameters
TEMP_DERATING_COEFF = 0.004  # per °C (0.4% per °C)
TEMP_REFERENCE = 25  # °C
MODULE_TEMP_RISE_COEFF = 0.03  # °C per W/m² irradiance

# System losses (fixed MVP)
INVERTER_EFFICIENCY = 0.97  # 97%
WIRING_LOSS_FACTOR = 0.99  # 1% loss
SOILING_LOSS_FACTOR = 0.98  # 2% loss
SYSTEM_LOSSES_FACTOR = INVERTER_EFFICIENCY * WIRING_LOSS_FACTOR * SOILING_LOSS_FACTOR  # ~0.942

# Seasonal variation for Ångström model
SEASONAL_MIN = 0.6  # Winter
SEASONAL_MAX = 1.1  # Summer

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

# Ambient temperature for calculations (default)
AMBIENT_TEMP_CELSIUS = 20
