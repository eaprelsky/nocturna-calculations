"""
Unit tests for astrological calculations
"""
import pytest
from datetime import datetime
import pytz

from nocturna_calculations.core.chart import Chart
from nocturna_calculations.core.constants import (
    FixedStar, Asteroid, LunarNode, ArabicPart, 
    Harmonic, Midpoint, MidpointStructure,
    Antiscia, AntisciaType, Declination, DeclinationType,
    Planet, HouseSystem, AspectType, Aspect,
    SolarReturnType, LunarReturnType, ProgressionType,
    SolarArcDirection
)
from nocturna_calculations.core.config import Config

def test_fixed_stars_calculation():
    """Test fixed stars calculation"""
    # Create test chart
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Calculate all fixed stars
    all_stars = chart.calculate_fixed_stars()
    assert isinstance(all_stars, dict)
    assert len(all_stars) == len(FixedStar)
    
    # Test specific stars
    test_stars = [FixedStar.REGULUS, FixedStar.SPICA]
    specific_stars = chart.calculate_fixed_stars(test_stars)
    assert isinstance(specific_stars, dict)
    assert len(specific_stars) == len(test_stars)
    
    # Verify star data structure
    for star_name, position in specific_stars.items():
        assert isinstance(position, dict)
        assert 'longitude' in position
        assert 'latitude' in position
        assert 'distance' in position
        assert 'speed_long' in position
        assert 'speed_lat' in position
        assert 'speed_dist' in position
        
        # Verify value ranges
        assert 0 <= position['longitude'] <= 360
        assert -90 <= position['latitude'] <= 90
        assert position['distance'] > 0 

def test_asteroid_calculation():
    """Test asteroid calculation"""
    # Create test chart
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Calculate all asteroids
    all_asteroids = chart.calculate_asteroids()
    assert isinstance(all_asteroids, dict)
    assert len(all_asteroids) == len(Asteroid)
    
    # Test specific asteroids
    test_asteroids = [Asteroid.CERES, Asteroid.CHIRON]
    specific_asteroids = chart.calculate_asteroids(test_asteroids)
    assert isinstance(specific_asteroids, dict)
    assert len(specific_asteroids) == len(test_asteroids)
    
    # Verify asteroid data structure
    for asteroid_name, position in specific_asteroids.items():
        assert isinstance(position, dict)
        assert 'longitude' in position
        assert 'latitude' in position
        assert 'distance' in position
        assert 'speed_long' in position
        assert 'speed_lat' in position
        assert 'speed_dist' in position
        
        # Verify value ranges
        assert 0 <= position['longitude'] <= 360
        assert -90 <= position['latitude'] <= 90
        assert position['distance'] > 0 

def test_lunar_node_calculation():
    """Test lunar node calculation"""
    # Create test chart
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Calculate all lunar nodes
    all_nodes = chart.calculate_lunar_nodes()
    assert isinstance(all_nodes, dict)
    assert len(all_nodes) == len(LunarNode)
    
    # Test specific nodes
    test_nodes = [LunarNode.NORTH_NODE, LunarNode.SOUTH_NODE]
    specific_nodes = chart.calculate_lunar_nodes(test_nodes)
    assert isinstance(specific_nodes, dict)
    assert len(specific_nodes) == len(test_nodes)
    
    # Verify node data structure
    for node_name, position in specific_nodes.items():
        assert isinstance(position, dict)
        assert 'longitude' in position
        assert 'latitude' in position
        assert 'distance' in position
        assert 'speed_long' in position
        assert 'speed_lat' in position
        assert 'speed_dist' in position
        
        # Verify value ranges
        assert 0 <= position['longitude'] <= 360
        assert -90 <= position['latitude'] <= 90
        assert position['distance'] > 0
    
    # Verify North and South nodes are opposite
    north_pos = specific_nodes['NORTH_NODE']
    south_pos = specific_nodes['SOUTH_NODE']
    assert abs((north_pos['longitude'] - south_pos['longitude']) % 360 - 180) < 0.1
    assert abs(north_pos['latitude'] + south_pos['latitude']) < 0.1 

