"""
Error handling tests for chart calculations
"""
import pytest
from datetime import datetime, time
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import AstroConfig
from nocturna_calculations.adapters.swisseph_adapter import SwissEphAdapter
from nocturna_calculations.core.exceptions import (
    InvalidDateError,
    InvalidTimeError,
    InvalidCoordinateError,
    InvalidTimezoneError,
    InvalidHouseSystemError,
    InvalidAspectError,
    InvalidPlanetError,
    CalculationError
)

# --- Invalid Input Tests ---

class TestChartErrorHandling:
    def test_invalid_date_format(self):
        """Test error handling for invalid date formats"""
        with pytest.raises(InvalidDateError):
            Chart(
                date="invalid-date",
                time="12:00:00",
                latitude=55.7558,
                longitude=37.6173
            )

        with pytest.raises(InvalidDateError):
            Chart(
                date="2024-13-01",  # Invalid month
                time="12:00:00",
                latitude=55.7558,
                longitude=37.6173
            )

        with pytest.raises(InvalidDateError):
            Chart(
                date="2024-01-32",  # Invalid day
                time="12:00:00",
                latitude=55.7558,
                longitude=37.6173
            )

    def test_invalid_time_format(self):
        """Test error handling for invalid time formats"""
        with pytest.raises(InvalidTimeError):
            Chart(
                date="2024-01-01",
                time="invalid-time",
                latitude=55.7558,
                longitude=37.6173
            )

        with pytest.raises(InvalidTimeError):
            Chart(
                date="2024-01-01",
                time="25:00:00",  # Invalid hour
                latitude=55.7558,
                longitude=37.6173
            )

        with pytest.raises(InvalidTimeError):
            Chart(
                date="2024-01-01",
                time="12:61:00",  # Invalid minute
                latitude=55.7558,
                longitude=37.6173
            )

    def test_invalid_coordinates(self):
        """Test error handling for invalid coordinates"""
        with pytest.raises(InvalidCoordinateError):
            Chart(
                date="2024-01-01",
                time="12:00:00",
                latitude=91.0,  # Invalid latitude
                longitude=37.6173
            )

        with pytest.raises(InvalidCoordinateError):
            Chart(
                date="2024-01-01",
                time="12:00:00",
                latitude=55.7558,
                longitude=181.0  # Invalid longitude
            )

        with pytest.raises(InvalidCoordinateError):
            Chart(
                date="2024-01-01",
                time="12:00:00",
                latitude="invalid",  # Invalid type
                longitude=37.6173
            )

    def test_invalid_timezone(self):
        """Test error handling for invalid timezone"""
        with pytest.raises(InvalidTimezoneError):
            Chart(
                date="2024-01-01",
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

class TestCalculationErrorHandling:
    @pytest.fixture
    def valid_chart(self):
        return Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )

    def test_invalid_house_system(self, valid_chart):
        """Test error handling for invalid house system"""
        with pytest.raises(InvalidHouseSystemError):
            valid_chart.calculate_houses(system="InvalidSystem")

    def test_invalid_aspect_type(self, valid_chart):
        """Test error handling for invalid aspect type"""
        with pytest.raises(InvalidAspectError):
            valid_chart.calculate_aspects(aspect_types=["InvalidAspect"])

    def test_invalid_planet(self, valid_chart):
        """Test error handling for invalid planet"""
        with pytest.raises(InvalidPlanetError):
            valid_chart.calculate_planetary_positions(planets=["InvalidPlanet"])

    def test_invalid_rectification_method(self, valid_chart):
        """Test error handling for invalid rectification method"""
        events = [
            {"date": "2020-01-01", "description": "Test event"}
        ]
        time_window = (
            datetime(2024, 1, 1),
            datetime(2024, 1, 2)
        )
        
        with pytest.raises(CalculationError):
            valid_chart.calculate_rectification(
                events=events,
                time_window=time_window,
                method="InvalidMethod"
            )

    def test_invalid_direction_method(self, valid_chart):
        """Test error handling for invalid direction method"""
        with pytest.raises(CalculationError):
            valid_chart.calculate_primary_directions(
                target_date=datetime(2024, 1, 1),
                method="InvalidMethod"
            )

    def test_invalid_progression_method(self, valid_chart):
        """Test error handling for invalid progression method"""
        with pytest.raises(CalculationError):
            valid_chart.calculate_secondary_progressions(
                target_date=datetime(2024, 1, 1),
                method="InvalidMethod"
            )

    def test_invalid_harmonic_number(self, valid_chart):
        """Test error handling for invalid harmonic number"""
        with pytest.raises(CalculationError):
            valid_chart.calculate_harmonics(harmonic=0)  # Invalid harmonic

        with pytest.raises(CalculationError):
            valid_chart.calculate_harmonics(harmonic=-1)  # Negative harmonic

    def test_invalid_time_window(self, valid_chart):
        """Test error handling for invalid time window"""
        events = [
            {"date": "2020-01-01", "description": "Test event"}
        ]
        time_window = (
            datetime(2024, 1, 2),  # End before start
            datetime(2024, 1, 1)
        )
        
        with pytest.raises(CalculationError):
            valid_chart.calculate_rectification(
                events=events,
                time_window=time_window
            )

    def test_empty_events_list(self, valid_chart):
        """Test error handling for empty events list"""
        time_window = (
            datetime(2024, 1, 1),
            datetime(2024, 1, 2)
        )
        
        with pytest.raises(CalculationError):
            valid_chart.calculate_rectification(
                events=[],
                time_window=time_window
            )

    def test_invalid_event_format(self, valid_chart):
        """Test error handling for invalid event format"""
        events = [
            {"invalid_key": "2020-01-01"}  # Missing required fields
        ]
        time_window = (
            datetime(2024, 1, 1),
            datetime(2024, 1, 2)
        )
        
        with pytest.raises(CalculationError):
            valid_chart.calculate_rectification(
                events=events,
                time_window=time_window
            )

    def test_invalid_transit_date_range(self, valid_chart):
        """Test error handling for invalid transit date range"""
        with pytest.raises(CalculationError):
            valid_chart.calculate_transits(
                start_date=datetime(2024, 1, 2),  # End before start
                end_date=datetime(2024, 1, 1)
            )

    def test_invalid_return_date(self, valid_chart):
        """Test error handling for invalid return date"""
        with pytest.raises(CalculationError):
            valid_chart.calculate_solar_returns(
                target_date=datetime(1990, 1, 1)  # Before birth date
            ) 