import pytest
from datetime import datetime, timedelta
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import Config
from nocturna_calculations.adapters.swisseph import SwissEphAdapter

@pytest.fixture
def swisseph_adapter():
    """Create a SwissEph adapter instance"""
    return SwissEphAdapter()

@pytest.fixture
def natal_chart():
    """Create a natal chart for testing"""
    return Chart(
        date="1990-01-01",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        timezone="Europe/Moscow"
    )

class TestPrimaryDirections:
    def test_semi_arc_directions(self, swisseph_adapter, natal_chart):
        """Test primary directions using semi-arc method"""
        target_date = datetime(2024, 1, 1)
        directions = natal_chart.calculate_primary_directions(
            target_date=target_date,
            method="semi-arc"
        )
        
        assert directions is not None
        assert isinstance(directions, list)
        assert len(directions) > 0
        
        # Verify direction structure
        direction = directions[0]
        assert hasattr(direction, 'planet')
        assert hasattr(direction, 'angle')
        assert hasattr(direction, 'date')

    def test_placidus_directions(self, swisseph_adapter, natal_chart):
        """Test primary directions using Placidus method"""
        target_date = datetime(2024, 1, 1)
        directions = natal_chart.calculate_primary_directions(
            target_date=target_date,
            method="placidus"
        )
        
        assert directions is not None
        assert isinstance(directions, list)
        assert len(directions) > 0

    def test_regiomontanus_directions(self, swisseph_adapter, natal_chart):
        """Test primary directions using Regiomontanus method"""
        target_date = datetime(2024, 1, 1)
        directions = natal_chart.calculate_primary_directions(
            target_date=target_date,
            method="regiomontanus"
        )
        
        assert directions is not None
        assert isinstance(directions, list)
        assert len(directions) > 0

    def test_directions_with_specific_planets(self, swisseph_adapter, natal_chart):
        """Test primary directions for specific planets"""
        target_date = datetime(2024, 1, 1)
        planets = ["Sun", "Moon", "Mars"]
        directions = natal_chart.calculate_primary_directions(
            target_date=target_date,
            planets=planets
        )
        
        assert directions is not None
        assert isinstance(directions, list)
        assert len(directions) > 0
        
        # Verify only requested planets are included
        direction_planets = {d.planet for d in directions}
        assert all(p in direction_planets for p in planets)

class TestSecondaryProgressions:
    def test_day_for_year_progressions(self, swisseph_adapter, natal_chart):
        """Test secondary progressions using day-for-year method"""
        target_date = datetime(2024, 1, 1)
        progressions = natal_chart.calculate_secondary_progressions(
            target_date=target_date,
            method="day-for-year"
        )
        
        assert progressions is not None
        assert isinstance(progressions, list)
        assert len(progressions) > 0
        
        # Verify progression structure
        progression = progressions[0]
        assert hasattr(progression, 'planet')
        assert hasattr(progression, 'position')
        assert hasattr(progression, 'date')

    def test_progressions_with_specific_planets(self, swisseph_adapter, natal_chart):
        """Test secondary progressions for specific planets"""
        target_date = datetime(2024, 1, 1)
        planets = ["Sun", "Moon", "Venus"]
        progressions = natal_chart.calculate_secondary_progressions(
            target_date=target_date,
            planets=planets
        )
        
        assert progressions is not None
        assert isinstance(progressions, list)
        assert len(progressions) > 0
        
        # Verify only requested planets are included
        progression_planets = {p.planet for p in progressions}
        assert all(p in progression_planets for p in planets)

class TestReturns:
    def test_solar_returns(self, swisseph_adapter, natal_chart):
        """Test solar return calculations"""
        target_date = datetime(2024, 1, 1)
        returns = natal_chart.calculate_solar_returns(
            target_date=target_date
        )
        
        assert returns is not None
        assert isinstance(returns, list)
        assert len(returns) > 0
        
        # Verify return structure
        return_chart = returns[0]
        assert isinstance(return_chart, Chart)
        assert return_chart.date.year == 2024

    def test_lunar_returns(self, swisseph_adapter, natal_chart):
        """Test lunar return calculations"""
        target_date = datetime(2024, 1, 1)
        returns = natal_chart.calculate_lunar_returns(
            target_date=target_date
        )
        
        assert returns is not None
        assert isinstance(returns, list)
        assert len(returns) > 0
        
        # Verify return structure
        return_chart = returns[0]
        assert isinstance(return_chart, Chart)
        assert return_chart.date.year == 2024

    def test_progressed_returns(self, swisseph_adapter, natal_chart):
        """Test progressed return calculations"""
        target_date = datetime(2024, 1, 1)
        returns = natal_chart.calculate_progressed_returns(
            target_date=target_date
        )
        
        assert returns is not None
        assert isinstance(returns, list)
        assert len(returns) > 0
        
        # Verify return structure
        return_chart = returns[0]
        assert isinstance(return_chart, Chart)
        assert return_chart.date.year == 2024

class TestTransits:
    def test_transit_calculations(self, swisseph_adapter, natal_chart):
        """Test transit calculations"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        transits = natal_chart.calculate_transits(
            start_date=start_date,
            end_date=end_date
        )
        
        assert transits is not None
        assert isinstance(transits, list)
        assert len(transits) > 0
        
        # Verify transit structure
        transit = transits[0]
        assert hasattr(transit, 'planet')
        assert hasattr(transit, 'aspect')
        assert hasattr(transit, 'date')

    def test_transits_with_specific_planets(self, swisseph_adapter, natal_chart):
        """Test transit calculations for specific planets"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        planets = ["Jupiter", "Saturn", "Uranus"]
        transits = natal_chart.calculate_transits(
            start_date=start_date,
            end_date=end_date,
            planets=planets
        )
        
        assert transits is not None
        assert isinstance(transits, list)
        assert len(transits) > 0
        
        # Verify only requested planets are included
        transit_planets = {t.planet for t in transits}
        assert all(p in transit_planets for p in planets)

class TestRectification:
    def test_event_based_rectification(self, swisseph_adapter, natal_chart):
        """Test event-based rectification"""
        events = [
            {"date": "2020-01-01", "description": "Career change"},
            {"date": "2021-06-15", "description": "Relationship start"},
            {"date": "2022-12-31", "description": "Major move"}
        ]
        time_window = (
            datetime(1989, 12, 31, 0, 0),
            datetime(1990, 1, 1, 23, 59)
        )
        
        result = natal_chart.calculate_rectification(
            events=events,
            time_window=time_window,
            method="event-based"
        )
        
        assert result is not None
        assert hasattr(result, 'rectified_time')
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'matching_events')

    def test_pattern_based_rectification(self, swisseph_adapter, natal_chart):
        """Test pattern-based rectification"""
        events = [
            {"date": "2020-01-01", "description": "Career change"},
            {"date": "2021-06-15", "description": "Relationship start"},
            {"date": "2022-12-31", "description": "Major move"}
        ]
        time_window = (
            datetime(1989, 12, 31, 0, 0),
            datetime(1990, 1, 1, 23, 59)
        )
        
        result = natal_chart.calculate_rectification(
            events=events,
            time_window=time_window,
            method="pattern-based"
        )
        
        assert result is not None
        assert hasattr(result, 'rectified_time')
        assert hasattr(result, 'confidence_score')
        assert hasattr(result, 'pattern_matches') 