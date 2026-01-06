import pytest
from nocturna_calculations.core.position import Position

class TestPosition:
    @pytest.fixture
    def valid_position(self):
        return Position(longitude=45.0, latitude=10.0, distance=1.0, declination=20.0)

    def test_position_initialization(self):
        """Test basic position initialization with all parameters"""
        pos = Position(longitude=45.0, latitude=10.0, distance=1.0, declination=20.0)
        assert pos.longitude == 45.0
        assert pos.latitude == 10.0
        assert pos.distance == 1.0
        assert pos.declination == 20.0

    def test_position_default_values(self):
        """Test position initialization with default values"""
        pos = Position(longitude=45.0)
        assert pos.longitude == 45.0
        assert pos.latitude == 0.0
        assert pos.distance == 1.0
        assert pos.declination is None

    def test_position_longitude_validation(self):
        """Test longitude validation"""
        # Test valid longitude
        pos = Position(longitude=180.0)
        assert pos.longitude == 180.0

        # Test negative longitude
        pos = Position(longitude=-180.0)
        assert pos.longitude == -180.0

        # Test invalid longitude
        with pytest.raises(ValueError):
            Position(longitude=361.0)

        with pytest.raises(ValueError):
            Position(longitude=-361.0)

    def test_position_latitude_validation(self):
        """Test latitude validation"""
        # Test valid latitude
        pos = Position(longitude=45.0, latitude=90.0)
        assert pos.latitude == 90.0

        # Test negative latitude
        pos = Position(longitude=45.0, latitude=-90.0)
        assert pos.latitude == -90.0

        # Test invalid latitude
        with pytest.raises(ValueError):
            Position(longitude=45.0, latitude=91.0)

        with pytest.raises(ValueError):
            Position(longitude=45.0, latitude=-91.0)

    def test_position_distance_validation(self):
        """Test distance validation"""
        # Test valid distance
        pos = Position(longitude=45.0, distance=2.0)
        assert pos.distance == 2.0

        # Test zero distance
        with pytest.raises(ValueError):
            Position(longitude=45.0, distance=0.0)

        # Test negative distance
        with pytest.raises(ValueError):
            Position(longitude=45.0, distance=-1.0)

    def test_position_declination_validation(self):
        """Test declination validation"""
        # Test valid declination
        pos = Position(longitude=45.0, declination=90.0)
        assert pos.declination == 90.0

        # Test negative declination
        pos = Position(longitude=45.0, declination=-90.0)
        assert pos.declination == -90.0

        # Test invalid declination
        with pytest.raises(ValueError):
            Position(longitude=45.0, declination=91.0)

        with pytest.raises(ValueError):
            Position(longitude=45.0, declination=-91.0)

    def test_position_immutability(self, valid_position):
        """Test that position attributes are immutable"""
        with pytest.raises(AttributeError):
            valid_position.longitude = 90.0

        with pytest.raises(AttributeError):
            valid_position.latitude = 20.0

        with pytest.raises(AttributeError):
            valid_position.distance = 2.0

        with pytest.raises(AttributeError):
            valid_position.declination = 30.0

    def test_position_equality(self):
        """Test position equality comparison"""
        pos1 = Position(longitude=45.0, latitude=10.0, distance=1.0, declination=20.0)
        pos2 = Position(longitude=45.0, latitude=10.0, distance=1.0, declination=20.0)
        pos3 = Position(longitude=46.0, latitude=10.0, distance=1.0, declination=20.0)

        assert pos1 == pos2
        assert pos1 != pos3
        assert pos2 != pos3

    def test_position_string_representation(self, valid_position):
        """Test position string representation"""
        expected_str = "Position(longitude=45.0, latitude=10.0, distance=1.0, declination=20.0)"
        assert str(valid_position) == expected_str