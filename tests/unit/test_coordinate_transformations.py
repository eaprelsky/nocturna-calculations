import pytest
import math
from datetime import datetime
import pytz
from nocturna_calculations.calculations.coordinates import CoordinateTransformer
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem

class TestCoordinateTransformations:
    @pytest.fixture
    def transformer(self):
        return CoordinateTransformer()

    @pytest.fixture
    def test_date(self):
        return datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)

    def test_ecliptic_to_equatorial(self, transformer):
        """Test conversion from ecliptic to equatorial coordinates"""
        # Test at vernal equinox
        ecliptic_pos = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(ecliptic_pos)
        assert isinstance(equatorial_pos, Position)
        assert equatorial_pos.system == CoordinateSystem.EQUATORIAL
        assert equatorial_pos.longitude == pytest.approx(0.0, abs=1e-6)
        assert equatorial_pos.latitude == pytest.approx(0.0, abs=1e-6)

        # Test at summer solstice
        ecliptic_pos = Position(90.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(ecliptic_pos)
        assert equatorial_pos.longitude == pytest.approx(90.0, abs=1e-6)
        assert equatorial_pos.latitude == pytest.approx(23.4393, abs=1e-4)

        # Test at winter solstice
        ecliptic_pos = Position(270.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(ecliptic_pos)
        assert equatorial_pos.longitude == pytest.approx(270.0, abs=1e-6)
        assert equatorial_pos.latitude == pytest.approx(-23.4393, abs=1e-4)

    def test_equatorial_to_horizontal(self, transformer):
        """Test conversion from equatorial to horizontal coordinates"""
        # Test at zenith
        equatorial_pos = Position(0.0, 90.0, 1.0, CoordinateSystem.EQUATORIAL)
        horizontal_pos = transformer.equatorial_to_horizontal(
            equatorial_pos,
            latitude=0.0,
            longitude=0.0,
            sidereal_time=0.0
        )
        assert isinstance(horizontal_pos, Position)
        assert horizontal_pos.system == CoordinateSystem.HORIZONTAL
        assert horizontal_pos.altitude == pytest.approx(90.0, abs=1e-6)
        assert horizontal_pos.azimuth == pytest.approx(0.0, abs=1e-6)

        # Test at horizon
        equatorial_pos = Position(0.0, 0.0, 1.0, CoordinateSystem.EQUATORIAL)
        horizontal_pos = transformer.equatorial_to_horizontal(
            equatorial_pos,
            latitude=0.0,
            longitude=0.0,
            sidereal_time=0.0
        )
        assert horizontal_pos.altitude == pytest.approx(0.0, abs=1e-6)

    def test_geographic_to_geocentric(self, transformer):
        """Test conversion from geographic to geocentric coordinates"""
        # Test at equator
        geographic_pos = Position(0.0, 0.0, 0.0, CoordinateSystem.GEOGRAPHIC)
        geocentric_pos = transformer.geographic_to_geocentric(geographic_pos)
        assert isinstance(geocentric_pos, Position)
        assert geocentric_pos.system == CoordinateSystem.GEOCENTRIC
        assert geocentric_pos.latitude == pytest.approx(0.0, abs=1e-6)

        # Test at poles
        geographic_pos = Position(0.0, 90.0, 0.0, CoordinateSystem.GEOGRAPHIC)
        geocentric_pos = transformer.geographic_to_geocentric(geographic_pos)
        assert geocentric_pos.latitude == pytest.approx(90.0, abs=1e-6)

        # Test at mid-latitudes
        geographic_pos = Position(0.0, 45.0, 0.0, CoordinateSystem.GEOGRAPHIC)
        geocentric_pos = transformer.geographic_to_geocentric(geographic_pos)
        assert geocentric_pos.latitude == pytest.approx(45.0, abs=1e-6)

    def test_coordinate_roundtrip(self, transformer):
        """Test roundtrip conversions between coordinate systems"""
        # Test ecliptic to equatorial and back
        original_pos = Position(45.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(original_pos)
        back_to_ecliptic = transformer.equatorial_to_ecliptic(equatorial_pos)
        assert back_to_ecliptic.longitude == pytest.approx(original_pos.longitude, abs=1e-6)
        assert back_to_ecliptic.latitude == pytest.approx(original_pos.latitude, abs=1e-6)

        # Test equatorial to horizontal and back
        original_pos = Position(45.0, 30.0, 1.0, CoordinateSystem.EQUATORIAL)
        horizontal_pos = transformer.equatorial_to_horizontal(
            original_pos,
            latitude=0.0,
            longitude=0.0,
            sidereal_time=0.0
        )
        back_to_equatorial = transformer.horizontal_to_equatorial(
            horizontal_pos,
            latitude=0.0,
            longitude=0.0,
            sidereal_time=0.0
        )
        assert back_to_equatorial.longitude == pytest.approx(original_pos.longitude, abs=1e-6)
        assert back_to_equatorial.latitude == pytest.approx(original_pos.latitude, abs=1e-6)

    def test_precession_correction(self, transformer, test_date):
        """Test precession correction in coordinate transformations"""
        # Test precession over long time periods
        ecliptic_pos = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos1 = transformer.ecliptic_to_equatorial(ecliptic_pos, date=test_date)
        equatorial_pos2 = transformer.ecliptic_to_equatorial(
            ecliptic_pos,
            date=datetime(2100, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        )
        assert equatorial_pos1.longitude != equatorial_pos2.longitude
        assert equatorial_pos1.latitude != equatorial_pos2.latitude

    def test_edge_cases(self, transformer):
        """Test edge cases in coordinate transformations"""
        # Test invalid coordinate system
        with pytest.raises(ValueError):
            transformer.ecliptic_to_equatorial(
                Position(0.0, 0.0, 1.0, "INVALID_SYSTEM")
            )

        # Test invalid coordinates
        with pytest.raises(ValueError):
            transformer.ecliptic_to_equatorial(
                Position(361.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
            )

        # Test missing required parameters
        with pytest.raises(ValueError):
            transformer.equatorial_to_horizontal(
                Position(0.0, 0.0, 1.0, CoordinateSystem.EQUATORIAL),
                latitude=None,
                longitude=0.0,
                sidereal_time=0.0
            )

    def test_precision_limits(self, transformer):
        """Test precision limits of coordinate transformations"""
        # Test very small angles
        ecliptic_pos = Position(0.000001, 0.000001, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(ecliptic_pos)
        assert isinstance(equatorial_pos, Position)
        assert not math.isnan(equatorial_pos.longitude)
        assert not math.isnan(equatorial_pos.latitude)

        # Test very large angles
        ecliptic_pos = Position(359.999999, 89.999999, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(ecliptic_pos)
        assert isinstance(equatorial_pos, Position)
        assert not math.isnan(equatorial_pos.longitude)
        assert not math.isnan(equatorial_pos.latitude)

    def test_coordinate_system_validation(self, transformer):
        """Test validation of coordinate system conversions"""
        # Test valid conversion path
        ecliptic_pos = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(ecliptic_pos)
        assert equatorial_pos.system == CoordinateSystem.EQUATORIAL

        # Test invalid conversion path
        with pytest.raises(ValueError):
            transformer.ecliptic_to_equatorial(
                Position(0.0, 0.0, 1.0, CoordinateSystem.HORIZONTAL)
            )

    def test_coordinate_normalization(self, transformer):
        """Test normalization of coordinates after transformation"""
        # Test longitude normalization
        ecliptic_pos = Position(370.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(ecliptic_pos)
        assert 0 <= equatorial_pos.longitude < 360

        # Test latitude normalization
        ecliptic_pos = Position(0.0, 95.0, 1.0, CoordinateSystem.ECLIPTIC)
        equatorial_pos = transformer.ecliptic_to_equatorial(ecliptic_pos)
        assert -90 <= equatorial_pos.latitude <= 90 