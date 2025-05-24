"""
Unit tests for Swiss Ephemeris adapter
"""
import pytest
from datetime import datetime
import swisseph as swe

from nocturna_calculations.adapters.swisseph import SwissEphAdapter

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
    
    # Check cusps (should be 13 values for 12 houses + ASC)
    assert len(houses['cusps']) == 13
    
    # Check angles (should be 4 values: ASC, MC, ARMC, Vertex)
    assert len(houses['angles']) == 4 