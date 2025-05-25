"""
Configuration tests for chart calculations
"""
import pytest
from datetime import datetime, time
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import AstroConfig

# --- Configuration Test Setup ---

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

# --- House System Tests ---

def test_placidus_house_system():
    """Test Placidus house system configuration"""
    config = AstroConfig(house_system="Placidus")
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    houses = chart.calculate_houses()
    assert houses is not None
    assert len(houses) == 12

def test_koch_house_system():
    """Test Koch house system configuration"""
    config = AstroConfig(house_system="Koch")
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    houses = chart.calculate_houses()
    assert houses is not None
    assert len(houses) == 12

def test_whole_sign_house_system():
    """Test Whole Sign house system configuration"""
    config = AstroConfig(house_system="Whole Sign")
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    houses = chart.calculate_houses()
    assert houses is not None
    assert len(houses) == 12

# --- Aspect Orb Tests ---

def test_custom_aspect_orbs():
    """Test custom aspect orb configuration"""
    config = AstroConfig(orbs={
        "conjunction": 10.0,
        "opposition": 10.0,
        "trine": 8.0,
        "square": 8.0,
        "sextile": 6.0
    })
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    aspects = chart.calculate_aspects()
    assert aspects is not None
    assert all(aspect.get("orb", 0) <= 10.0 for aspect in aspects)

def test_minimum_aspect_orbs():
    """Test minimum aspect orb configuration"""
    config = AstroConfig(orbs={
        "conjunction": 1.0,
        "opposition": 1.0,
        "trine": 1.0,
        "square": 1.0,
        "sextile": 1.0
    })
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    aspects = chart.calculate_aspects()
    assert aspects is not None
    assert all(aspect.get("orb", 0) <= 1.0 for aspect in aspects)

# --- Fixed Stars Tests ---

def test_specific_fixed_stars():
    """Test specific fixed stars configuration"""
    config = AstroConfig(fixed_stars=["Aldebaran", "Regulus", "Spica"])
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    stars = chart.calculate_fixed_stars()
    assert stars is not None
    assert all(star in stars for star in ["Aldebaran", "Regulus", "Spica"])

def test_all_fixed_stars():
    """Test all fixed stars configuration"""
    config = AstroConfig(fixed_stars=["*"])
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    stars = chart.calculate_fixed_stars()
    assert stars is not None
    assert len(stars) > 0

# --- Arabic Parts Tests ---

def test_specific_arabic_parts():
    """Test specific Arabic parts configuration"""
    config = AstroConfig(arabic_parts=["Fortune", "Spirit", "Eros"])
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    parts = chart.calculate_arabic_parts()
    assert parts is not None
    assert all(part in parts for part in ["Fortune", "Spirit", "Eros"])

def test_all_arabic_parts():
    """Test all Arabic parts configuration"""
    config = AstroConfig(arabic_parts=["*"])
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    parts = chart.calculate_arabic_parts()
    assert parts is not None
    assert len(parts) > 0

# --- Combined Configuration Tests ---

def test_combined_configuration():
    """Test combined configuration settings"""
    config = AstroConfig(
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
    
    houses = chart.calculate_houses()
    aspects = chart.calculate_aspects()
    stars = chart.calculate_fixed_stars()
    parts = chart.calculate_arabic_parts()
    
    assert houses is not None
    assert aspects is not None
    assert stars is not None
    assert parts is not None
    
    assert len(houses) == 12
    assert all(aspect.get("orb", 0) <= 10.0 for aspect in aspects)
    assert all(star in stars for star in ["Aldebaran", "Regulus"])
    assert all(part in parts for part in ["Fortune", "Spirit"])

# --- Configuration Validation Tests ---

def test_invalid_house_system():
    """Test invalid house system configuration"""
    with pytest.raises(ValueError):
        AstroConfig(house_system="InvalidSystem")

def test_invalid_aspect_orb():
    """Test invalid aspect orb configuration"""
    with pytest.raises(ValueError):
        AstroConfig(orbs={"conjunction": -1.0})

def test_invalid_fixed_star():
    """Test invalid fixed star configuration"""
    with pytest.raises(ValueError):
        AstroConfig(fixed_stars=["InvalidStar"])

def test_invalid_arabic_part():
    """Test invalid Arabic part configuration"""
    with pytest.raises(ValueError):
        AstroConfig(arabic_parts=["InvalidPart"])

# --- Configuration Persistence Tests ---

def test_configuration_persistence():
    """Test configuration persistence across calculations"""
    config = AstroConfig(
        house_system="Koch",
        orbs={"conjunction": 10.0},
        fixed_stars=["Aldebaran"],
        arabic_parts=["Fortune"]
    )
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    # First calculation
    houses1 = chart.calculate_houses()
    aspects1 = chart.calculate_aspects()
    stars1 = chart.calculate_fixed_stars()
    parts1 = chart.calculate_arabic_parts()
    
    # Second calculation
    houses2 = chart.calculate_houses()
    aspects2 = chart.calculate_aspects()
    stars2 = chart.calculate_fixed_stars()
    parts2 = chart.calculate_arabic_parts()
    
    # Verify configuration persists
    assert houses1 == houses2
    assert aspects1 == aspects2
    assert stars1 == stars2
    assert parts1 == parts2 