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
    Planet, HouseSystem, AspectType, SolarReturnType, SolarReturn,
    LunarReturnType, LunarReturn, ProgressionType, ProgressedChart,
    SolarArcDirection
)

class SwissEphAdapter:
    """Adapter for Swiss Ephemeris calculations"""
    
    def __init__(self):
        """Initialize Swiss Ephemeris adapter"""
        self.version = swe.version
        self.ephe_path = os.getenv('EPHE_PATH', '/usr/share/ephe')  # Default path
        
        # Set ephemeris path if it exists
        if os.path.exists(self.ephe_path):
            swe.set_ephe_path(self.ephe_path)
        
        # Set calculation flags - use the correct constant names
        self.flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
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
            result, ret_flag = swe.calc_ut(julian_day, planet, self.flags)
            
            # Extract position data (result is a tuple with longitude, latitude, distance, speed_lon, speed_lat, speed_dist)
            if len(result) >= 6:
                positions[planet] = {
                    'longitude': result[0],  # Longitude in degrees
                    'latitude': result[1],   # Latitude in degrees
                    'distance': result[2],   # Distance in AU
                    'speed_long': result[3], # Speed in longitude
                    'speed_lat': result[4],  # Speed in latitude
                    'speed_dist': result[5]  # Speed in distance
                }
            elif len(result) >= 3:
                positions[planet] = {
                    'longitude': result[0],  # Longitude in degrees
                    'latitude': result[1],   # Latitude in degrees
                    'distance': result[2],   # Distance in AU
                    'speed_long': 0.0,       # Default speed
                    'speed_lat': 0.0,        # Default speed
                    'speed_dist': 0.0        # Default speed
                }
            else:
                # Fallback for unexpected result format
                positions[planet] = {
                    'longitude': result[0] if len(result) > 0 else 0.0,
                    'latitude': result[1] if len(result) > 1 else 0.0,
                    'distance': 1.0,         # Default distance
                    'speed_long': 0.0,       # Default speed
                    'speed_lat': 0.0,        # Default speed
                    'speed_dist': 0.0        # Default speed
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
        cusps, ascmc = swe.houses(julian_day, latitude, longitude, b'P')
        
        return {
            'cusps': list(cusps),     # House cusps
            'angles': list(ascmc),    # Angles (ASC, MC, ARMC, Vertex)
            'system': 'PLACIDUS'      # Placidus system
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
        angles = self.calculate_angles(
            return_jd,
            birth_latitude,
            birth_longitude
        )
        
        return {
            "return_time": return_time,
            "julian_day": return_jd,
            "planets": planets,
            "houses": houses,
            "angles": angles
        }
    
    def calculate_lunar_return(
        self,
        birth_date: datetime,
        birth_latitude: float,
        birth_longitude: float,
        return_type: LunarReturnType = LunarReturnType.NEXT,
        target_month: Optional[Tuple[int, int]] = None,
        house_system: HouseSystem = HouseSystem.PLACIDUS
    ) -> Dict:
        """
        Calculate lunar return chart
        
        Args:
            birth_date: Birth date and time
            birth_latitude: Birth latitude in degrees
            birth_longitude: Birth longitude in degrees
            return_type: Type of lunar return to calculate
            target_month: Target month for specific return (required for SPECIFIC type)
            house_system: House system to use
            
        Returns:
            Dictionary containing:
            - return_time: Exact time of lunar return
            - julian_day: Julian day of return
            - planets: Dictionary of planet positions
            - houses: Dictionary of house cusps
            - angles: Dictionary of angle positions
        """
        # Calculate exact return time
        return_time, return_jd = LunarReturn.calculate_return_time(
            birth_date,
            birth_latitude,
            birth_longitude,
            return_type,
            target_month
        )
        
        # Calculate planetary positions
        planets = self.calculate_planetary_positions(return_jd, swe.calc_ut(return_jd, swe.SUN, swe.SEFLG_SWIEPH)[0:])
        
        # Calculate house cusps
        houses = self.calculate_houses(
            return_jd,
            birth_latitude,
            birth_longitude
        )
        
        # Calculate angles
        angles = self.calculate_angles(
            return_jd,
            birth_latitude,
            birth_longitude
        )
        
        return {
            "return_time": return_time,
            "julian_day": return_jd,
            "planets": planets,
            "houses": houses,
            "angles": angles
        }
    
    def calculate_progressed_chart(
        self,
        birth_date: datetime,
        birth_latitude: float,
        birth_longitude: float,
        target_date: datetime,
        progression_type: ProgressionType = ProgressionType.SECONDARY,
        house_system: HouseSystem = HouseSystem.PLACIDUS
    ) -> Dict:
        """
        Calculate progressed chart
        
        Args:
            birth_date: Birth date and time
            birth_latitude: Birth latitude in degrees
            birth_longitude: Birth longitude in degrees
            target_date: Target date to calculate progression for
            progression_type: Type of progression to use
            house_system: House system to use
            
        Returns:
            Dictionary containing:
            - progressed_date: Progressed date and time
            - julian_day: Julian day of progressed date
            - planets: Dictionary of progressed planet positions
            - houses: Dictionary of progressed house cusps
            - angles: Dictionary of progressed angle positions
            - solar_arc: Solar arc in degrees (for solar arc progression)
        """
        # Calculate progressed date
        progressed_date = ProgressedChart.calculate_progressed_date(
            birth_date,
            target_date,
            progression_type
        )
        
        # Convert progressed date to Julian day
        progressed_jd = swe.julday(
            progressed_date.year,
            progressed_date.month,
            progressed_date.day,
            progressed_date.hour + progressed_date.minute/60.0 + progressed_date.second/3600.0
        )
        
        # Calculate planetary positions
        planets = self.calculate_planetary_positions(progressed_jd, swe.calc_ut(progressed_jd, swe.SUN, swe.SEFLG_SWIEPH)[0:])
        
        # Calculate house cusps
        houses = self.calculate_houses(
            progressed_jd,
            birth_latitude,
            birth_longitude
        )
        
        # Calculate angles
        angles = self.calculate_angles(
            progressed_jd,
            birth_latitude,
            birth_longitude
        )
        
        # Calculate solar arc if needed
        solar_arc = None
        if progression_type == ProgressionType.SOLAR_ARC:
            # Get birth Sun position
            birth_jd = swe.julday(
                birth_date.year,
                birth_date.month,
                birth_date.day,
                birth_date.hour + birth_date.minute/60.0 + birth_date.second/3600.0
            )
            birth_sun = swe.calc_ut(birth_jd, swe.SUN, swe.SEFLG_SWIEPH)
            birth_sun_pos = birth_sun[0]
            
            # Get progressed Sun position
            progressed_sun = swe.calc_ut(progressed_jd, swe.SUN, swe.SEFLG_SWIEPH)
            progressed_sun_pos = progressed_sun[0]
            
            # Calculate solar arc
            solar_arc = ProgressedChart.calculate_solar_arc(
                birth_date,
                target_date,
                birth_sun_pos,
                progressed_sun_pos
            )
            
            # Adjust positions by solar arc
            for planet in planets.values():
                planet['longitude'] = ProgressedChart.calculate_progressed_position(
                    planet['longitude'],
                    solar_arc,
                    progression_type
                )
            
            for house in houses['cusps']:
                house = ProgressedChart.calculate_progressed_position(
                    house,
                    solar_arc,
                    progression_type
                )
            
            for angle in angles.values():
                angle = ProgressedChart.calculate_progressed_position(
                    angle,
                    solar_arc,
                    progression_type
                )
        
        return {
            "progressed_date": progressed_date,
            "julian_day": progressed_jd,
            "planets": planets,
            "houses": houses,
            "angles": angles,
            "solar_arc": solar_arc
        }
        
    def calculate_harmonic_chart(
        self,
        julian_day: float,
        latitude: float,
        longitude: float,
        harmonic: Union[int, Harmonic],
        house_system: HouseSystem = HouseSystem.PLACIDUS,
        orb: float = 1.0
    ) -> Dict:
        """
        Calculate harmonic chart
        
        Args:
            julian_day: Julian day for calculations
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            harmonic: Harmonic number (1-12) or Harmonic enum value
            house_system: House system to use
            orb: Orb for aspects in degrees (default: 1.0)
            
        Returns:
            Dictionary containing:
            - harmonic: Harmonic number used
            - planets: Dictionary of harmonic planet positions
            - houses: Dictionary of harmonic house cusps
            - angles: Dictionary of harmonic angle positions
            - aspects: List of harmonic aspects between planets
        """
        # Convert harmonic to integer if enum
        if isinstance(harmonic, Harmonic):
            harmonic = harmonic.value
        
        # Calculate planetary positions
        planets = self.calculate_planetary_positions(julian_day, swe.calc_ut(julian_day, swe.SUN, swe.SEFLG_SWIEPH)[0:])
        
        # Calculate house cusps
        houses = self.calculate_houses(julian_day, latitude, longitude)
        
        # Calculate angles
        angles = self.calculate_angles(julian_day, latitude, longitude)
        
        # Calculate harmonic positions
        harmonic_planets = {}
        for name, pos in planets.items():
            harmonic_lon, harmonic_lat, harmonic_dist = HarmonicChart.calculate_harmonic_position(
                pos['longitude'],
                pos['latitude'],
                pos['distance'],
                harmonic
            )
            
            harmonic_planets[name] = {
                'longitude': harmonic_lon,
                'latitude': harmonic_lat,
                'distance': harmonic_dist,
                'speed_long': pos['speed_long'] * harmonic,
                'speed_lat': pos['speed_lat'] * harmonic,
                'speed_dist': pos['speed_dist'] * harmonic,
                'harmonic': harmonic
            }
        
        # Calculate harmonic house cusps
        harmonic_houses = {
            'cusps': [HarmonicChart.calculate_harmonic_position(cusp, 0, 1, harmonic)[0] for cusp in houses['cusps']],
            'angles': [HarmonicChart.calculate_harmonic_position(angle, 0, 1, harmonic)[0] for angle in houses['angles']],
            'system': houses['system']
        }
        
        # Calculate harmonic angles
        harmonic_angles = {
            name: HarmonicChart.calculate_harmonic_position(angle, 0, 1, harmonic)[0]
            for name, angle in angles.items()
        }
        
        # Calculate harmonic aspects
        aspects = []
        planet_names = list(harmonic_planets.keys())
        
        for i, name1 in enumerate(planet_names):
            for name2 in planet_names[i+1:]:
                pos1 = harmonic_planets[name1]
                pos2 = harmonic_planets[name2]
                
                # Calculate harmonic aspect
                aspect = HarmonicChart.calculate_harmonic_aspect(
                    (pos1['longitude'], pos1['latitude'], pos1['distance']),
                    (pos2['longitude'], pos2['latitude'], pos2['distance']),
                    harmonic,
                    orb
                )
                
                if aspect:
                    aspects.append({
                        'planet1': name1,
                        'planet2': name2,
                        'aspect': aspect,
                        'orb': abs(pos1['longitude'] - pos2['longitude']) % 360,
                        'harmonic': harmonic
                    })
        
        return {
            "harmonic": harmonic,
            "planets": harmonic_planets,
            "houses": harmonic_houses,
            "angles": harmonic_angles,
            "aspects": aspects
        }

    def calculate_composite_chart(
        self,
        chart1_data: Dict[str, Any],
        chart2_data: Dict[str, Any],
        orb: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate composite chart from two charts
        
        Args:
            chart1_data: First chart data containing planets, houses, and angles
            chart2_data: Second chart data containing planets, houses, and angles
            orb: Orb for aspects in degrees (default: 1.0)
            
        Returns:
            Dictionary containing:
            - planets: Dictionary of composite planet positions
            - houses: Dictionary of composite house cusps
            - angles: Dictionary of composite angle positions
            - aspects: List of aspects between composite positions
        """
        # Calculate composite planetary positions
        composite_planets = {}
        for name in chart1_data['planets'].keys():
            if name in chart2_data['planets']:
                pos1 = chart1_data['planets'][name]
                pos2 = chart2_data['planets'][name]
                
                # Calculate composite position
                composite_lon, composite_lat, composite_dist = CompositeChart.calculate_composite_position(
                    (pos1['longitude'], pos1['latitude'], pos1['distance']),
                    (pos2['longitude'], pos2['latitude'], pos2['distance'])
                )
                
                # Calculate composite speeds
                composite_speed_long = (pos1['speed_long'] + pos2['speed_long']) / 2
                composite_speed_lat = (pos1['speed_lat'] + pos2['speed_lat']) / 2
                composite_speed_dist = (pos1['speed_dist'] + pos2['speed_dist']) / 2
                
                composite_planets[name] = {
                    'longitude': composite_lon,
                    'latitude': composite_lat,
                    'distance': composite_dist,
                    'speed_long': composite_speed_long,
                    'speed_lat': composite_speed_lat,
                    'speed_dist': composite_speed_dist
                }
        
        # Calculate composite house cusps
        composite_houses = {
            'cusps': [],
            'angles': [],
            'system': chart1_data['houses']['system']
        }
        
        # Calculate composite cusps
        for i in range(len(chart1_data['houses']['cusps'])):
            cusp1 = chart1_data['houses']['cusps'][i]
            cusp2 = chart2_data['houses']['cusps'][i]
            composite_cusp = CompositeChart.calculate_composite_position(
                (cusp1, 0, 1),
                (cusp2, 0, 1)
            )[0]
            composite_houses['cusps'].append(composite_cusp)
        
        # Calculate composite angles
        for i in range(len(chart1_data['houses']['angles'])):
            angle1 = chart1_data['houses']['angles'][i]
            angle2 = chart2_data['houses']['angles'][i]
            composite_angle = CompositeChart.calculate_composite_position(
                (angle1, 0, 1),
                (angle2, 0, 1)
            )[0]
            composite_houses['angles'].append(composite_angle)
        
        # Calculate composite aspects
        aspects = []
        planet_names = list(composite_planets.keys())
        
        for i, name1 in enumerate(planet_names):
            for name2 in planet_names[i+1:]:
                pos1 = composite_planets[name1]
                pos2 = composite_planets[name2]
                
                # Calculate composite aspect
                aspect = CompositeChart.calculate_composite_aspect(
                    (pos1['longitude'], pos1['latitude'], pos1['distance']),
                    (pos2['longitude'], pos2['latitude'], pos2['distance']),
                    orb
                )
                
                if aspect:
                    aspects.append({
                        'planet1': name1,
                        'planet2': name2,
                        'aspect': aspect,
                        'orb': abs(pos1['longitude'] - pos2['longitude']) % 360
                    })
        
        return {
            "planets": composite_planets,
            "houses": composite_houses,
            "aspects": aspects
        }
    
    def calculate_synastry_chart(
        self,
        chart1_data: Dict[str, Any],
        chart2_data: Dict[str, Any],
        orb: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate synastry between two charts
        
        Args:
            chart1_data: First chart data containing planets and houses
            chart2_data: Second chart data containing planets and houses
            orb: Orb multiplier for aspects (default: 1.0)
            
        Returns:
            Dictionary containing:
            - aspects: List of aspects between charts
            - total_strength: Overall synastry strength (0-1)
            - planet_aspects: Dictionary of aspects per planet
            - house_aspects: Dictionary of aspects per house (if applicable)
        """
        # Default orbs for aspects
        default_orbs = {
            "conjunction": 10.0,
            "opposition": 10.0,
            "trine": 8.0,
            "square": 8.0,
            "sextile": 6.0,
            "semisextile": 3.0,
            "semisquare": 3.0,
            "sesquisquare": 3.0,
            "quincunx": 3.0
        }
        
        # Apply orb multiplier
        orbs = {k: v * orb for k, v in default_orbs.items()}
        
        aspects = []
        planet_aspects = {}
        total_strength = 0.0
        aspect_count = 0
        
        # Calculate aspects between planets from chart1 and chart2
        for planet1_name, planet1_data in chart1_data['planets'].items():
            if planet1_name not in planet_aspects:
                planet_aspects[planet1_name] = []
            
            for planet2_name, planet2_data in chart2_data['planets'].items():
                lon1 = planet1_data['longitude']
                lon2 = planet2_data['longitude']
                
                # Calculate angular distance
                distance = abs(lon1 - lon2)
                if distance > 180:
                    distance = 360 - distance
                
                # Check each aspect type
                aspect_angles = {
                    "conjunction": 0,
                    "opposition": 180,
                    "trine": 120,
                    "square": 90,
                    "sextile": 60,
                    "semisextile": 30,
                    "semisquare": 45,
                    "sesquisquare": 135,
                    "quincunx": 150
                }
                
                for aspect_type, aspect_angle in aspect_angles.items():
                    orb_for_aspect = orbs.get(aspect_type, 8.0)
                    actual_orb = abs(distance - aspect_angle)
                    
                    if actual_orb <= orb_for_aspect:
                        # Determine if applying or separating
                        speed1 = planet1_data.get('speed_long', 0)
                        speed2 = planet2_data.get('speed_long', 0)
                        applying = self._is_applying(lon1, lon2, speed1, speed2)
                        
                        # Calculate aspect strength (1.0 for exact, 0.0 at orb limit)
                        strength = 1.0 - (actual_orb / orb_for_aspect) if orb_for_aspect > 0 else 1.0
                        
                        aspect_info = {
                            "planet1": planet1_name,
                            "planet2": planet2_name,
                            "aspect_type": aspect_type,
                            "orb": actual_orb,
                            "applying": applying,
                            "strength": strength
                        }
                        
                        aspects.append(aspect_info)
                        planet_aspects[planet1_name].append(f"{aspect_type}_{planet2_name}")
                        
                        total_strength += strength
                        aspect_count += 1
                        
                        # Only one aspect per planet pair
                        break
        
        # Calculate average strength
        if aspect_count > 0:
            total_strength = total_strength / aspect_count
        
        # Calculate house aspects (planets from chart2 in houses of chart1)
        house_aspects = {}
        if 'houses' in chart1_data and 'cusps' in chart1_data['houses']:
            cusps = chart1_data['houses']['cusps']
            
            for planet_name, planet_data in chart2_data['planets'].items():
                lon = planet_data['longitude']
                
                # Find which house the planet is in
                house_num = self._find_house(lon, cusps)
                
                if house_num not in house_aspects:
                    house_aspects[house_num] = []
                
                house_aspects[house_num].append(f"{planet_name}")
        
        return {
            "aspects": aspects,
            "total_strength": total_strength,
            "planet_aspects": planet_aspects,
            "house_aspects": house_aspects
        }
    
    def _is_applying(
        self,
        lon1: float,
        lon2: float,
        speed1: float,
        speed2: float
    ) -> bool:
        """
        Determine if an aspect is applying (getting closer) or separating
        
        Args:
            lon1: Longitude of first planet
            lon2: Longitude of second planet
            speed1: Speed of first planet
            speed2: Speed of second planet
            
        Returns:
            True if applying, False if separating
        """
        # Calculate if planets are moving towards each other
        distance = (lon2 - lon1) % 360
        relative_speed = speed2 - speed1
        
        # If relative speed is reducing the distance, it's applying
        if distance < 180:
            return relative_speed < 0
        else:
            return relative_speed > 0
    
    def _find_house(self, longitude: float, cusps: List[float]) -> int:
        """
        Find which house a longitude falls into
        
        Args:
            longitude: Longitude in degrees
            cusps: List of house cusps
            
        Returns:
            House number (1-12)
        """
        if not cusps or len(cusps) < 12:
            return 1
        
        # Normalize longitude
        lon = longitude % 360
        
        # Check each house
        for i in range(12):
            cusp1 = cusps[i] % 360
            cusp2 = cusps[(i + 1) % 12] % 360
            
            # Handle house crossing 0 degrees
            if cusp1 > cusp2:
                if lon >= cusp1 or lon < cusp2:
                    return i + 1
            else:
                if cusp1 <= lon < cusp2:
                    return i + 1
        
        return 1  # Default to first house

    def calculate_solar_arc_directions(
        self,
        birth_date: datetime,
        birth_latitude: float,
        birth_longitude: float,
        target_date: datetime,
        direction_type: int = SolarArcDirection.DIRECT,
        orb: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate solar arc directions for given dates
        
        Args:
            birth_date: Birth date and time
            birth_latitude: Birth latitude in degrees
            birth_longitude: Birth longitude in degrees
            target_date: Target date for direction
            direction_type: Type of direction (DIRECT/CONVERSE)
            orb: Orb for aspects in degrees (default: 1.0)
            
        Returns:
            Dictionary containing:
            - solar_arc: Solar arc in degrees
            - directed_planets: Dictionary of directed planet positions
            - directed_houses: Dictionary of directed house cusps
            - directed_angles: Dictionary of directed angle positions
            - aspects: List of aspects between directed and natal positions
            - total_strength: Overall direction strength (0-1)
        """
        import swisseph as swe
        
        # Calculate Julian days
        birth_jd = swe.julday(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            birth_date.hour + birth_date.minute/60.0 + birth_date.second/3600.0
        )
        target_jd = swe.julday(
            target_date.year,
            target_date.month,
            target_date.day,
            target_date.hour + target_date.minute/60.0 + target_date.second/3600.0
        )
        
        # Get Sun positions
        birth_sun = swe.calc_ut(birth_jd, swe.SUN, swe.SEFLG_SWIEPH)
        target_sun = swe.calc_ut(target_jd, swe.SUN, swe.SEFLG_SWIEPH)
        
        # Calculate solar arc
        solar_arc = SolarArcDirection.calculate_solar_arc(
            birth_date,
            target_date,
            birth_sun[0],
            target_sun[0]
        )
        
        # Get natal positions
        natal_planets = self.calculate_planetary_positions(birth_jd)
        natal_houses = self.calculate_houses(birth_jd, birth_latitude, birth_longitude)
        
        # Calculate directed positions
        directed_planets = {}
        for name, pos in natal_planets.items():
            directed_pos = SolarArcDirection.calculate_directed_position(
                pos['longitude'],
                solar_arc,
                direction_type
            )
            directed_planets[name] = {
                'longitude': directed_pos,
                'latitude': pos['latitude'],
                'distance': pos['distance'],
                'speed_long': pos['speed_long'],
                'speed_lat': pos['speed_lat'],
                'speed_dist': pos['speed_dist']
            }
        
        # Calculate directed house cusps
        directed_houses = {
            'cusps': [],
            'angles': [],
            'system': natal_houses['system']
        }
        
        for cusp in natal_houses['cusps']:
            directed_cusp = SolarArcDirection.calculate_directed_position(
                cusp,
                solar_arc,
                direction_type
            )
            directed_houses['cusps'].append(directed_cusp)
        
        # Calculate directed angles
        directed_angles = {}
        for name, angle in natal_houses['angles'].items():
            directed_angle = SolarArcDirection.calculate_directed_position(
                angle,
                solar_arc,
                direction_type
            )
            directed_angles[name] = directed_angle
        
        # Calculate aspects
        aspects = []
        total_strength = 0.0
        
        # Planet to planet aspects
        for name1, pos1 in directed_planets.items():
            for name2, pos2 in natal_planets.items():
                aspect_result = SolarArcDirection.calculate_directed_aspect(
                    pos1['longitude'],
                    pos2['longitude'],
                    orb
                )
                
                if aspect_result:
                    aspect, aspect_orb = aspect_result
                    strength = SolarArcDirection.calculate_direction_strength(
                        aspect,
                        aspect_orb,
                        'planet'
                    )
                    
                    aspects.append({
                        'directed_point': name1,
                        'natal_point': name2,
                        'aspect': aspect,
                        'orb': aspect_orb,
                        'strength': strength
                    })
                    
                    total_strength += strength
        
        # Planet to angle aspects
        for name, pos in directed_planets.items():
            for angle_name, angle in natal_houses['angles'].items():
                aspect_result = SolarArcDirection.calculate_directed_aspect(
                    pos['longitude'],
                    angle,
                    orb
                )
                
                if aspect_result:
                    aspect, aspect_orb = aspect_result
                    strength = SolarArcDirection.calculate_direction_strength(
                        aspect,
                        aspect_orb,
                        'angle'
                    )
                    
                    aspects.append({
                        'directed_point': name,
                        'natal_point': angle_name,
                        'aspect': aspect,
                        'orb': aspect_orb,
                        'strength': strength
                    })
                    
                    total_strength += strength
        
        # Normalize total strength
        if aspects:
            total_strength /= len(aspects)
        
        return {
            'solar_arc': solar_arc,
            'directed_planets': directed_planets,
            'directed_houses': directed_houses,
            'directed_angles': directed_angles,
            'aspects': aspects,
            'total_strength': total_strength
        }