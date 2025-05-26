"""
Constants for astrological calculations
"""
from enum import Enum
from typing import Optional, Tuple
from datetime import datetime, timedelta

class AspectType(Enum):
    """Types of astrological aspects"""
    CONJUNCTION = 0
    OPPOSITION = 180
    TRINE = 120
    SQUARE = 90
    SEXTILE = 60
    SEMISEXTILE = 30
    SEMISQUARE = 45
    SESQUISQUARE = 135
    QUINCUNX = 150
    QUINTILE = 72
    BIQUINTILE = 144
    SEPTILE = 51.43
    BISEPTILE = 102.86
    TRISEPTILE = 154.29
    NOVILE = 40
    BINOVILE = 80
    QUADRINOVILE = 160

class CoordinateSystem(Enum):
    """Coordinate systems for astrological calculations"""
    ECLIPTIC = "ecliptic"
    EQUATORIAL = "equatorial"
    HORIZONTAL = "horizontal"
    GALACTIC = "galactic"

class FixedStar(Enum):
    """Fixed stars with their Swiss Ephemeris numbers"""
    ALDEBARAN = 1  # Alpha Tauri
    ALGOL = 2      # Beta Persei
    ALPHA_CENTAURI = 3
    ANTARES = 4    # Alpha Scorpii
    ARCTURUS = 5   # Alpha Bootis
    BETELGEUSE = 6 # Alpha Orionis
    CANOPUS = 7    # Alpha Carinae
    CAPELLA = 8    # Alpha Aurigae
    DENEB = 9      # Alpha Cygni
    FOMALHAUT = 10 # Alpha Piscis Austrini
    POLLUX = 11    # Beta Geminorum
    PROCYON = 12   # Alpha Canis Minoris
    REGULUS = 13   # Alpha Leonis
    SIRIUS = 14    # Alpha Canis Majoris
    SPICA = 15     # Alpha Virginis
    VEGA = 16      # Alpha Lyrae

class Asteroid(Enum):
    """Asteroids with their Swiss Ephemeris numbers"""
    CERES = 1      # Dwarf planet
    PALLAS = 2     # Asteroid
    JUNO = 3       # Asteroid
    VESTA = 4      # Asteroid
    CHIRON = 5     # Centaur
    PHOLUS = 6     # Centaur
    NESSUS = 7     # Centaur
    CHARIKLO = 8   # Centaur
    ERIS = 9       # Dwarf planet
    HAUMEA = 10    # Dwarf planet
    MAKEMAKE = 11  # Dwarf planet
    SEDNA = 12     # Trans-Neptunian object
    ORCUS = 13     # Trans-Neptunian object
    QUAOAR = 14    # Trans-Neptunian object
    IXION = 15     # Trans-Neptunian object
    VARUNA = 16    # Trans-Neptunian object

class LunarNode(Enum):
    """Lunar nodes with their Swiss Ephemeris numbers"""
    NORTH_NODE = 1  # Mean North Node
    SOUTH_NODE = 2  # Mean South Node
    TRUE_NORTH_NODE = 3  # True North Node
    TRUE_SOUTH_NODE = 4  # True South Node
    MEAN_APOGEE = 5  # Mean Lunar Apogee
    OSCULATING_APOGEE = 6  # Osculating Lunar Apogee
    MEAN_PERIGEE = 7  # Mean Lunar Perigee
    OSCULATING_PERIGEE = 8  # Osculating Lunar Perigee

class ArabicPart(Enum):
    """Arabic parts with their calculation formulas"""
    FORTUNA = 1  # Part of Fortune: ASC + Moon - Sun
    SPIRIT = 2   # Part of Spirit: ASC + Sun - Moon
    NECESSITY = 3  # Part of Necessity: ASC + Saturn - Moon
    VALOR = 4    # Part of Valor: ASC + Mars - Sun
    VICTORY = 5  # Part of Victory: ASC + Jupiter - Sun
    BASIS = 6    # Part of Basis: ASC + Moon - Saturn
    MARRIAGE = 7  # Part of Marriage: ASC + Venus - Saturn
    CHILDREN = 8  # Part of Children: ASC + Jupiter - Saturn
    FATHER = 9   # Part of Father: ASC + Sun - Saturn
    MOTHER = 10  # Part of Mother: ASC + Venus - Moon
    BROTHERS = 11  # Part of Brothers: ASC + Jupiter - Mercury
    SISTERS = 12  # Part of Sisters: ASC + Venus - Mercury
    HEALTH = 13  # Part of Health: ASC + Mars - Saturn
    DEATH = 14   # Part of Death: ASC + Saturn - Mars
    TRAVEL = 15  # Part of Travel: ASC + Mercury - Moon
    WEALTH = 16  # Part of Wealth: ASC + Jupiter - Venus
    CAREER = 17  # Part of Career: ASC + MC - Sun
    HONOR = 18   # Part of Honor: ASC + Sun - Jupiter
    RELIGION = 19  # Part of Religion: ASC + Jupiter - Moon
    HAPPINESS = 20  # Part of Happiness: ASC + Jupiter - Venus

