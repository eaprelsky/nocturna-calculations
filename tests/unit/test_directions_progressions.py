import pytest
from datetime import datetime, timedelta
import pytz
from nocturna_calculations.calculations.directions import DirectionCalculator
from nocturna_calculations.calculations.progressions import ProgressionCalculator
from nocturna_calculations.calculations.constants import DirectionType, ProgressionType, Planet
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem
from nocturna_calculations.calculations.chart import Chart

class TestDirectionsProgressions:
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
    def direction_calculator(self):
        return DirectionCalculator()

    @pytest.fixture
    def progression_calculator(self):
        return ProgressionCalculator()

    def test_primary_directions(self, direction_calculator, test_chart):
        """Test primary directions calculations"""
        # Test solar arc direction
        result = direction_calculator.calculate_primary_direction(
            test_chart,
            direction_type=DirectionType.SOLAR_ARC,
            age=30
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

        # Test key direction
        result = direction_calculator.calculate_primary_direction(
            test_chart,
            direction_type=DirectionType.KEY,
            age=30
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

        # Test custom promissor
        result = direction_calculator.calculate_primary_direction(
            test_chart,
            direction_type=DirectionType.CUSTOM,
            age=30,
            promissor=Planet.MARS
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

    def test_secondary_progressions(self, progression_calculator, test_chart):
        """Test secondary progressions calculations"""
        # Test day-for-year progression
        result = progression_calculator.calculate_secondary_progression(
            test_chart,
            age=30
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

        # Test month-for-year progression
        result = progression_calculator.calculate_secondary_progression(
            test_chart,
            age=30,
            progression_type=ProgressionType.MONTH_FOR_YEAR
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

    def test_solar_arc_directions(self, direction_calculator, test_chart):
        """Test solar arc directions calculations"""
        # Test basic solar arc
        result = direction_calculator.calculate_solar_arc(
            test_chart,
            age=30
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

        # Test solar arc with custom key
        result = direction_calculator.calculate_solar_arc(
            test_chart,
            age=30,
            key=Planet.MARS
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

    def test_profections(self, progression_calculator, test_chart):
        """Test profections calculations"""
        # Test annual profection
        result = progression_calculator.calculate_profection(
            test_chart,
            age=30
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

        # Test monthly profection
        result = progression_calculator.calculate_profection(
            test_chart,
            age=30,
            period_type="monthly"
        )
        assert result is not None
        assert isinstance(result, dict)
        assert all(isinstance(pos, Position) for pos in result.values())

    def test_direction_precision(self, direction_calculator, test_chart):
        """Test precision of direction calculations"""
        # Test precision of solar arc direction
        result1 = direction_calculator.calculate_solar_arc(test_chart, age=30)
        result2 = direction_calculator.calculate_solar_arc(test_chart, age=30)
        assert result1 == result2  # Same input should give same output

        # Test precision with different ages
        result1 = direction_calculator.calculate_solar_arc(test_chart, age=30)
        result2 = direction_calculator.calculate_solar_arc(test_chart, age=31)
        assert result1 != result2  # Different ages should give different results

    def test_progression_precision(self, progression_calculator, test_chart):
        """Test precision of progression calculations"""
        # Test precision of secondary progression
        result1 = progression_calculator.calculate_secondary_progression(test_chart, age=30)
        result2 = progression_calculator.calculate_secondary_progression(test_chart, age=30)
        assert result1 == result2  # Same input should give same output

        # Test precision with different progression types
        result1 = progression_calculator.calculate_secondary_progression(
            test_chart,
            age=30,
            progression_type=ProgressionType.DAY_FOR_YEAR
        )
        result2 = progression_calculator.calculate_secondary_progression(
            test_chart,
            age=30,
            progression_type=ProgressionType.MONTH_FOR_YEAR
        )
        assert result1 != result2  # Different progression types should give different results

    def test_edge_cases(self, direction_calculator, progression_calculator, test_chart):
        """Test edge cases in directions and progressions"""
        # Test very young age
        result = direction_calculator.calculate_solar_arc(test_chart, age=0)
        assert result is not None
        assert isinstance(result, dict)

        # Test very old age
        result = direction_calculator.calculate_solar_arc(test_chart, age=100)
        assert result is not None
        assert isinstance(result, dict)

        # Test negative age
        with pytest.raises(ValueError):
            direction_calculator.calculate_solar_arc(test_chart, age=-1)

        # Test invalid progression type
        with pytest.raises(ValueError):
            progression_calculator.calculate_secondary_progression(
                test_chart,
                age=30,
                progression_type="invalid_type"
            )

    def test_direction_combinations(self, direction_calculator, test_chart):
        """Test combinations of different direction types"""
        # Test solar arc with key direction
        solar_arc = direction_calculator.calculate_solar_arc(test_chart, age=30)
        key_dir = direction_calculator.calculate_primary_direction(
            test_chart,
            direction_type=DirectionType.KEY,
            age=30
        )
        assert solar_arc is not None and key_dir is not None
        assert isinstance(solar_arc, dict) and isinstance(key_dir, dict)

        # Test custom promissor with solar arc
        custom_dir = direction_calculator.calculate_primary_direction(
            test_chart,
            direction_type=DirectionType.CUSTOM,
            age=30,
            promissor=Planet.MARS
        )
        assert custom_dir is not None
        assert isinstance(custom_dir, dict)

    def test_progression_combinations(self, progression_calculator, test_chart):
        """Test combinations of different progression types"""
        # Test secondary progression with profection
        sec_prog = progression_calculator.calculate_secondary_progression(test_chart, age=30)
        profection = progression_calculator.calculate_profection(test_chart, age=30)
        assert sec_prog is not None and profection is not None
        assert isinstance(sec_prog, dict) and isinstance(profection, dict)

        # Test different progression periods
        monthly = progression_calculator.calculate_profection(test_chart, age=30, period_type="monthly")
        annual = progression_calculator.calculate_profection(test_chart, age=30, period_type="annual")
        assert monthly is not None and annual is not None
        assert isinstance(monthly, dict) and isinstance(annual, dict)
        assert monthly != annual  # Different periods should give different results 