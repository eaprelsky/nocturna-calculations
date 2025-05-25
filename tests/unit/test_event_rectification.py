import pytest
from datetime import datetime, timedelta
import pytz
from nocturna.calculations.rectification import EventRectification
from nocturna.calculations.constants import EventType, RectificationMethod
from nocturna.calculations.position import Position
from nocturna.calculations.constants import CoordinateSystem
from nocturna.calculations.chart import Chart

class TestEventRectification:
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
        return EventRectification()

    @pytest.fixture
    def sample_events(self):
        return [
            {
                "date": datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
                "type": EventType.MARRIAGE,
                "description": "First marriage"
            },
            {
                "date": datetime(2005, 6, 15, 15, 30, 0, tzinfo=pytz.UTC),
                "type": EventType.CAREER,
                "description": "Career change"
            },
            {
                "date": datetime(2010, 12, 31, 23, 59, 0, tzinfo=pytz.UTC),
                "type": EventType.RELOCATION,
                "description": "Major move"
            }
        ]

    def test_single_event_rectification(self, rectification_calculator, test_chart, sample_events):
        """Test rectification based on a single event"""
        event = sample_events[0]
        result = rectification_calculator.rectify_single_event(
            test_chart,
            event,
            method=RectificationMethod.EVENT_BASED
        )
        assert result is not None
        assert isinstance(result, dict)
        assert "rectified_time" in result
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

    def test_multiple_events_rectification(self, rectification_calculator, test_chart, sample_events):
        """Test rectification based on multiple events"""
        result = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.EVENT_BASED
        )
        assert result is not None
        assert isinstance(result, dict)
        assert "rectified_time" in result
        assert "confidence" in result
        assert "event_matches" in result
        assert len(result["event_matches"]) == len(sample_events)

    def test_time_window_calculations(self, rectification_calculator, test_chart, sample_events):
        """Test rectification with different time windows"""
        # Test narrow time window
        time_window = (
            datetime(2000, 1, 1, 11, 0, 0, tzinfo=pytz.UTC),
            datetime(2000, 1, 1, 13, 0, 0, tzinfo=pytz.UTC)
        )
        result = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            time_window=time_window,
            method=RectificationMethod.EVENT_BASED
        )
        assert result is not None
        assert result["rectified_time"] >= time_window[0]
        assert result["rectified_time"] <= time_window[1]

        # Test wide time window
        time_window = (
            datetime(1999, 12, 31, 0, 0, 0, tzinfo=pytz.UTC),
            datetime(2000, 1, 2, 0, 0, 0, tzinfo=pytz.UTC)
        )
        result = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            time_window=time_window,
            method=RectificationMethod.EVENT_BASED
        )
        assert result is not None
        assert result["rectified_time"] >= time_window[0]
        assert result["rectified_time"] <= time_window[1]

    def test_event_type_weights(self, rectification_calculator, test_chart, sample_events):
        """Test rectification with different event type weights"""
        weights = {
            EventType.MARRIAGE: 2.0,
            EventType.CAREER: 1.5,
            EventType.RELOCATION: 1.0
        }
        result = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            event_weights=weights,
            method=RectificationMethod.EVENT_BASED
        )
        assert result is not None
        assert "event_matches" in result
        for match in result["event_matches"]:
            assert match["weight"] == weights[match["event"]["type"]]

    def test_confidence_calculation(self, rectification_calculator, test_chart, sample_events):
        """Test confidence calculation in rectification results"""
        result = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.EVENT_BASED
        )
        assert result is not None
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1
        assert "confidence_factors" in result
        assert isinstance(result["confidence_factors"], dict)

    def test_edge_cases(self, rectification_calculator, test_chart):
        """Test edge cases in event rectification"""
        # Test empty events list
        with pytest.raises(ValueError):
            rectification_calculator.rectify_multiple_events(
                test_chart,
                [],
                method=RectificationMethod.EVENT_BASED
            )

        # Test invalid time window
        with pytest.raises(ValueError):
            rectification_calculator.rectify_multiple_events(
                test_chart,
                [{"date": datetime.now(pytz.UTC), "type": EventType.MARRIAGE}],
                time_window=(datetime.now(pytz.UTC), datetime.now(pytz.UTC) - timedelta(hours=1)),
                method=RectificationMethod.EVENT_BASED
            )

        # Test invalid event type
        with pytest.raises(ValueError):
            rectification_calculator.rectify_single_event(
                test_chart,
                {"date": datetime.now(pytz.UTC), "type": "INVALID_TYPE"},
                method=RectificationMethod.EVENT_BASED
            )

    def test_rectification_methods(self, rectification_calculator, test_chart, sample_events):
        """Test different rectification methods"""
        # Test event-based method
        result = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.EVENT_BASED
        )
        assert result is not None
        assert result["method"] == RectificationMethod.EVENT_BASED

        # Test pattern-based method
        result = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.PATTERN_BASED
        )
        assert result is not None
        assert result["method"] == RectificationMethod.PATTERN_BASED

        # Test harmonic method
        result = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.HARMONIC
        )
        assert result is not None
        assert result["method"] == RectificationMethod.HARMONIC

    def test_result_consistency(self, rectification_calculator, test_chart, sample_events):
        """Test consistency of rectification results"""
        # Test same input gives same output
        result1 = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.EVENT_BASED
        )
        result2 = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.EVENT_BASED
        )
        assert result1["rectified_time"] == result2["rectified_time"]
        assert result1["confidence"] == result2["confidence"]

        # Test different methods give different results
        result1 = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.EVENT_BASED
        )
        result2 = rectification_calculator.rectify_multiple_events(
            test_chart,
            sample_events,
            method=RectificationMethod.PATTERN_BASED
        )
        assert result1["rectified_time"] != result2["rectified_time"] 