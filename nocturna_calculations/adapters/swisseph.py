"""
Swiss Ephemeris adapter for astrological calculations
"""
import os
from typing import Dict, List, Any, Union, Tuple, Optional
import swisseph as swe
from datetime import datetime

from ..core.position import Position
from ..core.aspect import Aspect
from ..core.constants import (
    CoordinateSystem, FixedStar, Asteroid, LunarNode, 
    ArabicPart, Harmonic, Midpoint, MidpointStructure,
    Antiscia, AntisciaType, Declination, DeclinationType,
    Planet, HouseSystem, AspectType, SolarReturnType, SolarReturn
)

class SwissEphAdapter:
    """Adapter for Swiss Ephemeris calculations"""
    
    def __init__(self):
        """Initialize Swiss Ephemeris adapter"""
        self.version = swe.version()
        self.ephe_path = os.getenv('EPHE_PATH', swe.get_ephe_path())
        
        # Set ephemeris path
        swe.set_ephe_path(self.ephe_path)
        
        # Set calculation flags
        self.flags = swe.SEFLG_SWIEPH | swe.SEFLG_SPEED
    
    def calculate_planetary_positions(
        self,
        julian_day: float,
        planets: List[int]
    ) -> Dict[int, Dict[str, float]]:
        """
        Calculate planetary positions for given Julian day
        
        Args:
            julian_day: Julian day for calculations
            planets: List of planet constants from swisseph
            
        Returns:
            Dict mapping planet constants to their positions
        """
        positions = {}
        
        for planet in planets:
            # Calculate planet position
            result = swe.calc_ut(julian_day, planet, self.flags)
            
            # Extract position data
            positions[planet] = {
                'longitude': result[0],  # Longitude in degrees
                'latitude': result[1],   # Latitude in degrees
                'distance': result[2],   # Distance in AU
                'speed_long': result[3], # Speed in longitude
                'speed_lat': result[4],  # Speed in latitude
                'speed_dist': result[5]  # Speed in distance
            }
        
        return positions
    
    def calculate_houses(
        self,
        julian_day: float,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Calculate house cusps and angles
        
        Args:
            julian_day: Julian day for calculations
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            
        Returns:
            Dict containing house cusps and angles
        """
        # Calculate houses using Placidus system
        result = swe.houses(julian_day, self.flags, latitude, longitude, b'P')
        
        return {
            'cusps': result[0],      # House cusps (13 values)
            'angles': result[1],     # Angles (ASC, MC, ARMC, Vertex)
            'system': 'P'            # Placidus system
        }
    
    def calculate_aspects(
        self,
        positions: Dict[str, Dict[str, float]],
        orbs: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Calculate aspects between planets
        
        Args:
            positions: Dict of planet positions
            orbs: Dictionary of orbs for different aspects
            
        Returns:
            List of aspects
        """
        aspects = []
        planet_names = list(positions.keys())
        
        # Convert positions to Position objects
        pos_objects = {}
        for name, pos in positions.items():
            pos_objects[name] = Position(
                longitude=pos['longitude'],
                latitude=pos['latitude'],
                distance=pos['distance'],
                system=CoordinateSystem.ECLIPTIC,
                speed_long=pos.get('speed_long'),
                speed_lat=pos.get('speed_lat'),
                speed_dist=pos.get('speed_dist')
            )
        
        # Calculate aspects between all pairs of planets
        for i, name1 in enumerate(planet_names):
            for name2 in planet_names[i+1:]:
                # Get positions
                pos1 = pos_objects[name1]
                pos2 = pos_objects[name2]
                
                # Detect aspects
                detected_aspects = Aspect.detect_all(pos1, pos2, orbs)
                
                # Add to results
                for aspect in detected_aspects:
                    aspects.append({
                        'planet1': name1,
                        'planet2': name2,
                        'angle': aspect.angle,
                        'orb': aspect.orb,
                        'aspect_type': aspect.aspect_type,
                        'applying': aspect.applying,
                        'strength': aspect.strength,
                        'is_partile': aspect.is_partile,
                        'is_exact': aspect.is_exact
                    })
        
        return aspects
    
    def calculate_fixed_stars(
        self,
        julian_day: float,
        stars: List[FixedStar] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate fixed star positions for given Julian day
        
        Args:
            julian_day: Julian day for calculations
            stars: List of fixed stars to calculate (default: all)
            
        Returns:
            Dict mapping star names to their positions
        """
        positions = {}
        
        # Use all stars if none specified
        if stars is None:
            stars = list(FixedStar)
        
        for star in stars:
            # Calculate star position
            # Note: Swiss Ephemeris uses star number + 10000 for fixed stars
            result = swe.fixstar2_ut(julian_day, star.value + 10000, self.flags)
            
            # Extract position data
            positions[star.name] = {
                'longitude': result[0],  # Longitude in degrees
                'latitude': result[1],   # Latitude in degrees
                'distance': result[2],   # Distance in AU
                'speed_long': result[3], # Speed in longitude
                'speed_lat': result[4],  # Speed in latitude
                'speed_dist': result[5]  # Speed in distance
            }
        
        return positions
    
    def calculate_asteroids(
        self,
        julian_day: float,
        asteroids: List[Asteroid] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate asteroid positions for given Julian day
        
        Args:
            julian_day: Julian day for calculations
            asteroids: List of asteroids to calculate (default: all)
            
        Returns:
            Dict mapping asteroid names to their positions
        """
        positions = {}
        
        # Use all asteroids if none specified
        if asteroids is None:
            asteroids = list(Asteroid)
        
        for asteroid in asteroids:
            # Calculate asteroid position
            # Note: Swiss Ephemeris uses asteroid number + 10000 for asteroids
            result = swe.calc_ut(julian_day, asteroid.value + 10000, self.flags)
            
            # Extract position data
            positions[asteroid.name] = {
                'longitude': result[0],  # Longitude in degrees
                'latitude': result[1],   # Latitude in degrees
                'distance': result[2],   # Distance in AU
                'speed_long': result[3], # Speed in longitude
                'speed_lat': result[4],  # Speed in latitude
                'speed_dist': result[5]  # Speed in distance
            }
        
        return positions
    
    def calculate_lunar_nodes(
        self,
        julian_day: float,
        nodes: List[LunarNode] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate lunar node positions for given Julian day
        
        Args:
            julian_day: Julian day for calculations
            nodes: List of lunar nodes to calculate (default: all)
            
        Returns:
            Dict mapping node names to their positions
        """
        positions = {}
        
        # Use all nodes if none specified
        if nodes is None:
            nodes = list(LunarNode)
        
        for node in nodes:
            # Calculate node position
            # Note: Swiss Ephemeris uses different constants for lunar nodes
            if node == LunarNode.NORTH_NODE:
                result = swe.calc_ut(julian_day, swe.MEAN_NODE, self.flags)
            elif node == LunarNode.SOUTH_NODE:
                # South node is opposite to North node
                result = swe.calc_ut(julian_day, swe.MEAN_NODE, self.flags)
                result = list(result)
                result[0] = (result[0] + 180) % 360  # Add 180° to longitude
                result[1] = -result[1]  # Negate latitude
            elif node == LunarNode.TRUE_NORTH_NODE:
                result = swe.calc_ut(julian_day, swe.TRUE_NODE, self.flags)
            elif node == LunarNode.TRUE_SOUTH_NODE:
                # True South node is opposite to True North node
                result = swe.calc_ut(julian_day, swe.TRUE_NODE, self.flags)
                result = list(result)
                result[0] = (result[0] + 180) % 360  # Add 180° to longitude
                result[1] = -result[1]  # Negate latitude
            elif node == LunarNode.MEAN_APOGEE:
                result = swe.calc_ut(julian_day, swe.MEAN_APOG, self.flags)
            elif node == LunarNode.OSCULATING_APOGEE:
                result = swe.calc_ut(julian_day, swe.OSCU_APOG, self.flags)
            elif node == LunarNode.MEAN_PERIGEE:
                result = swe.calc_ut(julian_day, swe.MEAN_PERIG, self.flags)
            elif node == LunarNode.OSCULATING_PERIGEE:
                result = swe.calc_ut(julian_day, swe.OSCU_PERIG, self.flags)
            
            # Extract position data
            positions[node.name] = {
                'longitude': result[0],  # Longitude in degrees
                'latitude': result[1],   # Latitude in degrees
                'distance': result[2],   # Distance in AU
                'speed_long': result[3], # Speed in longitude
                'speed_lat': result[4],  # Speed in latitude
                'speed_dist': result[5]  # Speed in distance
            }
        
        return positions
    
    def calculate_arabic_parts(
        self,
        julian_day: float,
        ascendant: float,
        mc: float,
        planet_positions: Dict[str, Dict[str, float]],
        parts: List[ArabicPart] = None
    ) -> Dict[str, float]:
        """
        Calculate Arabic parts positions
        
        Args:
            julian_day: Julian day for calculations
            ascendant: Ascendant longitude in degrees
            mc: Midheaven longitude in degrees
            planet_positions: Dict of planet positions
            parts: List of Arabic parts to calculate (default: all)
            
        Returns:
            Dict mapping part names to their longitudes
        """
        positions = {}
        
        # Use all parts if none specified
        if parts is None:
            parts = list(ArabicPart)
        
        # Helper function to normalize longitude
        def normalize_longitude(lon: float) -> float:
            return lon % 360
        
        # Helper function to get planet longitude
        def get_planet_longitude(planet: str) -> float:
            if planet not in planet_positions:
                raise ValueError(f"Planet {planet} not found in positions")
            return planet_positions[planet]['longitude']
        
        for part in parts:
            # Calculate part longitude based on formula
            if part == ArabicPart.FORTUNA:
                lon = normalize_longitude(ascendant + get_planet_longitude('Moon') - get_planet_longitude('Sun'))
            elif part == ArabicPart.SPIRIT:
                lon = normalize_longitude(ascendant + get_planet_longitude('Sun') - get_planet_longitude('Moon'))
            elif part == ArabicPart.NECESSITY:
                lon = normalize_longitude(ascendant + get_planet_longitude('Saturn') - get_planet_longitude('Moon'))
            elif part == ArabicPart.VALOR:
                lon = normalize_longitude(ascendant + get_planet_longitude('Mars') - get_planet_longitude('Sun'))
            elif part == ArabicPart.VICTORY:
                lon = normalize_longitude(ascendant + get_planet_longitude('Jupiter') - get_planet_longitude('Sun'))
            elif part == ArabicPart.BASIS:
                lon = normalize_longitude(ascendant + get_planet_longitude('Moon') - get_planet_longitude('Saturn'))
            elif part == ArabicPart.MARRIAGE:
                lon = normalize_longitude(ascendant + get_planet_longitude('Venus') - get_planet_longitude('Saturn'))
            elif part == ArabicPart.CHILDREN:
                lon = normalize_longitude(ascendant + get_planet_longitude('Jupiter') - get_planet_longitude('Saturn'))
            elif part == ArabicPart.FATHER:
                lon = normalize_longitude(ascendant + get_planet_longitude('Sun') - get_planet_longitude('Saturn'))
            elif part == ArabicPart.MOTHER:
                lon = normalize_longitude(ascendant + get_planet_longitude('Venus') - get_planet_longitude('Moon'))
            elif part == ArabicPart.BROTHERS:
                lon = normalize_longitude(ascendant + get_planet_longitude('Jupiter') - get_planet_longitude('Mercury'))
            elif part == ArabicPart.SISTERS:
                lon = normalize_longitude(ascendant + get_planet_longitude('Venus') - get_planet_longitude('Mercury'))
            elif part == ArabicPart.HEALTH:
                lon = normalize_longitude(ascendant + get_planet_longitude('Mars') - get_planet_longitude('Saturn'))
            elif part == ArabicPart.DEATH:
                lon = normalize_longitude(ascendant + get_planet_longitude('Saturn') - get_planet_longitude('Mars'))
            elif part == ArabicPart.TRAVEL:
                lon = normalize_longitude(ascendant + get_planet_longitude('Mercury') - get_planet_longitude('Moon'))
            elif part == ArabicPart.WEALTH:
                lon = normalize_longitude(ascendant + get_planet_longitude('Jupiter') - get_planet_longitude('Venus'))
            elif part == ArabicPart.CAREER:
                lon = normalize_longitude(ascendant + mc - get_planet_longitude('Sun'))
            elif part == ArabicPart.HONOR:
                lon = normalize_longitude(ascendant + get_planet_longitude('Sun') - get_planet_longitude('Jupiter'))
            elif part == ArabicPart.RELIGION:
                lon = normalize_longitude(ascendant + get_planet_longitude('Jupiter') - get_planet_longitude('Moon'))
            elif part == ArabicPart.HAPPINESS:
                lon = normalize_longitude(ascendant + get_planet_longitude('Jupiter') - get_planet_longitude('Venus'))
            
            positions[part.name] = lon 
    
    def calculate_harmonic_positions(
        self,
        positions: Dict[str, Dict[str, float]],
        harmonic: Union[int, Harmonic]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate harmonic positions for given positions
        
        Args:
            positions: Dict of positions to calculate harmonics for
            harmonic: Harmonic number (1-12) or Harmonic enum value
            
        Returns:
            Dict mapping position names to their harmonic positions
        """
        # Convert harmonic to integer if enum
        if isinstance(harmonic, Harmonic):
            harmonic = harmonic.value
        
        # Validate harmonic number
        if not 1 <= harmonic <= 12:
            raise ValueError("Harmonic must be between 1 and 12")
        
        harmonic_positions = {}
        
        for name, pos in positions.items():
            # Calculate harmonic longitude
            harmonic_lon = (pos['longitude'] * harmonic) % 360
            
            # Calculate harmonic latitude
            # For harmonics, latitude is multiplied by the harmonic number
            harmonic_lat = pos['latitude'] * harmonic
            
            # Calculate harmonic distance
            # For harmonics, distance is multiplied by the harmonic number
            harmonic_dist = pos['distance'] * harmonic
            
            # Calculate harmonic speeds
            harmonic_speed_long = pos['speed_long'] * harmonic
            harmonic_speed_lat = pos['speed_lat'] * harmonic
            harmonic_speed_dist = pos['speed_dist'] * harmonic
            
            harmonic_positions[name] = {
                'longitude': harmonic_lon,
                'latitude': harmonic_lat,
                'distance': harmonic_dist,
                'speed_long': harmonic_speed_long,
                'speed_lat': harmonic_speed_lat,
                'speed_dist': harmonic_speed_dist,
                'harmonic': harmonic
            }
        
        return harmonic_positions 
    
    def calculate_midpoints(
        self,
        positions: Dict[str, Dict[str, float]],
        points: List[Tuple[str, str]] = None,
        orb: float = 1.0
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate midpoints between points
        
        Args:
            positions: Dict of positions to calculate midpoints for
            points: List of point pairs to calculate midpoints for (default: all pairs)
            orb: Orb for midpoint structures in degrees (default: 1.0)
            
        Returns:
            Dict mapping midpoint names to their data
        """
        midpoints = {}
        
        # Generate all point pairs if none specified
        if points is None:
            point_names = list(positions.keys())
            points = [(p1, p2) for i, p1 in enumerate(point_names) 
                     for p2 in point_names[i+1:]]
        
        # Calculate midpoints for each pair
        for point1, point2 in points:
            # Create midpoint object
            midpoint = Midpoint(point1, point2)
            
            # Get point positions
            pos1 = positions[point1]
            pos2 = positions[point2]
            
            # Calculate midpoint longitude
            midpoint_lon = Midpoint.calculate_midpoint(
                pos1['longitude'],
                pos2['longitude']
            )
            
            # Find midpoint structures with other points
            structures = []
            for name, pos in positions.items():
                if name not in (point1, point2):
                    # Calculate structure
                    structure = Midpoint.calculate_structure(midpoint_lon, pos['longitude'])
                    
                    # Calculate orb
                    structure_orb = abs(
                        (midpoint_lon - pos['longitude']) % 360 - structure.value
                    )
                    
                    # Add if within orb
                    if structure_orb <= orb:
                        structures.append({
                            'point': name,
                            'structure': structure,
                            'orb': structure_orb
                        })
            
            # Store midpoint data
            midpoints[midpoint.name] = {
                'longitude': midpoint_lon,
                'point1': point1,
                'point2': point2,
                'structures': structures
            }
        
        return midpoints 
    
    def calculate_antiscia(
        self,
        positions: Dict[str, Dict[str, float]],
        antiscia_type: AntisciaType = AntisciaType.DIRECT,
        points: List[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate antiscia points for given positions
        
        Args:
            positions: Dict of positions to calculate antiscia for
            antiscia_type: Type of antiscia to calculate (default: DIRECT)
            points: List of points to calculate antiscia for (default: all)
            
        Returns:
            Dict mapping point names to their antiscia data
        """
        antiscia_points = {}
        
        # Use all points if none specified
        if points is None:
            points = list(positions.keys())
        
        # Calculate antiscia for each point
        for name in points:
            if name not in positions:
                continue
                
            # Get point position
            pos = positions[name]
            
            # Calculate antiscia longitude
            antiscia_lon = Antiscia.calculate_antiscia(
                pos['longitude'],
                antiscia_type
            )
            
            # Store antiscia data
            antiscia_points[name] = {
                'longitude': antiscia_lon,
                'latitude': pos['latitude'],  # Latitude remains the same
                'distance': pos['distance'],  # Distance remains the same
                'speed_long': -pos['speed_long'],  # Speed is reversed
                'speed_lat': pos['speed_lat'],  # Lat speed remains the same
                'speed_dist': pos['speed_dist'],  # Dist speed remains the same
                'antiscia_type': antiscia_type,
                'original_point': name
            }
        
        return antiscia_points 
    
    def calculate_declinations(
        self,
        positions: Dict[str, Dict[str, float]],
        points: List[str] = None,
        orb: float = 1.0
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate declinations and their aspects for given positions
        
        Args:
            positions: Dict of positions to calculate declinations for
            points: List of points to calculate declinations for (default: all)
            orb: Orb for declination aspects in degrees (default: 1.0)
            
        Returns:
            Dict mapping point names to their declination data
        """
        declinations = {}
        
        # Use all points if none specified
        if points is None:
            points = list(positions.keys())
        
        # Calculate declinations for each point
        for name in points:
            if name not in positions:
                continue
                
            # Get point position
            pos = positions[name]
            
            # Calculate declination
            decl = Declination.calculate_declination(
                pos['longitude'],
                pos['latitude']
            )
            
            # Find declination aspects with other points
            aspects = []
            for other_name, other_pos in positions.items():
                if other_name != name:
                    # Calculate other point's declination
                    other_decl = Declination.calculate_declination(
                        other_pos['longitude'],
                        other_pos['latitude']
                    )
                    
                    # Check for declination aspect
                    aspect = Declination.calculate_declination_aspect(
                        decl,
                        other_decl,
                        orb
                    )
                    
                    if aspect:
                        aspects.append({
                            'point': other_name,
                            'aspect': aspect,
                            'orb': abs(decl - other_decl) if aspect == DeclinationType.PARALLEL
                                  else abs(decl + other_decl)
                        })
            
            # Store declination data
            declinations[name] = {
                'declination': decl,
                'longitude': pos['longitude'],
                'latitude': pos['latitude'],
                'aspects': aspects
            }
        
        return declinations 
    
    def calculate_solar_return(
        self,
        birth_date: datetime,
        birth_latitude: float,
        birth_longitude: float,
        return_type: SolarReturnType = SolarReturnType.NEXT,
        target_year: Optional[int] = None,
        house_system: HouseSystem = HouseSystem.PLACIDUS
    ) -> Dict:
        """
        Calculate solar return chart
        
        Args:
            birth_date: Birth date and time
            birth_latitude: Birth latitude in degrees
            birth_longitude: Birth longitude in degrees
            return_type: Type of solar return to calculate
            target_year: Target year for specific return (required for SPECIFIC type)
            house_system: House system to use
            
        Returns:
            Dictionary containing:
            - return_time: Exact time of solar return
            - julian_day: Julian day of return
            - planets: Dictionary of planet positions
            - houses: Dictionary of house cusps
            - angles: Dictionary of angle positions
        """
        # Calculate exact return time
        return_time, return_jd = SolarReturn.calculate_return_time(
            birth_date,
            birth_latitude,
            birth_longitude,
            return_type,
            target_year
        )
        
        # Calculate planetary positions
        planets = self.calculate_planetary_positions(return_jd, swe.calc_ut(return_jd, swe.SUN, swe.SEFLG_SWIEPH | swe.SEFLG_SPEED)[0:])
        
        # Calculate house cusps
        houses = self.calculate_houses(
            return_jd,
            birth_latitude,
            birth_longitude
        )
        
        # Calculate angles