def test_arabic_parts_calculation():
    """Test Arabic parts calculation"""
    # Create test chart
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Calculate all Arabic parts
    all_parts = chart.calculate_arabic_parts()
    assert isinstance(all_parts, dict)
    assert len(all_parts) == len(ArabicPart)
    
    # Test specific parts
    test_parts = [ArabicPart.FORTUNA, ArabicPart.SPIRIT]
    specific_parts = chart.calculate_arabic_parts(test_parts)
    assert isinstance(specific_parts, dict)
    assert len(specific_parts) == len(test_parts)
    
    # Verify part data structure
    for part_name, longitude in specific_parts.items():
        assert isinstance(longitude, float)
        assert 0 <= longitude <= 360
    
    # Verify Part of Fortune and Part of Spirit are complementary
    fortuna = specific_parts['FORTUNA']
    spirit = specific_parts['SPIRIT']
    assert abs((fortuna - spirit) % 360 - 180) < 0.1  # Should be opposite 

def test_harmonic_positions_calculation():
    """Test harmonic positions calculation"""
    # Create test chart
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Get planetary positions
    positions = chart.calculate_planetary_positions()
    
    # Test different harmonics
    test_harmonics = [Harmonic.HARMONIC_1, Harmonic.HARMONIC_2, Harmonic.HARMONIC_3]
    
    for harmonic in test_harmonics:
        # Calculate harmonic positions
        harmonic_positions = chart.calculate_harmonic_positions(positions, harmonic)
        
        # Verify data structure
        assert isinstance(harmonic_positions, dict)
        assert len(harmonic_positions) == len(positions)
        
        # Verify each position
        for name, pos in harmonic_positions.items():
            assert isinstance(pos, dict)
            assert 'longitude' in pos
            assert 'latitude' in pos
            assert 'distance' in pos
            assert 'speed_long' in pos
            assert 'speed_lat' in pos
            assert 'speed_dist' in pos
            assert 'harmonic' in pos
            
            # Verify value ranges
            assert 0 <= pos['longitude'] <= 360
            assert -90 <= pos['latitude'] <= 90
            assert pos['distance'] > 0
            assert pos['harmonic'] == harmonic.value
            
            # Verify harmonic calculations
            original_pos = positions[name]
            assert abs(pos['longitude'] - (original_pos['longitude'] * harmonic.value) % 360) < 0.1
            assert abs(pos['latitude'] - original_pos['latitude'] * harmonic.value) < 0.1
            assert abs(pos['distance'] - original_pos['distance'] * harmonic.value) < 0.1 

def test_midpoints_calculation():
    """Test midpoint calculations"""
    # Create test chart
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Get planetary positions
    positions = chart.calculate_planetary_positions()
    
    # Test all midpoints
    all_midpoints = chart.calculate_midpoints()
    assert isinstance(all_midpoints, dict)
    assert len(all_midpoints) > 0
    
    # Test specific midpoint pair
    test_points = [('Sun', 'Moon')]
    specific_midpoints = chart.calculate_midpoints(points=test_points)
    assert isinstance(specific_midpoints, dict)
    assert len(specific_midpoints) == len(test_points)
    
    # Verify midpoint data structure
    for name, data in specific_midpoints.items():
        assert isinstance(data, dict)
        assert 'longitude' in data
        assert 'point1' in data
        assert 'point2' in data
        assert 'structures' in data
        
        # Verify value ranges
        assert 0 <= data['longitude'] <= 360
        assert isinstance(data['structures'], list)
        
        # Verify structures
        for structure in data['structures']:
            assert isinstance(structure, dict)
            assert 'point' in structure
            assert 'structure' in structure
            assert 'orb' in structure
            assert isinstance(structure['structure'], MidpointStructure)
            assert 0 <= structure['orb'] <= 1.0
    
    # Test midpoint calculation
    sun_pos = positions['Sun']['longitude']
    moon_pos = positions['Moon']['longitude']
    midpoint = Midpoint.calculate_midpoint(sun_pos, moon_pos)
    assert abs(midpoint - specific_midpoints['Sun/Moon']['longitude']) < 0.1
    
    # Test midpoint structure
    structure = Midpoint.calculate_structure(midpoint, positions['Mercury']['longitude'])
    assert isinstance(structure, MidpointStructure) 

