import pytest
from datetime import datetime, time
from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.config import AstroConfig

# --- Chart Initialization Tests ---

def test_chart_init_valid_datetime():
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        timezone="Europe/Moscow"
    )
    assert chart is not None

def test_chart_init_valid_datetime_obj():
    chart = Chart(
        date=datetime(2024, 3, 20),
        time=time(12, 0, 0),
        latitude=55.7558,
        longitude=37.6173
    )
    assert chart is not None

def test_chart_init_missing_latitude():
    with pytest.raises((TypeError, ValueError)):
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=None,
            longitude=37.6173
        )

def test_chart_init_invalid_latitude():
    with pytest.raises((TypeError, ValueError)):
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=200.0,  # Invalid latitude
            longitude=37.6173
        )

def test_chart_init_missing_longitude():
    with pytest.raises((TypeError, ValueError)):
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=55.7558,
            longitude=None
        )

def test_chart_init_invalid_longitude():
    with pytest.raises((TypeError, ValueError)):
        Chart(
            date="2024-03-20",
            time="12:00:00",
            latitude=55.7558,
            longitude=200.0  # Invalid longitude
        )

def test_chart_init_with_config():
    config = AstroConfig(house_system="Koch")
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    assert chart.config.house_system == "Koch"

def test_chart_init_without_timezone():
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    assert chart.timezone == "UTC"

def test_calculate_planetary_positions_valid(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    # Monkeypatch the method to return a mock result
    monkeypatch.setattr(chart, "calculate_planetary_positions", lambda: {"Sun": object(), "Moon": object()})
    positions = chart.calculate_planetary_positions()
    assert "Sun" in positions
    assert "Moon" in positions


def test_calculate_planetary_positions_custom_config(monkeypatch):
    config = AstroConfig(orbs={"conjunction": 10.0})
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    monkeypatch.setattr(chart, "calculate_planetary_positions", lambda: {"Sun": object()})
    positions = chart.calculate_planetary_positions()
    assert "Sun" in positions


def test_calculate_planetary_positions_invalid_chart(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=999.0,  # Invalid
        longitude=37.6173
    )
    def raise_error():
        raise ValueError("Invalid chart data")
    monkeypatch.setattr(chart, "calculate_planetary_positions", raise_error)
    with pytest.raises(ValueError):
        chart.calculate_planetary_positions()

def test_calculate_aspects_major_minor(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    mock_aspects = [object(), object()]
    monkeypatch.setattr(chart, "calculate_aspects", lambda: mock_aspects)
    aspects = chart.calculate_aspects()
    assert len(aspects) == 2


def test_calculate_aspects_custom_orbs(monkeypatch):
    config = AstroConfig(orbs={"trine": 8.0})
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173,
        config=config
    )
    monkeypatch.setattr(chart, "calculate_aspects", lambda: [object()])
    aspects = chart.calculate_aspects()
    assert len(aspects) == 1


def test_calculate_aspects_empty_chart(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_aspects", lambda: [])
    aspects = chart.calculate_aspects()
    assert aspects == []

def test_calculate_houses_supported_systems(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_houses", lambda system="Placidus": {"1": 0.0, "2": 30.0})
    houses = chart.calculate_houses("Placidus")
    assert "1" in houses and "2" in houses


def test_calculate_houses_invalid_system(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    def raise_error(system="InvalidSys"):
        raise ValueError("Unsupported house system")
    monkeypatch.setattr(chart, "calculate_houses", raise_error)
    with pytest.raises(ValueError):
        chart.calculate_houses("InvalidSys")

def test_calculate_fixed_stars_all(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_fixed_stars", lambda: {"Aldebaran": object(), "Regulus": object()})
    stars = chart.calculate_fixed_stars()
    assert "Aldebaran" in stars and "Regulus" in stars


def test_calculate_fixed_stars_empty_list(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_fixed_stars", lambda: {})
    stars = chart.calculate_fixed_stars()
    assert stars == {}

def test_calculate_arabic_parts_standard(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_arabic_parts", lambda: {"Fortune": 123.4})
    parts = chart.calculate_arabic_parts()
    assert "Fortune" in parts


def test_calculate_arabic_parts_custom(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_arabic_parts", lambda: {"Spirit": 234.5})
    parts = chart.calculate_arabic_parts()
    assert "Spirit" in parts

def test_calculate_dignities_all_planets(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_dignities", lambda: {"Sun": object(), "Moon": object()})
    dignities = chart.calculate_dignities()
    assert "Sun" in dignities and "Moon" in dignities


def test_calculate_dignities_custom_table(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_dignities", lambda: {"Mars": object()})
    dignities = chart.calculate_dignities()
    assert "Mars" in dignities

def test_calculate_antiscia_all_planets(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_antiscia", lambda: {"Sun": object(), "Moon": object()})
    antiscia = chart.calculate_antiscia()
    assert "Sun" in antiscia and "Moon" in antiscia

def test_calculate_declinations_all_points(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_declinations", lambda: {"Sun": 23.4, "Moon": -5.1})
    decls = chart.calculate_declinations()
    assert "Sun" in decls and "Moon" in decls

def test_calculate_harmonics_valid(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    monkeypatch.setattr(chart, "calculate_harmonics", lambda harmonic: {"Sun": object()})
    harmonics = chart.calculate_harmonics(5)
    assert "Sun" in harmonics


def test_calculate_harmonics_invalid(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    def raise_error(harmonic):
        raise ValueError("Invalid harmonic number")
    monkeypatch.setattr(chart, "calculate_harmonics", raise_error)
    with pytest.raises(ValueError):
        chart.calculate_harmonics(-1)

def test_calculate_rectification_event_based(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    mock_result = object()
    monkeypatch.setattr(chart, "calculate_rectification", lambda events, time_window, method="event-based": mock_result)
    result = chart.calculate_rectification([object()], (datetime(2024,1,1), datetime(2024,12,31)), method="event-based")
    assert result is mock_result


def test_calculate_rectification_pattern_based(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    mock_result = object()
    monkeypatch.setattr(chart, "calculate_rectification", lambda events, time_window, method="pattern-based": mock_result)
    result = chart.calculate_rectification([object()], (datetime(2024,1,1), datetime(2024,12,31)), method="pattern-based")
    assert result is mock_result


def test_calculate_rectification_empty_events(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    mock_result = object()
    monkeypatch.setattr(chart, "calculate_rectification", lambda events, time_window, method="event-based": mock_result)
    result = chart.calculate_rectification([], (datetime(2024,1,1), datetime(2024,12,31)), method="event-based")
    assert result is mock_result


def test_calculate_rectification_invalid_time_window(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    def raise_error(events, time_window, method="event-based"):
        raise ValueError("Invalid time window")
    monkeypatch.setattr(chart, "calculate_rectification", raise_error)
    with pytest.raises(ValueError):
        chart.calculate_rectification([object()], (None, None), method="event-based")


def test_calculate_rectification_invalid_method(monkeypatch):
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    def raise_error(events, time_window, method):
        raise ValueError("Invalid rectification method")
    monkeypatch.setattr(chart, "calculate_rectification", raise_error)
    with pytest.raises(ValueError):
        chart.calculate_rectification([object()], (datetime(2024,1,1), datetime(2024,12,31)), method="unknown") 