class Harmonic(Enum):
    """Harmonic numbers for harmonic calculations"""
    HARMONIC_1 = 1   # Fundamental harmonic
    HARMONIC_2 = 2   # Opposition harmonic
    HARMONIC_3 = 3   # Trine harmonic
    HARMONIC_4 = 4   # Square harmonic
    HARMONIC_5 = 5   # Quintile harmonic
    HARMONIC_6 = 6   # Sextile harmonic
    HARMONIC_7 = 7   # Septile harmonic
    HARMONIC_8 = 8   # Semi-square harmonic
    HARMONIC_9 = 9   # Novile harmonic
    HARMONIC_10 = 10 # Decile harmonic
    HARMONIC_11 = 11 # Undecile harmonic
    HARMONIC_12 = 12 # Semi-sextile harmonic

class MidpointStructure(Enum):
    """Types of midpoint structures"""
    CONJUNCTION = 0    # 0° - Direct midpoint
    SEMISQUARE = 45    # 45° - First indirect midpoint
    SQUARE = 90        # 90° - Second indirect midpoint
    SESQUISQUARE = 135 # 135° - Third indirect midpoint
    OPPOSITION = 180   # 180° - Fourth indirect midpoint

class Midpoint:
    """Class for midpoint calculations and properties"""
    
    def __init__(self, point1: str, point2: str):
        """
        Initialize midpoint between two points
        
        Args:
            point1: First point name
            point2: Second point name
        """
        self.point1 = point1
        self.point2 = point2
        self.name = f"{point1}/{point2}"
        
    @staticmethod
    def calculate_midpoint(lon1: float, lon2: float) -> float:
        """
        Calculate midpoint between two longitudes
        
        Args:
            lon1: First longitude in degrees
            lon2: Second longitude in degrees
            
        Returns:
            Midpoint longitude in degrees
        """
        # Normalize longitudes to 0-360 range
        lon1 = lon1 % 360
        lon2 = lon2 % 360
        
        # Calculate midpoint
        if abs(lon1 - lon2) > 180:
            # Handle case when points are on opposite sides of 0°
            if lon1 < lon2:
                lon1 += 360
            else:
                lon2 += 360
        
        return (lon1 + lon2) / 2 % 360
    
    @staticmethod
    def calculate_structure(midpoint: float, point: float) -> MidpointStructure:
        """
        Calculate midpoint structure between midpoint and point
        
        Args:
            midpoint: Midpoint longitude in degrees
            point: Point longitude in degrees
            
        Returns:
            MidpointStructure enum value
        """
        # Calculate angular distance
        distance = abs(midpoint - point) % 360
        
        # Find closest structure
        structures = {
            MidpointStructure.CONJUNCTION: 0,
            MidpointStructure.SEMISQUARE: 45,
            MidpointStructure.SQUARE: 90,
            MidpointStructure.SESQUISQUARE: 135,
            MidpointStructure.OPPOSITION: 180
        }
        
        # Find closest structure
        closest = min(structures.items(), key=lambda x: abs(x[1] - distance))
        return closest[0]

class AntisciaType(Enum):
    """Types of antiscia points"""
    DIRECT = 1    # Direct antiscia (mirror across 0° Cancer)
    INVERSE = 2   # Inverse antiscia (mirror across 0° Capricorn)

class Antiscia:
    """Class for antiscia calculations and properties"""
    
    # Cancer/Capricorn axis points
    CANCER_POINT = 90.0    # 0° Cancer
    CAPRICORN_POINT = 270.0  # 0° Capricorn
    
    @staticmethod
    def calculate_direct_antiscia(longitude: float) -> float:
        """
        Calculate direct antiscia point (mirror across 0° Cancer)
        
        Args:
            longitude: Point longitude in degrees
            
        Returns:
            Direct antiscia longitude in degrees
        """
        # Normalize longitude to 0-360 range
        lon = longitude % 360
        
        # Calculate distance from Cancer point
        distance = lon - Antiscia.CANCER_POINT
        
        # Mirror the point
        antiscia = (Antiscia.CANCER_POINT - distance) % 360
        
        return antiscia
    
    @staticmethod
    def calculate_inverse_antiscia(longitude: float) -> float:
        """
        Calculate inverse antiscia point (mirror across 0° Capricorn)
        
        Args:
            longitude: Point longitude in degrees
            
        Returns:
            Inverse antiscia longitude in degrees
        """
        # Normalize longitude to 0-360 range
        lon = longitude % 360
        
        # Calculate distance from Capricorn point
        distance = lon - Antiscia.CAPRICORN_POINT
        
        # Mirror the point
        antiscia = (Antiscia.CAPRICORN_POINT - distance) % 360
        
        return antiscia
    
    @staticmethod
    def calculate_antiscia(longitude: float, antiscia_type: AntisciaType) -> float:
        """
        Calculate antiscia point based on type
        
        Args:
            longitude: Point longitude in degrees
            antiscia_type: Type of antiscia to calculate
            
        Returns:
            Antiscia longitude in degrees
        """
        if antiscia_type == AntisciaType.DIRECT:
            return Antiscia.calculate_direct_antiscia(longitude)
        else:
            return Antiscia.calculate_inverse_antiscia(longitude)

