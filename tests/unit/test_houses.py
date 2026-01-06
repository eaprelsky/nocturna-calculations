"""
House calculation tests for astrological charts
"""
import pytest
from datetime import datetime, time
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import Config

# --- Test Data ---

@pytest.fixture
def test_chart():
    """Create a test chart with known house cusps"""
    return Chart(
        date="2024-03-20",  # Spring Equinox
        time="12:00:00",    # Noon
        latitude=55.7558,   # Moscow
        longitude=37.6173,
        timezone="Europe/Moscow"
    )

# --- House System Tests ---

def test_placidus_house_system(test_chart):
    """Test Placidus house system calculations"""
    config = Config(house_system="Placidus")
    test_chart.config = config
    
    houses = test_chart.calculate_houses()
    
    # Basic validation
    assert houses is not None
    assert len(houses) == 12
    
    # Validate house cusps
    for house_num, cusp in houses.items():
        assert 0 <= cusp < 360, f"House {house_num} cusp {cusp} out of range"
    
    # Validate house relationships
    assert houses["1"] == 0.0  # First house cusp should be at 0° Aries at noon on equinox
    assert abs(houses["7"] - 180.0) < 0.1  # Opposite houses should be 180° apart
    assert abs(houses["4"] - 270.0) < 0.1  # IC should be at 270°
    assert abs(houses["10"] - 90.0) < 0.1  # MC should be at 90°

def test_koch_house_system(test_chart):
    """Test Koch house system calculations"""
    config = Config(house_system="Koch")
    test_chart.config = config
    
    houses = test_chart.calculate_houses()
    
    # Basic validation
    assert houses is not None
    assert len(houses) == 12
    
    # Validate house cusps
    for house_num, cusp in houses.items():
        assert 0 <= cusp < 360, f"House {house_num} cusp {cusp} out of range"
    
    # Validate Koch-specific relationships
    assert houses["1"] == 0.0  # First house cusp should be at 0° Aries at noon on equinox
    assert abs(houses["7"] - 180.0) < 0.1  # Opposite houses should be 180° apart

def test_whole_sign_house_system(test_chart):
    """Test Whole Sign house system calculations"""
    config = Config(house_system="Whole Sign")
    test_chart.config = config
    
    houses = test_chart.calculate_houses()
    
    # Basic validation
    assert houses is not None
    assert len(houses) == 12
    
    # Validate house cusps
    for house_num, cusp in houses.items():
        assert 0 <= cusp < 360, f"House {house_num} cusp {cusp} out of range"
        assert cusp % 30 == 0, f"House {house_num} cusp {cusp} not aligned to sign boundaries"

def test_equal_house_system(test_chart):
    """Test Equal House system calculations"""
    config = Config(house_system="Equal")
    test_chart.config = config
    
    houses = test_chart.calculate_houses()
    
    # Basic validation
    assert houses is not None
    assert len(houses) == 12
    
    # Validate house cusps
    for house_num, cusp in houses.items():
        assert 0 <= cusp < 360, f"House {house_num} cusp {cusp} out of range"
    
    # Validate equal house relationships
    first_house = houses["1"]
    for house_num, cusp in houses.items():
        expected_cusp = (first_house + (int(house_num) - 1) * 30) % 360
        assert abs(cusp - expected_cusp) < 0.1, f"House {house_num} cusp {cusp} not equal to expected {expected_cusp}"

def test_campanus_house_system(test_chart):
    """Test Campanus house system calculations"""
    config = Config(house_system="Campanus")
    test_chart.config = config
    
    houses = test_chart.calculate_houses()
    
    # Basic validation
    assert houses is not None
    assert len(houses) == 12
    
    # Validate house cusps
    for house_num, cusp in houses.items():
        assert 0 <= cusp < 360, f"House {house_num} cusp {cusp} out of range"
    
    # Validate Campanus-specific relationships
    assert houses["1"] == 0.0  # First house cusp should be at 0° Aries at noon on equinox
    assert abs(houses["7"] - 180.0) < 0.1  # Opposite houses should be 180° apart

# --- Latitude Tests ---

def test_houses_at_equator():
    """Test house calculations at the equator"""
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=0.0,
        longitude=0.0
    )
    
    # Test different house systems
    systems = ["Placidus", "Koch", "Whole Sign", "Equal", "Campanus"]
    for system in systems:
        config = Config(house_system=system)
        chart.config = config
        houses = chart.calculate_houses()
        
        assert houses is not None
        assert len(houses) == 12
        
        # Validate house cusps
        for house_num, cusp in houses.items():
            assert 0 <= cusp < 360, f"House {house_num} cusp {cusp} out of range"

def test_houses_at_polar_regions():
    """Test house calculations at polar regions"""
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
    
    # Test different house systems
    systems = ["Placidus", "Koch", "Whole Sign", "Equal", "Campanus"]
    for system in systems:
        config = Config(house_system=system)
        
        # North Pole
        north_chart.config = config
        north_houses = north_chart.calculate_houses()
        assert north_houses is not None
        assert len(north_houses) == 12
        
        # South Pole
        south_chart.config = config
        south_houses = south_chart.calculate_houses()
        assert south_houses is not None
        assert len(south_houses) == 12

# --- Time Tests ---

def test_houses_at_different_times():
    """Test house calculations at different times of day"""
    times = ["00:00:00", "06:00:00", "12:00:00", "18:00:00"]
    
    for time_str in times:
        chart = Chart(
            date="2024-03-20",
            time=time_str,
            latitude=55.7558,
            longitude=37.6173
        )
        
        # Test different house systems
        systems = ["Placidus", "Koch", "Whole Sign", "Equal", "Campanus"]
        for system in systems:
            config = Config(house_system=system)
            chart.config = config
            houses = chart.calculate_houses()
            
            assert houses is not None
            assert len(houses) == 12
            
            # Validate house cusps
            for house_num, cusp in houses.items():
                assert 0 <= cusp < 360, f"House {house_num} cusp {cusp} out of range"

# --- House System Validation Tests ---

def test_house_system_validation():
    """Test validation of house system calculations"""
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Test invalid house system
    with pytest.raises(ValueError):
        config = Config(house_system="InvalidSystem")
        chart.config = config
        chart.calculate_houses()
    
    # Test missing house system
    with pytest.raises(ValueError):
        config = Config(house_system=None)
        chart.config = config
        chart.calculate_houses()

# --- House Calculation Edge Cases ---

def test_houses_at_date_line():
    """Test house calculations at the international date line"""
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=0.0,
        longitude=180.0
    )
    
    # Test different house systems
    systems = ["Placidus", "Koch", "Whole Sign", "Equal", "Campanus"]
    for system in systems:
        config = Config(house_system=system)
        chart.config = config
        houses = chart.calculate_houses()
        
        assert houses is not None
        assert len(houses) == 12
        
        # Validate house cusps
        for house_num, cusp in houses.items():
            assert 0 <= cusp < 360, f"House {house_num} cusp {cusp} out of range"

def test_houses_at_dst_transition():
    """Test house calculations during DST transition"""
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
    
    # Test different house systems
    systems = ["Placidus", "Koch", "Whole Sign", "Equal", "Campanus"]
    for system in systems:
        config = Config(house_system=system)
        
        # Spring forward
        spring_chart.config = config
        spring_houses = spring_chart.calculate_houses()
        assert spring_houses is not None
        assert len(spring_houses) == 12
        
        # Fall back
        fall_chart.config = config
        fall_houses = fall_chart.calculate_houses()
        assert fall_houses is not None
        assert len(fall_houses) == 12 