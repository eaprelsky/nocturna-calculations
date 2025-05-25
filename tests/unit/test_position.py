import pytest
from datetime import datetime
from nocturna.calculations.position import Position
from nocturna.calculations.constants import CoordinateSystem

class TestPosition:
    @pytest.fixture
    def valid_position(self):
        return Position(
            longitude=45.0,
            latitude=30.0,
            distance=1.0,
            coordinate_system=CoordinateSystem.ECLIPTIC
        )

    def test_position_initialization(self):
        """Test basic position initialization with valid parameters"""
        pos = Position(45.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)
        assert pos.longitude == 45.0
        assert pos.latitude == 30.0
        assert pos.distance == 1.0
        assert pos.coordinate_system == CoordinateSystem.ECLIPTIC

    def test_invalid_coordinates(self):
        """Test position initialization with invalid coordinates"""
        with pytest.raises(ValueError):
            Position(361.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)  # Longitude > 360
        with pytest.raises(ValueError):
            Position(45.0, 91.0, 1.0, CoordinateSystem.ECLIPTIC)   # Latitude > 90
        with pytest.raises(ValueError):
            Position(45.0, 30.0, -1.0, CoordinateSystem.ECLIPTIC)  # Negative distance

    def test_coordinate_normalization(self):
        """Test that coordinates are properly normalized"""
        pos = Position(370.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)
        assert pos.longitude == 10.0  # 370 - 360 = 10

        pos = Position(-10.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)
        assert pos.longitude == 350.0  # -10 + 360 = 350

    def test_distance_calculation(self, valid_position):
        """Test distance calculations between positions"""
        pos2 = Position(50.0, 35.0, 1.0, CoordinateSystem.ECLIPTIC)
        distance = valid_position.distance_to(pos2)
        assert isinstance(distance, float)
        assert distance > 0

    def test_declination_calculation(self, valid_position):
        """Test declination calculations"""
        declination = valid_position.calculate_declination()
        assert isinstance(declination, float)
        assert -90 <= declination <= 90

    def test_coordinate_system_conversion(self, valid_position):
        """Test conversion between coordinate systems"""
        equatorial_pos = valid_position.to_equatorial()
        assert equatorial_pos.coordinate_system == CoordinateSystem.EQUATORIAL
        assert isinstance(equatorial_pos.longitude, float)
        assert isinstance(equatorial_pos.latitude, float)

    def test_edge_cases(self):
        """Test position calculations with edge cases"""
        # Test poles
        north_pole = Position(0.0, 90.0, 1.0, CoordinateSystem.ECLIPTIC)
        assert north_pole.latitude == 90.0

        # Test equator
        equator = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        assert equator.latitude == 0.0

        # Test prime meridian
        prime_meridian = Position(0.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)
        assert prime_meridian.longitude == 0.0

    def test_precision_limits(self):
        """Test position calculations with extreme precision values"""
        # Test very small angles
        small_angle = Position(0.000001, 0.000001, 1.0, CoordinateSystem.ECLIPTIC)
        assert small_angle.longitude == pytest.approx(0.000001)
        assert small_angle.latitude == pytest.approx(0.000001)

        # Test very large angles
        large_angle = Position(359.999999, 89.999999, 1.0, CoordinateSystem.ECLIPTIC)
        assert large_angle.longitude == pytest.approx(359.999999)
        assert large_angle.latitude == pytest.approx(89.999999)

    def test_immutable_properties(self, valid_position):
        """Test that position properties are immutable"""
        with pytest.raises(AttributeError):
            valid_position.longitude = 50.0
        with pytest.raises(AttributeError):
            valid_position.latitude = 40.0
        with pytest.raises(AttributeError):
            valid_position.distance = 2.0
        with pytest.raises(AttributeError):
            valid_position.coordinate_system = CoordinateSystem.EQUATORIAL