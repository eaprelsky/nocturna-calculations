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

    @pytest.fixture
    def valid_aspect(self):
        return Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=2.5,
            aspect_type="trine",
            applying=True
        )

    def test_aspect_initialization_all_parameters(self, valid_aspect):
        """Test basic aspect initialization with all parameters"""
        assert valid_aspect.planet1 == "Sun"
        assert valid_aspect.planet2 == "Moon"
        assert valid_aspect.angle == 120.0
        assert valid_aspect.orb == 2.5
        assert valid_aspect.aspect_type == "trine"
        assert valid_aspect.applying is True

    def test_aspect_default_values(self):
        """Test aspect initialization with default values"""
        aspect = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=2.5,
            aspect_type="trine"
        )
        assert aspect.applying is None

    def test_aspect_angle_validation(self):
        """Test angle validation"""
        # Test valid angle
        aspect = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=360.0,
            orb=2.5,
            aspect_type="conjunction"
        )
        assert aspect.angle == 360.0

        # Test negative angle
        aspect = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=-45.0,
            orb=2.5,
            aspect_type="square"
        )
        assert aspect.angle == 315.0  # -45 + 360 = 315

        # Test invalid angle
        with pytest.raises(ValueError):
            Aspect(
                planet1="Sun",
                planet2="Moon",
                angle=361.0,
                orb=2.5,
                aspect_type="conjunction"
            )

    def test_aspect_orb_validation(self):
        """Test orb validation"""
        # Test valid orb
        aspect = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=10.0,
            aspect_type="trine"
        )
        assert aspect.orb == 10.0

        # Test zero orb
        aspect = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=0.0,
            aspect_type="trine"
        )
        assert aspect.orb == 0.0

        # Test negative orb
        with pytest.raises(ValueError):
            Aspect(
                planet1="Sun",
                planet2="Moon",
                angle=120.0,
                orb=-1.0,
                aspect_type="trine"
            )

    def test_aspect_type_validation(self):
        """Test aspect type validation"""
        valid_types = ["conjunction", "opposition", "trine", "square", "sextile"]
        
        for aspect_type in valid_types:
            aspect = Aspect(
                planet1="Sun",
                planet2="Moon",
                angle=120.0,
                orb=2.5,
                aspect_type=aspect_type
            )
            assert aspect.aspect_type == aspect_type

        # Test invalid aspect type
        with pytest.raises(ValueError):
            Aspect(
                planet1="Sun",
                planet2="Moon",
                angle=120.0,
                orb=2.5,
                aspect_type="invalid_type"
            )

    def test_aspect_immutability(self, valid_aspect):
        """Test that aspect attributes are immutable"""
        with pytest.raises(AttributeError):
            valid_aspect.planet1 = "Mars"

        with pytest.raises(AttributeError):
            valid_aspect.planet2 = "Venus"

        with pytest.raises(AttributeError):
            valid_aspect.angle = 90.0

        with pytest.raises(AttributeError):
            valid_aspect.orb = 1.0

        with pytest.raises(AttributeError):
            valid_aspect.aspect_type = "square"

        with pytest.raises(AttributeError):
            valid_aspect.applying = False

    def test_aspect_equality(self):
        """Test aspect equality comparison"""
        aspect1 = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=2.5,
            aspect_type="trine",
            applying=True
        )
        aspect2 = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=2.5,
            aspect_type="trine",
            applying=True
        )
        aspect3 = Aspect(
            planet1="Sun",
            planet2="Mars",
            angle=120.0,
            orb=2.5,
            aspect_type="trine",
            applying=True
        )

        assert aspect1 == aspect2
        assert aspect1 != aspect3
        assert aspect2 != aspect3

    def test_aspect_string_representation(self, valid_aspect):
        """Test aspect string representation"""
        expected_str = "Aspect(Sun-Moon trine, angle=120.0°, orb=2.5°, applying=True)"
        assert str(valid_aspect) == expected_str

    def test_aspect_partile(self):
        """Test partile aspect detection"""
        # Partile aspect (orb = 0)
        partile = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=0.0,
            aspect_type="trine"
        )
        assert partile.is_partile() is True

        # Non-partile aspect
        non_partile = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=2.5,
            aspect_type="trine"
        )
        assert non_partile.is_partile() is False

    def test_aspect_exact(self):
        """Test exact aspect detection"""
        # Exact aspect (orb <= 0.1)
        exact = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=0.1,
            aspect_type="trine"
        )
        assert exact.is_exact() is True

        # Non-exact aspect
        non_exact = Aspect(
            planet1="Sun",
            planet2="Moon",
            angle=120.0,
            orb=2.5,
            aspect_type="trine"
        )
        assert non_exact.is_exact() is False 