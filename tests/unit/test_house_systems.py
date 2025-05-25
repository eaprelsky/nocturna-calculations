import pytest
from datetime import datetime
from nocturna.calculations.house_systems import HouseSystem
from nocturna.calculations.constants import HouseSystemType
from nocturna.calculations.position import Position
from nocturna.calculations.constants import CoordinateSystem

class TestHouseSystems:
    @pytest.fixture
    def test_date(self):
        return datetime(2000, 1, 1, 12, 0, 0)

    @pytest.fixture
    def test_location(self):
        return Position(0.0, 51.5, 0.0, CoordinateSystem.GEOGRAPHIC)  # London coordinates

    @pytest.fixture
    def calculator(self):
        return HouseSystem()

    def test_placidus_system(self, calculator, test_date, test_location):
        """Test Placidus house system calculations"""
        houses = calculator.calculate_houses(
            test_date,
            test_location,
            HouseSystemType.PLACIDUS
        )
        assert len(houses) == 12
        assert all(0 <= house.longitude <= 360 for house in houses)
        assert all(isinstance(house, Position) for house in houses)
        assert all(house.coordinate_system == CoordinateSystem.ECLIPTIC for house in houses)

        # Verify house order
        for i in range(len(houses) - 1):
            assert houses[i].longitude < houses[i + 1].longitude

    def test_koch_system(self, calculator, test_date, test_location):
        """Test Koch house system calculations"""
        houses = calculator.calculate_houses(
            test_date,
            test_location,
            HouseSystemType.KOCH
        )
        assert len(houses) == 12
        assert all(0 <= house.longitude <= 360 for house in houses)
        assert all(isinstance(house, Position) for house in houses)

        # Verify house order
        for i in range(len(houses) - 1):
            assert houses[i].longitude < houses[i + 1].longitude

    def test_equal_house_system(self, calculator, test_date, test_location):
        """Test Equal house system calculations"""
        houses = calculator.calculate_houses(
            test_date,
            test_location,
            HouseSystemType.EQUAL
        )
        assert len(houses) == 12
        assert all(0 <= house.longitude <= 360 for house in houses)
        assert all(isinstance(house, Position) for house in houses)

        # Verify equal spacing
        spacing = 360 / 12
        for i in range(len(houses) - 1):
            assert abs((houses[i + 1].longitude - houses[i].longitude) - spacing) < 0.001

    def test_whole_sign_houses(self, calculator, test_date, test_location):
        """Test Whole Sign house system calculations"""
        houses = calculator.calculate_houses(
            test_date,
            test_location,
            HouseSystemType.WHOLE_SIGN
        )
        assert len(houses) == 12
        assert all(0 <= house.longitude <= 360 for house in houses)
        assert all(isinstance(house, Position) for house in houses)

        # Verify whole sign boundaries
        for i in range(len(houses)):
            assert houses[i].longitude % 30 == 0

    def test_regiomontanus_system(self, calculator, test_date, test_location):
        """Test Regiomontanus house system calculations"""
        houses = calculator.calculate_houses(
            test_date,
            test_location,
            HouseSystemType.REGIOMONTANUS
        )
        assert len(houses) == 12
        assert all(0 <= house.longitude <= 360 for house in houses)
        assert all(isinstance(house, Position) for house in houses)

        # Verify house order
        for i in range(len(houses) - 1):
            assert houses[i].longitude < houses[i + 1].longitude

    def test_extreme_latitude_handling(self, calculator, test_date):
        """Test house system calculations at extreme latitudes"""
        # Test near North Pole
        north_pole = Position(0.0, 89.9, 0.0, CoordinateSystem.GEOGRAPHIC)
        houses = calculator.calculate_houses(
            test_date,
            north_pole,
            HouseSystemType.PLACIDUS
        )
        assert len(houses) == 12
        assert all(isinstance(house, Position) for house in houses)

        # Test near South Pole
        south_pole = Position(0.0, -89.9, 0.0, CoordinateSystem.GEOGRAPHIC)
        houses = calculator.calculate_houses(
            test_date,
            south_pole,
            HouseSystemType.PLACIDUS
        )
        assert len(houses) == 12
        assert all(isinstance(house, Position) for house in houses)

    def test_invalid_inputs(self, calculator, test_date, test_location):
        """Test handling of invalid inputs"""
        with pytest.raises(ValueError):
            calculator.calculate_houses(test_date, test_location, "INVALID_SYSTEM")

        with pytest.raises(ValueError):
            calculator.calculate_houses("invalid_date", test_location, HouseSystemType.PLACIDUS)

        with pytest.raises(ValueError):
            calculator.calculate_houses(test_date, "invalid_location", HouseSystemType.PLACIDUS)

    def test_house_cusp_precision(self, calculator, test_date, test_location):
        """Test precision of house cusp calculations"""
        # Calculate houses using different systems
        placidus_houses = calculator.calculate_houses(
            test_date,
            test_location,
            HouseSystemType.PLACIDUS
        )
        koch_houses = calculator.calculate_houses(
            test_date,
            test_location,
            HouseSystemType.KOCH
        )

        # Verify precision of calculations
        for i in range(12):
            assert abs(placidus_houses[i].longitude - koch_houses[i].longitude) < 5.0

    def test_house_system_comparison(self, calculator, test_date, test_location):
        """Test comparison between different house systems"""
        systems = [
            HouseSystemType.PLACIDUS,
            HouseSystemType.KOCH,
            HouseSystemType.EQUAL,
            HouseSystemType.WHOLE_SIGN,
            HouseSystemType.REGIOMONTANUS
        ]

        results = {}
        for system in systems:
            houses = calculator.calculate_houses(test_date, test_location, system)
            results[system] = houses

        # Verify that all systems produce valid results
        assert all(len(houses) == 12 for houses in results.values())
        assert all(all(0 <= house.longitude <= 360 for house in houses) 
                  for houses in results.values())

    def test_house_system_edge_cases(self, calculator, test_date):
        """Test house system calculations with edge cases"""
        # Test at equator
        equator = Position(0.0, 0.0, 0.0, CoordinateSystem.GEOGRAPHIC)
        houses = calculator.calculate_houses(
            test_date,
            equator,
            HouseSystemType.PLACIDUS
        )
        assert len(houses) == 12
        assert all(isinstance(house, Position) for house in houses)

        # Test at prime meridian
        prime_meridian = Position(0.0, 45.0, 0.0, CoordinateSystem.GEOGRAPHIC)
        houses = calculator.calculate_houses(
            test_date,
            prime_meridian,
            HouseSystemType.PLACIDUS
        )
        assert len(houses) == 12
        assert all(isinstance(house, Position) for house in houses)

        # Test at international date line
        date_line = Position(180.0, 45.0, 0.0, CoordinateSystem.GEOGRAPHIC)
        houses = calculator.calculate_houses(
            test_date,
            date_line,
            HouseSystemType.PLACIDUS
        )
        assert len(houses) == 12
        assert all(isinstance(house, Position) for house in houses) 