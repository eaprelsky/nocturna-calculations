import pytest
import json
from datetime import datetime, timedelta
import pytz
from nocturna.calculations.chart import Chart
from nocturna.calculations.position import Position
from nocturna.calculations.constants import CoordinateSystem
from nocturna.exceptions import ValidationError, AuthenticationError, AuthorizationError

class TestIntegration:
    @pytest.fixture
    def test_chart_data(self):
        return {
            "date": datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
            "location": Position(0.0, 51.5, 0.0, CoordinateSystem.GEOGRAPHIC)  # London coordinates
        }

    @pytest.fixture
    def test_user_data(self):
        return {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User"
        }

    def test_full_chart_calculation_flow(self, test_chart_data, test_user_data):
        """Test the complete flow of chart calculation from user registration to results"""
        # 1. Register user
        register_response = self.make_request(
            "POST",
            "/api/auth/register",
            json=test_user_data
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["user_id"]
        token = register_response.json()["token"]

        # 2. Create natal chart
        chart_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert chart_response.status_code == 201
        chart_id = chart_response.json()["chart_id"]

        # 3. Calculate positions
        positions_response = self.make_request(
            "POST",
            "/api/calculations/positions",
            json={
                "chart_id": chart_id,
                "planets": ["SUN", "MOON", "MARS", "VENUS", "JUPITER"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert positions_response.status_code == 200
        assert "positions" in positions_response.json()

        # 4. Calculate aspects
        aspects_response = self.make_request(
            "POST",
            "/api/calculations/aspects",
            json={
                "chart_id": chart_id,
                "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert aspects_response.status_code == 200
        assert "aspects" in aspects_response.json()

        # 5. Calculate houses
        houses_response = self.make_request(
            "POST",
            "/api/calculations/houses",
            json={
                "chart_id": chart_id,
                "house_system": "PLACIDUS"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert houses_response.status_code == 200
        assert "houses" in houses_response.json()

        # 6. Get complete chart
        chart_response = self.make_request(
            "GET",
            f"/api/charts/{chart_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert chart_response.status_code == 200
        chart_data = chart_response.json()
        assert "planets" in chart_data
        assert "aspects" in chart_data
        assert "houses" in chart_data

    def test_user_chart_management(self, test_chart_data, test_user_data):
        """Test user's ability to manage multiple charts"""
        # 1. Register and login
        self.make_request("POST", "/api/auth/register", json=test_user_data)
        login_response = self.make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["token"]

        # 2. Create multiple charts
        chart_ids = []
        for i in range(3):
            response = self.make_request(
                "POST",
                "/api/charts/natal",
                json={
                    "date": (test_chart_data["date"] + timedelta(days=i)).isoformat(),
                    "latitude": test_chart_data["location"].latitude,
                    "longitude": test_chart_data["location"].longitude
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 201
            chart_ids.append(response.json()["chart_id"])

        # 3. List user's charts
        response = self.make_request(
            "GET",
            "/api/charts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        charts = response.json()["charts"]
        assert len(charts) == 3

        # 4. Delete one chart
        response = self.make_request(
            "DELETE",
            f"/api/charts/{chart_ids[0]}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

        # 5. Verify chart count
        response = self.make_request(
            "GET",
            "/api/charts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        charts = response.json()["charts"]
        assert len(charts) == 2

    def test_concurrent_calculations(self, test_chart_data, test_user_data):
        """Test handling of concurrent calculation requests"""
        # 1. Register and login
        self.make_request("POST", "/api/auth/register", json=test_user_data)
        login_response = self.make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["token"]

        # 2. Create chart
        chart_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        chart_id = chart_response.json()["chart_id"]

        # 3. Make concurrent calculation requests
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for _ in range(5):
                futures.append(
                    executor.submit(
                        self.make_request,
                        "POST",
                        "/api/calculations/positions",
                        json={
                            "chart_id": chart_id,
                            "planets": ["SUN", "MOON", "MARS"]
                        },
                        headers={"Authorization": f"Bearer {token}"}
                    )
                )

            # Wait for all requests to complete
            responses = [f.result() for f in futures]

        # 4. Verify all requests were successful
        assert all(r.status_code == 200 for r in responses)

    def test_error_handling_flow(self, test_chart_data, test_user_data):
        """Test error handling in a complete flow"""
        # 1. Register and login
        self.make_request("POST", "/api/auth/register", json=test_user_data)
        login_response = self.make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["token"]

        # 2. Try to create chart with invalid data
        response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": "invalid_date",
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

        # 3. Create valid chart
        chart_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        chart_id = chart_response.json()["chart_id"]

        # 4. Try to calculate with invalid planet
        response = self.make_request(
            "POST",
            "/api/calculations/positions",
            json={
                "chart_id": chart_id,
                "planets": ["INVALID_PLANET"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

        # 5. Try to access non-existent chart
        response = self.make_request(
            "GET",
            "/api/charts/nonexistent",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_data_persistence(self, test_chart_data, test_user_data):
        """Test data persistence across requests"""
        # 1. Register and login
        self.make_request("POST", "/api/auth/register", json=test_user_data)
        login_response = self.make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["token"]

        # 2. Create chart
        chart_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        chart_id = chart_response.json()["chart_id"]

        # 3. Calculate positions
        positions_response = self.make_request(
            "POST",
            "/api/calculations/positions",
            json={
                "chart_id": chart_id,
                "planets": ["SUN", "MOON", "MARS"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        positions = positions_response.json()["positions"]

        # 4. Get chart and verify positions are persisted
        chart_response = self.make_request(
            "GET",
            f"/api/charts/{chart_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert chart_response.status_code == 200
        assert "planets" in chart_response.json()
        assert chart_response.json()["planets"] == positions

    # Helper method for making requests
    def make_request(self, method, endpoint, json=None, headers=None):
        """Helper method to make HTTP requests"""
        # This is a placeholder for the actual request implementation
        # In a real implementation, this would use a proper HTTP client
        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self._json = json_data

            def json(self):
                return self._json

        # Mock implementation for testing
        if method == "POST" and endpoint == "/api/auth/register":
            return MockResponse(201, {"user_id": 1, "token": "mock_token"})
        
        if method == "POST" and endpoint == "/api/auth/login":
            return MockResponse(200, {"token": "mock_token", "refresh_token": "mock_refresh_token"})
        
        if method == "POST" and endpoint == "/api/charts/natal":
            if json.get("date") == "invalid_date":
                return MockResponse(400, {"error": "Invalid date format"})
            return MockResponse(201, {
                "chart_id": "mock_chart_id",
                "planets": {},
                "houses": {}
            })
        
        if method == "GET" and endpoint == "/api/charts":
            return MockResponse(200, {"charts": [{"id": "mock_chart_id"}] * 3})
        
        if method == "GET" and endpoint.startswith("/api/charts/"):
            if endpoint.endswith("nonexistent"):
                return MockResponse(404, {"error": "Chart not found"})
            return MockResponse(200, {
                "chart_id": "mock_chart_id",
                "planets": {},
                "houses": {}
            })
        
        if method == "POST" and endpoint == "/api/calculations/positions":
            if "INVALID_PLANET" in json.get("planets", []):
                return MockResponse(400, {"error": "Invalid planet"})
            return MockResponse(200, {"positions": {}})
        
        if method == "POST" and endpoint == "/api/calculations/aspects":
            return MockResponse(200, {"aspects": {}})
        
        if method == "POST" and endpoint == "/api/calculations/houses":
            return MockResponse(200, {"houses": {}})
        
        if method == "DELETE" and endpoint.startswith("/api/charts/"):
            return MockResponse(204, {})
        
        return MockResponse(404, {"error": "Endpoint not found"}) 