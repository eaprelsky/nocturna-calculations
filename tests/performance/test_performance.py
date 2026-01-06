"""
Performance tests for chart calculations
"""
import pytest
import psutil
import os
from datetime import datetime, time
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import Config

# --- Performance Test Setup ---

@pytest.fixture
def basic_chart():
    """Create a basic chart for testing"""
    return Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        timezone="Europe/Moscow"
    )

# --- Calculation Speed Tests ---

def test_planetary_positions_calculation_speed(basic_chart, benchmark):
    """Test speed of planetary positions calculation"""
    positions = benchmark(basic_chart.calculate_planetary_positions)
    assert positions is not None

def test_aspects_calculation_speed(basic_chart, benchmark):
    """Test speed of aspects calculation"""
    aspects = benchmark(basic_chart.calculate_aspects)
    assert aspects is not None

def test_houses_calculation_speed(basic_chart, benchmark):
    """Test speed of houses calculation"""
    houses = benchmark(basic_chart.calculate_houses)
    assert houses is not None

def test_fixed_stars_calculation_speed(basic_chart, benchmark):
    """Test speed of fixed stars calculation"""
    stars = benchmark(basic_chart.calculate_fixed_stars)
    assert stars is not None

# --- Memory Usage Tests ---

def test_memory_usage_planetary_positions(basic_chart):
    """Test memory usage during planetary positions calculation"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    positions = basic_chart.calculate_planetary_positions()
    
    final_memory = process.memory_info().rss
    memory_used = final_memory - initial_memory
    
    assert memory_used < 50 * 1024 * 1024  # Should use less than 50MB
    assert positions is not None

def test_memory_usage_aspects(basic_chart):
    """Test memory usage during aspects calculation"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    aspects = basic_chart.calculate_aspects()
    
    final_memory = process.memory_info().rss
    memory_used = final_memory - initial_memory
    
    assert memory_used < 50 * 1024 * 1024  # Should use less than 50MB
    assert aspects is not None

# --- Concurrent Calculation Tests ---

def test_concurrent_planetary_positions(benchmark):
    """Test concurrent planetary positions calculations"""
    charts = [
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        ) for _ in range(10)
    ]
    
    def calculate_all():
        return [chart.calculate_planetary_positions() for chart in charts]
    
    positions = benchmark(calculate_all)
    assert all(pos is not None for pos in positions)

def test_concurrent_aspects(benchmark):
    """Test concurrent aspects calculations"""
    charts = [
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=55.7558,
            longitude=37.6173
        ) for _ in range(10)
    ]
    
    def calculate_all():
        return [chart.calculate_aspects() for chart in charts]
    
    aspects = benchmark(calculate_all)
    assert all(asp is not None for asp in aspects)

# --- Large Dataset Tests ---

def test_large_fixed_stars_dataset(benchmark):
    """Test calculation with large fixed stars dataset"""
    config = Config(fixed_stars=["*"])  # All fixed stars
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    stars = benchmark(chart.calculate_fixed_stars)
    assert len(stars) > 0

def test_large_aspects_dataset(benchmark):
    """Test calculation with large aspects dataset"""
    config = Config(orbs={"conjunction": 15.0})  # Large orb for more aspects
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    
    aspects = benchmark(chart.calculate_aspects)
    assert len(aspects) > 0

# --- Resource Cleanup Tests ---

def test_memory_cleanup_after_calculation(basic_chart):
    """Test memory cleanup after calculation"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform calculations
    basic_chart.calculate_planetary_positions()
    basic_chart.calculate_aspects()
    basic_chart.calculate_houses()
    
    # Force garbage collection
    import gc
    gc.collect()
    
    final_memory = process.memory_info().rss
    memory_difference = abs(final_memory - initial_memory)
    
    assert memory_difference < 10 * 1024 * 1024  # Should clean up to within 10MB of initial

def test_file_handle_cleanup(basic_chart):
    """Test file handle cleanup after calculation"""
    import psutil
    process = psutil.Process(os.getpid())
    initial_handles = process.num_handles()
    
    # Perform calculations
    basic_chart.calculate_planetary_positions()
    basic_chart.calculate_aspects()
    
    final_handles = process.num_handles()
    handle_difference = final_handles - initial_handles
    
    assert handle_difference <= 0  # Should not leak file handles 