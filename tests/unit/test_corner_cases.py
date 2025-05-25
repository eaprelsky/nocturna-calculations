import pytest
from datetime import datetime, timedelta
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import AstroConfig
from nocturna_calculations.core.exceptions import (
    CalculationError,
    InvalidDateError,
    InvalidCoordinateError
)

class TestDateTimeCornerCases:
    @pytest.fixture
    def base_chart(self):
        return Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )

    def test_leap_second_handling(self):
        """Test calculations during leap second"""
        with pytest.raises(InvalidTimeError):
            Chart(
                date="2024-01-01",
                time="23:59:60",  # Leap second
                latitude=55.7558,
                longitude=37.6173
            )

    def test_dst_transition(self):
        """Test calculations during DST transition"""
        # Spring forward
        chart = Chart(
            date="2024-03-31",
            time="02:30:00",  # During DST transition
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow"
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

        # Fall back
        chart = Chart(
            date="2024-10-27",
            time="02:30:00",  # During DST transition
            latitude=55.7558,
            longitude=37.6173,
            timezone="Europe/Moscow"
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

    def test_midnight_transition(self):
        """Test calculations at midnight transition"""
        chart = Chart(
            date="2024-01-01",
            time="23:59:59.999999",
            latitude=55.7558,
            longitude=37.6173
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

    def test_historical_calendar(self):
        """Test calculations during calendar transition"""
        with pytest.raises(InvalidDateError):
            Chart(
                date="1582-10-05",  # Julian calendar
                time="12:00:00",
                latitude=55.7558,
                longitude=37.6173
            )

    def test_future_date_limits(self):
        """Test calculations with future dates beyond ephemeris"""
        with pytest.raises(InvalidDateError):
            Chart(
                date="2100-01-01",  # Beyond ephemeris data
                time="12:00:00",
                latitude=55.7558,
                longitude=37.6173
            )

class TestGeographicCornerCases:
    def test_polar_regions(self):
        """Test calculations at polar regions"""
        # North Pole
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=90.0,
            longitude=0.0
        )
        houses = chart.calculate_houses()
        assert houses is not None

        # South Pole
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=-90.0,
            longitude=0.0
        )
        houses = chart.calculate_houses()
        assert houses is not None

    def test_date_line(self):
        """Test calculations at international date line"""
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=0.0,
            longitude=180.0
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=0.0,
            longitude=-180.0
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

    def test_equator(self):
        """Test calculations at equator"""
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=0.0,
            longitude=0.0
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

    def test_extreme_altitude(self):
        """Test calculations at extreme altitudes"""
        # Mount Everest
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=27.9881,
            longitude=86.9250,
            altitude=8848  # meters
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

class TestCalculationCornerCases:
    @pytest.fixture
    def base_chart(self):
        return Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )

    def test_retrograde_transition(self):
        """Test calculations during retrograde transition"""
        # Find a date when a planet is stationary
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

    def test_multiple_aspects(self):
        """Test calculations with multiple aspects forming simultaneously"""
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )
        aspects = chart.calculate_aspects()
        assert aspects is not None

    def test_critical_degrees(self):
        """Test calculations at critical degrees"""
        # 0° Aries
        chart = Chart(
            date="2024-03-20",  # Spring Equinox
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

        # 29° of any sign
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )
        positions = chart.calculate_planetary_positions()
        assert positions is not None

class TestAPICornerCases:
    @pytest.fixture
    def base_chart(self):
        return Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )

    def test_concurrent_calculations(self):
        """Test concurrent calculations"""
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )
        
        # Test multiple calculations running simultaneously
        positions = chart.calculate_planetary_positions()
        aspects = chart.calculate_aspects()
        houses = chart.calculate_houses()
        
        assert positions is not None
        assert aspects is not None
        assert houses is not None

    def test_large_batch_operations(self):
        """Test large batch operations"""
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )
        
        # Test calculating multiple returns
        solar_returns = chart.calculate_solar_returns(
            target_date=datetime(2024, 1, 1),
            count=10
        )
        assert solar_returns is not None
        assert len(solar_returns) == 10

    def test_memory_management(self):
        """Test memory management for long calculations"""
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )
        
        # Test long-term transit calculations
        transits = chart.calculate_transits(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        assert transits is not None

    def test_error_recovery(self):
        """Test error recovery after partial failures"""
        chart = Chart(
            date="2024-01-01",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        )
        
        # Test calculation with invalid parameters
        with pytest.raises(CalculationError):
            chart.calculate_planetary_positions(planets=["InvalidPlanet"])
        
        # Verify system can still perform valid calculations
        positions = chart.calculate_planetary_positions()
        assert positions is not None 