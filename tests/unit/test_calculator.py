import pytest
from datetime import datetime
from nocturna_calculations.core.calculator import Calculator
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.position import Position
from nocturna_calculations.core.aspect import Aspect

class TestCalculator:
    @pytest.fixture
    def calculator(self):
        """Create a calculator instance for testing."""
        return Calculator()

    @pytest.fixture
    def sample_chart(self):
        """Create a sample chart for testing."""
        return Chart(
            name="Test Chart",
            date=datetime(2000, 1, 1, 12, 0),
            latitude=51.5074,
            longitude=-0.1278
        )

    def test_calculator_initialization(self, calculator):
        """Test calculator initialization."""
        assert calculator is not None
        assert hasattr(calculator, 'calculate_positions')
        assert hasattr(calculator, 'calculate_aspects')

    def test_calculate_positions(self, calculator, sample_chart):
        """Test position calculation."""
        positions = calculator.calculate_positions(sample_chart)
        assert positions is not None
        assert isinstance(positions, list)
        assert all(isinstance(pos, Position) for pos in positions)
        assert len(positions) > 0

    def test_calculate_aspects(self, calculator, sample_chart):
        """Test aspect calculation."""
        aspects = calculator.calculate_aspects(sample_chart)
        assert aspects is not None
        assert isinstance(aspects, list)
        assert all(isinstance(asp, Aspect) for asp in aspects)

    def test_calculate_houses(self, calculator, sample_chart):
        """Test house calculation."""
        houses = calculator.calculate_houses(sample_chart)
        assert houses is not None
        assert isinstance(houses, list)
        assert len(houses) == 12

    def test_calculate_dignities(self, calculator, sample_chart):
        """Test dignity calculation."""
        dignities = calculator.calculate_dignities(sample_chart)
        assert dignities is not None
        assert isinstance(dignities, dict)

    def test_calculate_progressions(self, calculator, sample_chart):
        """Test progression calculation."""
        progressions = calculator.calculate_progressions(sample_chart, years=1)
        assert progressions is not None
        assert isinstance(progressions, dict)

    def test_calculate_directions(self, calculator, sample_chart):
        """Test direction calculation."""
        directions = calculator.calculate_directions(sample_chart, years=1)
        assert directions is not None
        assert isinstance(directions, dict)

    def test_invalid_chart(self, calculator):
        """Test calculator behavior with invalid chart."""
        with pytest.raises(ValueError):
            calculator.calculate_positions(None)

    def test_edge_case_dates(self, calculator):
        """Test calculator with edge case dates."""
        # Test with date before 1900
        old_chart = Chart(
            name="Old Chart",
            date=datetime(1800, 1, 1, 12, 0),
            latitude=51.5074,
            longitude=-0.1278
        )
        positions = calculator.calculate_positions(old_chart)
        assert positions is not None

        # Test with future date
        future_chart = Chart(
            name="Future Chart",
            date=datetime(2100, 1, 1, 12, 0),
            latitude=51.5074,
            longitude=-0.1278
        )
        positions = calculator.calculate_positions(future_chart)
        assert positions is not None

    def test_edge_case_coordinates(self, calculator, sample_chart):
        """Test calculator with edge case coordinates."""
        # Test with coordinates at poles
        polar_chart = Chart(
            name="Polar Chart",
            date=datetime(2000, 1, 1, 12, 0),
            latitude=90.0,
            longitude=0.0
        )
        positions = calculator.calculate_positions(polar_chart)
        assert positions is not None

        # Test with coordinates at equator
        equatorial_chart = Chart(
            name="Equatorial Chart",
            date=datetime(2000, 1, 1, 12, 0),
            latitude=0.0,
            longitude=0.0
        )
        positions = calculator.calculate_positions(equatorial_chart)
        assert positions is not None 