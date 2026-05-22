"""Unit tests for irradiance module (GHI, DNI, DHI, tilted irradiance)."""

import math
from datetime import datetime

import pytest

from app.irradiance import (
    air_mass,
    clear_sky_dni,
    clear_sky_ghi,
    cloud_factor,
    decompose_ghi,
    extraterrestrial_irradiance,
    hourly_irradiance,
    tilted_irradiance,
)


class TestExtraterrestrialIrradiance:
    """Tests for extraterrestrial irradiance (Earth-Sun distance correction)."""

    def test_extraterrestrial_near_1361_wm2(self):
        """Extraterrestrial irradiance should be near solar constant ~1361 W/m²."""
        for doy in [1, 100, 200, 355]:
            e0 = extraterrestrial_irradiance(doy)
            # Earth-Sun distance varies ±3.3%, so range is ~1317 to 1407 W/m²
            assert 1315 < e0 < 1410, f"E0 {e0} on doy {doy} outside realistic range"

    def test_extraterrestrial_varies_by_season(self):
        """E0 should vary slightly by Earth-Sun distance (perihelion/aphelion)."""
        # Perihelion: early January (doy ~3), closest to sun
        # Aphelion: early July (doy ~185), farthest from sun
        e0_jan = extraterrestrial_irradiance(3)
        e0_jul = extraterrestrial_irradiance(185)

        # Perihelion should be slightly higher than aphelion
        assert e0_jan > e0_jul, "January E0 should be higher than July (perihelion effect)"

        # Difference should be ~3.3% (known physics)
        ratio = e0_jan / e0_jul
        assert 1.025 < ratio < 1.040, f"E0 perihelion/aphelion ratio {ratio} not ~3.3%"


class TestAirMass:
    """Tests for relative optical air mass (Kasten & Young)."""

    def test_air_mass_at_90_elevation(self):
        """At 90° elevation (sun at zenith), air mass should be very close to 1.0."""
        am = air_mass(90.0)
        assert am == pytest.approx(1.0, rel=1e-3)

    def test_air_mass_increases_with_lower_elevation(self):
        """Air mass should increase as elevation decreases."""
        am_90 = air_mass(90.0)
        am_45 = air_mass(45.0)
        am_10 = air_mass(10.0)

        assert am_90 < am_45 < am_10, "Air mass should increase with lower elevation"

    def test_air_mass_near_horizon(self):
        """At ~0° elevation, air mass should be high (~38)."""
        am = air_mass(0.5)
        assert am > 30, f"Near horizon air mass {am} should be very high"

    def test_air_mass_at_typical_elevations(self):
        """Air mass at typical elevations matches known values."""
        # At 30° elevation, AM should be ~2
        am_30 = air_mass(30.0)
        assert 1.9 < am_30 < 2.1, f"AM at 30° should be ~2, got {am_30}"

        # At 60° elevation, AM should be ~1.15
        am_60 = air_mass(60.0)
        assert 1.1 < am_60 < 1.2, f"AM at 60° should be ~1.15, got {am_60}"


class TestClearSkyGHI:
    """Tests for clear-sky Global Horizontal Irradiance."""

    def test_ghi_zero_at_negative_elevation(self):
        """GHI should be 0 when sun is below horizon."""
        ghi = clear_sky_ghi(-5.0, 172)
        assert ghi == pytest.approx(0.0, abs=1e-9)

    def test_ghi_increases_with_elevation(self):
        """Clear-sky GHI should increase with sun elevation."""
        ghi_10 = clear_sky_ghi(10.0, 172)
        ghi_45 = clear_sky_ghi(45.0, 172)
        ghi_80 = clear_sky_ghi(80.0, 172)

        assert ghi_10 < ghi_45 < ghi_80, "GHI should increase with elevation"

    def test_ghi_peak_near_1000_wm2(self):
        """At peak elevation (near zenith), clear-sky GHI should approach ~1000 W/m²."""
        # June 21 (doy 172), high elevation
        ghi_peak = clear_sky_ghi(89.0, 172)
        assert ghi_peak > 900, f"Peak clear-sky GHI {ghi_peak} should exceed 900 W/m²"

    def test_ghi_seasonal_variation(self):
        """Clear-sky GHI should vary with day of year due to atmospheric effects."""
        # Test that GHI varies somewhat between seasons at same elevation
        ghi_jun = clear_sky_ghi(45.0, 172)  # June
        ghi_jan = clear_sky_ghi(45.0, 1)  # January

        # These should be different due to Earth-Sun distance effects
        assert ghi_jun != ghi_jan, "GHI should vary between seasons"
        # Absolute difference should be small relative to magnitude (Earth-Sun distance is ~3.3%)
        relative_diff = abs(ghi_jun - ghi_jan) / max(ghi_jun, ghi_jan)
        assert relative_diff > 0.01, "Seasonal variation should be measurable"


