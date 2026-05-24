"""Integration tests for /simulate endpoint including validation, rate limiting, security, and CORS."""

import time
import unittest.mock

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app


@pytest.fixture
def client():
    """FastAPI TestClient for /simulate endpoint."""
    return TestClient(app)


@pytest.fixture
def valid_solar_payload():
    """Valid solar input payload."""
    return {
        "latitude": 45.0703,
        "longitude": 7.6869,
        "panel_count": 10,
        "panel_area_m2": 2.0,
        "panel_efficiency": 20,
        "tilt_angle_deg": 35,
        "azimuth_deg": 180,
        "start_date": "2026-06-21",
        "duration_days": 1,
    }


@pytest.fixture
def valid_battery_payload():
    """Valid solar + battery input payload."""
    return {
        "latitude": 45.0703,
        "longitude": 7.6869,
        "panel_count": 10,
        "panel_area_m2": 2.0,
        "panel_efficiency": 20,
        "tilt_angle_deg": 35,
        "azimuth_deg": 180,
        "start_date": "2026-06-21",
        "duration_days": 1,
        "battery_capacity_kwh": 10.0,
        "battery_charge_efficiency": 95.0,
        "battery_discharge_efficiency": 95.0,
        "daily_load_kwh": 10.0,
        "initial_soc_pct": 50.0,
    }


@pytest.fixture
def invalid_inputs():
    """Invalid inputs for parameterized tests."""
    return [
        ({"latitude": 95, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "latitude"),
        ({"latitude": 45, "longitude": 181, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "longitude"),
        ({"latitude": 45, "longitude": 7, "panel_count": 0, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "panel_count"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": -1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "panel_area"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 101, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "panel_efficiency"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": -1, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "tilt_angle"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 361, "start_date": "2026-06-21", "duration_days": 1}, "azimuth"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 0}, "duration"),
    ]


class TestSimulateEndpointIntegration:
    """Test the /simulate endpoint with valid inputs."""

    def test_valid_solar_request_returns_200(self, client, valid_solar_payload):
        """Test valid solar request returns 200 with complete response."""
        response = client.post("/simulate", json=valid_solar_payload)
        assert response.status_code == 200
        data = response.json()
        assert "daily_hourly_generation" in data
        assert "monthly_energy_kwh" in data
        assert "annual_energy_kwh" in data
        assert "average_daily_kwh" in data
        assert "peak_hour_kw" in data
        assert "system_capacity_kw" in data

    def test_solar_response_field_types(self, client, valid_solar_payload):
        """Verify field types and ranges."""
        response = client.post("/simulate", json=valid_solar_payload)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["daily_hourly_generation"], list)
        assert isinstance(data["monthly_energy_kwh"], list)
        assert isinstance(data["annual_energy_kwh"], (int, float))
        assert isinstance(data["average_daily_kwh"], (int, float))
        assert isinstance(data["peak_hour_kw"], (int, float))
        assert isinstance(data["system_capacity_kw"], (int, float))
        assert data["annual_energy_kwh"] > 0
        assert data["system_capacity_kw"] > 0
        assert len(data["daily_hourly_generation"]) == 24
        assert len(data["monthly_energy_kwh"]) == 12

    def test_legacy_request_no_battery_fields(self, client, valid_solar_payload):
        """Test legacy request (no battery fields) returns 200 without battery fields."""
        response = client.post("/simulate", json=valid_solar_payload)
        assert response.status_code == 200
        data = response.json()
        assert "battery_hourly_soc" not in data
        assert "self_consumption_pct" not in data
        assert "grid_import_kwh" not in data
        assert "grid_export_kwh" not in data

    def test_response_time_under_500ms(self, client, valid_solar_payload):
        """Test response time <500ms for typical request."""
        start = time.time()
        response = client.post("/simulate", json=valid_solar_payload)
        elapsed_ms = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed_ms < 500


