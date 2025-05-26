import pytest
from datetime import datetime
from nocturna_calculations.calculations.planetary_positions import PlanetaryPositions
from nocturna_calculations.calculations.constants import Planet
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem

class TestPlanetaryPositions:
    @pytest.fixture
    def test_date(self):
        return datetime(2000, 1, 1, 12, 0, 0)

    @pytest.fixture
    def calculator(self):
        return PlanetaryPositions()

    def test_basic_planet_calculation(self, calculator, test_date):
        """Test calculation of basic planet positions"""
        positions = calculator.calculate_positions(test_date)
        assert isinstance(positions, dict)
        assert all(isinstance(pos, Position) for pos in positions.values())
        assert all(pos.coordinate_system == CoordinateSystem.ECLIPTIC for pos in positions.values())

    def test_specific_planet_calculation(self, calculator, test_date):
        """Test calculation of specific planet positions"""
        # Test Sun position
        sun_pos = calculator.calculate_planet_position(Planet.SUN, test_date)
        assert isinstance(sun_pos, Position)
        assert sun_pos.coordinate_system == CoordinateSystem.ECLIPTIC
        assert 0 <= sun_pos.longitude <= 360
        assert -90 <= sun_pos.latitude <= 90

        # Test Moon position
        moon_pos = calculator.calculate_planet_position(Planet.MOON, test_date)
        assert isinstance(moon_pos, Position)
        assert moon_pos.coordinate_system == CoordinateSystem.ECLIPTIC
        assert 0 <= moon_pos.longitude <= 360
        assert -90 <= moon_pos.latitude <= 90

    def test_retrograde_detection(self, calculator, test_date):
        """Test detection of retrograde motion"""
        # Test a known retrograde period for a planet
        retrograde_info = calculator.check_retrograde(Planet.MARS, test_date)
        assert isinstance(retrograde_info, dict)
        assert 'is_retrograde' in retrograde_info
        assert isinstance(retrograde_info['is_retrograde'], bool)
        assert 'speed' in retrograde_info
        assert isinstance(retrograde_info['speed'], float)

    def test_planet_speed_calculation(self, calculator, test_date):
        """Test calculation of planet speeds"""
        speed = calculator.calculate_planet_speed(Planet.SUN, test_date)
        assert isinstance(speed, float)
        assert speed != 0  # Planets are always moving

    def test_precision_validation(self, calculator, test_date):
        """Test precision of calculations against known ephemeris data"""
        # Test Sun position against known ephemeris data
        sun_pos = calculator.calculate_planet_position(Planet.SUN, test_date)
        # Known position for 2000-01-01 12:00:00 UTC
        expected_longitude = 280.731  # Approximate value
        assert abs(sun_pos.longitude - expected_longitude) < 0.1

    def test_edge_cases(self, calculator):
        """Test calculations with edge cases"""
        # Test far future date
        future_date = datetime(2100, 1, 1, 12, 0, 0)
        positions = calculator.calculate_positions(future_date)
        assert all(isinstance(pos, Position) for pos in positions.values())

        # Test far past date
        past_date = datetime(1900, 1, 1, 12, 0, 0)
        positions = calculator.calculate_positions(past_date)
        assert all(isinstance(pos, Position) for pos in positions.values())

    def test_invalid_inputs(self, calculator):
        """Test handling of invalid inputs"""
        with pytest.raises(ValueError):
            calculator.calculate_planet_position("INVALID_PLANET", datetime.now())

        with pytest.raises(ValueError):
            calculator.calculate_planet_position(Planet.SUN, "invalid_date")

    def test_planet_selection(self, calculator, test_date):
        """Test calculation with specific planet selection"""
        selected_planets = [Planet.SUN, Planet.MOON, Planet.MARS]
        positions = calculator.calculate_positions(test_date, planets=selected_planets)
        assert set(positions.keys()) == set(selected_planets)
        assert all(isinstance(pos, Position) for pos in positions.values())

    def test_coordinate_system_conversion(self, calculator, test_date):
        """Test conversion between coordinate systems"""
        # Calculate in ecliptic
        ecliptic_pos = calculator.calculate_planet_position(
            Planet.SUN, 
            test_date,
            coordinate_system=CoordinateSystem.ECLIPTIC
        )
        assert ecliptic_pos.coordinate_system == CoordinateSystem.ECLIPTIC

        # Calculate in equatorial
        equatorial_pos = calculator.calculate_planet_position(
            Planet.SUN,
            test_date,
            coordinate_system=CoordinateSystem.EQUATORIAL
        )
        assert equatorial_pos.coordinate_system == CoordinateSystem.EQUATORIAL

        # Verify coordinates are different but valid
        assert ecliptic_pos.longitude != equatorial_pos.longitude
        assert 0 <= equatorial_pos.longitude <= 360
        assert -90 <= equatorial_pos.latitude <= 90 