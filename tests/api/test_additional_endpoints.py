import pytest
import asyncio
from datetime import datetime, timedelta
import pytz
from nocturna_calculations.calculations.chart import Chart
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem
from nocturna_calculations.exceptions import ValidationError, CalculationError

class TestAdditionalEndpoints:
    @pytest.fixture
    def test_chart_data(self):
        return {
            "date": datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
            "location": Position(0.0, 51.5, 0.0, CoordinateSystem.GEOGRAPHIC)  # London coordinates
        }

    @pytest.fixture
    def test_user_data(self):
        return {
            "email": f"test_{int(time.time())}@example.com",
            "username": f"testuser_{int(time.time())}",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User"
        }

    def test_chart_comparison_endpoint(self, test_chart_data):
        """Test chart comparison endpoint"""
        chart1 = Chart(**test_chart_data)
        chart2 = Chart(
            date=test_chart_data["date"] + timedelta(days=1),
            location=test_chart_data["location"]
        )

        # Test basic comparison
        response = chart1.compare_with(chart2)
        assert "aspects" in response
        assert "planetary_positions" in response
        assert "house_positions" in response

        # Test comparison with specific focus
        response = chart1.compare_with(chart2, focus=["aspects", "houses"])
        assert "aspects" in response
        assert "houses" in response
        assert "planetary_positions" not in response

    def test_chart_synastry_endpoint(self, test_chart_data):
        """Test chart synastry endpoint"""
        chart1 = Chart(**test_chart_data)
        chart2 = Chart(
            date=test_chart_data["date"] + timedelta(days=1),
            location=test_chart_data["location"]
        )

        # Test basic synastry
        response = chart1.calculate_synastry(chart2)
        assert "aspects" in response
        assert "composite_points" in response
        assert "relationship_dynamics" in response

        # Test synastry with specific parameters
        response = chart1.calculate_synastry(
            chart2,
            include_minor_aspects=True,
            orb_multiplier=1.2
        )
        assert "minor_aspects" in response
        assert "orb_settings" in response

    def test_chart_composite_endpoint(self, test_chart_data):
        """Test chart composite endpoint"""
        chart1 = Chart(**test_chart_data)
        chart2 = Chart(
            date=test_chart_data["date"] + timedelta(days=1),
            location=test_chart_data["location"]
        )

        # Test basic composite
        response = chart1.calculate_composite(chart2)
        assert "composite_chart" in response
        assert "midpoints" in response
        assert "relationship_indicators" in response

        # Test composite with specific house system
        response = chart1.calculate_composite(
            chart2,
            house_system="KOCH",
            include_arabic_parts=True
        )
        assert "house_system" in response
        assert "arabic_parts" in response

    def test_chart_progression_endpoint(self, test_chart_data):
        """Test chart progression endpoint"""
        chart = Chart(**test_chart_data)

        # Test basic progression
        response = chart.calculate_progression(
            progression_date=test_chart_data["date"] + timedelta(days=365)
        )
        assert "progressed_chart" in response
        assert "progressed_aspects" in response
        assert "progressed_houses" in response

        # Test progression with specific method
        response = chart.calculate_progression(
            progression_date=test_chart_data["date"] + timedelta(days=365),
            method="SECONDARY",
            include_returns=True
        )
        assert "progressed_returns" in response
        assert "progressed_angles" in response

    def test_chart_directions_endpoint(self, test_chart_data):
        """Test chart directions endpoint"""
        chart = Chart(**test_chart_data)

        # Test basic directions
        response = chart.calculate_directions(
            direction_date=test_chart_data["date"] + timedelta(days=365)
        )
        assert "directed_points" in response
        assert "directed_aspects" in response
        assert "directed_houses" in response

        # Test directions with specific parameters
        response = chart.calculate_directions(
            direction_date=test_chart_data["date"] + timedelta(days=365),
            method="PRIMARY",
            include_converse=True
        )
        assert "converse_directions" in response
        assert "direction_angles" in response

    def test_chart_returns_endpoint(self, test_chart_data):
        """Test chart returns endpoint"""
        chart = Chart(**test_chart_data)

        # Test basic returns
        response = chart.calculate_returns(
            start_date=test_chart_data["date"],
            end_date=test_chart_data["date"] + timedelta(days=365)
        )
        assert "solar_returns" in response
        assert "lunar_returns" in response
        assert "return_aspects" in response

        # Test returns with specific parameters
        response = chart.calculate_returns(
            start_date=test_chart_data["date"],
            end_date=test_chart_data["date"] + timedelta(days=365),
            include_minor_returns=True,
            location=test_chart_data["location"]
        )
        assert "minor_returns" in response
        assert "return_locations" in response

    def test_chart_eclipses_endpoint(self, test_chart_data):
        """Test chart eclipses endpoint"""
        chart = Chart(**test_chart_data)

        # Test basic eclipses
        response = chart.calculate_eclipses(
            start_date=test_chart_data["date"],
            end_date=test_chart_data["date"] + timedelta(days=365)
        )
        assert "solar_eclipses" in response
        assert "lunar_eclipses" in response
        assert "eclipse_aspects" in response

        # Test eclipses with specific parameters
        response = chart.calculate_eclipses(
            start_date=test_chart_data["date"],
            end_date=test_chart_data["date"] + timedelta(days=365),
            include_partial=True,
            include_penumbral=True
        )
        assert "partial_eclipses" in response
        assert "penumbral_eclipses" in response

    def test_chart_ingresses_endpoint(self, test_chart_data):
        """Test chart ingresses endpoint"""
        chart = Chart(**test_chart_data)

        # Test basic ingresses
        response = chart.calculate_ingresses(
            start_date=test_chart_data["date"],
            end_date=test_chart_data["date"] + timedelta(days=365)
        )
        assert "sign_ingresses" in response
        assert "house_ingresses" in response
        assert "ingress_aspects" in response

        # Test ingresses with specific parameters
        response = chart.calculate_ingresses(
            start_date=test_chart_data["date"],
            end_date=test_chart_data["date"] + timedelta(days=365),
            include_retrograde=True,
            include_stationary=True
        )
        assert "retrograde_ingresses" in response
        assert "stationary_points" in response

    def test_chart_arabic_parts_endpoint(self, test_chart_data):
        """Test chart Arabic parts endpoint"""
        chart = Chart(**test_chart_data)

        # Test basic Arabic parts
        response = chart.calculate_arabic_parts()
        assert "traditional_parts" in response
        assert "modern_parts" in response
        assert "part_aspects" in response

        # Test Arabic parts with specific parameters
        response = chart.calculate_arabic_parts(
            include_custom_parts=True,
            include_part_relationships=True
        )
        assert "custom_parts" in response
        assert "part_relationships" in response

    def test_chart_fixed_stars_endpoint(self, test_chart_data):
        """Test chart fixed stars endpoint"""
        chart = Chart(**test_chart_data)

        # Test basic fixed stars
        response = chart.calculate_fixed_stars()
        assert "conjunctions" in response
        assert "star_positions" in response
        assert "star_aspects" in response

        # Test fixed stars with specific parameters
        response = chart.calculate_fixed_stars(
            include_parans=True,
            include_star_classes=True
        )
        assert "parans" in response
        assert "star_classes" in response 