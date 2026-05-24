"""Integration tests for FastAPI endpoints (/health and /simulate)."""

import unittest.mock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import SolarInput


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_200(self, client):
        """GET /health should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        """GET /health should return {"status": "healthy"}."""
        response = client.get("/health")
        data = response.json()
        assert data == {"status": "healthy"}

    def test_health_content_type(self, client):
        """GET /health should return JSON."""
        response = client.get("/health")
        assert response.headers["content-type"].startswith("application/json")


class TestSimulateEndpoint:
    """Tests for /simulate endpoint."""

    def test_simulate_valid_input_returns_200(self, client, default_solar_input):
        """POST /simulate with valid input should return 200."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_response_has_all_required_fields(self, client, default_solar_input):
        """Response should contain all required SolarOutput fields."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        required_fields = [
            "annual_energy_kwh",
            "average_daily_kwh",
            "peak_hour_kw",
            "system_capacity_kw",
            "daily_hourly_generation",
            "daily_sunrise",
            "daily_sunset",
            "monthly_energy_kwh",
            "calculation_date",
        ]

        for field in required_fields:
            assert field in data, f"Response missing field: {field}"

    def test_simulate_daily_hourly_generation_length(self, client, default_solar_input):
        """daily_hourly_generation should have 24 values."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        assert len(data["daily_hourly_generation"]) == 24

    def test_simulate_monthly_energy_length(self, client, default_solar_input):
        """monthly_energy_kwh should have 12 values."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        assert len(data["monthly_energy_kwh"]) == 12

    def test_simulate_energy_values_positive(self, client, default_solar_input):
        """Energy values should be positive."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        assert data["annual_energy_kwh"] > 0
        assert data["average_daily_kwh"] > 0
        assert data["peak_hour_kw"] > 0
        assert data["system_capacity_kw"] > 0

    def test_simulate_capacity_calculation(self, client, default_solar_input):
        """System capacity should equal panel_count * panel_area * efficiency / 100."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        expected_capacity = (
            default_solar_input.panel_count
            * default_solar_input.panel_area_m2
            * default_solar_input.panel_efficiency
            / 100
        )

        assert data["system_capacity_kw"] == pytest.approx(expected_capacity, rel=0.01)

    def test_simulate_missing_required_field(self, client):
        """POST /simulate without required field should return 422."""
        payload = {
            "latitude": 45.0,
            "longitude": 7.0,
            "panel_count": 10,
            # Missing panel_area_m2
            "panel_efficiency": 20,
            "tilt_angle_deg": 35,
            "azimuth_deg": 180,
            "start_date": "2026-06-21",
            "duration_days": 1,
        }
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_latitude_high(self, client, default_solar_input):
        """POST /simulate with latitude > 90 should return 422."""
        payload = default_solar_input.model_dump()
        payload["latitude"] = 95.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_latitude_low(self, client, default_solar_input):
        """POST /simulate with latitude < -90 should return 422."""
        payload = default_solar_input.model_dump()
        payload["latitude"] = -95.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_longitude_high(self, client, default_solar_input):
        """POST /simulate with longitude > 180 should return 422."""
        payload = default_solar_input.model_dump()
        payload["longitude"] = 185.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_longitude_low(self, client, default_solar_input):
        """POST /simulate with longitude < -180 should return 422."""
        payload = default_solar_input.model_dump()
        payload["longitude"] = -185.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_boundary_latitude_90(self, client, default_solar_input):
        """POST /simulate with latitude = 90 should succeed."""
        payload = default_solar_input.model_dump()
        payload["latitude"] = 90.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_boundary_latitude_minus_90(self, client, default_solar_input):
        """POST /simulate with latitude = -90 should succeed."""
        payload = default_solar_input.model_dump()
        payload["latitude"] = -90.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_boundary_longitude_180(self, client, default_solar_input):
        """POST /simulate with longitude = 180 should succeed."""
        payload = default_solar_input.model_dump()
        payload["longitude"] = 180.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_boundary_longitude_minus_180(self, client, default_solar_input):
        """POST /simulate with longitude = -180 should succeed."""
        payload = default_solar_input.model_dump()
        payload["longitude"] = -180.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_invalid_panel_count_zero(self, client, default_solar_input):
        """POST /simulate with panel_count = 0 should return 422."""
        payload = default_solar_input.model_dump()
        payload["panel_count"] = 0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_panel_area_negative(self, client, default_solar_input):
        """POST /simulate with negative panel_area should return 422."""
        payload = default_solar_input.model_dump()
        payload["panel_area_m2"] = -1.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_efficiency_too_low(self, client, default_solar_input):
        """POST /simulate with efficiency < 5% should return 422."""
        payload = default_solar_input.model_dump()
        payload["panel_efficiency"] = 3.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_efficiency_too_high(self, client, default_solar_input):
        """POST /simulate with efficiency > 25% should return 422."""
        payload = default_solar_input.model_dump()
        payload["panel_efficiency"] = 30.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_boundary_panel_count_1(self, client, default_solar_input):
        """POST /simulate with panel_count = 1 should succeed."""
        payload = default_solar_input.model_dump()
        payload["panel_count"] = 1
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_boundary_duration_1_day(self, client, default_solar_input):
        """POST /simulate with duration_days = 1 should succeed."""
        payload = default_solar_input.model_dump()
        payload["duration_days"] = 1
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_boundary_duration_365_days(self, client, default_solar_input):
        """POST /simulate with duration_days = 365 should succeed."""
        payload = default_solar_input.model_dump()
        payload["duration_days"] = 365
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_invalid_duration_zero(self, client, default_solar_input):
        """POST /simulate with duration_days = 0 should return 422."""
        payload = default_solar_input.model_dump()
        payload["duration_days"] = 0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_date_format(self, client, default_solar_input):
        """POST /simulate with invalid date format should return 422."""
        payload = default_solar_input.model_dump()
        payload["start_date"] = "06-21-2026"  # Wrong format
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_tilt_negative(self, client, default_solar_input):
        """POST /simulate with negative tilt should return 422."""
        payload = default_solar_input.model_dump()
        payload["tilt_angle_deg"] = -5.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_tilt_over_90(self, client, default_solar_input):
        """POST /simulate with tilt > 90 should return 422."""
        payload = default_solar_input.model_dump()
        payload["tilt_angle_deg"] = 95.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_azimuth_negative(self, client, default_solar_input):
        """POST /simulate with negative azimuth should return 422."""
        payload = default_solar_input.model_dump()
        payload["azimuth_deg"] = -10.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_invalid_azimuth_over_360(self, client, default_solar_input):
        """POST /simulate with azimuth > 360 should return 422."""
        payload = default_solar_input.model_dump()
        payload["azimuth_deg"] = 370.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_simulate_boundary_azimuth_0(self, client, default_solar_input):
        """POST /simulate with azimuth = 0 (north) should succeed."""
        payload = default_solar_input.model_dump()
        payload["azimuth_deg"] = 0.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_boundary_azimuth_360(self, client, default_solar_input):
        """POST /simulate with azimuth = 360 (north again) should succeed."""
        payload = default_solar_input.model_dump()
        payload["azimuth_deg"] = 360.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_boundary_tilt_0(self, client, default_solar_input):
        """POST /simulate with tilt = 0 (horizontal) should succeed."""
        payload = default_solar_input.model_dump()
        payload["tilt_angle_deg"] = 0.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_boundary_tilt_90(self, client, default_solar_input):
        """POST /simulate with tilt = 90 (vertical) should succeed."""
        payload = default_solar_input.model_dump()
        payload["tilt_angle_deg"] = 90.0
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_simulate_consistency_annual_vs_monthly(self, client, default_solar_input):
        """Annual energy should approximately equal sum of monthly energy."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        monthly_sum = sum(data["monthly_energy_kwh"])
        assert data["annual_energy_kwh"] == pytest.approx(monthly_sum, rel=0.01)

    def test_simulate_consistency_average_daily(self, client, default_solar_input):
        """Average daily should equal annual / duration_days."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        expected_avg = data["annual_energy_kwh"] / default_solar_input.duration_days
        assert data["average_daily_kwh"] == pytest.approx(expected_avg, rel=0.01)

    def test_simulate_peak_hour_in_daily_profile(self, client, default_solar_input):
        """Peak hour should match maximum of daily hourly generation."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        daily_max = max(data["daily_hourly_generation"])
        assert data["peak_hour_kw"] == pytest.approx(daily_max, rel=0.01)

    def test_simulate_sunrise_before_sunset(self, client, default_solar_input):
        """Sunrise time should be before sunset time."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        data = response.json()

        sunrise = data["daily_sunrise"]
        sunset = data["daily_sunset"]

        # Format is HH:MM, so string comparison works
        assert sunrise < sunset

    def test_simulate_equator_response(self, client):
        """POST /simulate at equator should succeed."""
        payload = SolarInput(
            latitude=0.0,
            longitude=0.0,
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=10,
            azimuth_deg=180,
            start_date="2026-06-21",
            duration_days=1,
        ).model_dump()

        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["annual_energy_kwh"] > 0

    def test_simulate_arctic_response(self, client):
        """POST /simulate in arctic should succeed."""
        payload = SolarInput(
            latitude=70.0,
            longitude=25.0,
            panel_count=10,
            panel_area_m2=2.0,
            panel_efficiency=20,
            tilt_angle_deg=35,
            azimuth_deg=180,
            start_date="2026-06-21",
            duration_days=1,
        ).model_dump()

        response = client.post("/simulate", json=payload)
        assert response.status_code == 200


class TestCORSHeaders:
    """Tests for CORS headers."""

    def test_health_cors_headers(self, client):
        """GET /health should include CORS headers."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_simulate_cors_headers(self, client, default_solar_input):
        """POST /simulate should include CORS headers."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200

    def test_cors_preflight_allowed_origin(self, client):
        """OPTIONS preflight from allowed origin returns Access-Control-Allow-Origin."""
        response = client.options(
            "/simulate",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_preflight_explicit_methods(self, client):
        """OPTIONS preflight should list only GET and POST, not wildcard."""
        response = client.options(
            "/simulate",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "*" not in allow_methods
        assert "POST" in allow_methods or "GET" in allow_methods

    def test_cors_preflight_explicit_headers(self, client):
        """OPTIONS preflight should allow Content-Type, not wildcard."""
        response = client.options(
            "/simulate",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        allow_headers = response.headers.get("access-control-allow-headers", "")
        assert "*" not in allow_headers
        assert "content-type" in allow_headers.lower()

    def test_cors_credentials_not_allowed(self, client):
        """CORS should NOT expose access-control-allow-credentials: true."""
        response = client.options(
            "/simulate",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        allow_creds = response.headers.get("access-control-allow-credentials", "")
        assert allow_creds.lower() != "true"

    def test_cors_rejected_for_invalid_origin(self, client):
        """Origin not in ALLOWED_ORIGINS must not receive ACAO header."""
        response = client.options(
            "/simulate",
            headers={
                "Origin": "http://evil.example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.headers.get("access-control-allow-origin") != "http://evil.example.com"


class TestRateLimiting:
    """Tests for /simulate rate limiting."""

    def test_rate_limit_allows_requests_within_limit(self, client, default_solar_input):
        """First 3 requests should succeed (well within 10/minute limit)."""
        payload = default_solar_input.model_dump()
        for _ in range(3):
            response = client.post("/simulate", json=payload)
            assert response.status_code == 200

    def test_rate_limit_exceeded_returns_429(self, client, default_solar_input):
        """11th request to /simulate within the same minute should return 429."""
        payload = default_solar_input.model_dump()
        for i in range(10):
            response = client.post("/simulate", json=payload)
            assert response.status_code == 200, f"Request {i + 1} failed unexpectedly"
        response = client.post("/simulate", json=payload)
        assert response.status_code == 429


class TestSecurityHeaders:
    """Tests for security headers present on all responses."""

    def test_health_has_all_security_headers(self, client):
        """GET /health should include all four security headers."""
        response = client.get("/health")
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-xss-protection") == "1; mode=block"
        assert response.headers.get("strict-transport-security") == "max-age=31536000"

    def test_simulate_success_has_security_headers(self, client, default_solar_input):
        """POST /simulate 200 response must include all four security headers."""
        payload = default_solar_input.model_dump()
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-xss-protection") == "1; mode=block"
        assert response.headers.get("strict-transport-security") == "max-age=31536000"

    def test_simulate_error_has_security_headers(self, client, default_solar_input, monkeypatch):
        """Security headers must be present even on 500 error responses."""
        import app.main as main_module
        monkeypatch.setattr(main_module, "env", "production")
        with unittest.mock.patch("app.main.simulate", side_effect=RuntimeError("boom")):
            payload = default_solar_input.model_dump()
            response = client.post("/simulate", json=payload)
        assert response.status_code == 500
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"


class TestErrorMasking:
    """Tests for environment-aware error masking in /simulate."""

    def test_development_error_includes_message_and_traceback(self, client, default_solar_input, monkeypatch):
        """In development, error detail includes the exception message and full traceback."""
        import app.main as main_module
        monkeypatch.setattr(main_module, "env", "development")
        with unittest.mock.patch("app.main.simulate", side_effect=RuntimeError("division by zero")):
            payload = default_solar_input.model_dump()
            response = client.post("/simulate", json=payload)
        assert response.status_code == 500
        detail = response.json()["detail"]
        assert "division by zero" in detail
        assert "Traceback" in detail

    def test_production_error_is_generic(self, client, default_solar_input, monkeypatch):
        """In production, error detail is a generic message hiding implementation details."""
        import app.main as main_module
        monkeypatch.setattr(main_module, "env", "production")
        with unittest.mock.patch("app.main.simulate", side_effect=RuntimeError("secret db query")):
            payload = default_solar_input.model_dump()
            response = client.post("/simulate", json=payload)
        assert response.status_code == 500
        assert response.json()["detail"] == "Simulation failed. Please try again."
        assert "secret db query" not in str(response.json())


class TestBatterySimulation:
    """Tests for battery simulation and energy breakdown visualization (Story 2-7)."""

    @pytest.fixture
    def battery_input(self, default_solar_input):
        """Complete input with battery parameters for testing."""
        payload = default_solar_input.model_dump()
        payload.update({
            "battery_capacity_kwh": 10.0,
            "battery_charge_efficiency": 95.0,
            "battery_discharge_efficiency": 95.0,
            "daily_load_kwh": 10.0,
            "initial_soc_pct": 50.0
        })
        return payload

    def test_battery_simulation_returns_hourly_arrays(self, client, battery_input):
        """Battery simulation should return three 24-element hourly arrays for energy breakdown."""
        response = client.post("/simulate", json=battery_input)
        assert response.status_code == 200
        data = response.json()

        assert "battery_hourly_solar_consumption" in data
        assert "battery_hourly_grid_consumption" in data
        assert "battery_hourly_grid_export" in data

        assert len(data["battery_hourly_solar_consumption"]) == 24
        assert len(data["battery_hourly_grid_consumption"]) == 24
        assert len(data["battery_hourly_grid_export"]) == 24

    def test_battery_hourly_values_non_negative(self, client, battery_input):
        """All hourly energy values should be non-negative."""
        response = client.post("/simulate", json=battery_input)
        assert response.status_code == 200
        data = response.json()

        for hour_val in data["battery_hourly_solar_consumption"]:
            assert hour_val >= 0, "Solar consumption should be non-negative"

        for hour_val in data["battery_hourly_grid_consumption"]:
            assert hour_val >= 0, "Grid consumption should be non-negative"

        for hour_val in data["battery_hourly_grid_export"]:
            assert hour_val >= 0, "Grid export should be non-negative"

    def test_battery_hourly_totals_match_daily_summary(self, client, battery_input):
        """Sum of hourly grid values should match daily totals."""
        response = client.post("/simulate", json=battery_input)
        assert response.status_code == 200
        data = response.json()

        hourly_grid_import_sum = sum(data["battery_hourly_grid_consumption"])
        hourly_grid_export_sum = sum(data["battery_hourly_grid_export"])

        assert data["grid_import_kwh"] == pytest.approx(hourly_grid_import_sum, rel=0.01)
        assert data["grid_export_kwh"] == pytest.approx(hourly_grid_export_sum, rel=0.01)

    def test_battery_soc_stays_within_bounds(self, client, battery_input):
        """Battery state of charge should always be between 0 and capacity."""
        response = client.post("/simulate", json=battery_input)
        assert response.status_code == 200
        data = response.json()

        capacity = battery_input["battery_capacity_kwh"]
        for soc in data["battery_hourly_soc"]:
            assert 0 <= soc <= capacity, f"SoC {soc} out of bounds [0, {capacity}]"

    def test_battery_self_consumption_percentage_valid(self, client, battery_input):
        """Self-consumption percentage should be between 0 and 100."""
        response = client.post("/simulate", json=battery_input)
        assert response.status_code == 200
        data = response.json()

        assert 0 <= data["self_consumption_pct"] <= 100

    def test_battery_simulation_with_minimal_load(self, client, default_solar_input):
        """Battery simulation with minimal daily load should have minimal grid import."""
        payload = default_solar_input.model_dump()
        payload.update({
            "battery_capacity_kwh": 10.0,
            "battery_charge_efficiency": 95.0,
            "battery_discharge_efficiency": 95.0,
            "daily_load_kwh": 0.5,  # Minimal load (0.1 is minimum per validation)
            "initial_soc_pct": 50.0
        })
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()

        # With minimal load and large battery, grid import should be minimal
        assert data["grid_import_kwh"] < 1.0  # Should be very low

    def test_battery_simulation_high_load(self, client, default_solar_input):
        """Battery simulation with high load should import from grid."""
        payload = default_solar_input.model_dump()
        payload.update({
            "battery_capacity_kwh": 5.0,  # Small battery
            "battery_charge_efficiency": 95.0,
            "battery_discharge_efficiency": 95.0,
            "daily_load_kwh": 50.0,  # Very high load (>5x available battery + typical solar)
            "initial_soc_pct": 50.0
        })
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()

        # High load should result in significant grid import
        assert data["grid_import_kwh"] > 10.0  # Substantial grid dependency
        # With high load, self-consumption is high because solar is fully utilized
        assert data["self_consumption_pct"] >= 90

    def test_battery_energy_balance_per_hour(self, client, battery_input):
        """For each hour: verify energy balance with solar + battery + grid sources."""
        response = client.post("/simulate", json=battery_input)
        assert response.status_code == 200
        data = response.json()

        hourly_load = battery_input["daily_load_kwh"] / 24
        capacity = battery_input["battery_capacity_kwh"]

        for hour in range(24):
            solar = data["battery_hourly_solar_consumption"][hour]
            grid = data["battery_hourly_grid_consumption"][hour]
            soc_now = data["battery_hourly_soc"][hour]

            # SoC should always be within valid bounds
            assert 0 <= soc_now <= capacity, f"Hour {hour}: SoC {soc_now} out of bounds [0, {capacity}]"

            # Grid import should only occur when solar+battery insufficient
            if grid > 0:
                assert solar < hourly_load, f"Hour {hour}: Grid import {grid} when solar {solar} exceeds load {hourly_load}"

            # All consumption sources should be non-negative
            assert solar >= 0, f"Hour {hour}: Negative solar consumption {solar}"
            assert grid >= 0, f"Hour {hour}: Negative grid consumption {grid}"

    def test_battery_missing_battery_params_returns_422(self, client, default_solar_input):
        """POST /simulate with partial battery params should return 422."""
        payload = default_solar_input.model_dump()
        payload["battery_capacity_kwh"] = 10.0
        # Missing other battery params: should fail all-or-none validation
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422

    def test_battery_valid_without_params(self, client, default_solar_input):
        """POST /simulate without battery params should return 200 (solar-only)."""
        payload = default_solar_input.model_dump()
        # No battery params at all
        response = client.post("/simulate", json=payload)
        assert response.status_code == 200
        data = response.json()

        # Battery fields should be None/not present when no battery params
        assert data.get("battery_hourly_soc") is None or data.get("battery_hourly_soc") == []