class DeclinationType(Enum):
    """Types of declination aspects"""
    PARALLEL = 1      # Same declination
    CONTRAPARALLEL = 2  # Opposite declination

class Declination:
    """Class for declination calculations and properties"""
    
    @staticmethod
    def calculate_declination(
        longitude: float,
        latitude: float,
        obliquity: float = 23.4367  # Current obliquity of the ecliptic
    ) -> float:
        """
        Calculate declination from ecliptic coordinates
        
        Args:
            longitude: Ecliptic longitude in degrees
            latitude: Ecliptic latitude in degrees
            obliquity: Obliquity of the ecliptic in degrees (default: current value)
            
        Returns:
            Declination in degrees
        """
        import math
        
        # Convert to radians
        lon_rad = math.radians(longitude)
        lat_rad = math.radians(latitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate declination
        decl = math.asin(
            math.sin(lat_rad) * math.cos(obl_rad) +
            math.cos(lat_rad) * math.sin(obl_rad) * math.sin(lon_rad)
        )
        
        return math.degrees(decl)
    
    @staticmethod
    def calculate_parallel(
        decl1: float,
        decl2: float,
        orb: float = 1.0
    ) -> bool:
        """
        Check if two declinations form a parallel aspect
        
        Args:
            decl1: First declination in degrees
            decl2: Second declination in degrees
            orb: Orb for parallel in degrees (default: 1.0)
            
        Returns:
            True if declinations form a parallel within orb
        """
        return abs(decl1 - decl2) <= orb
    
    @staticmethod
    def calculate_contraparallel(
        decl1: float,
        decl2: float,
        orb: float = 1.0
    ) -> bool:
        """
        Check if two declinations form a contraparallel aspect
        
        Args:
            decl1: First declination in degrees
            decl2: Second declination in degrees
            orb: Orb for contraparallel in degrees (default: 1.0)
            
        Returns:
            True if declinations form a contraparallel within orb
        """
        return abs(decl1 + decl2) <= orb
    
    @staticmethod
    def calculate_declination_aspect(
        decl1: float,
        decl2: float,
        orb: float = 1.0
    ) -> Optional[DeclinationType]:
        """
        Calculate declination aspect between two points
        
        Args:
            decl1: First declination in degrees
            decl2: Second declination in degrees
            orb: Orb for aspects in degrees (default: 1.0)
            
        Returns:
            DeclinationType if aspect exists, None otherwise
        """
        if Declination.calculate_parallel(decl1, decl2, orb):
            return DeclinationType.PARALLEL
        elif Declination.calculate_contraparallel(decl1, decl2, orb):
            return DeclinationType.CONTRAPARALLEL
        return None

class SolarReturnType(Enum):
    """Types of solar return calculations"""
    NEXT = 1      # Next solar return
    PREVIOUS = 2  # Previous solar return
    SPECIFIC = 3  # Specific year solar return

class SolarReturn:
    """Class for solar return calculations and properties"""
    
    @staticmethod
    def calculate_return_time(
        birth_date: datetime,
        birth_latitude: float,
        birth_longitude: float,
        return_type: SolarReturnType = SolarReturnType.NEXT,
        target_year: Optional[int] = None
    ) -> Tuple[datetime, float]:
        """
        Calculate exact time of solar return
        
        Args:
            birth_date: Birth date and time
            birth_latitude: Birth latitude in degrees
            birth_longitude: Birth longitude in degrees
            return_type: Type of solar return to calculate
            target_year: Target year for specific return (required for SPECIFIC type)
            
        Returns:
            Tuple of (return datetime, return Julian day)
        """
        import swisseph as swe
        
        # Convert birth date to Julian day
        birth_jd = swe.julday(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            birth_date.hour + birth_date.minute/60.0 + birth_date.second/3600.0
        )
        
        # Get birth Sun position
        birth_sun = swe.calc_ut(birth_jd, swe.SUN, swe.SEFLG_SWIEPH)
        birth_sun_lon = birth_sun[0]
        
        # Calculate target date based on return type
        if return_type == SolarReturnType.NEXT:
            target_date = birth_date + timedelta(days=365)
        elif return_type == SolarReturnType.PREVIOUS:
            target_date = birth_date - timedelta(days=365)
        elif return_type == SolarReturnType.SPECIFIC:
            if target_year is None:
                raise ValueError("target_year is required for SPECIFIC return type")
            target_date = birth_date.replace(year=target_year)
        else:
            raise ValueError(f"Invalid return type: {return_type}")
        
        # Convert target date to Julian day
        target_jd = swe.julday(
            target_date.year,
            target_date.month,
            target_date.day,
            12.0  # Start at noon for better convergence
        )
        
        # Find exact return time using binary search
        max_iterations = 50
        tolerance = 0.0001  # About 8.6 seconds
        
        for _ in range(max_iterations):
            # Calculate Sun position at target time
            target_sun = swe.calc_ut(target_jd, swe.SUN, swe.SEFLG_SWIEPH)
            target_sun_lon = target_sun[0]
            
            # Calculate angular distance
            angle_diff = (target_sun_lon - birth_sun_lon) % 360
            
            # Check if we've found the return
            if abs(angle_diff) < tolerance:
                break
            
            # Adjust time based on angle difference
            # One degree is approximately 4 minutes
            time_adjustment = angle_diff * 4 / 60.0  # Convert to days
            target_jd -= time_adjustment
        
        # Convert Julian day back to datetime
        year, month, day, hour = swe.revjul(target_jd)
        return_time = datetime(
            year, month, day,
            int(hour),
            int((hour % 1) * 60),
            int(((hour % 1) * 60) % 1 * 60)
        )
        
        return return_time, target_jd

class LunarReturnType(Enum):
    """Types of lunar return calculations"""
    NEXT = 1      # Next lunar return
    PREVIOUS = 2  # Previous lunar return
    SPECIFIC = 3  # Specific month lunar return

class LunarReturn:
    """Class for lunar return calculations and properties"""
    
    @staticmethod
    def calculate_return_time(
        birth_date: datetime,
        birth_latitude: float,
        birth_longitude: float,
        return_type: LunarReturnType = LunarReturnType.NEXT,
        target_month: Optional[Tuple[int, int]] = None  # (year, month)
    ) -> Tuple[datetime, float]:
        """
        Calculate exact time of lunar return
        
        Args:
            birth_date: Birth date and time
            birth_latitude: Birth latitude in degrees
            birth_longitude: Birth longitude in degrees
            return_type: Type of lunar return to calculate
            target_month: Target month for specific return (required for SPECIFIC type)
            
        Returns:
            Tuple of (return datetime, return Julian day)
        """
        import swisseph as swe
        
        # Convert birth date to Julian day
        birth_jd = swe.julday(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            birth_date.hour + birth_date.minute/60.0 + birth_date.second/3600.0
        )
        
        # Get birth Moon position
        birth_moon = swe.calc_ut(birth_jd, swe.MOON, swe.SEFLG_SWIEPH)
        birth_moon_lon = birth_moon[0]
        
        # Calculate target date based on return type
        if return_type == LunarReturnType.NEXT:
            # Moon's synodic period is approximately 29.53 days
            target_date = birth_date + timedelta(days=29)
        elif return_type == LunarReturnType.PREVIOUS:
            target_date = birth_date - timedelta(days=29)
        elif return_type == LunarReturnType.SPECIFIC:
            if target_month is None:
                raise ValueError("target_month is required for SPECIFIC return type")
            target_year, target_month = target_month
            target_date = birth_date.replace(year=target_year, month=target_month)
        else:
            raise ValueError(f"Invalid return type: {return_type}")
        
        # Convert target date to Julian day
        target_jd = swe.julday(
            target_date.year,
            target_date.month,
            target_date.day,
            12.0  # Start at noon for better convergence
        )
        
        # Find exact return time using binary search
        max_iterations = 50
        tolerance = 0.0001  # About 8.6 seconds
        
        for _ in range(max_iterations):
            # Calculate Moon position at target time
            target_moon = swe.calc_ut(target_jd, swe.MOON, swe.SEFLG_SWIEPH)
            target_moon_lon = target_moon[0]
            
            # Calculate angular distance
            angle_diff = (target_moon_lon - birth_moon_lon) % 360
            
            # Check if we've found the return
            if abs(angle_diff) < tolerance:
                break
            
            # Adjust time based on angle difference
            # Moon moves about 13.2 degrees per day
            time_adjustment = angle_diff / 13.2  # Convert to days
            target_jd -= time_adjustment
        
        # Convert Julian day back to datetime
        year, month, day, hour = swe.revjul(target_jd)
        return_time = datetime(
            year, month, day,
            int(hour),
            int((hour % 1) * 60),
            int(((hour % 1) * 60) % 1 * 60)
        )
        
        return return_time, target_jd 

class ProgressionType(Enum):
    """Types of chart progressions"""
    SECONDARY = 1    # Secondary progression (1 day = 1 year)
    SOLAR_ARC = 2    # Solar arc progression
    TERTIARY = 3     # Tertiary progression (1 day = 1 month)

class ProgressedChart:
    """Class for progressed chart calculations and properties"""
    
    # Progression rates
    SECONDARY_RATE = 1.0  # 1 day = 1 year
    TERTIARY_RATE = 12.0  # 1 day = 1 month
    
    @staticmethod
    def calculate_progressed_date(
        birth_date: datetime,
        target_date: datetime,
        progression_type: ProgressionType = ProgressionType.SECONDARY
    ) -> datetime:
        """
        Calculate progressed date for given target date
        
        Args:
            birth_date: Birth date and time
            target_date: Target date to calculate progression for
            progression_type: Type of progression to use
            
        Returns:
            Progressed date and time
        """
        # Calculate years between birth and target
        years_diff = target_date.year - birth_date.year
        months_diff = target_date.month - birth_date.month
        days_diff = target_date.day - birth_date.day
        
        # Convert to total days
        total_days = years_diff * 365 + months_diff * 30 + days_diff
        
        # Calculate progressed days based on progression type
        if progression_type == ProgressionType.SECONDARY:
            progressed_days = total_days * ProgressedChart.SECONDARY_RATE
        elif progression_type == ProgressionType.TERTIARY:
            progressed_days = total_days * ProgressedChart.TERTIARY_RATE
        else:
            raise ValueError(f"Invalid progression type: {progression_type}")
        
        # Calculate progressed date
        progressed_date = birth_date + timedelta(days=progressed_days)
        
        return progressed_date
    
    @staticmethod
    def calculate_solar_arc(
        birth_date: datetime,
        target_date: datetime,
        birth_sun_pos: float,
        progressed_sun_pos: float
    ) -> float:
        """
        Calculate solar arc for given dates
        
        Args:
            birth_date: Birth date and time
            target_date: Target date to calculate progression for
            birth_sun_pos: Sun's position at birth
            progressed_sun_pos: Sun's position at target date
            
        Returns:
            Solar arc in degrees
        """
        # Calculate solar arc
        solar_arc = (progressed_sun_pos - birth_sun_pos) % 360
        
        return solar_arc
    
    @staticmethod
    def calculate_progressed_position(
        original_pos: float,
        solar_arc: float,
        progression_type: ProgressionType = ProgressionType.SECONDARY
    ) -> float:
        """
        Calculate progressed position
        
        Args:
            original_pos: Original position in degrees
            solar_arc: Solar arc in degrees
            progression_type: Type of progression to use
            
        Returns:
            Progressed position in degrees
        """
        if progression_type == ProgressionType.SOLAR_ARC:
            # For solar arc, add the arc to the original position
            progressed_pos = (original_pos + solar_arc) % 360
        else:
            # For secondary and tertiary, use the original position
            # as the progressed position is calculated from the progressed date
            progressed_pos = original_pos
        
        return progressed_pos

class HarmonicChart:
    """Class for harmonic chart calculations and properties"""
    
    @staticmethod
    def calculate_harmonic_position(
        longitude: float,
        latitude: float,
        distance: float,
        harmonic: int
    ) -> Tuple[float, float, float]:
        """
        Calculate harmonic position for given coordinates
        
        Args:
            longitude: Original longitude in degrees
            latitude: Original latitude in degrees
            distance: Original distance in AU
            harmonic: Harmonic number (1-12)
            
        Returns:
            Tuple of (harmonic longitude, harmonic latitude, harmonic distance)
        """
        # Validate harmonic number
        if not 1 <= harmonic <= 12:
            raise ValueError("Harmonic must be between 1 and 12")
        
        # Calculate harmonic longitude
        harmonic_lon = (longitude * harmonic) % 360
        
        # Calculate harmonic latitude
        # For harmonics, latitude is multiplied by the harmonic number
        harmonic_lat = latitude * harmonic
        
        # Calculate harmonic distance
        # For harmonics, distance is multiplied by the harmonic number
        harmonic_dist = distance * harmonic
        
        return harmonic_lon, harmonic_lat, harmonic_dist
    
    @staticmethod
    def calculate_harmonic_aspect(
        pos1: Tuple[float, float, float],
        pos2: Tuple[float, float, float],
        harmonic: int,
        orb: float = 1.0
    ) -> Optional[AspectType]:
        """
        Calculate harmonic aspect between two positions
        
        Args:
            pos1: First position tuple (longitude, latitude, distance)
            pos2: Second position tuple (longitude, latitude, distance)
            harmonic: Harmonic number (1-12)
            orb: Orb for aspect in degrees (default: 1.0)
            
        Returns:
            AspectType if aspect exists, None otherwise
        """
        # Calculate angular distance between harmonic positions
        lon1, lat1, dist1 = pos1
        lon2, lat2, dist2 = pos2
        
        # Calculate angular distance
        angle_diff = abs(lon1 - lon2) % 360
        
        # Check for harmonic aspects
        # In harmonic charts, aspects are based on divisions of 360° by the harmonic number
        harmonic_angle = 360 / harmonic
        
        # Check each possible aspect
        for aspect in AspectType:
            # Calculate expected angle for this aspect in the harmonic
            expected_angle = (aspect.value * harmonic_angle / 360) % 360
            
            # Check if positions form this aspect
            if abs(angle_diff - expected_angle) <= orb:
                return aspect
        
        return None 

class CompositeChart:
    """Class for composite chart calculations and properties"""
    
    @staticmethod
    def calculate_composite_position(
        pos1: Tuple[float, float, float],
        pos2: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        """
        Calculate composite position between two positions
        
        Args:
            pos1: First position tuple (longitude, latitude, distance)
            pos2: Second position tuple (longitude, latitude, distance)
            
        Returns:
            Tuple of (composite longitude, composite latitude, composite distance)
        """
        lon1, lat1, dist1 = pos1
        lon2, lat2, dist2 = pos2
        
        # Calculate composite longitude
        # Normalize longitudes to 0-360 range
        lon1 = lon1 % 360
        lon2 = lon2 % 360
        
        # Calculate midpoint longitude
        if abs(lon1 - lon2) > 180:
            # Handle case when points are on opposite sides of 0°
            if lon1 < lon2:
                lon1 += 360
            else:
                lon2 += 360
        
        composite_lon = (lon1 + lon2) / 2 % 360
        
        # Calculate composite latitude
        composite_lat = (lat1 + lat2) / 2
        
        # Calculate composite distance
        composite_dist = (dist1 + dist2) / 2
        
        return composite_lon, composite_lat, composite_dist
    
    @staticmethod
    def calculate_composite_aspect(
        pos1: Tuple[float, float, float],
        pos2: Tuple[float, float, float],
        orb: float = 1.0
    ) -> Optional[AspectType]:
        """
        Calculate aspect between two composite positions
        
        Args:
            pos1: First position tuple (longitude, latitude, distance)
            pos2: Second position tuple (longitude, latitude, distance)
            orb: Orb for aspect in degrees (default: 1.0)
            
        Returns:
            AspectType if aspect exists, None otherwise
        """
        lon1, lat1, dist1 = pos1
        lon2, lat2, dist2 = pos2
        
        # Calculate angular distance
        angle_diff = abs(lon1 - lon2) % 360
        
        # Check each possible aspect
        for aspect in AspectType:
            if abs(angle_diff - aspect.value) <= orb:
                return aspect
        
        return None 

class SynastryChart:
    """Class for synastry chart calculations and properties"""
    
    # Aspect strength weights
    MAJOR_ASPECT_WEIGHT = 1.0
    MINOR_ASPECT_WEIGHT = 0.7
    HARMONIC_ASPECT_WEIGHT = 0.5
    
    # Planet type weights
    PERSONAL_PLANET_WEIGHT = 1.0
    SOCIAL_PLANET_WEIGHT = 0.8
    OUTER_PLANET_WEIGHT = 0.6
    
    @staticmethod
    def calculate_synastry_aspect(
        pos1: Tuple[float, float, float],
        pos2: Tuple[float, float, float],
        orb: float = 1.0
    ) -> Optional[Tuple[AspectType, float]]:
        """
        Calculate aspect between positions from different charts
        
        Args:
            pos1: First position tuple (longitude, latitude, distance)
            pos2: Second position tuple (longitude, latitude, distance)
            orb: Orb for aspect in degrees (default: 1.0)
            
        Returns:
            Tuple of (AspectType, orb) if aspect exists, None otherwise
        """
        lon1, lat1, dist1 = pos1
        lon2, lat2, dist2 = pos2
        
        # Calculate angular distance
        angle_diff = abs(lon1 - lon2) % 360
        
        # Check each possible aspect
        for aspect in AspectType:
            aspect_orb = abs(angle_diff - aspect.value)
            if aspect_orb <= orb:
                return aspect, aspect_orb
        
        return None
    
    @staticmethod
    def calculate_synastry_strength(
        aspect: AspectType,
        orb: float,
        planet1_type: str,
        planet2_type: str
    ) -> float:
        """
        Calculate strength of synastry aspect
        
        Args:
            aspect: Type of aspect
            orb: Orb of aspect in degrees
            planet1_type: Type of first planet (personal/social/outer)
            planet2_type: Type of second planet (personal/social/outer)
            
        Returns:
            Aspect strength as float between 0 and 1
        """
        # Get aspect weight
        if aspect in [AspectType.CONJUNCTION, AspectType.OPPOSITION, 
                     AspectType.TRINE, AspectType.SQUARE, AspectType.SEXTILE]:
            aspect_weight = SynastryChart.MAJOR_ASPECT_WEIGHT
        elif aspect in [AspectType.SEMISEXTILE, AspectType.SEMISQUARE, 
                       AspectType.SESQUISQUARE, AspectType.QUINCUNX]:
            aspect_weight = SynastryChart.MINOR_ASPECT_WEIGHT
        else:
            aspect_weight = SynastryChart.HARMONIC_ASPECT_WEIGHT
        
        # Get planet weights
        planet_weights = {
            'personal': SynastryChart.PERSONAL_PLANET_WEIGHT,
            'social': SynastryChart.SOCIAL_PLANET_WEIGHT,
            'outer': SynastryChart.OUTER_PLANET_WEIGHT
        }
        
        planet1_weight = planet_weights.get(planet1_type, 1.0)
        planet2_weight = planet_weights.get(planet2_type, 1.0)
        
        # Calculate orb factor (closer = stronger)
        orb_factor = 1.0 - (orb / 1.0)  # Normalize orb to 0-1 range
        
        # Calculate final strength
        strength = aspect_weight * planet1_weight * planet2_weight * orb_factor
        
        return min(max(strength, 0.0), 1.0)  # Ensure result is between 0 and 1
    
    @staticmethod
    def get_planet_type(planet_name: str) -> str:
        """
        Get type of planet for synastry calculations
        
        Args:
            planet_name: Name of the planet
            
        Returns:
            Planet type (personal/social/outer)
        """
        personal_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
        social_planets = ['Jupiter', 'Saturn']
        outer_planets = ['Uranus', 'Neptune', 'Pluto']
        
        if planet_name in personal_planets:
            return 'personal'
        elif planet_name in social_planets:
            return 'social'
        elif planet_name in outer_planets:
            return 'outer'
        else:
            return 'other' 

class SolarArcDirection:
    """Class for solar arc direction calculations and properties"""
    
    # Direction types
    DIRECT = 1    # Forward direction (future)
    CONVERSE = 2  # Backward direction (past)
    
    @staticmethod
    def calculate_solar_arc(
        birth_date: datetime,
        target_date: datetime,
        birth_sun_pos: float,
        target_sun_pos: float
    ) -> float:
        """
        Calculate solar arc for given dates
        
        Args:
            birth_date: Birth date and time
            target_date: Target date for direction
            birth_sun_pos: Sun's position at birth
            target_sun_pos: Sun's position at target date
            
        Returns:
            Solar arc in degrees
        """
        # Calculate solar arc
        solar_arc = (target_sun_pos - birth_sun_pos) % 360
        
        return solar_arc
    
    @staticmethod
    def calculate_directed_position(
        original_pos: float,
        solar_arc: float,
        direction_type: int = DIRECT
    ) -> float:
        """
        Calculate directed position using solar arc
        
        Args:
            original_pos: Original position in degrees
            solar_arc: Solar arc in degrees
            direction_type: Type of direction (DIRECT/CONVERSE)
            
        Returns:
            Directed position in degrees
        """
        if direction_type == SolarArcDirection.DIRECT:
            # For direct direction, add the arc
            directed_pos = (original_pos + solar_arc) % 360
        else:
            # For converse direction, subtract the arc
            directed_pos = (original_pos - solar_arc) % 360
        
        return directed_pos
    
    @staticmethod
    def calculate_directed_aspect(
        directed_pos: float,
        natal_pos: float,
        orb: float = 1.0
    ) -> Optional[Tuple[AspectType, float]]:
        """
        Calculate aspect between directed and natal positions
        
        Args:
            directed_pos: Directed position in degrees
            natal_pos: Natal position in degrees
            orb: Orb for aspect in degrees (default: 1.0)
            
        Returns:
            Tuple of (AspectType, orb) if aspect exists, None otherwise
        """
        # Calculate angular distance
        angle_diff = abs(directed_pos - natal_pos) % 360
        
        # Check each possible aspect
        for aspect in AspectType:
            aspect_orb = abs(angle_diff - aspect.value)
            if aspect_orb <= orb:
                return aspect, aspect_orb
        
        return None
    
    @staticmethod
    def calculate_direction_strength(
        aspect: AspectType,
        orb: float,
        point_type: str
    ) -> float:
        """
        Calculate strength of directed aspect
        
        Args:
            aspect: Type of aspect
            orb: Orb of aspect in degrees
            point_type: Type of point (planet/angle/house)
            
        Returns:
            Aspect strength as float between 0 and 1
        """
        # Get aspect weight
        if aspect in [AspectType.CONJUNCTION, AspectType.OPPOSITION, 
                     AspectType.TRINE, AspectType.SQUARE, AspectType.SEXTILE]:
            aspect_weight = 1.0
        elif aspect in [AspectType.SEMISEXTILE, AspectType.SEMISQUARE, 
                       AspectType.SESQUISQUARE, AspectType.QUINCUNX]:
            aspect_weight = 0.7
        else:
            aspect_weight = 0.5
        
        # Get point weight
        point_weights = {
            'planet': 1.0,
            'angle': 0.8,
            'house': 0.6
        }
        point_weight = point_weights.get(point_type, 0.5)
        
        # Calculate orb factor (closer = stronger)
        orb_factor = 1.0 - (orb / 1.0)  # Normalize orb to 0-1 range
        
        # Calculate final strength
        strength = aspect_weight * point_weight * orb_factor
        
        return min(max(strength, 0.0), 1.0)  # Ensure result is between 0 and 1 

class HouseSystem(Enum):
    """House systems for astrological calculations"""
    PLACIDUS = "P"      # Placidus house system
    KOCH = "K"         # Koch house system
    EQUAL = "E"        # Equal house system
    WHOLE_SIGN = "W"   # Whole sign house system
    CAMPANUS = "C"     # Campanus house system
    REGIOMONTANUS = "R" # Regiomontanus house system
    MERIDIAN = "M"     # Meridian house system
    MORINUS = "O"      # Morinus house system

class ProgressedChart:
    """Class for progressed chart calculations and properties"""
    
    # Progression rates
    SECONDARY_RATE = 1.0  # 1 day = 1 year
    TERTIARY_RATE = 12.0  # 1 day = 1 month
    
    @staticmethod
    def calculate_progressed_date(
        birth_date: datetime,
        target_date: datetime,
        progression_type: ProgressionType = ProgressionType.SECONDARY
    ) -> datetime:
        """
        Calculate progressed date for given target date
        
        Args:
            birth_date: Birth date and time
            target_date: Target date to calculate progression for
            progression_type: Type of progression to use
            
        Returns:
            Progressed date and time
        """
        # Calculate years between birth and target
        years_diff = target_date.year - birth_date.year
        months_diff = target_date.month - birth_date.month
        days_diff = target_date.day - birth_date.day
        
        # Convert to total days
        total_days = years_diff * 365 + months_diff * 30 + days_diff
        
        # Calculate progressed days based on progression type
        if progression_type == ProgressionType.SECONDARY:
            progressed_days = total_days * ProgressedChart.SECONDARY_RATE
        elif progression_type == ProgressionType.TERTIARY:
            progressed_days = total_days * ProgressedChart.TERTIARY_RATE
        else:
            raise ValueError(f"Invalid progression type: {progression_type}")
        
        # Calculate progressed date
        progressed_date = birth_date + timedelta(days=progressed_days)
        
        return progressed_date
    
    @staticmethod
    def calculate_solar_arc(
        birth_date: datetime,
        target_date: datetime,
        birth_sun_pos: float,
        progressed_sun_pos: float
    ) -> float:
        """
        Calculate solar arc for given dates
        
        Args:
            birth_date: Birth date and time
            target_date: Target date to calculate progression for
            birth_sun_pos: Sun's position at birth
            progressed_sun_pos: Sun's position at target date
            
        Returns:
            Solar arc in degrees
        """
        # Calculate solar arc
        solar_arc = (progressed_sun_pos - birth_sun_pos) % 360
        
        return solar_arc
    
    @staticmethod
    def calculate_progressed_position(
        original_pos: float,
        solar_arc: float,
        progression_type: ProgressionType = ProgressionType.SECONDARY
    ) -> float:
        """
        Calculate progressed position
        
        Args:
            original_pos: Original position in degrees
            solar_arc: Solar arc in degrees
            progression_type: Type of progression to use
            
        Returns:
            Progressed position in degrees
        """
        if progression_type == ProgressionType.SOLAR_ARC:
            # For solar arc, add the arc to the original position
            progressed_pos = (original_pos + solar_arc) % 360
        else:
            # For secondary and tertiary, use the original position
            # as the progressed position is calculated from the progressed date
            progressed_pos = original_pos
        
        return progressed_pos 