import pytest
from datetime import datetime
from typing import Dict, Any
from nocturna_calculations.core.calculator import ChartData, ChartCalculator

class TestChartData:
    """Test suite for ChartData model"""
    
    def test_chart_data_creation(self):
        """Test creating a ChartData instance with valid data"""
        data = ChartData(
            date="2024-03-20",
            time="12:00:00",
            latitude=51.5074,
            longitude=-0.1278,
            options={"house_system": "Placidus"}
        )
        
        assert data.date == "2024-03-20"
        assert data.time == "12:00:00"
        assert data.latitude == 51.5074
        assert data.longitude == -0.1278
        assert data.options == {"house_system": "Placidus"}
    
    def test_chart_data_optional_options(self):
        """Test creating a ChartData instance without options"""
        data = ChartData(
            date="2024-03-20",
            time="12:00:00",
            latitude=51.5074,
            longitude=-0.1278
        )
        
        assert data.options is None
    
    @pytest.mark.parametrize("invalid_data", [
        {"date": "invalid", "time": "12:00:00", "latitude": 51.5074, "longitude": -0.1278},
        {"date": "2024-03-20", "time": "invalid", "latitude": 51.5074, "longitude": -0.1278},
        {"date": "2024-03-20", "time": "12:00:00", "latitude": "invalid", "longitude": -0.1278},
        {"date": "2024-03-20", "time": "12:00:00", "latitude": 51.5074, "longitude": "invalid"},
    ])
    def test_chart_data_validation(self, invalid_data):
        """Test ChartData validation with invalid data"""
        with pytest.raises(ValueError):
            ChartData(**invalid_data)

class MockAdapter:
    """Mock adapter for testing ChartCalculator"""
    def calculate_positions(self, *args, **kwargs):
        return {"positions": "mock_positions"}
    
    def calculate_aspects(self, *args, **kwargs):
        return {"aspects": "mock_aspects"}

class MockCalculator(ChartCalculator):
    """Mock calculator implementation for testing"""
    def calculate_natal_chart(self, data: ChartData) -> Dict[str, Any]:
        return self.adapter.calculate_positions(data)
    
    def calculate_aspects(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.adapter.calculate_aspects(chart_data)

class TestChartCalculator:
    """Test suite for ChartCalculator class"""
    
    @pytest.fixture
    def calculator(self):
        """Create a calculator instance with mock adapter"""
        return MockCalculator(MockAdapter())
    
    @pytest.fixture
    def chart_data(self):
        """Create test chart data"""
        return ChartData(
            date="2024-03-20",
            time="12:00:00",
            latitude=51.5074,
            longitude=-0.1278
        )
    
    def test_calculator_initialization(self):
        """Test calculator initialization with adapter"""
        adapter = MockAdapter()
        calculator = MockCalculator(adapter)
        assert calculator.adapter == adapter
    
    def test_calculate_natal_chart(self, calculator, chart_data):
        """Test natal chart calculation"""
        result = calculator.calculate_natal_chart(chart_data)
        assert result == {"positions": "mock_positions"}
    
    def test_calculate_aspects(self, calculator):
        """Test aspect calculation"""
        chart_data = {"positions": "mock_positions"}
        result = calculator.calculate_aspects(chart_data)
        assert result == {"aspects": "mock_aspects"}
    
    def test_abstract_methods(self):
        """Test that ChartCalculator cannot be instantiated directly"""
        with pytest.raises(TypeError):
            ChartCalculator(MockAdapter()) 