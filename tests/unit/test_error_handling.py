"""
Error handling tests for chart calculations
"""
import pytest
from datetime import datetime, time
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import AstroConfig
from nocturna_calculations.adapters.swisseph_adapter import SwissEphAdapter

# --- Invalid Input Tests ---

def test_invalid_date_format():
    """Test chart initialization with invalid date format"""
    with pytest.raises(ValueError):
        Chart(
            date="invalid-date",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )

def test_invalid_time_format():
    """Test chart initialization with invalid time format"""
    with pytest.raises(ValueError):
        Chart(
            date="2024-03-20",
            time="invalid-time",
            latitude=55.7558,
            longitude=37.6173
        )

def test_invalid_latitude_range():
    """Test chart initialization with invalid latitude range"""
    with pytest.raises(ValueError):
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=100.0,  # Invalid latitude
            longitude=37.6173
        )

def test_invalid_longitude_range():
    """Test chart initialization with invalid longitude range"""
    with pytest.raises(ValueError):
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=55.7558,
            longitude=200.0  # Invalid longitude
        )

def test_invalid_timezone():
    """Test chart initialization with invalid timezone"""
    with pytest.raises(ValueError):
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173,
            timezone="Invalid/Timezone"
        )

# --- Calculation Error Tests ---

def test_calculation_with_missing_data():
    """Test calculation with missing required data"""
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    with pytest.raises(ValueError):
        chart.calculate_planetary_positions()

def test_calculation_with_invalid_house_system():
    """Test calculation with invalid house system"""
    config = AstroConfig(house_system="InvalidSystem")
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    with pytest.raises(ValueError):
        chart.calculate_houses()

def test_calculation_with_invalid_aspect_orb():
    """Test calculation with invalid aspect orb"""
    config = AstroConfig(orbs={"conjunction": -1.0})  # Invalid orb
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    with pytest.raises(ValueError):
        chart.calculate_aspects()

# --- Adapter Error Tests ---

def test_adapter_initialization_error():
    """Test adapter initialization error"""
    with pytest.raises(RuntimeError):
        SwissEphAdapter(ephemeris_path="/invalid/path")

def test_adapter_calculation_error():
    """Test adapter calculation error"""
    adapter = SwissEphAdapter()
    with pytest.raises(RuntimeError):
        adapter.calculate_planet_position("InvalidPlanet", 0.0)

# --- Resource Error Tests ---

def test_memory_error_handling(monkeypatch):
    """Test memory error handling"""
    def mock_calculation():
        raise MemoryError("Not enough memory")
    
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    monkeypatch.setattr(chart, "calculate_planetary_positions", mock_calculation)
    
    with pytest.raises(MemoryError):
        chart.calculate_planetary_positions()

def test_network_error_handling(monkeypatch):
    """Test network error handling"""
    def mock_calculation():
        raise ConnectionError("Network error")
    
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    monkeypatch.setattr(chart, "calculate_planetary_positions", mock_calculation)
    
    with pytest.raises(ConnectionError):
        chart.calculate_planetary_positions()

# --- Configuration Error Tests ---

def test_invalid_config_values():
    """Test invalid configuration values"""
    with pytest.raises(ValueError):
        AstroConfig(
            house_system="InvalidSystem",
            orbs={"conjunction": -1.0},
            fixed_stars=["InvalidStar"],
            arabic_parts=["InvalidPart"]
        )

def test_missing_config_values():
    """Test missing configuration values"""
    with pytest.raises(ValueError):
        AstroConfig(
            house_system=None,
            orbs={},
            fixed_stars=[],
            arabic_parts=[]
        )

# --- Edge Case Error Tests ---

def test_calculation_at_time_boundary():
    """Test calculation at time boundary"""
    chart = Chart(
        date="2024-03-20",
        time="23:59:59.999999",
        latitude=55.7558,
        longitude=37.6173
    )
    
    with pytest.raises(ValueError):
        chart.calculate_planetary_positions()

def test_calculation_at_coordinate_boundary():
    """Test calculation at coordinate boundary"""
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=90.000001,  # Slightly beyond valid range
        longitude=37.6173
    )
    
    with pytest.raises(ValueError):
        chart.calculate_planetary_positions()

def test_calculation_with_invalid_date_range():
    """Test calculation with invalid date range"""
    chart = Chart(
        date="9999-12-31",  # Far future date
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    with pytest.raises(ValueError):
        chart.calculate_planetary_positions() 