def test_antiscia_calculation():
    """Test antiscia calculations"""
    # Create test chart
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Get planetary positions
    positions = chart.calculate_planetary_positions()
    
    # Test direct antiscia
    direct_antiscia = chart.calculate_antiscia(antiscia_type=AntisciaType.DIRECT)
    assert isinstance(direct_antiscia, dict)
    assert len(direct_antiscia) == len(positions)
    
    # Test inverse antiscia
    inverse_antiscia = chart.calculate_antiscia(antiscia_type=AntisciaType.INVERSE)
    assert isinstance(inverse_antiscia, dict)
    assert len(inverse_antiscia) == len(positions)
    
    # Test specific points
    test_points = ['Sun', 'Moon']
    specific_antiscia = chart.calculate_antiscia(points=test_points)
    assert isinstance(specific_antiscia, dict)
    assert len(specific_antiscia) == len(test_points)
    
    # Verify antiscia data structure
    for name, data in specific_antiscia.items():
        assert isinstance(data, dict)
        assert 'longitude' in data
        assert 'latitude' in data
        assert 'distance' in data
        assert 'speed_long' in data
        assert 'speed_lat' in data
        assert 'speed_dist' in data
        assert 'antiscia_type' in data
        assert 'original_point' in data
        
        # Verify value ranges
        assert 0 <= data['longitude'] <= 360
        assert -90 <= data['latitude'] <= 90
        assert data['distance'] > 0
        assert isinstance(data['antiscia_type'], AntisciaType)
        assert data['original_point'] == name
    
    # Test antiscia calculations
    sun_pos = positions['Sun']['longitude']
    direct_sun_antiscia = Antiscia.calculate_direct_antiscia(sun_pos)
    inverse_sun_antiscia = Antiscia.calculate_inverse_antiscia(sun_pos)
    
    assert abs(direct_sun_antiscia - direct_antiscia['Sun']['longitude']) < 0.1
    assert abs(inverse_sun_antiscia - inverse_antiscia['Sun']['longitude']) < 0.1
    
    # Verify antiscia properties
    for name, data in direct_antiscia.items():
        original_pos = positions[name]
        assert data['latitude'] == original_pos['latitude']
        assert data['distance'] == original_pos['distance']
        assert data['speed_long'] == -original_pos['speed_long']
        assert data['speed_lat'] == original_pos['speed_lat']
        assert data['speed_dist'] == original_pos['speed_dist'] 