class TestClearSkyNI:
    """Tests for clear-sky Direct Normal Irradiance."""

    def test_dni_zero_at_negative_elevation(self):
        """DNI should be 0 when sun is below horizon."""
        dni = clear_sky_dni(-5.0, 172)
        assert dni == pytest.approx(0.0, abs=1e-9)

    def test_dni_peak_near_900_wm2(self):
        """At high elevation, clear-sky DNI should peak ~900 W/m²."""
        dni = clear_sky_dni(85.0, 172)
        assert 800 < dni < 950, f"Peak clear-sky DNI {dni} outside expected range"

    def test_dni_higher_than_ghi(self):
        """DNI should generally be higher than GHI at high sun elevations."""
        for elev in [30, 50, 70]:
            dni = clear_sky_dni(elev, 172)
            ghi = clear_sky_ghi(elev, 172)
            # At high elevations, DNI (normal irradiance) > GHI (horizontal)
            assert dni >= ghi, f"DNI {dni} should be >= GHI {ghi} at elevation {elev}°"


class TestCloudFactor:
    """Tests for seasonal cloud factor."""

    def test_cloud_factor_range(self):
        """Cloud factor should be between 0.05 and 1.0."""
        for lat in [-60, -30, 0, 30, 60]:
            for doy in [1, 100, 200, 355]:
                cf = cloud_factor(lat, doy)
                assert 0.0 <= cf <= 1.0, f"Cloud factor {cf} outside [0, 1] for lat {lat} doy {doy}"

    def test_nh_clearest_in_summer(self):
        """Northern hemisphere should be clearest around summer solstice."""
        cf_jun = cloud_factor(45.0, 172)  # June
        cf_dec = cloud_factor(45.0, 355)  # December
        assert cf_jun > cf_dec, "NH should be clearer in summer than winter"

    def test_sh_inverted_seasonality(self):
        """Southern hemisphere should show inverted seasonality from NH."""
        # Check that cloud factor varies differently in SH vs NH
        cf_jun_nh = cloud_factor(45.0, 172)  # NH summer
        cf_jun_sh = cloud_factor(-45.0, 172)  # NH summer = SH winter
        cf_dec_sh = cloud_factor(-45.0, 355)  # NH winter = SH summer
        cf_dec_nh = cloud_factor(45.0, 355)  # NH winter

        # In NH, summer should be clearer than winter
        assert cf_jun_nh > cf_dec_nh, "NH summer should be clearer than winter"
        # In SH, summer should be clearer than winter
        assert cf_dec_sh > cf_jun_sh, "SH summer (Dec) should be clearer than winter (Jun)"

    def test_cloud_factor_amplitude_with_latitude(self):
        """Cloud factor amplitude should increase with latitude."""
        # Compare amplitude at different latitudes
        cf_equator = []
        cf_arctic = []
        for doy in range(1, 366, 30):
            cf_equator.append(cloud_factor(0.0, doy))
            cf_arctic.append(cloud_factor(60.0, doy))

        amp_equator = max(cf_equator) - min(cf_equator)
        amp_arctic = max(cf_arctic) - min(cf_arctic)

        assert amp_arctic > amp_equator, "Arctic should have larger seasonal variation"

    def test_cloud_factor_near_extreme(self):
        """At extreme latitudes, should still be bounded."""
        cf_pole = cloud_factor(89.9, 172)
        assert 0.0 <= cf_pole <= 1.0, "Cloud factor at pole should be bounded"


