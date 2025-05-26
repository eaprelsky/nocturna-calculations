import pytest
from datetime import datetime
import pytz
from nocturna_calculations.calculations.aspect_calculations import AspectCalculator
from nocturna_calculations.calculations.constants import AspectType, Planet
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem
from nocturna_calculations.calculations.chart import Chart

class TestAspectCalculations:
    @pytest.fixture
    def test_date(self):
        return datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)

    @pytest.fixture
    def test_location(self):
        return Position(0.0, 51.5, 0.0, CoordinateSystem.GEOGRAPHIC)  # London coordinates

    @pytest.fixture
    def test_chart(self, test_date, test_location):
        return Chart(date=test_date, location=test_location)

    @pytest.fixture
    def calculator(self):
        return AspectCalculator()

    def test_major_aspects(self, calculator, test_chart):
        """Test calculation of major aspects"""
        # Test conjunction
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(1.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.CONJUNCTION for aspect in aspects)

        # Test opposition
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(180.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.OPPOSITION for aspect in aspects)

        # Test trine
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(120.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.TRINE for aspect in aspects)

        # Test square
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(90.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.SQUARE for aspect in aspects)

        # Test sextile
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(60.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.SEXTILE for aspect in aspects)

    def test_minor_aspects(self, calculator):
        """Test calculation of minor aspects"""
        # Test quincunx
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(150.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.QUINCUNX for aspect in aspects)

        # Test semi-sextile
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(30.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.SEMI_SEXTILE for aspect in aspects)

        # Test semi-square
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(45.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.SEMI_SQUARE for aspect in aspects)

        # Test sesquisquare
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(135.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.SESQUISQUARE for aspect in aspects)

    def test_custom_orb_settings(self, calculator):
        """Test aspect calculations with custom orb settings"""
        # Test with wider orb
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(8.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2, orbs={AspectType.CONJUNCTION: 10.0})
        assert any(aspect.type == AspectType.CONJUNCTION for aspect in aspects)

        # Test with narrower orb
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(8.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2, orbs={AspectType.CONJUNCTION: 5.0})
        assert not any(aspect.type == AspectType.CONJUNCTION for aspect in aspects)

    def test_aspect_patterns(self, calculator):
        """Test detection of aspect patterns"""
        # Test T-square
        positions = [
            Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),    # First point
            Position(90.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),   # Second point
            Position(180.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)   # Third point
        ]
        patterns = calculator.detect_patterns(positions)
        assert any(pattern.name == "T-Square" for pattern in patterns)

        # Test Grand Trine
        positions = [
            Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),     # First point
            Position(120.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),   # Second point
            Position(240.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)    # Third point
        ]
        patterns = calculator.detect_patterns(positions)
        assert any(pattern.name == "Grand Trine" for pattern in patterns)

        # Test Yod
        positions = [
            Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),     # First point
            Position(150.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),   # Second point
            Position(300.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)    # Third point
        ]
        patterns = calculator.detect_patterns(positions)
        assert any(pattern.name == "Yod" for pattern in patterns)

    def test_aspect_strength_calculation(self, calculator):
        """Test calculation of aspect strength"""
        # Test exact aspect
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(120.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        trine_aspect = next(aspect for aspect in aspects if aspect.type == AspectType.TRINE)
        assert trine_aspect.strength == pytest.approx(1.0)

        # Test aspect with orb
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(121.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        trine_aspect = next(aspect for aspect in aspects if aspect.type == AspectType.TRINE)
        assert 0.0 < trine_aspect.strength < 1.0

    def test_multiple_aspects_between_points(self, calculator):
        """Test detection of multiple aspects between the same points"""
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(60.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert len(aspects) > 1
        assert any(aspect.type == AspectType.SEXTILE for aspect in aspects)
        assert any(aspect.type == AspectType.SEMI_SEXTILE for aspect in aspects)

    def test_aspect_filtering(self, calculator):
        """Test filtering of aspects by type and orb"""
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(8.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        
        # Test filtering by aspect type
        aspects = calculator.calculate_aspects(
            pos1, 
            pos2,
            aspect_types=[AspectType.CONJUNCTION]
        )
        assert all(aspect.type == AspectType.CONJUNCTION for aspect in aspects)

        # Test filtering by orb
        aspects = calculator.calculate_aspects(
            pos1,
            pos2,
            max_orb=5.0
        )
        assert all(aspect.orb <= 5.0 for aspect in aspects)

    def test_aspect_calculation_with_latitude(self, calculator):
        """Test aspect calculations with different latitudes"""
        # Test with same longitude but different latitudes
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(0.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.CONJUNCTION for aspect in aspects)

        # Test with different longitudes and latitudes
        pos1 = Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)
        pos2 = Position(120.0, 30.0, 1.0, CoordinateSystem.ECLIPTIC)
        aspects = calculator.calculate_aspects(pos1, pos2)
        assert any(aspect.type == AspectType.TRINE for aspect in aspects) 