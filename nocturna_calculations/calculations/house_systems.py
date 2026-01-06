"""
House system calculations for astrological charts
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, List
import math
import swisseph as swe
from ..core.constants import HouseSystem
from datetime import datetime
from .astro_math import (
    calculate_sidereal_time,
    calculate_obliquity,
    calculate_ascendant,
    calculate_mc,
    normalize_angle
)

class BaseHouseSystem(ABC):
    """Base class for house system calculations"""
    
    def __init__(self):
        """Initialize the house system calculator"""
        self._julian_day: Optional[float] = None
        self._latitude: Optional[float] = None
        self._longitude: Optional[float] = None
        self._obliquity: Optional[float] = None
    
    def calculate_cusps(
        self,
        latitude: float,
        longitude: float,
        date_time: Optional[datetime] = None,
        obliquity: Optional[float] = None
    ) -> List[float]:
        """
        Calculate house cusps for the given location and time.
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            date_time: Date and time for calculation (optional)
            obliquity: Obliquity of the ecliptic in degrees (optional)
            
        Returns:
            List of 12 house cusps in degrees
        """
        # Validate coordinates
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        
        # Store parameters
        self._latitude = latitude
        self._longitude = longitude
        
        # Calculate Julian day if date_time is provided
        if date_time is not None:
            self._julian_day = swe.julday(
                date_time.year,
                date_time.month,
                date_time.day,
                date_time.hour + date_time.minute/60.0 + date_time.second/3600.0
            )
        
        # Calculate or use provided obliquity
        if obliquity is not None:
            self._obliquity = obliquity
        elif self._julian_day is not None:
            self._obliquity = calculate_obliquity(self._julian_day)
        
        # Calculate house cusps
        return self._calculate_house_cusps()
    
    @abstractmethod
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps for the specific house system"""
        pass

