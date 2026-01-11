"""
Tests for Stateless API endpoints.

These tests verify that all stateless calculations work correctly
without requiring database access.
"""
import pytest
from fastapi.testclient import TestClient
from nocturna_calculations.api.app import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Create test user and return auth token."""
    import uuid
    # Use unique email for each test run to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "email": f"stateless_test_{unique_id}@example.com",
        "username": f"stateless_testuser_{unique_id}",
        "password": "Test123!@#",
        "first_name": "Stateless",
        "last_name": "Test"
    }
    
    # Register user
    response = client.post("/api/auth/register", json=user_data)
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Registration failed with status {response.status_code}: {response.json()}")
    
    # Login to get token (register doesn't return token, only user data)
    login_data = {
        "username": user_data["email"],  # Login uses email as username
        "password": user_data["password"]
    }
    response = client.post(
        "/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed with status {response.status_code}: {response.json()}")


@pytest.fixture
def auth_headers(auth_token):
    """Get authentication headers with service token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_chart_data():
    """Sample chart data for testing."""
    return {
        "date": "1990-01-15",
        "time": "14:30:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
        "house_system": "PLACIDUS"
    }


@pytest.fixture
def sample_chart_data_2():
    """Second sample chart data for two-chart operations."""
    return {
        "date": "1992-06-20",
        "time": "09:15:00",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "timezone": "America/Los_Angeles",
        "house_system": "PLACIDUS"
    }


