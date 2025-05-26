import pytest
from datetime import datetime, timedelta
import pytz
from nocturna_calculations.calculations.rectification import HarmonicRectification
from nocturna_calculations.calculations.constants import HarmonicType, RectificationMethod
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem
from nocturna_calculations.calculations.chart import Chart

class TestHarmonicRectification:
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
    def rectification_calculator(self):
        return HarmonicRectification()

    @pytest.fixture
    def sample_harmonics(self):
        return [
            {
                "type": HarmonicType.AGE,
                "harmonic_number": 12,
                "points": [
                    Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),    # Sun
                    Position(30.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),   # Moon
                    Position(60.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)    # Mercury
                ],
                "strength": 0.85
            },
            {
                "type": HarmonicType.EVENT,
                "harmonic_number": 8,
                "points": [
                    Position(45.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),   # Venus
                    Position(90.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),   # Mars
                    Position(135.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)   # Jupiter
                ],
                "strength": 0.8
            }
        ]

    def test_harmonic_analysis(self, rectification_calculator, test_chart, sample_harmonics):
        """Test harmonic analysis calculations"""
        # Test age harmonic analysis
        harmonic = sample_harmonics[0]
        result = rectification_calculator.analyze_harmonic(
            test_chart,
            harmonic["points"],
            harmonic_number=harmonic["harmonic_number"]
        )
        assert result is not None
        assert "harmonic_strength" in result
        assert "resonance_points" in result
        assert 0 <= result["harmonic_strength"] <= 1

        # Test event harmonic analysis
        harmonic = sample_harmonics[1]
        result = rectification_calculator.analyze_harmonic(
            test_chart,
            harmonic["points"],
            harmonic_number=harmonic["harmonic_number"]
        )
        assert result is not None
        assert "harmonic_strength" in result
        assert "resonance_points" in result
        assert 0 <= result["harmonic_strength"] <= 1

    def test_age_harmonics(self, rectification_calculator, test_chart, sample_harmonics):
        """Test age-based harmonic calculations"""
        # Test single age harmonic
        harmonic = sample_harmonics[0]
        result = rectification_calculator.calculate_age_harmonic(
            test_chart,
            harmonic["harmonic_number"],
            harmonic["points"]
        )
        assert result is not None
        assert "harmonic_age" in result
        assert "resonance_strength" in result
        assert 0 <= result["resonance_strength"] <= 1

        # Test multiple age harmonics
        result = rectification_calculator.calculate_age_harmonics(
            test_chart,
            [12, 24, 36],  # Common harmonic numbers
            harmonic["points"]
        )
        assert result is not None
        assert "harmonic_ages" in result
        assert "combined_strength" in result
        assert len(result["harmonic_ages"]) == 3

    def test_event_harmonics(self, rectification_calculator, test_chart, sample_harmonics):
        """Test event-based harmonic calculations"""
        # Test single event harmonic
        harmonic = sample_harmonics[1]
        result = rectification_calculator.calculate_event_harmonic(
            test_chart,
            harmonic["harmonic_number"],
            harmonic["points"]
        )
        assert result is not None
        assert "event_timing" in result
        assert "harmonic_strength" in result
        assert 0 <= result["harmonic_strength"] <= 1

        # Test multiple event harmonics
        result = rectification_calculator.calculate_event_harmonics(
            test_chart,
            [8, 16, 24],  # Common harmonic numbers
            harmonic["points"]
        )
        assert result is not None
        assert "event_timings" in result
        assert "combined_strength" in result
        assert len(result["event_timings"]) == 3

    def test_harmonic_rectification(self, rectification_calculator, test_chart, sample_harmonics):
        """Test harmonic-based rectification"""
        # Test single harmonic rectification
        harmonic = sample_harmonics[0]
        result = rectification_calculator.rectify_by_harmonic(
            test_chart,
            harmonic,
            method=RectificationMethod.HARMONIC
        )
        assert result is not None
        assert "rectified_time" in result
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

        # Test multiple harmonics rectification
        result = rectification_calculator.rectify_by_harmonics(
            test_chart,
            sample_harmonics,
            method=RectificationMethod.HARMONIC
        )
        assert result is not None
        assert "rectified_time" in result
        assert "confidence" in result
        assert "harmonic_matches" in result

    def test_harmonic_combinations(self, rectification_calculator, test_chart, sample_harmonics):
        """Test combinations of different harmonics"""
        # Test complementary harmonics
        result = rectification_calculator.analyze_harmonic_combinations(
            test_chart,
            sample_harmonics
        )
        assert result is not None
        assert "complementary_harmonics" in result
        assert "conflicting_harmonics" in result

        # Test harmonic interactions
        result = rectification_calculator.analyze_harmonic_interactions(
            test_chart,
            sample_harmonics
        )
        assert result is not None
        assert "interactions" in result
        assert "strength_modifications" in result

    def test_edge_cases(self, rectification_calculator, test_chart):
        """Test edge cases in harmonic rectification"""
        # Test empty harmonics list
        with pytest.raises(ValueError):
            rectification_calculator.rectify_by_harmonics(
                test_chart,
                [],
                method=RectificationMethod.HARMONIC
            )

        # Test invalid harmonic number
        with pytest.raises(ValueError):
            rectification_calculator.analyze_harmonic(
                test_chart,
                [Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)],
                harmonic_number=0
            )

        # Test insufficient points
        with pytest.raises(ValueError):
            rectification_calculator.analyze_harmonic(
                test_chart,
                [Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)],
                harmonic_number=12
            )

    def test_harmonic_precision(self, rectification_calculator, test_chart, sample_harmonics):
        """Test precision of harmonic calculations"""
        # Test harmonic analysis precision
        harmonic = sample_harmonics[0]
        result1 = rectification_calculator.analyze_harmonic(
            test_chart,
            harmonic["points"],
            harmonic_number=harmonic["harmonic_number"]
        )
        result2 = rectification_calculator.analyze_harmonic(
            test_chart,
            harmonic["points"],
            harmonic_number=harmonic["harmonic_number"]
        )
        assert result1["harmonic_strength"] == result2["harmonic_strength"]

        # Test rectification precision
        result1 = rectification_calculator.rectify_by_harmonic(
            test_chart,
            harmonic,
            method=RectificationMethod.HARMONIC
        )
        result2 = rectification_calculator.rectify_by_harmonic(
            test_chart,
            harmonic,
            method=RectificationMethod.HARMONIC
        )
        assert result1["rectified_time"] == result2["rectified_time"]
        assert result1["confidence"] == result2["confidence"]

    def test_harmonic_validation(self, rectification_calculator, test_chart, sample_harmonics):
        """Test validation of harmonic rectification results"""
        # Test result consistency
        harmonic = sample_harmonics[0]
        result = rectification_calculator.rectify_by_harmonic(
            test_chart,
            harmonic,
            method=RectificationMethod.HARMONIC
        )
        validation = rectification_calculator.validate_rectification(
            test_chart,
            result["rectified_time"],
            harmonic
        )
        assert validation is not None
        assert "is_valid" in validation
        assert "validation_score" in validation
        assert 0 <= validation["validation_score"] <= 1 