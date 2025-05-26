"""
Unit tests for the Chart class
"""
import pytest
from datetime import datetime
import pytz
from nocturna_calculations.calculations.chart import Chart
from nocturna_calculations.core.constants import HouseSystem

class TestChart:
    @pytest.fixture
    def test_chart(self):
        """Create a test chart"""
        tz = pytz.timezone("Europe/Moscow")
        date_time = datetime(2024, 3, 20, 12, 0, 0, tzinfo=tz)
        return Chart(
            latitude=55.7558,
            longitude=37.6173,
            date_time=date_time,
            house_system=HouseSystem.PLACIDUS
        )
    
    def test_calculate_house_position(self, test_chart):
        """Test house position calculation"""
        # Test positions in different houses
        assert test_chart._calculate_house_position(0) == 1
        assert test_chart._calculate_house_position(30) == 2
        assert test_chart._calculate_house_position(60) == 3
        assert test_chart._calculate_house_position(90) == 4
        assert test_chart._calculate_house_position(120) == 5
        assert test_chart._calculate_house_position(150) == 6
        assert test_chart._calculate_house_position(180) == 7
        assert test_chart._calculate_house_position(210) == 8
        assert test_chart._calculate_house_position(240) == 9
        assert test_chart._calculate_house_position(270) == 10
        assert test_chart._calculate_house_position(300) == 11
        assert test_chart._calculate_house_position(330) == 12
    
    def test_calculate_sign(self, test_chart):
        """Test sign calculation"""
        # Test positions in different signs
        assert test_chart._calculate_sign(0) == 1
        assert test_chart._calculate_sign(30) == 2
        assert test_chart._calculate_sign(60) == 3
        assert test_chart._calculate_sign(90) == 4
        assert test_chart._calculate_sign(120) == 5
        assert test_chart._calculate_sign(150) == 6
        assert test_chart._calculate_sign(180) == 7
        assert test_chart._calculate_sign(210) == 8
        assert test_chart._calculate_sign(240) == 9
        assert test_chart._calculate_sign(270) == 10
        assert test_chart._calculate_sign(300) == 11
        assert test_chart._calculate_sign(330) == 12
    
    def test_is_aspect_applying(self, test_chart):
        """Test aspect applying calculation"""
        # Test applying aspects
        assert test_chart._is_aspect_applying(0, 10, 15) == True
        assert test_chart._is_aspect_applying(350, 5, 15) == True
        assert test_chart._is_aspect_applying(180, 190, 15) == True
        
        # Test separating aspects
        assert test_chart._is_aspect_applying(10, 0, 15) == False
        assert test_chart._is_aspect_applying(5, 350, 15) == False
        assert test_chart._is_aspect_applying(190, 180, 15) == False
    
    def test_calculate_orb(self, test_chart):
        """Test orb calculation"""
        # Test orbs for different angles
        assert test_chart._calculate_orb(0, 10, 15) == 10
        assert test_chart._calculate_orb(350, 5, 15) == 15
        assert test_chart._calculate_orb(180, 190, 15) == 10
        assert test_chart._calculate_orb(0, 350, 15) == 10
    
    def test_invalid_coordinates(self):
        """Test chart creation with invalid coordinates"""
        tz = pytz.timezone("Europe/Moscow")
        date_time = datetime(2024, 3, 20, 12, 0, 0, tzinfo=tz)
        
        # Test invalid latitude
        with pytest.raises(ValueError):
            Chart(
                latitude=100.0,  # Invalid latitude
                longitude=37.6173,
                date_time=date_time
            )
        
        # Test invalid longitude
        with pytest.raises(ValueError):
            Chart(
                latitude=55.7558,
                longitude=200.0,  # Invalid longitude
                date_time=date_time
            )
    
    def test_polar_regions(self):
        """Test chart calculations in polar regions"""
        tz = pytz.timezone("Europe/Moscow")
        date_time = datetime(2024, 3, 20, 12, 0, 0, tzinfo=tz)
        
        # Test near North Pole
        north_pole_chart = Chart(
            latitude=89.0,
            longitude=0.0,
            date_time=date_time
        )
        houses = north_pole_chart.calculate_houses()
        assert len(houses) == 12
        assert all(0 <= cusp < 360 for cusp in houses)
        
        # Test near South Pole
        south_pole_chart = Chart(
            latitude=-89.0,
            longitude=0.0,
            date_time=date_time
        )
        houses = south_pole_chart.calculate_houses()
        assert len(houses) == 12
        assert all(0 <= cusp < 360 for cusp in houses)
    
    def test_different_house_systems(self):
        """Test chart calculations with different house systems"""
        tz = pytz.timezone("Europe/Moscow")
        date_time = datetime(2024, 3, 20, 12, 0, 0, tzinfo=tz)
        
        # Test each house system
        for house_system in HouseSystem:
            chart = Chart(
                latitude=55.7558,
                longitude=37.6173,
                date_time=date_time,
                house_system=house_system
            )
            houses = chart.calculate_houses()
            assert len(houses) == 12
            assert all(0 <= cusp < 360 for cusp in houses)