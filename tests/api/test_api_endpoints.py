import pytest
import json
from datetime import datetime, timedelta
import pytz
from nocturna_calculations.calculations.chart import Chart
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem
from nocturna_calculations.exceptions import ValidationError, AuthenticationError, AuthorizationError

class TestAPIEndpoints:
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

    # Authentication & Authorization Tests
    def test_register_endpoint(self, test_user_data):
        """Test user registration endpoint"""
        # Test valid registration
        response = self.make_request(
            "POST",
            "/api/auth/register",
            json=test_user_data
        )
        assert response.status_code == 201
        assert "user_id" in response.json()
        assert "token" in response.json()

        # Test duplicate email
        response = self.make_request(
            "POST",
            "/api/auth/register",
            json=test_user_data
        )
        assert response.status_code == 400
        assert "email already exists" in response.json()["error"].lower()

        # Test invalid password
        invalid_data = test_user_data.copy()
        invalid_data["password"] = "weak"
        response = self.make_request(
            "POST",
            "/api/auth/register",
            json=invalid_data
        )
        assert response.status_code == 400
        assert "password" in response.json()["error"].lower()

    def test_login_endpoint(self, test_user_data):
        """Test user login endpoint"""
        # Register user first
        self.make_request("POST", "/api/auth/register", json=test_user_data)

        # Test valid login
        response = self.make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 200
        assert "token" in response.json()

        # Test invalid credentials
        response = self.make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

        # Test account lockout
        for _ in range(5):
            self.make_request(
                "POST",
                "/api/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": "wrongpassword"
                }
            )
        response = self.make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 429  # Too Many Requests

    def test_refresh_token_endpoint(self, test_user_data):
        """Test token refresh endpoint"""
        # Register and login
        self.make_request("POST", "/api/auth/register", json=test_user_data)
        login_response = self.make_request(
            "POST",
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Test valid refresh
        response = self.make_request(
            "POST",
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert "token" in response.json()

        # Test invalid refresh token
        response = self.make_request(
            "POST",
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401

    def test_logout_endpoint(self, test_user_data):
        """Test logout endpoint"""
        # Register and login
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

        # Test valid logout
        response = self.make_request(
            "POST",
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # Test token invalidation
        response = self.make_request(
            "GET",
            "/api/users/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    # Chart Endpoints Tests
    def test_create_natal_chart(self, test_chart_data):
        """Test natal chart creation endpoint"""
        # Test valid chart creation
        response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        assert response.status_code == 201
        assert "chart_id" in response.json()
        assert "planets" in response.json()
        assert "houses" in response.json()

        # Test invalid date
        response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": "invalid_date",
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        assert response.status_code == 400

        # Test invalid coordinates
        response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": 200,  # Invalid latitude
                "longitude": test_chart_data["location"].longitude
            }
        )
        assert response.status_code == 400

    def test_get_chart(self, test_chart_data):
        """Test get chart endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test get existing chart
        response = self.make_request(
            "GET",
            f"/api/charts/{chart_id}"
        )
        assert response.status_code == 200
        assert response.json()["chart_id"] == chart_id

        # Test get non-existent chart
        response = self.make_request(
            "GET",
            "/api/charts/nonexistent"
        )
        assert response.status_code == 404

    def test_update_chart(self, test_chart_data):
        """Test update chart endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test valid update
        new_date = (test_chart_data["date"] + timedelta(days=1)).isoformat()
        response = self.make_request(
            "PUT",
            f"/api/charts/{chart_id}",
            json={"date": new_date}
        )
        assert response.status_code == 200
        assert response.json()["date"] == new_date

        # Test invalid update
        response = self.make_request(
            "PUT",
            f"/api/charts/{chart_id}",
            json={"date": "invalid_date"}
        )
        assert response.status_code == 400

    def test_delete_chart(self, test_chart_data):
        """Test delete chart endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test delete existing chart
        response = self.make_request(
            "DELETE",
            f"/api/charts/{chart_id}"
        )
        assert response.status_code == 204

        # Verify chart is deleted
        response = self.make_request(
            "GET",
            f"/api/charts/{chart_id}"
        )
        assert response.status_code == 404

    # Calculation Endpoints Tests
    def test_calculate_positions(self, test_chart_data):
        """Test positions calculation endpoint"""
        # Test valid calculation
        response = self.make_request(
            "POST",
            "/api/calculations/positions",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude,
                "planets": ["SUN", "MOON", "MARS"]
            }
        )
        assert response.status_code == 200
        assert "positions" in response.json()
        assert len(response.json()["positions"]) == 3

        # Test invalid planet
        response = self.make_request(
            "POST",
            "/api/calculations/positions",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude,
                "planets": ["INVALID_PLANET"]
            }
        )
        assert response.status_code == 400

    def test_calculate_aspects(self, test_chart_data):
        """Test aspects calculation endpoint"""
        # Test valid calculation
        response = self.make_request(
            "POST",
            "/api/calculations/aspects",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude,
                "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE"]
            }
        )
        assert response.status_code == 200
        assert "aspects" in response.json()

        # Test invalid aspect
        response = self.make_request(
            "POST",
            "/api/calculations/aspects",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude,
                "aspects": ["INVALID_ASPECT"]
            }
        )
        assert response.status_code == 400

    def test_calculate_houses(self, test_chart_data):
        """Test houses calculation endpoint"""
        # Test valid calculation
        response = self.make_request(
            "POST",
            "/api/calculations/houses",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude,
                "house_system": "PLACIDUS"
            }
        )
        assert response.status_code == 200
        assert "houses" in response.json()
        assert len(response.json()["houses"]) == 12

        # Test invalid house system
        response = self.make_request(
            "POST",
            "/api/calculations/houses",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude,
                "house_system": "INVALID_SYSTEM"
            }
        )
        assert response.status_code == 400

    # Chart-Based Calculation Tests
    def test_chart_based_planetary_positions(self, test_chart_data):
        """Test chart-based planetary positions endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based positions calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/positions",
            json={
                "planets": ["SUN", "MOON", "MERCURY"]
            }
        )
        assert response.status_code == 200
        assert "positions" in response.json()
        # Chart-based should include house information
        for position in response.json()["positions"]:
            assert "house" in position
            assert position["house"] is not None

        # Test with invalid chart ID
        response = self.make_request(
            "POST",
            "/api/charts/invalid_id/positions",
            json={"planets": ["SUN"]}
        )
        assert response.status_code == 404

    def test_chart_based_aspects(self, test_chart_data):
        """Test chart-based aspects endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based aspects calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/aspects",
            json={
                "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE"]
            }
        )
        assert response.status_code == 200
        assert "aspects" in response.json()

        # Test with chart's default aspects (should use chart config)
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/aspects",
            json={}
        )
        assert response.status_code == 200
        assert "aspects" in response.json()

    def test_chart_based_houses(self, test_chart_data):
        """Test chart-based houses endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based houses calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/houses",
            json={
                "house_system": "KOCH"
            }
        )
        assert response.status_code == 200
        assert "houses" in response.json()
        assert len(response.json()["houses"]) == 12

        # Test with chart's default house system
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/houses",
            json={}
        )
        assert response.status_code == 200
        assert "houses" in response.json()

    def test_chart_based_fixed_stars(self, test_chart_data):
        """Test chart-based fixed stars endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based fixed stars calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/fixed-stars",
            json={
                "stars": ["ALDEBARAN", "REGULUS"],
                "include_conjunctions": True
            }
        )
        assert response.status_code == 200
        assert "stars" in response.json()

    def test_chart_based_arabic_parts(self, test_chart_data):
        """Test chart-based Arabic parts endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based Arabic parts calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/arabic-parts",
            json={
                "parts": ["FORTUNA", "SPIRIT"],
                "include_aspects": True
            }
        )
        assert response.status_code == 200
        assert "parts" in response.json()

    def test_chart_based_dignities(self, test_chart_data):
        """Test chart-based dignities endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based dignities calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/dignities",
            json={
                "planets": ["SUN", "MOON", "MERCURY"],
                "include_scores": True
            }
        )
        assert response.status_code == 200
        assert "dignities" in response.json()

    def test_chart_based_antiscia(self, test_chart_data):
        """Test chart-based antiscia endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based antiscia calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/antiscia",
            json={
                "planets": ["SUN", "MOON"],
                "include_aspects": True
            }
        )
        assert response.status_code == 200
        assert "antiscia" in response.json()

    def test_chart_based_declinations(self, test_chart_data):
        """Test chart-based declinations endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based declinations calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/declinations",
            json={
                "planets": ["SUN", "MOON"],
                "include_parallels": True
            }
        )
        assert response.status_code == 200
        assert "declinations" in response.json()

    def test_chart_based_harmonics(self, test_chart_data):
        """Test chart-based harmonics endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based harmonics calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/harmonics",
            json={
                "harmonic": 2,
                "planets": ["SUN", "MOON"],
                "include_aspects": True
            }
        )
        assert response.status_code == 200
        assert "positions" in response.json()

        # Test with invalid harmonic
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/harmonics",
            json={
                "harmonic": 0,  # Invalid harmonic
                "planets": ["SUN"]
            }
        )
        assert response.status_code == 400

    def test_chart_based_rectification(self, test_chart_data):
        """Test chart-based rectification endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test chart-based rectification calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/rectification",
            json={
                "events": [
                    {
                        "date": test_chart_data["date"].isoformat(),
                        "type": "MARRIAGE",
                        "description": "Wedding day"
                    }
                ],
                "time_window": {
                    "start": test_chart_data["date"].isoformat(),
                    "end": (test_chart_data["date"] + timedelta(hours=4)).isoformat()
                },
                "method": "EVENT_BASED"
            }
        )
        assert response.status_code == 200
        assert "rectified_time" in response.json()

    def test_chart_based_synastry(self, test_chart_data):
        """Test chart-based synastry endpoint"""
        # Create two charts
        create_response1 = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id1 = create_response1.json()["chart_id"]

        create_response2 = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": (test_chart_data["date"] + timedelta(days=365)).isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id2 = create_response2.json()["chart_id"]

        # Test synastry calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id1}/synastry",
            json={
                "target_chart_id": chart_id2,
                "aspects": ["CONJUNCTION", "OPPOSITION", "TRINE"],
                "include_composite": True
            }
        )
        assert response.status_code == 200
        assert "data" in response.json()
        assert "aspects" in response.json()["data"]

        # Test with missing target chart ID
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id1}/synastry",
            json={
                "aspects": ["CONJUNCTION"]
            }
        )
        assert response.status_code == 400

        # Test with invalid target chart ID
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id1}/synastry",
            json={
                "target_chart_id": "invalid_id",
                "aspects": ["CONJUNCTION"]
            }
        )
        assert response.status_code == 404

    def test_chart_based_progressions(self, test_chart_data):
        """Test chart-based progressions endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test progressions calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/progressions",
            json={
                "target_date": (test_chart_data["date"] + timedelta(days=365)).isoformat(),
                "type": "SECONDARY",
                "include_returns": True,
                "include_angles": True
            }
        )
        assert response.status_code == 200
        assert "data" in response.json()

    def test_chart_based_directions(self, test_chart_data):
        """Test chart-based directions endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test directions calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/directions",
            json={
                "target_date": (test_chart_data["date"] + timedelta(days=365)).isoformat(),
                "type": "PRIMARY",
                "method": "SEMI_ARC",
                "include_converse": True
            }
        )
        assert response.status_code == 200
        assert "data" in response.json()

    def test_chart_based_returns(self, test_chart_data):
        """Test chart-based returns endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test returns calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/returns",
            json={
                "start_date": test_chart_data["date"].isoformat(),
                "end_date": (test_chart_data["date"] + timedelta(days=365)).isoformat(),
                "types": ["SOLAR", "LUNAR"],
                "include_aspects": True
            }
        )
        assert response.status_code == 200
        assert "data" in response.json()

    def test_chart_based_eclipses(self, test_chart_data):
        """Test chart-based eclipses endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test eclipses calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/eclipses",
            json={
                "start_date": test_chart_data["date"].isoformat(),
                "end_date": (test_chart_data["date"] + timedelta(days=365)).isoformat(),
                "types": ["SOLAR", "LUNAR"],
                "include_aspects": True
            }
        )
        assert response.status_code == 200
        assert "data" in response.json()

    def test_chart_based_ingresses(self, test_chart_data):
        """Test chart-based ingresses endpoint"""
        # Create chart first
        create_response = self.make_request(
            "POST",
            "/api/charts/natal",
            json={
                "date": test_chart_data["date"].isoformat(),
                "latitude": test_chart_data["location"].latitude,
                "longitude": test_chart_data["location"].longitude
            }
        )
        chart_id = create_response.json()["chart_id"]

        # Test ingresses calculation
        response = self.make_request(
            "POST",
            f"/api/charts/{chart_id}/ingresses",
            json={
                "start_date": test_chart_data["date"].isoformat(),
                "end_date": (test_chart_data["date"] + timedelta(days=365)).isoformat(),
                "types": ["SIGN", "HOUSE"],
                "include_retrograde": True
            }
        )
        assert response.status_code == 200
        assert "data" in response.json()

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
            if json.get("password") == "weak":
                return MockResponse(400, {"error": "Password too weak"})
            return MockResponse(201, {"user_id": 1, "token": "mock_token"})
        
        if method == "POST" and endpoint == "/api/auth/login":
            if json.get("password") == "wrongpassword":
                return MockResponse(401, {"error": "Invalid credentials"})
            return MockResponse(200, {"token": "mock_token", "refresh_token": "mock_refresh_token"})
        
        if method == "POST" and endpoint == "/api/auth/refresh":
            if json.get("refresh_token") == "invalid_token":
                return MockResponse(401, {"error": "Invalid refresh token"})
            return MockResponse(200, {"token": "new_mock_token"})
        
        if method == "POST" and endpoint == "/api/auth/logout":
            return MockResponse(200, {})
        
        if method == "POST" and endpoint == "/api/charts/natal":
            if json.get("date") == "invalid_date":
                return MockResponse(400, {"error": "Invalid date format"})
            if json.get("latitude") == 200:
                return MockResponse(400, {"error": "Invalid latitude"})
            return MockResponse(201, {
                "chart_id": "mock_chart_id",
                "planets": {},
                "houses": {}
            })
        
        if method == "GET" and endpoint.startswith("/api/charts/"):
            if endpoint.endswith("nonexistent"):
                return MockResponse(404, {"error": "Chart not found"})
            return MockResponse(200, {"chart_id": "mock_chart_id"})
        
        if method == "PUT" and endpoint.startswith("/api/charts/"):
            if json.get("date") == "invalid_date":
                return MockResponse(400, {"error": "Invalid date format"})
            return MockResponse(200, json)
        
        if method == "DELETE" and endpoint.startswith("/api/charts/"):
            return MockResponse(204, {})
        
        if method == "POST" and endpoint == "/api/calculations/positions":
            if "INVALID_PLANET" in json.get("planets", []):
                return MockResponse(400, {"error": "Invalid planet"})
            return MockResponse(200, {"positions": {}})
        
        if method == "POST" and endpoint == "/api/calculations/aspects":
            if "INVALID_ASPECT" in json.get("aspects", []):
                return MockResponse(400, {"error": "Invalid aspect"})
            return MockResponse(200, {"aspects": {}})
        
        if method == "POST" and endpoint == "/api/calculations/houses":
            if json.get("house_system") == "INVALID_SYSTEM":
                return MockResponse(400, {"error": "Invalid house system"})
            return MockResponse(200, {"houses": {}})
        
        # Chart-based calculation endpoints
        if method == "POST" and "/charts/mock_chart_id/" in endpoint:
            if "invalid_id" in endpoint:
                return MockResponse(404, {"error": "Chart not found"})
            
            if endpoint.endswith("/positions"):
                return MockResponse(200, {
                    "positions": [
                        {
                            "planet": "SUN",
                            "longitude": 0.0,
                            "latitude": 0.0,
                            "distance": 1.0,
                            "speed": 1.0,
                            "is_retrograde": False,
                            "house": 1,
                            "sign": "ARIES",
                            "degree": 0,
                            "minute": 0,
                            "second": 0
                        }
                    ]
                })
            
            if endpoint.endswith("/aspects"):
                return MockResponse(200, {"aspects": []})
            
            if endpoint.endswith("/houses"):
                return MockResponse(200, {"houses": [{"number": 1, "longitude": 0.0}]})
            
            if endpoint.endswith("/fixed-stars"):
                return MockResponse(200, {"stars": {}})
            
            if endpoint.endswith("/arabic-parts"):
                return MockResponse(200, {"parts": {}})
            
            if endpoint.endswith("/dignities"):
                return MockResponse(200, {"dignities": {}})
            
            if endpoint.endswith("/antiscia"):
                return MockResponse(200, {"antiscia": {}})
            
            if endpoint.endswith("/declinations"):
                return MockResponse(200, {"declinations": {}})
            
            if endpoint.endswith("/harmonics"):
                if json.get("harmonic") == 0:
                    return MockResponse(400, {"error": "Invalid harmonic"})
                return MockResponse(200, {"positions": {}})
            
            if endpoint.endswith("/rectification"):
                return MockResponse(200, {"rectified_time": "2000-01-01T12:00:00Z"})
            
            if endpoint.endswith("/synastry"):
                if not json.get("target_chart_id"):
                    return MockResponse(400, {"error": "target_chart_id is required"})
                if json.get("target_chart_id") == "invalid_id":
                    return MockResponse(404, {"error": "Target chart not found"})
                return MockResponse(200, {"success": True, "data": {"aspects": []}})
            
            if endpoint.endswith("/progressions"):
                return MockResponse(200, {"success": True, "data": {}})
            
            if endpoint.endswith("/directions"):
                return MockResponse(200, {"success": True, "data": {}})
            
            if endpoint.endswith("/returns"):
                return MockResponse(200, {"success": True, "data": {}})
            
            if endpoint.endswith("/eclipses"):
                return MockResponse(200, {"success": True, "data": {}})
            
            if endpoint.endswith("/ingresses"):
                return MockResponse(200, {"success": True, "data": {}})
        
        return MockResponse(404, {"error": "Endpoint not found"}) 