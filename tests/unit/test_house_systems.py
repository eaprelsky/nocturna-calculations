"""
Unit tests for house system calculations
"""
import pytest
from datetime import datetime
import math
import swisseph as swe
from nocturna_calculations.calculations.house_systems import (
    BaseHouseSystem,
    PlacidusHouseSystem,
    KochHouseSystem,
    EqualHouseSystem,
    WholeSignHouseSystem,
    CampanusHouseSystem,
    RegiomontanusHouseSystem,
    MeridianHouseSystem,
    MorinusHouseSystem,
    get_house_system
)
from nocturna_calculations.core.constants import HouseSystem
from nocturna_calculations.calculations.utils import (
    calculate_sidereal_time,
    calculate_obliquity
)

class TestHouseSystems:
    """Test suite for house system calculations"""
    
    @pytest.fixture
    def test_date(self):
        """Test date fixture"""
        return datetime(2024, 1, 1, 12, 0, 0)
    
    @pytest.fixture
    def test_location(self):
        """Test location fixture"""
        return {
            'latitude': 51.5074,  # London
            'longitude': -0.1278
        }
    
    @pytest.fixture
    def julian_day(self, test_date):
        """Julian day fixture"""
        return swe.julday(
            test_date.year,
            test_date.month,
            test_date.day,
            test_date.hour + test_date.minute/60.0 + test_date.second/3600.0
        )
    
    def test_sidereal_time_calculation(self, julian_day, test_location):
        """Test sidereal time calculation"""
        # Calculate LST using our utility function
        lst = calculate_sidereal_time(julian_day, test_location['longitude'])
        
        # Calculate LST using Swiss Ephemeris for comparison
        gmst = swe.swe_sidtime(julian_day)
        gmst_degrees = gmst * 15.0
        lst_swisseph = (gmst_degrees + test_location['longitude']) % 360
        
        # Compare results (allow for small floating point differences)
        assert abs(lst - lst_swisseph) < 0.0001
    
    def test_ascendant_calculation(self, julian_day, test_location):
        """Test ascendant calculation"""
        calculator = PlacidusHouseSystem()
        
        # Calculate obliquity
        obliquity = calculate_obliquity(julian_day)
        
        # Calculate ascendant using our method
        ascendant = calculator._calculate_ascendant(
            test_location['latitude'],
            test_location['longitude'],
            obliquity
        )
        
        # Calculate ascendant using Swiss Ephemeris for comparison
        ascendant_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'])[0]
        
        # Compare results (allow for small floating point differences)
        assert abs(ascendant - ascendant_swisseph) < 0.0001
    
    def test_mc_calculation(self, julian_day, test_location):
        """Test midheaven calculation"""
        calculator = PlacidusHouseSystem()
        
        # Calculate obliquity
        obliquity = calculate_obliquity(julian_day)
        
        # Calculate MC using our method
        mc = calculator._calculate_mc(
            test_location['latitude'],
            test_location['longitude'],
            obliquity
        )
        
        # Calculate MC using Swiss Ephemeris for comparison
        mc_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'])[1]
        
        # Compare results (allow for small floating point differences)
        assert abs(mc - mc_swisseph) < 0.0001
    
    def test_placidus_houses(self, julian_day, test_location):
        """Test Placidus house system calculations"""
        calculator = PlacidusHouseSystem()
        cusps = calculator.calculate_cusps(
            test_location['latitude'],
            test_location['longitude']
        )
        
        # Check that we get 12 cusps
        assert len(cusps) == 12
        
        # Check that cusps are in valid range
        for cusp in cusps:
            assert 0 <= cusp < 360
        
        # Compare with Swiss Ephemeris results
        houses_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'])[0]
        for i in range(12):
            assert abs(cusps[i] - houses_swisseph[i]) < 0.0001
    
    def test_koch_houses(self, julian_day, test_location):
        """Test Koch house system calculations"""
        calculator = KochHouseSystem()
        cusps = calculator.calculate_cusps(
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert len(cusps) == 12
        for cusp in cusps:
            assert 0 <= cusp < 360
        
        # Compare with Swiss Ephemeris results
        houses_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'], b'K')[0]
        for i in range(12):
            assert abs(cusps[i] - houses_swisseph[i]) < 0.0001
    
    def test_equal_houses(self, julian_day, test_location):
        """Test Equal house system calculations"""
        calculator = EqualHouseSystem()
        cusps = calculator.calculate_cusps(
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert len(cusps) == 12
        
        # Check that houses are 30° apart
        for i in range(1, len(cusps)):
            diff = (cusps[i] - cusps[i-1]) % 360
            assert abs(diff - 30) < 0.001
        
        # Compare with Swiss Ephemeris results
        houses_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'], b'E')[0]
        for i in range(12):
            assert abs(cusps[i] - houses_swisseph[i]) < 0.0001
    
    def test_whole_sign_houses(self, julian_day, test_location):
        """Test Whole sign house system calculations"""
        calculator = WholeSignHouseSystem()
        cusps = calculator.calculate_cusps(
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert len(cusps) == 12
        
        # Check that cusps align with sign boundaries
        for cusp in cusps:
            assert cusp % 30 == 0
        
        # Compare with Swiss Ephemeris results
        houses_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'], b'W')[0]
        for i in range(12):
            assert abs(cusps[i] - houses_swisseph[i]) < 0.0001
    
    def test_campanus_houses(self, julian_day, test_location):
        """Test Campanus house system calculations"""
        calculator = CampanusHouseSystem()
        cusps = calculator.calculate_cusps(
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert len(cusps) == 12
        for cusp in cusps:
            assert 0 <= cusp < 360
        
        # Compare with Swiss Ephemeris results
        houses_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'], b'C')[0]
        for i in range(12):
            assert abs(cusps[i] - houses_swisseph[i]) < 0.0001
    
    def test_regiomontanus_houses(self, julian_day, test_location):
        """Test Regiomontanus house system calculations"""
        calculator = RegiomontanusHouseSystem()
        cusps = calculator.calculate_cusps(
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert len(cusps) == 12
        for cusp in cusps:
            assert 0 <= cusp < 360
        
        # Compare with Swiss Ephemeris results
        houses_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'], b'R')[0]
        for i in range(12):
            assert abs(cusps[i] - houses_swisseph[i]) < 0.0001
    
    def test_polar_regions(self, julian_day):
        """Test house system calculations in polar regions"""
        calculator = PlacidusHouseSystem()
        
        # Test North Pole
        north_pole_cusps = calculator.calculate_cusps(90, 0)
        assert len(north_pole_cusps) == 12
        for cusp in north_pole_cusps:
            assert 0 <= cusp < 360
        
        # Test South Pole
        south_pole_cusps = calculator.calculate_cusps(-90, 0)
        assert len(south_pole_cusps) == 12
        for cusp in south_pole_cusps:
            assert 0 <= cusp < 360
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates"""
        calculator = PlacidusHouseSystem()
        
        # Test invalid latitude
        with pytest.raises(ValueError):
            calculator.calculate_cusps(91, 0)
        
        # Test invalid longitude
        with pytest.raises(ValueError):
            calculator.calculate_cusps(0, 181)
    
    def test_meridian_houses(self, julian_day, test_location):
        """Test Meridian house system calculations"""
        calculator = MeridianHouseSystem()
        cusps = calculator.calculate_cusps(
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert len(cusps) == 12
        for cusp in cusps:
            assert 0 <= cusp < 360
        
        # Compare with Swiss Ephemeris results
        houses_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'], b'M')[0]
        for i in range(12):
            assert abs(cusps[i] - houses_swisseph[i]) < 0.0001
    
    def test_morinus_houses(self, julian_day, test_location):
        """Test Morinus house system calculations"""
        calculator = MorinusHouseSystem()
        cusps = calculator.calculate_cusps(
            test_location['latitude'],
            test_location['longitude']
        )
        
        assert len(cusps) == 12
        for cusp in cusps:
            assert 0 <= cusp < 360
        
        # Compare with Swiss Ephemeris results
        houses_swisseph = swe.swe_houses(julian_day, test_location['latitude'], test_location['longitude'], b'O')[0]
        for i in range(12):
            assert abs(cusps[i] - houses_swisseph[i]) < 0.0001
    
    def test_get_house_system(self):
        """Test house system factory function"""
        # Test each supported house system
        systems = [
            (HouseSystem.PLACIDUS, PlacidusHouseSystem),
            (HouseSystem.KOCH, KochHouseSystem),
            (HouseSystem.EQUAL, EqualHouseSystem),
            (HouseSystem.WHOLE_SIGN, WholeSignHouseSystem),
            (HouseSystem.CAMPANUS, CampanusHouseSystem),
            (HouseSystem.REGIOMONTANUS, RegiomontanusHouseSystem),
            (HouseSystem.MERIDIAN, MeridianHouseSystem),
            (HouseSystem.MORINUS, MorinusHouseSystem)
        ]
        
        for system_type, expected_class in systems:
            calculator = get_house_system(system_type)
            assert isinstance(calculator, expected_class)
    
    def test_house_system_comparison(self, julian_day, test_location):
        """Test comparison between different house systems"""
        systems = [
            PlacidusHouseSystem(),
            KochHouseSystem(),
            EqualHouseSystem(),
            WholeSignHouseSystem(),
            CampanusHouseSystem(),
            RegiomontanusHouseSystem(),
            MeridianHouseSystem(),
            MorinusHouseSystem()
        ]
        
        # Calculate cusps for each system
        results = {}
        for system in systems:
            results[system.__class__.__name__] = system.calculate_cusps(
                test_location['latitude'],
                test_location['longitude']
            )
        
        # Verify that each system produces valid results
        for name, cusps in results.items():
            assert len(cusps) == 12
            for cusp in cusps:
                assert 0 <= cusp < 360 