class TestStatelessNatalChart:
    """Tests for stateless natal chart calculation."""
    
    def test_natal_chart_basic(self, client, auth_headers, sample_chart_data):
        """Test basic natal chart calculation."""
        response = client.post(
            "/api/stateless/natal-chart",
            json=sample_chart_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "planets" in data["data"]
        assert "houses" in data["data"]
        assert "aspects" in data["data"]
    
    def test_natal_chart_invalid_date(self, client, auth_headers, sample_chart_data):
        """Test natal chart with invalid date."""
        invalid_data = sample_chart_data.copy()
        invalid_data["date"] = "invalid-date"
        
        response = client.post(
            "/api/stateless/natal-chart",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422, 500]
    
    def test_natal_chart_invalid_coordinates(self, client, auth_headers, sample_chart_data):
        """Test natal chart with invalid coordinates."""
        invalid_data = sample_chart_data.copy()
        invalid_data["latitude"] = 100.0  # Invalid latitude
        
        response = client.post(
            "/api/stateless/natal-chart",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422, 500]


class TestStatelessSynastry:
    """Tests for stateless synastry calculation."""
    
    def test_synastry_basic(self, client, auth_headers, sample_chart_data, sample_chart_data_2):
        """Test basic synastry calculation."""
        request_data = {
            "chart1": sample_chart_data,
            "chart2": sample_chart_data_2,
            "options": {
                "orb_multiplier": 1.0
            }
        }
        
        response = client.post(
            "/api/stateless/synastry",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_synastry_with_custom_orb(self, client, auth_headers, sample_chart_data, sample_chart_data_2):
        """Test synastry with custom orb multiplier."""
        request_data = {
            "chart1": sample_chart_data,
            "chart2": sample_chart_data_2,
            "options": {
                "orb_multiplier": 0.5
            }
        }
        
        response = client.post(
            "/api/stateless/synastry",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatelessTransits:
    """Tests for stateless transit calculation."""
    
    def test_transits_basic(self, client, auth_headers, sample_chart_data):
        """Test basic transit calculation."""
        request_data = {
            "natal_chart": sample_chart_data,
            "transit_date": "2026-01-11",
            "transit_time": "12:00:00",
            "options": {
                "orb_multiplier": 0.8
            }
        }
        
        response = client.post(
            "/api/stateless/transits",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "transit_positions" in data["data"]
    
    def test_transits_current_date(self, client, auth_headers, sample_chart_data):
        """Test transit calculation for current date."""
        from datetime import datetime
        now = datetime.now()
        
        request_data = {
            "natal_chart": sample_chart_data,
            "transit_date": now.strftime("%Y-%m-%d"),
            "transit_time": now.strftime("%H:%M:%S"),
            "options": {}
        }
        
        response = client.post(
            "/api/stateless/transits",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatelessProgressions:
    """Tests for stateless progression calculation."""
    
    def test_progressions_secondary(self, client, auth_headers, sample_chart_data):
        """Test secondary progressions calculation."""
        request_data = {
            "natal_chart": sample_chart_data,
            "progression_date": "2026-01-11",
            "progression_type": "secondary",
            "options": {}
        }
        
        response = client.post(
            "/api/stateless/progressions",
            json=request_data,
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatelessComposite:
    """Tests for stateless composite chart calculation."""
    
    def test_composite_midpoint(self, client, auth_headers, sample_chart_data, sample_chart_data_2):
        """Test midpoint composite chart."""
        request_data = {
            "chart1": sample_chart_data,
            "chart2": sample_chart_data_2,
            "composite_type": "midpoint",
            "options": {}
        }
        
        response = client.post(
            "/api/stateless/composite",
            json=request_data,
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_composite_davison(self, client, auth_headers, sample_chart_data, sample_chart_data_2):
        """Test Davison composite chart."""
        request_data = {
            "chart1": sample_chart_data,
            "chart2": sample_chart_data_2,
            "composite_type": "davison",
            "options": {}
        }
        
        response = client.post(
            "/api/stateless/composite",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatelessReturns:
    """Tests for stateless returns calculation."""
    
    def test_solar_return(self, client, auth_headers, sample_chart_data):
        """Test solar return calculation."""
        request_data = {
            "natal_chart": sample_chart_data,
            "return_date": "2026-01-15",
            "return_type": "solar",
            "planet": "SUN",
            "location": None
        }
        
        response = client.post(
            "/api/stateless/returns",
            json=request_data,
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_lunar_return(self, client, auth_headers, sample_chart_data):
        """Test lunar return calculation."""
        request_data = {
            "natal_chart": sample_chart_data,
            "return_date": "2026-01-15",
            "return_type": "lunar",
            "planet": "MOON",
            "location": None
        }
        
        response = client.post(
            "/api/stateless/returns",
            json=request_data,
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatelessAdvancedTechniques:
    """Tests for advanced astrological techniques."""
    
    def test_fixed_stars(self, client, auth_headers, sample_chart_data):
        """Test fixed stars calculation."""
        request_data = {
            "chart_data": sample_chart_data,
            "orb": 1.0,
            "magnitude_limit": 2.0
        }
        
        response = client.post(
            "/api/stateless/fixed-stars",
            json=request_data,
            headers=auth_headers
        )

        if response.status_code != 200:
            print(f"Error response: {response.json()}")

        assert response.status_code == 200
        data = response.json()
        # Fixed stars may not work without Swiss Ephemeris star data files
        # Accept either success=True or success=False with error message
        if data["success"] is False:
            assert "error" in data
            assert "Swiss Ephemeris star data" in data["error"]
        else:
            assert data["success"] is True
    
    def test_arabic_parts(self, client, auth_headers, sample_chart_data):
        """Test Arabic parts calculation."""
        request_data = {
            "chart_data": sample_chart_data,
            "parts": ["FORTUNE", "SPIRIT"]
        }
        
        response = client.post(
            "/api/stateless/arabic-parts",
            json=request_data,
            headers=auth_headers
        )

        if response.status_code != 200:
            print(f"Error response: {response.json()}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_dignities(self, client, auth_headers, sample_chart_data):
        """Test dignities calculation."""
        request_data = {
            "chart_data": sample_chart_data,
            "dignity_system": "traditional"
        }
        
        response = client.post(
            "/api/stateless/dignities",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_antiscia(self, client, auth_headers, sample_chart_data):
        """Test antiscia calculation."""
        request_data = {
            "chart_data": sample_chart_data,
            "include_contra": True
        }
        
        response = client.post(
            "/api/stateless/antiscia",
            json=request_data,
            headers=auth_headers
        )

        if response.status_code != 200:
            print(f"Error response: {response.json()}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_declinations(self, client, auth_headers, sample_chart_data):
        """Test declinations calculation."""
        request_data = {
            "chart_data": sample_chart_data,
            "parallel_orb": 1.0
        }
        
        response = client.post(
            "/api/stateless/declinations",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_harmonics(self, client, auth_headers, sample_chart_data):
        """Test harmonic charts calculation."""
        request_data = {
            "chart_data": sample_chart_data,
            "harmonics": [2, 3, 4, 5]
        }
        
        response = client.post(
            "/api/stateless/harmonics",
            json=request_data,
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatelessPredictiveTechniques:
    """Tests for predictive astrological techniques."""
    
    def test_directions(self, client, auth_headers, sample_chart_data):
        """Test primary directions calculation."""
        request_data = {
            "natal_chart": sample_chart_data,
            "target_date": "2026-01-11",
            "direction_type": "primary",
            "key_rate": 1.0
        }
        
        response = client.post(
            "/api/stateless/directions",
            json=request_data,
            headers=auth_headers
        )

        if response.status_code != 200:
            print(f"Error response: {response.json()}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_eclipses(self, client, auth_headers, sample_chart_data):
        """Test eclipse analysis."""
        request_data = {
            "natal_chart": sample_chart_data,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "eclipse_type": "all"
        }
        
        response = client.post(
            "/api/stateless/eclipses",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_ingresses(self, client, auth_headers, sample_chart_data):
        """Test planetary ingresses."""
        request_data = {
            "natal_chart": sample_chart_data,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "planets": ["SUN", "MERCURY", "VENUS"]
        }
        
        response = client.post(
            "/api/stateless/ingresses",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatelessErrorHandling:
    """Tests for error handling in stateless API."""
    
    def test_missing_required_fields(self, client, auth_headers):
        """Test request with missing required fields."""
        incomplete_data = {
            "date": "1990-01-15"
            # Missing time, latitude, longitude
        }
        
        response = client.post(
            "/api/stateless/natal-chart",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_invalid_authentication(self, client, sample_chart_data):
        """Test request without authentication."""
        response = client.post(
            "/api/stateless/natal-chart",
            json=sample_chart_data
        )
        
        assert response.status_code == 401
    
    def test_malformed_json(self, client, auth_headers):
        """Test request with malformed JSON."""
        response = client.post(
            "/api/stateless/natal-chart",
            data="invalid json",
            headers=auth_headers
        )
        
        assert response.status_code == 422


class TestStatelessPerformance:
    """Performance tests for stateless API."""
    
    def test_concurrent_requests(self, client, auth_headers, sample_chart_data):
        """Test multiple concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return client.post(
                "/api/stateless/natal-chart",
                json=sample_chart_data,
                headers=auth_headers
            )
        
        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        assert all(r.json()["success"] is True for r in responses)


class TestStatelessSpecialPoints:
    """Tests for special astrological points endpoint."""
    
    def test_special_points_all(self, client, auth_token, sample_chart_data):
        """Test calculation of all special points (nodes, lilith, selena)."""
        auth_headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/api/stateless/special-points",
            json={
                "chart_data": sample_chart_data,
                "include_nodes": True,
                "include_lilith": True,
                "include_selena": True,
                "use_true_node": False
            },
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Check North Node
        assert "north_node" in data["data"]
        assert "longitude" in data["data"]["north_node"]
        assert "latitude" in data["data"]["north_node"]
        assert "speed" in data["data"]["north_node"]
        assert data["data"]["north_node"]["type"] == "mean"
        
        # Check South Node
        assert "south_node" in data["data"]
        assert "longitude" in data["data"]["south_node"]
        # South node should be opposite to north node
        north_long = data["data"]["north_node"]["longitude"]
        south_long = data["data"]["south_node"]["longitude"]
        assert abs((north_long + 180) % 360 - south_long) < 0.01
        
        # Check Lilith (Black Moon)
        assert "lilith_mean" in data["data"]
        assert "longitude" in data["data"]["lilith_mean"]
        assert data["data"]["lilith_mean"]["type"] == "mean"
        
        assert "lilith_true" in data["data"]
        assert "longitude" in data["data"]["lilith_true"]
        assert data["data"]["lilith_true"]["type"] == "osculating"
        
        # Check Selena (White Moon)
        assert "selena" in data["data"]
        assert "longitude" in data["data"]["selena"]
        assert data["data"]["selena"]["type"] == "mean_opposite"
    
    def test_special_points_true_node(self, client, auth_token, sample_chart_data):
        """Test calculation with true node instead of mean node."""
        auth_headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/api/stateless/special-points",
            json={
                "chart_data": sample_chart_data,
                "include_nodes": True,
                "include_lilith": False,
                "include_selena": False,
                "use_true_node": True
            },
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Error response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["north_node"]["type"] == "true"
        assert data["data"]["south_node"]["type"] == "true"
    
    def test_special_points_selective(self, client, auth_token, sample_chart_data):
        """Test calculation with selective points."""
        auth_headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Only nodes
        response = client.post(
            "/api/stateless/special-points",
            json={
                "chart_data": sample_chart_data,
                "include_nodes": True,
                "include_lilith": False,
                "include_selena": False
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "north_node" in data["data"]
        assert "south_node" in data["data"]
        assert "lilith_mean" not in data["data"]
        assert "lilith_true" not in data["data"]
        assert "selena" not in data["data"]