class PlacidusHouseSystem(BaseHouseSystem):
    """Placidus house system implementation"""
    
    def __init__(self):
        """Initialize Placidus house system calculator"""
        super().__init__()
        self.system = HouseSystem.PLACIDUS
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Placidus system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant and MC
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        mc = calculate_mc(lst, self._obliquity)
        
        # Calculate house cusps using Swiss Ephemeris
        cusps = swe.swe_houses(self._julian_day, 0, self._latitude, self._longitude, b'P')[0]
        return list(cusps)
    
    def _calculate_ascendant(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Ascendant (1st house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Ascendant in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate ascendant using the utility function
        return calculate_ascendant(lst, latitude, obliquity)
    
    def _calculate_mc(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Midheaven (10th house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Midheaven in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate MC using the utility function
        return calculate_mc(lst, obliquity)

class KochHouseSystem(BaseHouseSystem):
    """Koch house system implementation"""
    
    def __init__(self):
        """Initialize Koch house system calculator"""
        super().__init__()
        self.system = HouseSystem.KOCH
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Koch system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant and MC
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        mc = calculate_mc(lst, self._obliquity)
        
        # Calculate house cusps using Swiss Ephemeris
        cusps = swe.swe_houses(self._julian_day, 0, self._latitude, self._longitude, b'K')[0]
        return list(cusps)
    
    def _calculate_ascendant(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Ascendant (1st house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Ascendant in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate ascendant using the utility function
        return calculate_ascendant(lst, latitude, obliquity)
    
    def _calculate_mc(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Midheaven (10th house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Midheaven in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate MC using the utility function
        return calculate_mc(lst, obliquity)

class EqualHouseSystem(BaseHouseSystem):
    """Equal house system implementation"""
    
    def __init__(self):
        """Initialize Equal house system calculator"""
        super().__init__()
        self.system = HouseSystem.EQUAL
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Equal house system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        
        # Calculate equal house cusps (each 30 degrees from ascendant)
        cusps = []
        for i in range(12):
            cusp = (asc + i * 30) % 360
            cusps.append(cusp)
        
        return cusps

class WholeSignHouseSystem(BaseHouseSystem):
    """Whole sign house system implementation"""
    
    def __init__(self):
        """Initialize Whole sign house system calculator"""
        super().__init__()
        self.system = HouseSystem.WHOLE_SIGN
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Whole sign system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        
        # Calculate whole sign cusps (each 30 degrees from 0 Aries)
        cusps = []
        for i in range(12):
            cusp = i * 30
            cusps.append(cusp)
        
        return cusps

class CampanusHouseSystem(BaseHouseSystem):
    """Campanus house system implementation"""
    
    def __init__(self):
        """Initialize Campanus house system calculator"""
        super().__init__()
        self.system = HouseSystem.CAMPANUS
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Campanus system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant and MC
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        mc = calculate_mc(lst, self._obliquity)
        
        # Calculate house cusps using Swiss Ephemeris
        cusps = swe.swe_houses(self._julian_day, 0, self._latitude, self._longitude, b'C')[0]
        return list(cusps)
    
    def _calculate_ascendant(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Ascendant (1st house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Ascendant in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate ascendant using the utility function
        return calculate_ascendant(lst, latitude, obliquity)
    
    def _calculate_mc(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Midheaven (10th house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Midheaven in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate MC using the utility function
        return calculate_mc(lst, obliquity)

class RegiomontanusHouseSystem(BaseHouseSystem):
    """Regiomontanus house system implementation"""
    
    def __init__(self):
        """Initialize Regiomontanus house system calculator"""
        super().__init__()
        self.system = HouseSystem.REGIOMONTANUS
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Regiomontanus system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant and MC
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        mc = calculate_mc(lst, self._obliquity)
        
        # Calculate house cusps using Swiss Ephemeris
        cusps = swe.swe_houses(self._julian_day, 0, self._latitude, self._longitude, b'R')[0]
        return list(cusps)
    
    def _calculate_ascendant(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Ascendant (1st house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Ascendant in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate ascendant using the utility function
        return calculate_ascendant(lst, latitude, obliquity)
    
    def _calculate_mc(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Midheaven (10th house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Midheaven in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate MC using the utility function
        return calculate_mc(lst, obliquity)

class MeridianHouseSystem(BaseHouseSystem):
    """Meridian house system implementation"""
    
    def __init__(self):
        """Initialize Meridian house system calculator"""
        super().__init__()
        self.system = HouseSystem.MERIDIAN
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Meridian system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant and MC
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        mc = calculate_mc(lst, self._obliquity)
        
        # Calculate house cusps using Swiss Ephemeris
        cusps = swe.swe_houses(self._julian_day, 0, self._latitude, self._longitude, b'M')[0]
        return list(cusps)
    
    def _calculate_ascendant(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Ascendant (1st house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Ascendant in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate ascendant using the utility function
        return calculate_ascendant(lst, latitude, obliquity)
    
    def _calculate_mc(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Midheaven (10th house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Midheaven in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate MC using the utility function
        return calculate_mc(lst, obliquity)

class MorinusHouseSystem(BaseHouseSystem):
    """Morinus house system implementation"""
    
    def __init__(self):
        """Initialize Morinus house system calculator"""
        super().__init__()
        self.system = HouseSystem.MORINUS
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Morinus system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant and MC
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        mc = calculate_mc(lst, self._obliquity)
        
        # Calculate house cusps using Swiss Ephemeris
        cusps = swe.swe_houses(self._julian_day, 0, self._latitude, self._longitude, b'O')[0]
        return list(cusps)
    
    def _calculate_ascendant(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Ascendant (1st house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Ascendant in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate ascendant using the utility function
        return calculate_ascendant(lst, latitude, obliquity)
    
    def _calculate_mc(
        self,
        latitude: float,
        longitude: float,
        obliquity: float
    ) -> float:
        """
        Calculate the Midheaven (10th house cusp)
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            obliquity: Obliquity of the ecliptic in degrees
            
        Returns:
            Midheaven in degrees
        """
        # Calculate sidereal time
        lst = calculate_sidereal_time(self._julian_day, longitude)
        
        # Calculate MC using the utility function
        return calculate_mc(lst, obliquity)

def get_house_system(system_type: HouseSystem) -> BaseHouseSystem:
    """
    Get house system calculator for the specified system type
    
    Args:
        system_type: Type of house system to use
        
    Returns:
        House system calculator instance
    """
    systems = {
        HouseSystem.PLACIDUS: PlacidusHouseSystem,
        HouseSystem.KOCH: KochHouseSystem,
        HouseSystem.EQUAL: EqualHouseSystem,
        HouseSystem.WHOLE_SIGN: WholeSignHouseSystem,
        HouseSystem.CAMPANUS: CampanusHouseSystem,
        HouseSystem.REGIOMONTANUS: RegiomontanusHouseSystem,
        HouseSystem.MERIDIAN: MeridianHouseSystem,
        HouseSystem.MORINUS: MorinusHouseSystem
    }
    
    if system_type not in systems:
        raise ValueError(f"Unsupported house system: {system_type}")
    
    return systems[system_type]() 