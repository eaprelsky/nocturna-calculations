"""
Integration tests for the Nocturna Calculations API
"""
import pytest
from datetime import datetime
import pytz
from nocturna_calculations.calculations.chart import Chart
from nocturna_calculations.core.constants import HouseSystem

class TestIntegration:
    @pytest.fixture
    def test_client(self):
        """Create a test client"""
        from nocturna_calculations.api.app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def test_chart(self):
        """Create a test chart"""
        # Create datetime object with timezone
        tz = pytz.timezone("Europe/Moscow")
        date_time = datetime(2024, 3, 20, 12, 0, 0, tzinfo=tz)
        
        return Chart(
            latitude=55.7558,
            longitude=37.6173,
            date_time=date_time,
            house_system=HouseSystem.PLACIDUS
        )
    
    def test_chart_creation(self, test_client, test_chart):
        """Test chart creation endpoint"""
        response = test_client.post(
            "/api/charts/natal",
            json={
                "date": test_chart.date_time.strftime("%Y-%m-%d"),
                "time": test_chart.date_time.strftime("%H:%M:%S"),
                "latitude": test_chart.latitude,
                "longitude": test_chart.longitude,
                "timezone": test_chart.date_time.tzinfo.zone
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert "chart_id" in data
        assert "planets" in data
        assert "houses" in data
    
    def test_invalid_chart_creation(self, test_client):
        """Test chart creation with invalid data"""
        response = test_client.post(
            "/api/charts/natal",
            json={
                "date": "invalid_date",
                "time": "12:00:00",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_chart_retrieval(self, test_client, test_chart):
        """Test chart retrieval endpoint"""
        # First create a chart
        create_response = test_client.post(
            "/api/charts/natal",
            json={
                "date": test_chart.date_time.strftime("%Y-%m-%d"),
                "time": test_chart.date_time.strftime("%H:%M:%S"),
                "latitude": test_chart.latitude,
                "longitude": test_chart.longitude,
                "timezone": test_chart.date_time.tzinfo.zone
            }
        )
        
        chart_id = create_response.get_json()["chart_id"]
        
        # Then retrieve it
        response = test_client.get(f"/api/charts/{chart_id}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["chart_id"] == chart_id
        assert "planets" in data
        assert "houses" in data
    
    def test_nonexistent_chart(self, test_client):
        """Test retrieval of nonexistent chart"""
        response = test_client.get("/api/charts/nonexistent")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
    
    def test_chart_list(self, test_client, test_chart):
        """Test chart listing endpoint"""
        # Create multiple charts
        for _ in range(3):
            test_client.post(
                "/api/charts/natal",
                json={
                    "date": test_chart.date_time.strftime("%Y-%m-%d"),
                    "time": test_chart.date_time.strftime("%H:%M:%S"),
                    "latitude": test_chart.latitude,
                    "longitude": test_chart.longitude,
                    "timezone": test_chart.date_time.tzinfo.zone
                }
            )
        
        # Get the list
        response = test_client.get("/api/charts")
        
        assert response.status_code == 200
        data = response.get_json()
        assert "charts" in data
        assert len(data["charts"]) >= 3
    
    def test_chart_calculations(self, test_client, test_chart):
        """Test chart calculation endpoints"""
        # Create a chart
        create_response = test_client.post(
            "/api/charts/natal",
            json={
                "date": test_chart.date_time.strftime("%Y-%m-%d"),
                "time": test_chart.date_time.strftime("%H:%M:%S"),
                "latitude": test_chart.latitude,
                "longitude": test_chart.longitude,
                "timezone": test_chart.date_time.tzinfo.zone
            }
        )
        
        chart_id = create_response.get_json()["chart_id"]
        
        # Test different calculation endpoints
        endpoints = [
            "/planets",
            "/aspects",
            "/houses",
            "/fixed-stars",
            "/asteroids",
            "/lunar-nodes"
        ]
        
        for endpoint in endpoints:
            response = test_client.get(f"/api/charts/{chart_id}{endpoint}")
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, dict) or isinstance(data, list)
    
    def test_chart_comparison(self, test_client, test_chart):
        """Test chart comparison endpoint"""
        # Create two charts
        chart1_response = test_client.post(
            "/api/charts/natal",
            json={
                "date": test_chart.date_time.strftime("%Y-%m-%d"),
                "time": test_chart.date_time.strftime("%H:%M:%S"),
                "latitude": test_chart.latitude,
                "longitude": test_chart.longitude,
                "timezone": test_chart.date_time.tzinfo.zone
            }
        )
        
        # Create second chart with different date
        tz = pytz.timezone("Europe/Moscow")
        date_time2 = datetime(2024, 3, 21, 12, 0, 0, tzinfo=tz)
        
        chart2_response = test_client.post(
            "/api/charts/natal",
            json={
                "date": date_time2.strftime("%Y-%m-%d"),
                "time": date_time2.strftime("%H:%M:%S"),
                "latitude": test_chart.latitude,
                "longitude": test_chart.longitude,
                "timezone": test_chart.date_time.tzinfo.zone
            }
        )
        
        chart1_id = chart1_response.get_json()["chart_id"]
        chart2_id = chart2_response.get_json()["chart_id"]
        
        # Compare the charts
        response = test_client.post(
            "/api/charts/compare",
            json={
                "chart1_id": chart1_id,
                "chart2_id": chart2_id,
                "comparison_type": "synastry"
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "aspects" in data
        assert "points" in data 