def test_declinations_calculation():
    """Test declination calculations"""
    # Create test chart
    chart = Chart(
        date="2024-03-20",
        time="12:00:00",
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Get planetary positions
    positions = chart.calculate_planetary_positions()
    
    # Test all declinations
    all_declinations = chart.calculate_declinations()
    assert isinstance(all_declinations, dict)
    assert len(all_declinations) == len(positions)
    
    # Test specific points
    test_points = ['Sun', 'Moon']
    specific_declinations = chart.calculate_declinations(points=test_points)
    assert isinstance(specific_declinations, dict)
    assert len(specific_declinations) == len(test_points)
    
    # Verify declination data structure
    for name, data in specific_declinations.items():
        assert isinstance(data, dict)
        assert 'declination' in data
        assert 'longitude' in data
        assert 'latitude' in data
        assert 'aspects' in data
        
        # Verify value ranges
        assert -90 <= data['declination'] <= 90
        assert 0 <= data['longitude'] <= 360
        assert -90 <= data['latitude'] <= 90
        assert isinstance(data['aspects'], list)
        
        # Verify aspects
        for aspect in data['aspects']:
            assert isinstance(aspect, dict)
            assert 'point' in aspect
            assert 'aspect' in aspect
            assert 'orb' in aspect
            assert isinstance(aspect['aspect'], DeclinationType)
            assert 0 <= aspect['orb'] <= 1.0
    
    # Test declination calculations
    sun_pos = positions['Sun']
    sun_decl = Declination.calculate_declination(
        sun_pos['longitude'],
        sun_pos['latitude']
    )
    assert abs(sun_decl - specific_declinations['Sun']['declination']) < 0.1
    
    # Test parallel and contraparallel
    moon_pos = positions['Moon']
    moon_decl = Declination.calculate_declination(
        moon_pos['longitude'],
        moon_pos['latitude']
    )
    
    # Check if Sun and Moon form a declination aspect
    aspect = Declination.calculate_declination_aspect(sun_decl, moon_decl)
    if aspect:
        assert aspect in [DeclinationType.PARALLEL, DeclinationType.CONTRAPARALLEL]
        
        # Verify aspect is in the aspects list
        found = False
        for a in specific_declinations['Sun']['aspects']:
            if a['point'] == 'Moon' and a['aspect'] == aspect:
                found = True
                break
        assert found 

def test_solar_return_calculation():
    """Test solar return calculations"""
    # Create test chart
    chart = Chart(
        date=datetime(2024, 3, 20, 12, 0, 0),
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Test next solar return
    next_return = chart.calculate_solar_return(
        return_type=SolarReturnType.NEXT
    )
    
    # Verify data structure
    assert isinstance(next_return, dict)
    assert "return_time" in next_return
    assert "julian_day" in next_return
    assert "planets" in next_return
    assert "houses" in next_return
    assert "angles" in next_return
    
    # Verify return time
    assert isinstance(next_return["return_time"], datetime)
    assert next_return["return_time"].year == 2025
    assert next_return["return_time"].month == 3
    assert next_return["return_time"].day == 20
    
    # Verify planetary positions
    planets = next_return["planets"]
    assert isinstance(planets, dict)
    assert "Sun" in planets
    assert "Moon" in planets
    
    # Test specific year solar return
    specific_return = chart.calculate_solar_return(
        return_type=SolarReturnType.SPECIFIC,
        target_year=2030
    )
    
    # Verify return time
    assert specific_return["return_time"].year == 2030
    assert specific_return["return_time"].month == 3
    assert specific_return["return_time"].day == 20
    
    # Test previous solar return
    prev_return = chart.calculate_solar_return(
        return_type=SolarReturnType.PREVIOUS
    )
    
    # Verify return time
    assert prev_return["return_time"].year == 2023
    assert prev_return["return_time"].month == 3
    assert prev_return["return_time"].day == 20 

def test_lunar_return_calculation():
    """Test lunar return calculations"""
    # Create test chart
    chart = Chart(
        date=datetime(2024, 3, 20, 12, 0, 0),
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Test next lunar return
    next_return = chart.calculate_lunar_return()
    assert isinstance(next_return, dict)
    assert "return_time" in next_return
    assert "julian_day" in next_return
    assert "planets" in next_return
    assert "houses" in next_return
    assert "angles" in next_return
    
    # Verify return time is approximately 29 days later
    assert next_return["return_time"].year == 2024
    assert next_return["return_time"].month == 4
    assert next_return["return_time"].day == 18
    
    # Verify planetary positions
    assert "Sun" in next_return["planets"]
    assert "Moon" in next_return["planets"]
    
    # Test specific month lunar return
    specific_return = chart.calculate_lunar_return(
        return_type=LunarReturnType.SPECIFIC,
        target_month=datetime(2024, 6, 1)
    )
    assert specific_return["return_time"].year == 2024
    assert specific_return["return_time"].month == 6
    
    # Test previous lunar return
    prev_return = chart.calculate_lunar_return(return_type=LunarReturnType.PREVIOUS)
    assert prev_return["return_time"].year == 2024
    assert prev_return["return_time"].month == 2
    assert prev_return["return_time"].day == 20

def test_progressed_chart_calculation():
    # Create test chart
    chart = Chart(
        date=datetime(1990, 1, 1, 12, 0, 0),
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Test secondary progression
    target_date = datetime(2024, 1, 1)
    secondary_prog = chart.calculate_progressed_chart(
        target_date=target_date,
        progression_type=ProgressionType.SECONDARY
    )
    
    assert isinstance(secondary_prog, dict)
    assert "progressed_date" in secondary_prog
    assert "julian_day" in secondary_prog
    assert "planets" in secondary_prog
    assert "houses" in secondary_prog
    assert "angles" in secondary_prog
    assert "solar_arc" not in secondary_prog
    
    # Verify progressed date is approximately 34 days after birth
    # (34 years * 1 day per year)
    assert secondary_prog["progressed_date"].year == 1990
    assert secondary_prog["progressed_date"].month == 2
    assert secondary_prog["progressed_date"].day == 4
    
    # Test solar arc progression
    solar_arc_prog = chart.calculate_progressed_chart(
        target_date=target_date,
        progression_type=ProgressionType.SOLAR_ARC
    )
    
    assert isinstance(solar_arc_prog, dict)
    assert "solar_arc" in solar_arc_prog
    assert isinstance(solar_arc_prog["solar_arc"], float)
    assert 0 <= solar_arc_prog["solar_arc"] <= 360
    
    # Verify all positions are adjusted by solar arc
    for planet in solar_arc_prog["planets"].values():
        assert isinstance(planet["longitude"], float)
        assert 0 <= planet["longitude"] <= 360
    
    for house in solar_arc_prog["houses"]["cusps"]:
        assert isinstance(house, float)
        assert 0 <= house <= 360
    
    for angle in solar_arc_prog["angles"].values():
        assert isinstance(angle, float)
        assert 0 <= angle <= 360
    
    # Test tertiary progression
    tertiary_prog = chart.calculate_progressed_chart(
        target_date=target_date,
        progression_type=ProgressionType.TERTIARY
    )
    
    assert isinstance(tertiary_prog, dict)
    assert "progressed_date" in tertiary_prog
    assert "solar_arc" not in tertiary_prog
    
    # Verify progressed date is approximately 34 days before birth
    # (34 years * 1 day per year, moving backwards)
    assert tertiary_prog["progressed_date"].year == 1989
    assert tertiary_prog["progressed_date"].month == 11
    assert tertiary_prog["progressed_date"].day == 28 

def test_harmonic_chart_calculation():
    # Create test chart
    chart = Chart(
        date=datetime(1990, 1, 1, 12, 0, 0),
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Test 2nd harmonic
    result = chart.calculate_harmonic_chart(harmonic=2)
    
    # Verify data structure
    assert isinstance(result, dict)
    assert "harmonic" in result
    assert "planets" in result
    assert "houses" in result
    assert "angles" in result
    assert "aspects" in result
    
    # Verify harmonic number
    assert result["harmonic"] == 2
    
    # Verify planet positions are doubled
    for name, pos in result["planets"].items():
        original_pos = chart.calculate_planetary_positions()[name]
        assert abs(pos["longitude"] - (original_pos["longitude"] * 2) % 360) < 0.1
        assert abs(pos["speed_long"] - original_pos["speed_long"] * 2) < 0.1
    
    # Verify house cusps are doubled
    original_houses = chart.calculate_houses()
    for i, cusp in enumerate(result["houses"]["cusps"]):
        original_cusp = original_houses["cusps"][i]
        assert abs(cusp - (original_cusp * 2) % 360) < 0.1
    
    # Verify angles are doubled
    original_angles = chart.calculate_angles()
    for name, angle in result["angles"].items():
        original_angle = original_angles[name]
        assert abs(angle - (original_angle * 2) % 360) < 0.1
    
    # Verify aspects
    assert isinstance(result["aspects"], list)
    for aspect in result["aspects"]:
        assert "planet1" in aspect
        assert "planet2" in aspect
        assert "aspect" in aspect
        assert "orb" in aspect
        assert "harmonic" in aspect
        assert aspect["harmonic"] == 2
    
    # Test 5th harmonic
    result = chart.calculate_harmonic_chart(harmonic=5)
    
    # Verify harmonic number
    assert result["harmonic"] == 5
    
    # Verify planet positions are multiplied by 5
    for name, pos in result["planets"].items():
        original_pos = chart.calculate_planetary_positions()[name]
        assert abs(pos["longitude"] - (original_pos["longitude"] * 5) % 360) < 0.1
        assert abs(pos["speed_long"] - original_pos["speed_long"] * 5) < 0.1
    
    # Test invalid harmonic
    with pytest.raises(ValueError):
        chart.calculate_harmonic_chart(harmonic=0)
    
    with pytest.raises(ValueError):
        chart.calculate_harmonic_chart(harmonic=13) 

def test_composite_chart_calculation():
    """Test composite chart calculations"""
    # Create two test charts
    chart1 = Chart(
        date=datetime(1990, 1, 1, 12, 0, 0),
        latitude=55.7558,
        longitude=37.6173
    )
    
    chart2 = Chart(
        date=datetime(1995, 1, 1, 12, 0, 0),
        latitude=55.7558,
        longitude=37.6173
    )
    
    # Calculate composite chart
    result = chart1.calculate_composite_chart(chart2)
    
    # Verify data structure
    assert isinstance(result, dict)
    assert "planets" in result
    assert "houses" in result
    assert "aspects" in result
    
    # Verify planetary positions
    planets = result["planets"]
    assert isinstance(planets, dict)
    assert "Sun" in planets
    assert "Moon" in planets
    
    # Get original positions
    pos1 = chart1.calculate_planetary_positions()
    pos2 = chart2.calculate_planetary_positions()
    
    # Verify composite positions are midpoints
    for name, composite_pos in planets.items():
        original_pos1 = pos1[name]
        original_pos2 = pos2[name]
        
        # Calculate expected composite position
        expected_lon, expected_lat, expected_dist = CompositeChart.calculate_composite_position(
            (original_pos1['longitude'], original_pos1['latitude'], original_pos1['distance']),
            (original_pos2['longitude'], original_pos2['latitude'], original_pos2['distance'])
        )
        
        # Verify positions match
        assert abs(composite_pos['longitude'] - expected_lon) < 0.1
        assert abs(composite_pos['latitude'] - expected_lat) < 0.1
        assert abs(composite_pos['distance'] - expected_dist) < 0.1
        
        # Verify speeds are averaged
        expected_speed_long = (original_pos1['speed_long'] + original_pos2['speed_long']) / 2
        expected_speed_lat = (original_pos1['speed_lat'] + original_pos2['speed_lat']) / 2
        expected_speed_dist = (original_pos1['speed_dist'] + original_pos2['speed_dist']) / 2
        
        assert abs(composite_pos['speed_long'] - expected_speed_long) < 0.1
        assert abs(composite_pos['speed_lat'] - expected_speed_lat) < 0.1
        assert abs(composite_pos['speed_dist'] - expected_speed_dist) < 0.1
    
    # Verify house cusps
    houses = result["houses"]
    assert isinstance(houses, dict)
    assert "cusps" in houses
    assert "angles" in houses
    assert "system" in houses
    
    # Get original house cusps
    houses1 = chart1.calculate_houses()
    houses2 = chart2.calculate_houses()
    
    # Verify composite cusps are midpoints
    for i, composite_cusp in enumerate(houses["cusps"]):
        cusp1 = houses1["cusps"][i]
        cusp2 = houses2["cusps"][i]
        
        # Calculate expected composite cusp
        expected_cusp = CompositeChart.calculate_composite_position(
            (cusp1, 0, 1),
            (cusp2, 0, 1)
        )[0]
        
        # Verify cusps match
        assert abs(composite_cusp - expected_cusp) < 0.1
    
    # Verify aspects
    aspects = result["aspects"]
    assert isinstance(aspects, list)
    
    for aspect in aspects:
        assert "planet1" in aspect
        assert "planet2" in aspect
        assert "aspect" in aspect
        assert "orb" in aspect
        
        # Verify aspect calculation
        pos1 = planets[aspect["planet1"]]
        pos2 = planets[aspect["planet2"]]
        
        expected_aspect = CompositeChart.calculate_composite_aspect(
            (pos1['longitude'], pos1['latitude'], pos1['distance']),
            (pos2['longitude'], pos2['latitude'], pos2['distance'])
        )
        
        assert aspect["aspect"] == expected_aspect 

def test_synastry_chart_calculation():
    """Test synastry chart calculations"""
    # Create test charts
    chart1 = Chart(
        date=datetime(1990, 1, 1, 12, 0),
        latitude=40.7128,
        longitude=-74.0060
    )
    chart2 = Chart(
        date=datetime(1990, 1, 2, 12, 0),
        latitude=40.7128,
        longitude=-74.0060
    )
    
    # Calculate synastry chart
    result = chart1.calculate_synastry_chart(chart2)
    
    # Verify result structure
    assert 'aspects' in result
    assert 'total_strength' in result
    assert 'planet_aspects' in result
    assert 'house_aspects' in result
    
    # Verify aspects list
    assert isinstance(result['aspects'], list)
    for aspect in result['aspects']:
        assert 'planet1' in aspect or 'house1' in aspect
        assert 'planet2' in aspect or 'house2' in aspect
        assert 'aspect' in aspect
        assert 'orb' in aspect
        assert 'strength' in aspect
        assert 0 <= aspect['strength'] <= 1
    
    # Verify total strength
    assert 0 <= result['total_strength'] <= 1
    
    # Verify planet aspects
    assert isinstance(result['planet_aspects'], dict)
    for planet, aspects in result['planet_aspects'].items():
        assert isinstance(aspects, list)
        for aspect in aspects:
            assert 'planet' in aspect
            assert 'aspect' in aspect
            assert 'orb' in aspect
            assert 'strength' in aspect
    
    # Verify house aspects
    assert isinstance(result['house_aspects'], dict)
    for house, aspects in result['house_aspects'].items():
        assert isinstance(aspects, list)
        for aspect in aspects:
            assert 'house' in aspect
            assert 'aspect' in aspect
            assert 'orb' in aspect
            assert 'strength' in aspect
    
    # Test with different orb
    result = chart1.calculate_synastry_chart(chart2, orb=2.0)
    assert 'aspects' in result
    assert 'total_strength' in result
    
    # Test with same chart (should have many aspects)
    result = chart1.calculate_synastry_chart(chart1)
    assert len(result['aspects']) > 0
    assert result['total_strength'] > 0 

def test_solar_arc_directions_calculation():
    """Test solar arc directions calculations"""
    # Create test chart
    chart = Chart(
        date=datetime(1990, 1, 1, 12, 0),
        latitude=40.7128,
        longitude=-74.0060
    )
    
    # Test direct direction
    target_date = datetime(2024, 1, 1)
    result = chart.calculate_solar_arc_directions(
        target_date=target_date,
        direction_type=SolarArcDirection.DIRECT
    )
    
    # Verify result structure
    assert 'solar_arc' in result
    assert 'directed_planets' in result
    assert 'directed_houses' in result
    assert 'directed_angles' in result
    assert 'aspects' in result
    assert 'total_strength' in result
    
    # Verify solar arc
    assert isinstance(result['solar_arc'], float)
    assert 0 <= result['solar_arc'] <= 360
    
    # Verify directed planets
    assert isinstance(result['directed_planets'], dict)
    for name, pos in result['directed_planets'].items():
        assert isinstance(pos, dict)
        assert 'longitude' in pos
        assert 'latitude' in pos
        assert 'distance' in pos
        assert 'speed_long' in pos
        assert 'speed_lat' in pos
        assert 'speed_dist' in pos
        
        # Verify value ranges
        assert 0 <= pos['longitude'] <= 360
        assert -90 <= pos['latitude'] <= 90
        assert pos['distance'] > 0
    
    # Verify directed houses
    assert isinstance(result['directed_houses'], dict)
    assert 'cusps' in result['directed_houses']
    assert 'angles' in result['directed_houses']
    assert 'system' in result['directed_houses']
    
    for cusp in result['directed_houses']['cusps']:
        assert isinstance(cusp, float)
        assert 0 <= cusp <= 360
    
    # Verify directed angles
    assert isinstance(result['directed_angles'], dict)
    for name, angle in result['directed_angles'].items():
        assert isinstance(angle, float)
        assert 0 <= angle <= 360
    
    # Verify aspects
    assert isinstance(result['aspects'], list)
    for aspect in result['aspects']:
        assert 'directed_point' in aspect
        assert 'natal_point' in aspect
        assert 'aspect' in aspect
        assert 'orb' in aspect
        assert 'strength' in aspect
        assert 0 <= aspect['strength'] <= 1
    
    # Verify total strength
    assert 0 <= result['total_strength'] <= 1
    
    # Test converse direction
    result = chart.calculate_solar_arc_directions(
        target_date=target_date,
        direction_type=SolarArcDirection.CONVERSE
    )
    
    # Verify converse direction calculations
    assert 'solar_arc' in result
    assert 'directed_planets' in result
    assert 'aspects' in result
    
    # Test with different orb
    result = chart.calculate_solar_arc_directions(
        target_date=target_date,
        orb=2.0
    )
    assert 'aspects' in result
    assert 'total_strength' in result
    
    # Test with same date (should have many aspects)
    result = chart.calculate_solar_arc_directions(
        target_date=chart.date
    )
    assert len(result['aspects']) > 0
    assert result['total_strength'] > 0 