class TestInputValidation:
    """Test input validation with invalid inputs."""

    @pytest.mark.parametrize("invalid_payload,field", [
        ({"latitude": 95, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "latitude"),
        ({"latitude": -91, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "latitude"),
        ({"latitude": 45, "longitude": 181, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "longitude"),
        ({"latitude": 45, "longitude": -181, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "longitude"),
        ({"latitude": 45, "longitude": 7, "panel_count": 0, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "panel_count"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": -0.1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "panel_area"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 101, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "panel_efficiency"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": -1, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "panel_efficiency"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": -1, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "tilt_angle"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 91, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}, "tilt_angle"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": -1, "start_date": "2026-06-21", "duration_days": 1}, "azimuth"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 361, "start_date": "2026-06-21", "duration_days": 1}, "azimuth"),
        ({"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 0}, "duration"),
    ])
    def test_invalid_input_returns_422(self, client, invalid_payload, field):
        """Test invalid input returns 422."""
        response = client.post("/simulate", json=invalid_payload)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_partial_battery_fields_rejected(self, client, valid_solar_payload):
        """Test partial battery fields are rejected (all-or-nothing validation)."""
        payload = {**valid_solar_payload, "battery_capacity_kwh": 10.0}
        response = client.post("/simulate", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # Verify error message mentions battery validation
        error_text = str(data)
        assert "battery" in error_text.lower()


class TestRateLimiting:
    """Test rate limiting enforcement."""

    def test_single_request_succeeds(self, client, valid_solar_payload):
        """Test single request succeeds (within limit)."""
        response = client.post("/simulate", json=valid_solar_payload)
        assert response.status_code == 200

    def test_multiple_requests_within_limit(self, client, valid_solar_payload):
        """Test 10 requests in 60 seconds all succeed."""
        for i in range(10):
            response = client.post("/simulate", json=valid_solar_payload)
            assert response.status_code == 200, f"Request {i+1} failed"

    def test_eleventh_request_exceeds_limit(self, client, valid_solar_payload):
        """Test 11th request exceeds limit and receives 429."""
        for i in range(10):
            response = client.post("/simulate", json=valid_solar_payload)
            assert response.status_code == 200
        response = client.post("/simulate", json=valid_solar_payload)
        assert response.status_code == 429


class TestSecurityHeaders:
    """Test security headers on all responses."""

    def test_security_headers_on_success_response(self, client, valid_solar_payload):
        """Test security headers present on success response."""
        response = client.post("/simulate", json=valid_solar_payload)
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers

    def test_security_headers_on_error_response(self, client):
        """Test security headers on error response."""
        invalid_payload = {"latitude": 95, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}
        response = client.post("/simulate", json=invalid_payload)
        assert response.status_code == 422
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_security_headers_on_health(self, client):
        """Test security headers on /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"


class TestErrorHandling:
    """Test error handling in development vs. production."""

    def test_development_error_includes_traceback(self, client, monkeypatch):
        """Test development error response includes stack trace."""
        monkeypatch.setattr(main_module, "env", "development")
        with unittest.mock.patch("app.main.simulate", side_effect=RuntimeError("test error")):
            invalid_payload = {"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}
            response = client.post("/simulate", json=invalid_payload)
            assert response.status_code == 500
            assert "Traceback" in response.json()["detail"]

    def test_production_error_is_generic(self, client, monkeypatch):
        """Test production error response is generic."""
        monkeypatch.setattr(main_module, "env", "production")
        with unittest.mock.patch("app.main.simulate", side_effect=RuntimeError("test error")):
            invalid_payload = {"latitude": 45, "longitude": 7, "panel_count": 1, "panel_area_m2": 1, "panel_efficiency": 20, "tilt_angle_deg": 35, "azimuth_deg": 180, "start_date": "2026-06-21", "duration_days": 1}
            response = client.post("/simulate", json=invalid_payload)
            assert response.status_code == 500
            assert "Simulation failed" in response.json()["detail"]

    def test_invalid_endpoint_returns_404(self, client):
        """Test 404 for invalid endpoint."""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404

    def test_invalid_http_method_returns_405(self, client):
        """Test GET to POST-only endpoint returns 405."""
        response = client.get("/simulate")
        assert response.status_code == 405


class TestCORSBehavior:
    """Test CORS behavior."""

    def test_post_request_includes_cors_origin_header(self, client, valid_solar_payload):
        """Test POST request from allowed origin includes CORS origin header."""
        response = client.post("/simulate", json=valid_solar_payload, headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"

    def test_cors_from_allowed_origin(self, client, valid_solar_payload):
        """Test CORS request from allowed origin succeeds."""
        response = client.post("/simulate", json=valid_solar_payload, headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" in response.headers

    def test_cors_from_blocked_origin(self, client, valid_solar_payload):
        """Test CORS request from blocked origin fails."""
        response = client.post("/simulate", json=valid_solar_payload, headers={"Origin": "http://blocked-origin.com"})
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" not in response.headers
