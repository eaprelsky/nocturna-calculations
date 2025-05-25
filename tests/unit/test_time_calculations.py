import pytest
from datetime import datetime, timedelta
import pytz
from nocturna.calculations.time import TimeCalculator
from nocturna.calculations.constants import TimeSystem

class TestTimeCalculations:
    @pytest.fixture
    def calculator(self):
        return TimeCalculator()

    @pytest.fixture
    def test_date(self):
        return datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)

    def test_julian_day_conversion(self, calculator, test_date):
        """Test conversion between datetime and Julian Day"""
        # Test known date (2000-01-01 12:00:00 UTC)
        jd = calculator.datetime_to_julian_day(test_date)
        assert isinstance(jd, float)
        assert jd == pytest.approx(2451545.0, abs=1e-6)

        # Test conversion back to datetime
        dt = calculator.julian_day_to_datetime(jd)
        assert isinstance(dt, datetime)
        assert dt == test_date

        # Test date far in the past
        past_date = datetime(-4712, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        jd = calculator.datetime_to_julian_day(past_date)
        assert jd == pytest.approx(0.0, abs=1e-6)

        # Test date far in the future
        future_date = datetime(3000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        jd = calculator.datetime_to_julian_day(future_date)
        assert jd > 2816787.0  # JD for 3000-01-01

    def test_sidereal_time(self, calculator, test_date):
        """Test sidereal time calculations"""
        # Test Greenwich Mean Sidereal Time (GMST)
        gmst = calculator.calculate_gmst(test_date)
        assert isinstance(gmst, float)
        assert 0 <= gmst < 24

        # Test Local Sidereal Time (LST)
        lst = calculator.calculate_lst(test_date, longitude=0.0)
        assert isinstance(lst, float)
        assert 0 <= lst < 24
        assert lst == pytest.approx(gmst, abs=1e-6)  # At 0° longitude

        # Test LST at different longitudes
        lst_east = calculator.calculate_lst(test_date, longitude=90.0)
        lst_west = calculator.calculate_lst(test_date, longitude=-90.0)
        assert lst_east > lst_west
        assert abs(lst_east - lst_west) == pytest.approx(12.0, abs=1e-6)

    def test_delta_t_calculations(self, calculator):
        """Test Delta T calculations"""
        # Test known Delta T values
        dt_2000 = calculator.calculate_delta_t(datetime(2000, 1, 1, tzinfo=pytz.UTC))
        assert isinstance(dt_2000, float)
        assert dt_2000 == pytest.approx(63.83, abs=0.1)

        dt_2020 = calculator.calculate_delta_t(datetime(2020, 1, 1, tzinfo=pytz.UTC))
        assert dt_2020 > dt_2000  # Delta T increases over time

        # Test historical Delta T
        dt_1900 = calculator.calculate_delta_t(datetime(1900, 1, 1, tzinfo=pytz.UTC))
        assert dt_1900 < dt_2000

        # Test future Delta T (extrapolated)
        dt_2100 = calculator.calculate_delta_t(datetime(2100, 1, 1, tzinfo=pytz.UTC))
        assert dt_2100 > dt_2020

    def test_timezone_conversions(self, calculator, test_date):
        """Test timezone conversions"""
        # Test UTC to local time
        local_time = calculator.convert_timezone(
            test_date,
            from_tz=pytz.UTC,
            to_tz=pytz.timezone('America/New_York')
        )
        assert isinstance(local_time, datetime)
        assert local_time.tzinfo is not None
        assert local_time.hour != test_date.hour

        # Test local time to UTC
        utc_time = calculator.convert_timezone(
            local_time,
            from_tz=pytz.timezone('America/New_York'),
            to_tz=pytz.UTC
        )
        assert utc_time == test_date

        # Test across date line
        tokyo_time = calculator.convert_timezone(
            test_date,
            from_tz=pytz.UTC,
            to_tz=pytz.timezone('Asia/Tokyo')
        )
        assert tokyo_time.day != test_date.day

    def test_time_system_conversions(self, calculator, test_date):
        """Test conversions between different time systems"""
        # Test UTC to TAI
        tai = calculator.convert_time_system(
            test_date,
            from_system=TimeSystem.UTC,
            to_system=TimeSystem.TAI
        )
        assert isinstance(tai, datetime)
        assert tai > test_date

        # Test TAI to UTC
        utc = calculator.convert_time_system(
            tai,
            from_system=TimeSystem.TAI,
            to_system=TimeSystem.UTC
        )
        assert utc == test_date

        # Test UTC to TT
        tt = calculator.convert_time_system(
            test_date,
            from_system=TimeSystem.UTC,
            to_system=TimeSystem.TT
        )
        assert tt > test_date

    def test_edge_cases(self, calculator):
        """Test edge cases in time calculations"""
        # Test invalid timezone
        with pytest.raises(ValueError):
            calculator.convert_timezone(
                datetime.now(),
                from_tz=pytz.UTC,
                to_tz="INVALID_TIMEZONE"
            )

        # Test invalid time system
        with pytest.raises(ValueError):
            calculator.convert_time_system(
                datetime.now(),
                from_system=TimeSystem.UTC,
                to_system="INVALID_SYSTEM"
            )

        # Test missing timezone
        with pytest.raises(ValueError):
            calculator.convert_timezone(
                datetime.now(),
                from_tz=None,
                to_tz=pytz.UTC
            )

    def test_precision_validation(self, calculator, test_date):
        """Test precision of time calculations"""
        # Test Julian Day precision
        jd1 = calculator.datetime_to_julian_day(test_date)
        jd2 = calculator.datetime_to_julian_day(
            test_date + timedelta(microseconds=1)
        )
        assert jd2 > jd1

        # Test sidereal time precision
        st1 = calculator.calculate_gmst(test_date)
        st2 = calculator.calculate_gmst(
            test_date + timedelta(seconds=1)
        )
        assert st2 > st1

    def test_time_roundtrip(self, calculator, test_date):
        """Test roundtrip conversions between time systems"""
        # Test UTC -> TAI -> UTC
        tai = calculator.convert_time_system(
            test_date,
            from_system=TimeSystem.UTC,
            to_system=TimeSystem.TAI
        )
        back_to_utc = calculator.convert_time_system(
            tai,
            from_system=TimeSystem.TAI,
            to_system=TimeSystem.UTC
        )
        assert back_to_utc == test_date

        # Test UTC -> TT -> UTC
        tt = calculator.convert_time_system(
            test_date,
            from_system=TimeSystem.UTC,
            to_system=TimeSystem.TT
        )
        back_to_utc = calculator.convert_time_system(
            tt,
            from_system=TimeSystem.TT,
            to_system=TimeSystem.UTC
        )
        assert back_to_utc == test_date 