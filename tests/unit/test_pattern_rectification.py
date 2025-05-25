import pytest
from datetime import datetime, timedelta
import pytz
from nocturna.calculations.rectification import PatternRectification
from nocturna.calculations.constants import PatternType, RectificationMethod
from nocturna.calculations.position import Position
from nocturna.calculations.constants import CoordinateSystem
from nocturna.calculations.chart import Chart

class TestPatternRectification:
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
        return PatternRectification()

    @pytest.fixture
    def sample_patterns(self):
        return [
            {
                "type": PatternType.T_SQUARE,
                "points": [
                    Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),  # Sun
                    Position(180.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),  # Moon
                    Position(90.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)   # Mars
                ],
                "strength": 0.9
            },
            {
                "type": PatternType.GRAND_TRINE,
                "points": [
                    Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC),   # Sun
                    Position(120.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC), # Jupiter
                    Position(240.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)  # Saturn
                ],
                "strength": 0.85
            }
        ]

    def test_pattern_recognition(self, rectification_calculator, test_chart, sample_patterns):
        """Test recognition of astrological patterns"""
        # Test T-square recognition
        pattern = sample_patterns[0]
        result = rectification_calculator.recognize_pattern(
            test_chart,
            pattern["points"],
            pattern_type=PatternType.T_SQUARE
        )
        assert result is not None
        assert result["type"] == PatternType.T_SQUARE
        assert "strength" in result
        assert 0 <= result["strength"] <= 1

        # Test Grand Trine recognition
        pattern = sample_patterns[1]
        result = rectification_calculator.recognize_pattern(
            test_chart,
            pattern["points"],
            pattern_type=PatternType.GRAND_TRINE
        )
        assert result is not None
        assert result["type"] == PatternType.GRAND_TRINE
        assert "strength" in result
        assert 0 <= result["strength"] <= 1

    def test_statistical_analysis(self, rectification_calculator, test_chart, sample_patterns):
        """Test statistical analysis of patterns"""
        # Test pattern frequency analysis
        result = rectification_calculator.analyze_pattern_frequency(
            test_chart,
            sample_patterns,
            time_window=timedelta(days=365)
        )
        assert result is not None
        assert "pattern_frequencies" in result
        assert "confidence" in result

        # Test pattern strength distribution
        result = rectification_calculator.analyze_pattern_strength(
            test_chart,
            sample_patterns
        )
        assert result is not None
        assert "strength_distribution" in result
        assert "average_strength" in result

    def test_confidence_scoring(self, rectification_calculator, test_chart, sample_patterns):
        """Test confidence scoring for pattern-based rectification"""
        # Test single pattern confidence
        pattern = sample_patterns[0]
        result = rectification_calculator.calculate_pattern_confidence(
            test_chart,
            pattern
        )
        assert result is not None
        assert 0 <= result <= 1

        # Test multiple patterns confidence
        result = rectification_calculator.calculate_combined_confidence(
            test_chart,
            sample_patterns
        )
        assert result is not None
        assert "overall_confidence" in result
        assert "pattern_confidences" in result
        assert 0 <= result["overall_confidence"] <= 1

    def test_pattern_rectification(self, rectification_calculator, test_chart, sample_patterns):
        """Test pattern-based rectification"""
        # Test single pattern rectification
        pattern = sample_patterns[0]
        result = rectification_calculator.rectify_by_pattern(
            test_chart,
            pattern,
            method=RectificationMethod.PATTERN_BASED
        )
        assert result is not None
        assert "rectified_time" in result
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

        # Test multiple patterns rectification
        result = rectification_calculator.rectify_by_patterns(
            test_chart,
            sample_patterns,
            method=RectificationMethod.PATTERN_BASED
        )
        assert result is not None
        assert "rectified_time" in result
        assert "confidence" in result
        assert "pattern_matches" in result

    def test_pattern_combinations(self, rectification_calculator, test_chart, sample_patterns):
        """Test combinations of different patterns"""
        # Test complementary patterns
        result = rectification_calculator.analyze_pattern_combinations(
            test_chart,
            sample_patterns
        )
        assert result is not None
        assert "complementary_patterns" in result
        assert "conflicting_patterns" in result

        # Test pattern interactions
        result = rectification_calculator.analyze_pattern_interactions(
            test_chart,
            sample_patterns
        )
        assert result is not None
        assert "interactions" in result
        assert "strength_modifications" in result

    def test_edge_cases(self, rectification_calculator, test_chart):
        """Test edge cases in pattern-based rectification"""
        # Test empty patterns list
        with pytest.raises(ValueError):
            rectification_calculator.rectify_by_patterns(
                test_chart,
                [],
                method=RectificationMethod.PATTERN_BASED
            )

        # Test invalid pattern type
        with pytest.raises(ValueError):
            rectification_calculator.recognize_pattern(
                test_chart,
                [Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)],
                pattern_type="INVALID_PATTERN"
            )

        # Test insufficient points
        with pytest.raises(ValueError):
            rectification_calculator.recognize_pattern(
                test_chart,
                [Position(0.0, 0.0, 1.0, CoordinateSystem.ECLIPTIC)],
                pattern_type=PatternType.T_SQUARE
            )

    def test_pattern_precision(self, rectification_calculator, test_chart, sample_patterns):
        """Test precision of pattern recognition and rectification"""
        # Test pattern recognition precision
        pattern = sample_patterns[0]
        result1 = rectification_calculator.recognize_pattern(
            test_chart,
            pattern["points"],
            pattern_type=PatternType.T_SQUARE
        )
        result2 = rectification_calculator.recognize_pattern(
            test_chart,
            pattern["points"],
            pattern_type=PatternType.T_SQUARE
        )
        assert result1["strength"] == result2["strength"]

        # Test rectification precision
        result1 = rectification_calculator.rectify_by_pattern(
            test_chart,
            pattern,
            method=RectificationMethod.PATTERN_BASED
        )
        result2 = rectification_calculator.rectify_by_pattern(
            test_chart,
            pattern,
            method=RectificationMethod.PATTERN_BASED
        )
        assert result1["rectified_time"] == result2["rectified_time"]
        assert result1["confidence"] == result2["confidence"]

    def test_pattern_validation(self, rectification_calculator, test_chart, sample_patterns):
        """Test validation of pattern-based rectification results"""
        # Test result consistency
        pattern = sample_patterns[0]
        result = rectification_calculator.rectify_by_pattern(
            test_chart,
            pattern,
            method=RectificationMethod.PATTERN_BASED
        )
        validation = rectification_calculator.validate_rectification(
            test_chart,
            result["rectified_time"],
            pattern
        )
        assert validation is not None
        assert "is_valid" in validation
        assert "validation_score" in validation
        assert 0 <= validation["validation_score"] <= 1 