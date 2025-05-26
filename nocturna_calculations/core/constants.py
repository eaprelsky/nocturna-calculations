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