"""
Unit tests for Swiss Ephemeris adapter
"""
import pytest
from datetime import datetime
import swisseph as swe

from nocturna_calculations.adapters.swisseph import SwissEphAdapter
from nocturna_calculations.core.chart import Chart

def test_adapter_initialization():
    """Test adapter initialization"""
    adapter = SwissEphAdapter()
    assert adapter.version is not None
    assert adapter.ephe_path is not None

def test_planetary_positions():
    """Test planetary position calculations"""
    adapter = SwissEphAdapter()
    
    # Test date: 2024-03-20 12:00:00 UTC
    jd = swe.julday(2024, 3, 20, 12.0)
    
    # Test planets: Sun and Moon
    planets = [swe.SUN, swe.MOON]
    
    positions = adapter.calculate_planetary_positions(jd, planets)
    
    assert swe.SUN in positions
    assert swe.MOON in positions
    
    # Check position data structure
    for planet in positions.values():
        assert 'longitude' in planet
        assert 'latitude' in planet
        assert 'distance' in planet
        assert 'speed_long' in planet
        assert 'speed_lat' in planet
        assert 'speed_dist' in planet

def test_house_calculations():
    """Test house calculations"""
    adapter = SwissEphAdapter()
    
    # Test date: 2024-03-20 12:00:00 UTC
    jd = swe.julday(2024, 3, 20, 12.0)
    
    # Test location: Moscow
    lat = 55.7558
    lon = 37.6173
    
    houses = adapter.calculate_houses(jd, lat, lon)
    
    assert 'cusps' in houses
    assert 'angles' in houses
    assert 'system' in houses
    
    # Check cusps (12 house cusps)
    assert len(houses['cusps']) == 12
    
    # Check angles (ASC, MC, ARMC, Vertex; newer pyswisseph returns additional points)
    assert len(houses['angles']) >= 4

def test_house_system_argument_changes_cusps():
    """House-system parameter must be passed through to Swiss Ephemeris."""
    adapter = SwissEphAdapter()
    jd = swe.julday(1985, 3, 10, 14 + 37 / 60)
    lat = 59.9343
    lon = 30.3351

    placidus = adapter.calculate_houses(jd, lat, lon, house_system="PLACIDUS")
    whole_sign = adapter.calculate_houses(jd, lat, lon, house_system="WHOLE_SIGN")
    equal = adapter.calculate_houses(jd, lat, lon, house_system="equal")

    assert placidus["system"] == "PLACIDUS"
    assert whole_sign["system"] == "WHOLE_SIGN"
    assert equal["system"] == "EQUAL"
    assert placidus["cusps"] != whole_sign["cusps"]
    assert placidus["cusps"] != equal["cusps"]
    assert all(cusp % 30 == 0 for cusp in whole_sign["cusps"])

def test_house_system_aliases_are_supported():
    """Public API aliases should resolve to the same Swiss Ephemeris system."""
    adapter = SwissEphAdapter()
    jd = swe.julday(1985, 3, 10, 14 + 37 / 60)
    lat = 59.9343
    lon = 30.3351

    by_name = adapter.calculate_houses(jd, lat, lon, house_system="Whole Sign")
    by_code = adapter.calculate_houses(jd, lat, lon, house_system="W")

    assert by_name["system"] == "WHOLE_SIGN"
    assert by_name["cusps"] == by_code["cusps"]

def test_core_chart_passes_house_system_to_adapter():
    """CoreChart is the API path; it must not label Placidus cusps as another system."""
    chart = Chart(
        date="1985-03-10",
        time="14:37:00",
        latitude=59.9343,
        longitude=30.3351,
        timezone="Europe/Moscow",
    )

    placidus = chart.calculate_houses("PLACIDUS")
    whole_sign = chart.calculate_houses("WHOLE_SIGN")

    assert placidus["system"] == "PLACIDUS"
    assert whole_sign["system"] == "WHOLE_SIGN"
    assert placidus["cusps"] != whole_sign["cusps"]
    assert all(cusp % 30 == 0 for cusp in whole_sign["cusps"])
