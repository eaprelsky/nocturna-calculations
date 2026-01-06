"""
Integration tests for chart calculations
"""
import pytest
from datetime import datetime, time
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import Config
from nocturna_calculations.adapters.swisseph import SwissEphAdapter

# --- Integration Test Setup ---

@pytest.fixture
def swisseph_adapter():
    """Create a SwissEph adapter instance"""
    return SwissEphAdapter()

@pytest.fixture
def basic_chart():
    """Create a basic chart for testing"""
    return Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        timezone="Europe/Moscow"
    )

# --- End-to-End Calculation Tests ---

def test_full_chart_calculation(swisseph_adapter, basic_chart):
    """Test complete chart calculation with all components"""
    # Calculate all components
    positions = basic_chart.calculate_planetary_positions()
    aspects = basic_chart.calculate_aspects()
    houses = basic_chart.calculate_houses()
    fixed_stars = basic_chart.calculate_fixed_stars()
    arabic_parts = basic_chart.calculate_arabic_parts()
    dignities = basic_chart.calculate_dignities()
    
    # Verify all components are calculated
    assert positions is not None
    assert aspects is not None
    assert houses is not None
    assert fixed_stars is not None
    assert arabic_parts is not None
    assert dignities is not None
    
    # Verify data structure
    assert isinstance(positions, dict)
    assert isinstance(aspects, list)
    assert isinstance(houses, dict)
    assert isinstance(fixed_stars, dict)
    assert isinstance(arabic_parts, dict)
    assert isinstance(dignities, dict)

def test_chart_with_custom_config(swisseph_adapter):
    """Test chart calculation with custom configuration"""
    config = Config(
        house_system="Koch",
        orbs={"conjunction": 10.0, "opposition": 10.0},
        fixed_stars=["Aldebaran", "Regulus"],
        arabic_parts=["Fortune", "Spirit"]
    )
    
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    # Calculate components
    houses = chart.calculate_houses()
    aspects = chart.calculate_aspects()
    fixed_stars = chart.calculate_fixed_stars()
    arabic_parts = chart.calculate_arabic_parts()
    
    # Verify custom configuration is applied
    assert "Koch" in str(houses)
    assert any(aspect.get("orb", 0) <= 10.0 for aspect in aspects)
    assert "Aldebaran" in fixed_stars
    assert "Fortune" in arabic_parts

def test_chart_at_poles(swisseph_adapter):
    """Test chart calculation at polar regions"""
    # North Pole
    north_chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=90.0,
        longitude=0.0
    )
    
    # South Pole
    south_chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=-90.0,
        longitude=0.0
    )
    
    # Calculate houses for both charts
    north_houses = north_chart.calculate_houses()
    south_houses = south_chart.calculate_houses()
    
    assert north_houses is not None
    assert south_houses is not None

def test_chart_at_date_line(swisseph_adapter):
    """Test chart calculation at the international date line"""
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=0.0,
        longitude=180.0
    )
    
    positions = chart.calculate_planetary_positions()
    houses = chart.calculate_houses()
    
    assert positions is not None
    assert houses is not None

def test_chart_at_dst_transition(swisseph_adapter):
    """Test chart calculation during DST transition"""
    # Spring forward
    spring_chart = Chart(
        date="2024-03-31",
        time="02:00:00",
        latitude=55.7558,
        longitude=37.6173,
        timezone="Europe/Moscow"
    )
    
    # Fall back
    fall_chart = Chart(
        date="2024-10-27",
        time="02:00:00",
        latitude=55.7558,
        longitude=37.6173,
        timezone="Europe/Moscow"
    )
    
    spring_positions = spring_chart.calculate_planetary_positions()
    fall_positions = fall_chart.calculate_planetary_positions()
    
    assert spring_positions is not None
    assert fall_positions is not None

def test_chart_at_leap_year(swisseph_adapter):
    """Test chart calculation during leap year"""
    chart = Chart(
        date="2024-02-29",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    positions = chart.calculate_planetary_positions()
    houses = chart.calculate_houses()
    
    assert positions is not None
    assert houses is not None

def test_chart_with_historical_date(swisseph_adapter):
    """Test chart calculation with historical date"""
    chart = Chart(
        date="1900-01-01",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    positions = chart.calculate_planetary_positions()
    houses = chart.calculate_houses()
    
    assert positions is not None
    assert houses is not None

def test_chart_with_future_date(swisseph_adapter):
    """Test chart calculation with future date"""
    chart = Chart(
        date="2100-01-01",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    positions = chart.calculate_planetary_positions()
    houses = chart.calculate_houses()
    
    assert positions is not None
    assert houses is not None

def test_chart_with_multiple_timezones(swisseph_adapter):
    """Test chart calculation with different timezones"""
    timezones = [
        "UTC",
        "Europe/Moscow",
        "America/New_York",
        "Asia/Tokyo",
        "Australia/Sydney"
    ]
    
    for tz in timezones:
        chart = Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173,
            timezone=tz
        )
        
        positions = chart.calculate_planetary_positions()
        houses = chart.calculate_houses()
        
        assert positions is not None
        assert houses is not None

def test_chart_with_extreme_coordinates(swisseph_adapter):
    """Test chart calculation with extreme coordinates"""
    coordinates = [
        (0.0, 0.0),  # Null Island
        (0.0, 180.0),  # Date line
        (90.0, 0.0),  # North Pole
        (-90.0, 0.0),  # South Pole
        (0.0, -180.0),  # Date line
    ]
    
    for lat, lon in coordinates:
        chart = Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=lat,
            longitude=lon
        )
        
        positions = chart.calculate_planetary_positions()
        houses = chart.calculate_houses()
        
        assert positions is not None
        assert houses is not None