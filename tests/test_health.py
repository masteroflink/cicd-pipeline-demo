"""Tests for the health check endpoint.

TDD: These tests are written BEFORE the implementation.
"""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Test that GET /health returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client: TestClient) -> None:
        """Test that health response contains status field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_returns_version(self, client: TestClient) -> None:
        """Test that health response contains version field."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)

    def test_health_returns_timestamp(self, client: TestClient) -> None:
        """Test that health response contains timestamp field."""
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

    def test_health_returns_environment(self, client: TestClient) -> None:
        """Test that health response contains environment field."""
        response = client.get("/health")
        data = response.json()
        assert "environment" in data
        assert isinstance(data["environment"], str)

    def test_health_response_structure(self, client: TestClient) -> None:
        """Test the complete structure of health response."""
        response = client.get("/health")
        data = response.json()

        expected_keys = {"status", "version", "timestamp", "environment"}
        assert set(data.keys()) == expected_keys