class TestDecomposeGHI:
    """Tests for GHI decomposition into DNI and DHI (Erbs correlation)."""

    def test_decomposition_returns_tuple(self):
        """Should return (dni, dhi) tuple."""
        result = decompose_ghi(500.0, 45.0, 172)
        assert isinstance(result, tuple)
        assert len(result) == 2
        dni, dhi = result
        assert isinstance(dni, float)
        assert isinstance(dhi, float)

    def test_ghi_reconstructed_from_components(self):
        """DNI and DHI should reconstruct GHI: DNI*sin(elev) + DHI ≈ GHI."""
        ghi = 600.0
        elevation = 45.0
        dni, dhi = decompose_ghi(ghi, elevation, 172)

        # Reconstruct horizontal beam: direct_horizontal = DNI * sin(elevation)
        sin_elev = math.sin(math.radians(elevation))
        direct_horizontal = dni * sin_elev
        reconstructed = direct_horizontal + dhi

        assert reconstructed == pytest.approx(ghi, rel=0.05)

    def test_dhi_fraction_varies_with_clearness(self):
        """Diffuse fraction should increase when sky is cloudier (lower kt)."""
        elevation = 45.0
        doy = 172

        # Clear sky: high kt (ghi close to clear-sky max)
        ghi_clear = 800.0
        _, dhi_clear = decompose_ghi(ghi_clear, elevation, doy)

        # Cloudy: low kt
        ghi_cloudy = 300.0
        _, dhi_cloudy = decompose_ghi(ghi_cloudy, elevation, doy)

        # Cloudy condition should have higher diffuse fraction
        frac_clear = dhi_clear / ghi_clear if ghi_clear > 0 else 0
        frac_cloudy = dhi_cloudy / ghi_cloudy if ghi_cloudy > 0 else 0

        assert frac_cloudy > frac_clear, "Cloudy conditions should have higher diffuse fraction"

    def test_decomposition_zero_irradiance(self):
        """Zero input GHI should give zero outputs."""
        dni, dhi = decompose_ghi(0.0, 45.0, 172)
        assert dni == 0.0
        assert dhi == 0.0


class TestTiltedIrradiance:
    """Tests for irradiance on a tilted surface (isotropic-sky transposition)."""

    def test_tilted_zero_for_sun_below_horizon(self):
        """Tilted irradiance should be minimal when sun is below horizon."""
        # Negative elevation - only diffuse and reflected components
        tilted = tilted_irradiance(
            ghi=100,
            dhi=50,
            dni=0,  # At night, mainly diffuse
            elevation_deg=-10,
            tilt_deg=35,
            sun_azimuth_deg=180,
            surface_azimuth_deg=180,
        )
        # With 0 beam, should only have diffuse and reflected components
        # which should be small for night conditions
        assert tilted < 100, "Should be small when sun below horizon"

    def test_tilted_horizontal_equals_ghi(self):
        """For horizontal surface (tilt=0), tilted irradiance should be close to GHI."""
        ghi = 600.0
        elevation = 45.0
        doy = 172

        # Decompose GHI into DNI and DHI
        dni, dhi = decompose_ghi(ghi, elevation, doy)

        # Horizontal surface (tilt=0): tilted irradiance = beam*sin(elev) + diffuse + reflected
        # For horizontal: diffuse factor = 1, reflected factor = 0
        # So tilted should be: DNI*sin(elev) + DHI
        sin_elev = math.sin(math.radians(elevation))
        expected = dni * sin_elev + dhi

        tilted = tilted_irradiance(
            ghi=ghi,
            dhi=dhi,
            dni=dni,
            elevation_deg=elevation,
            tilt_deg=0,
            sun_azimuth_deg=180,
            surface_azimuth_deg=180,
        )

        assert tilted == pytest.approx(expected, rel=0.01)

    def test_south_facing_better_than_north(self):
        """South-facing surface should receive more than north-facing."""
        ghi = 600.0
        dhi = 100.0
        elevation = 45.0
        _, dni = __import__("app.irradiance", fromlist=["decompose_ghi"]).decompose_ghi(
            ghi, elevation, 172
        )

        # South facing (180°) at solar noon (sun is south)
        south = tilted_irradiance(
            ghi=ghi,
            dhi=dhi,
            dni=dni,
            elevation_deg=elevation,
            tilt_deg=35,
            sun_azimuth_deg=180,
            surface_azimuth_deg=180,
        )

        # North facing (0°)
        north = tilted_irradiance(
            ghi=ghi,
            dhi=dhi,
            dni=dni,
            elevation_deg=elevation,
            tilt_deg=35,
            sun_azimuth_deg=180,
            surface_azimuth_deg=0,
        )

        assert south > north, "South-facing should be better than north at noon"

    def test_components_non_negative(self):
        """All components (beam, diffuse, reflected) should be non-negative."""
        # This indirectly tests by ensuring result is non-negative
        ghi = 600.0
        dhi = 100.0
        elevation = 45.0
        _, dni = __import__("app.irradiance", fromlist=["decompose_ghi"]).decompose_ghi(
            ghi, elevation, 172
        )

        tilted = tilted_irradiance(
            ghi=ghi,
            dhi=dhi,
            dni=dni,
            elevation_deg=elevation,
            tilt_deg=35,
            sun_azimuth_deg=180,
            surface_azimuth_deg=180,
        )

        assert tilted >= 0, "Tilted irradiance should not be negative"


