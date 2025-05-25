import pytest
from nocturna.calculations.aspect import Aspect
from nocturna.calculations.constants import AspectType
from nocturna.calculations.position import Position
from nocturna.calculations.constants import CoordinateSystem

class TestAspect:
    @pytest.fixture
    def valid_positions(self):
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(120.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        return pos1, pos2

    def test_aspect_initialization(self, valid_positions):
        """Test basic aspect initialization with valid parameters"""
        pos1, pos2 = valid_positions
        aspect = Aspect(pos1, pos2, AspectType.TRINE)
        assert aspect.position1 == pos1
        assert aspect.position2 == pos2
        assert aspect.type == AspectType.TRINE
        assert isinstance(aspect.orb, float)

    def test_aspect_detection(self):
        """Test detection of different aspect types"""
        # Test conjunction
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(1.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect.detect(pos1, pos2)
        assert aspect.type == AspectType.CONJUNCTION
        assert aspect.orb == pytest.approx(1.0)

        # Test opposition
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(180.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect.detect(pos1, pos2)
        assert aspect.type == AspectType.OPPOSITION
        assert aspect.orb == pytest.approx(0.0)

        # Test trine
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(120.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect.detect(pos1, pos2)
        assert aspect.type == AspectType.TRINE
        assert aspect.orb == pytest.approx(0.0)

    def test_orb_calculation(self):
        """Test orb calculations for different aspects"""
        # Test exact aspect
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(120.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect(pos1, pos2, AspectType.TRINE)
        assert aspect.orb == pytest.approx(0.0)

        # Test aspect with orb
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(121.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect(pos1, pos2, AspectType.TRINE)
        assert aspect.orb == pytest.approx(1.0)

    def test_applying_separating(self):
        """Test determination of applying/separating aspects"""
        # Test applying aspect
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(119.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect(pos1, pos2, AspectType.TRINE)
        assert aspect.is_applying()

        # Test separating aspect
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(121.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect(pos1, pos2, AspectType.TRINE)
        assert aspect.is_separating()

    def test_aspect_strength(self):
        """Test calculation of aspect strength"""
        # Test exact aspect
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(120.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect(pos1, pos2, AspectType.TRINE)
        assert aspect.strength == pytest.approx(1.0)

        # Test aspect with orb
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(121.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect(pos1, pos2, AspectType.TRINE)
        assert 0.0 < aspect.strength < 1.0

    def test_multiple_aspects(self):
        """Test handling of multiple aspects between positions"""
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(60.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = Aspect.detect_all(pos1, pos2)
        assert len(aspects) > 0
        assert any(aspect.type == AspectType.SEXTILE for aspect in aspects)

    def test_aspect_patterns(self):
        """Test detection of aspect patterns"""
        positions = [
            Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),
            Position(90.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),
            Position(180.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        ]
        patterns = Aspect.detect_patterns(positions)
        assert len(patterns) > 0
        assert any(pattern.name == "T-Square" for pattern in patterns)

    def test_edge_cases(self):
        """Test aspect calculations with edge cases"""
        # Test positions at 0 and 360 degrees
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(360.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect.detect(pos1, pos2)
        assert aspect.type == AspectType.CONJUNCTION
        assert aspect.orb == pytest.approx(0.0)

        # Test positions with same longitude but different latitudes
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(0.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspect = Aspect.detect(pos1, pos2)
        assert aspect.type == AspectType.CONJUNCTION
        assert aspect.orb == pytest.approx(0.0) 