class TestHourlyIrradiance:
    """Tests for complete hourly tilted-plane irradiance."""

    def test_hourly_irradiance_zero_at_night(self, turin_location):
        """Hourly irradiance should be 0 at night (e.g., hour 0)."""
        date = datetime(2026, 6, 21)
        irrad = hourly_irradiance(
            turin_location["latitude"],
            turin_location["longitude"],
            date,
            hour=0,
            tilt=35.0,
            azimuth=180.0,
        )
        assert irrad == pytest.approx(0.0, abs=1e-6)

    def test_hourly_irradiance_positive_during_day(self, turin_location):
        """Hourly irradiance should be positive during daylight."""
        date = datetime(2026, 6, 21)
        irrad = hourly_irradiance(
            turin_location["latitude"],
            turin_location["longitude"],
            date,
            hour=12,  # Solar noon region
            tilt=35.0,
            azimuth=180.0,
        )
        assert irrad > 100, f"Noon irradiance {irrad} should be > 100 W/m²"

    def test_hourly_irradiance_peaks_near_noon(self, turin_location):
        """Irradiance should peak near solar noon."""
        date = datetime(2026, 6, 21)
        irradiances = []
        for hour in range(24):
            irrad = hourly_irradiance(
                turin_location["latitude"],
                turin_location["longitude"],
                date,
                hour=hour,
                tilt=35.0,
                azimuth=180.0,
            )
            irradiances.append(irrad)

        peak_hour = irradiances.index(max(irradiances))
        assert 8 <= peak_hour <= 16, f"Peak irradiance at hour {peak_hour} not near noon"

    def test_hourly_irradiance_seasonal_variation(self, turin_location):
        """Irradiance should be higher in June than December."""
        jun_date = datetime(2026, 6, 21)
        dec_date = datetime(2026, 12, 21)

        # Compare noon irradiance
        irrad_jun = hourly_irradiance(
            turin_location["latitude"],
            turin_location["longitude"],
            jun_date,
            hour=12,
            tilt=35.0,
            azimuth=180.0,
        )

        irrad_dec = hourly_irradiance(
            turin_location["latitude"],
            turin_location["longitude"],
            dec_date,
            hour=12,
            tilt=35.0,
            azimuth=180.0,
        )

        assert irrad_jun > irrad_dec, "June noon irradiance should exceed December"

    def test_hourly_irradiance_south_facing_better(self, turin_location):
        """South-facing (180°) should have better annual performance at 45°N."""
        date = datetime(2026, 6, 21)

        south = hourly_irradiance(
            turin_location["latitude"],
            turin_location["longitude"],
            date,
            hour=12,
            tilt=35.0,
            azimuth=180.0,  # South
        )

        north = hourly_irradiance(
            turin_location["latitude"],
            turin_location["longitude"],
            date,
            hour=12,
            tilt=35.0,
            azimuth=0.0,  # North
        )

        assert south > north, "South-facing should be better than north at 45°N"

    def test_hourly_irradiance_realistic_range(self, turin_location):
        """Hourly irradiance should stay within realistic physical bounds."""
        date = datetime(2026, 6, 21)
        for hour in range(24):
            irrad = hourly_irradiance(
                turin_location["latitude"],
                turin_location["longitude"],
                date,
                hour=hour,
                tilt=35.0,
                azimuth=180.0,
            )
            # Maximum possible: clear sky at high elevation ~1000 W/m²
            # With cloud factor typically 0.6-0.8, max expected ~800 W/m²
            assert 0 <= irrad <= 1100, f"Hourly irradiance {irrad} outside [0, 1100]"
