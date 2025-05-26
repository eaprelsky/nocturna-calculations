"""
House system calculations for astrological charts
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional, List
import math
import swisseph as swe
from ..core.constants import HouseSystem
from datetime import datetime
from nocturna_calculations.calculations.utils import (
    calculate_sidereal_time,
    calculate_obliquity,
    calculate_ascendant,
    calculate_mc,
    calculate_house_cusps,
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
        
        # Calculate house cusps
        return calculate_house_cusps(asc, mc, self._latitude, self._obliquity, 'P')
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate ascendant
        # Formula: tan(A) = (cos(ε) * sin(LST)) / (cos(LST) * cos(φ) - sin(ε) * sin(φ))
        # where A is ascendant, ε is obliquity, LST is local sidereal time, φ is latitude
        numerator = math.cos(obl_rad) * math.sin(sidereal_time)
        denominator = math.cos(sidereal_time) * math.cos(lat_rad) - math.sin(obl_rad) * math.sin(lat_rad)
        
        if abs(denominator) < 1e-10:
            # Handle polar regions
            if latitude > 0:
                return 0.0  # North Pole
            else:
                return 180.0  # South Pole
        
        ascendant = math.degrees(math.atan2(numerator, denominator))
        return (ascendant + 360.0) % 360.0
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate MC
        # Formula: tan(MC) = tan(LST) / cos(ε)
        # where MC is midheaven, LST is local sidereal time, ε is obliquity
        mc = math.degrees(math.atan2(
            math.tan(sidereal_time),
            math.cos(obl_rad)
        ))
        return (mc + 360.0) % 360.0

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
        
        # Calculate house cusps
        return calculate_house_cusps(asc, mc, self._latitude, self._obliquity, 'K')
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate ascendant
        # Formula: tan(A) = (cos(ε) * sin(LST)) / (cos(LST) * cos(φ) - sin(ε) * sin(φ))
        # where A is ascendant, ε is obliquity, LST is local sidereal time, φ is latitude
        numerator = math.cos(obl_rad) * math.sin(sidereal_time)
        denominator = math.cos(sidereal_time) * math.cos(lat_rad) - math.sin(obl_rad) * math.sin(lat_rad)
        
        if abs(denominator) < 1e-10:
            # Handle polar regions
            if latitude > 0:
                return 0.0  # North Pole
            else:
                return 180.0  # South Pole
        
        ascendant = math.degrees(math.atan2(numerator, denominator))
        return (ascendant + 360.0) % 360.0
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate MC
        # Formula: tan(MC) = tan(LST) / cos(ε)
        # where MC is midheaven, LST is local sidereal time, ε is obliquity
        mc = math.degrees(math.atan2(
            math.tan(sidereal_time),
            math.cos(obl_rad)
        ))
        return (mc + 360.0) % 360.0

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
        
        # Calculate house cusps
        return calculate_house_cusps(asc, 0, self._latitude, self._obliquity, 'E')
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate ascendant
        # Formula: tan(A) = (cos(ε) * sin(LST)) / (cos(LST) * cos(φ) - sin(ε) * sin(φ))
        # where A is ascendant, ε is obliquity, LST is local sidereal time, φ is latitude
        numerator = math.cos(obl_rad) * math.sin(sidereal_time)
        denominator = math.cos(sidereal_time) * math.cos(lat_rad) - math.sin(obl_rad) * math.sin(lat_rad)
        
        if abs(denominator) < 1e-10:
            # Handle polar regions
            if latitude > 0:
                return 0.0  # North Pole
            else:
                return 180.0  # South Pole
        
        ascendant = math.degrees(math.atan2(numerator, denominator))
        return (ascendant + 360.0) % 360.0

class WholeSignHouseSystem(BaseHouseSystem):
    """Whole sign house system implementation"""
    
    def __init__(self):
        """Initialize Whole sign house system calculator"""
        super().__init__()
        self.system = HouseSystem.WHOLE_SIGN
    
    def _calculate_house_cusps(self) -> List[float]:
        """Calculate house cusps using the Whole sign house system"""
        # Calculate LST and obliquity
        lst = calculate_sidereal_time(self._julian_day, self._longitude)
        
        # Calculate ascendant
        asc = calculate_ascendant(lst, self._latitude, self._obliquity)
        
        # Calculate house cusps
        return calculate_house_cusps(asc, 0, self._latitude, self._obliquity, 'W')
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate ascendant
        # Formula: tan(A) = (cos(ε) * sin(LST)) / (cos(LST) * cos(φ) - sin(ε) * sin(φ))
        # where A is ascendant, ε is obliquity, LST is local sidereal time, φ is latitude
        numerator = math.cos(obl_rad) * math.sin(sidereal_time)
        denominator = math.cos(sidereal_time) * math.cos(lat_rad) - math.sin(obl_rad) * math.sin(lat_rad)
        
        if abs(denominator) < 1e-10:
            # Handle polar regions
            if latitude > 0:
                return 0.0  # North Pole
            else:
                return 180.0  # South Pole
        
        ascendant = math.degrees(math.atan2(numerator, denominator))
        return (ascendant + 360.0) % 360.0

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
        
        # Calculate house cusps
        return calculate_house_cusps(asc, mc, self._latitude, self._obliquity, 'C')
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate ascendant
        # Formula: tan(A) = (cos(ε) * sin(LST)) / (cos(LST) * cos(φ) - sin(ε) * sin(φ))
        # where A is ascendant, ε is obliquity, LST is local sidereal time, φ is latitude
        numerator = math.cos(obl_rad) * math.sin(sidereal_time)
        denominator = math.cos(sidereal_time) * math.cos(lat_rad) - math.sin(obl_rad) * math.sin(lat_rad)
        
        if abs(denominator) < 1e-10:
            # Handle polar regions
            if latitude > 0:
                return 0.0  # North Pole
            else:
                return 180.0  # South Pole
        
        ascendant = math.degrees(math.atan2(numerator, denominator))
        return (ascendant + 360.0) % 360.0
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate MC
        # Formula: tan(MC) = tan(LST) / cos(ε)
        # where MC is midheaven, LST is local sidereal time, ε is obliquity
        mc = math.degrees(math.atan2(
            math.tan(sidereal_time),
            math.cos(obl_rad)
        ))
        return (mc + 360.0) % 360.0

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
        
        # Calculate house cusps
        return calculate_house_cusps(asc, mc, self._latitude, self._obliquity, 'R')
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate ascendant
        # Formula: tan(A) = (cos(ε) * sin(LST)) / (cos(LST) * cos(φ) - sin(ε) * sin(φ))
        # where A is ascendant, ε is obliquity, LST is local sidereal time, φ is latitude
        numerator = math.cos(obl_rad) * math.sin(sidereal_time)
        denominator = math.cos(sidereal_time) * math.cos(lat_rad) - math.sin(obl_rad) * math.sin(lat_rad)
        
        if abs(denominator) < 1e-10:
            # Handle polar regions
            if latitude > 0:
                return 0.0  # North Pole
            else:
                return 180.0  # South Pole
        
        ascendant = math.degrees(math.atan2(numerator, denominator))
        return (ascendant + 360.0) % 360.0
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate MC
        # Formula: tan(MC) = tan(LST) / cos(ε)
        # where MC is midheaven, LST is local sidereal time, ε is obliquity
        mc = math.degrees(math.atan2(
            math.tan(sidereal_time),
            math.cos(obl_rad)
        ))
        return (mc + 360.0) % 360.0

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
        
        # Calculate house cusps
        return calculate_house_cusps(asc, mc, self._latitude, self._obliquity, 'M')
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate ascendant
        # Formula: tan(A) = (cos(ε) * sin(LST)) / (cos(LST) * cos(φ) - sin(ε) * sin(φ))
        # where A is ascendant, ε is obliquity, LST is local sidereal time, φ is latitude
        numerator = math.cos(obl_rad) * math.sin(sidereal_time)
        denominator = math.cos(sidereal_time) * math.cos(lat_rad) - math.sin(obl_rad) * math.sin(lat_rad)
        
        if abs(denominator) < 1e-10:
            # Handle polar regions
            if latitude > 0:
                return 0.0  # North Pole
            else:
                return 180.0  # South Pole
        
        ascendant = math.degrees(math.atan2(numerator, denominator))
        return (ascendant + 360.0) % 360.0
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate MC
        # Formula: tan(MC) = tan(LST) / cos(ε)
        # where MC is midheaven, LST is local sidereal time, ε is obliquity
        mc = math.degrees(math.atan2(
            math.tan(sidereal_time),
            math.cos(obl_rad)
        ))
        return (mc + 360.0) % 360.0

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
        
        # Calculate house cusps
        return calculate_house_cusps(asc, mc, self._latitude, self._obliquity, 'O')
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate ascendant
        # Formula: tan(A) = (cos(ε) * sin(LST)) / (cos(LST) * cos(φ) - sin(ε) * sin(φ))
        # where A is ascendant, ε is obliquity, LST is local sidereal time, φ is latitude
        numerator = math.cos(obl_rad) * math.sin(sidereal_time)
        denominator = math.cos(sidereal_time) * math.cos(lat_rad) - math.sin(obl_rad) * math.sin(lat_rad)
        
        if abs(denominator) < 1e-10:
            # Handle polar regions
            if latitude > 0:
                return 0.0  # North Pole
            else:
                return 180.0  # South Pole
        
        ascendant = math.degrees(math.atan2(numerator, denominator))
        return (ascendant + 360.0) % 360.0
    
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
        # Convert to radians
        lat_rad = math.radians(latitude)
        long_rad = math.radians(longitude)
        obl_rad = math.radians(obliquity)
        
        # Calculate sidereal time (simplified)
        # TODO: Implement proper sidereal time calculation
        sidereal_time = 0.0
        
        # Calculate MC
        # Formula: tan(MC) = tan(LST) / cos(ε)
        # where MC is midheaven, LST is local sidereal time, ε is obliquity
        mc = math.degrees(math.atan2(
            math.tan(sidereal_time),
            math.cos(obl_rad)
        ))
        return (mc + 360.0) % 360.0

def get_house_system(system_type: HouseSystem) -> BaseHouseSystem:
    """
    Factory function to get a house system calculator.
    
    Args:
        system_type: Type of house system to create
        
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
        raise ValueError(f"Unknown house system: {system_type}")
    
    return systems[system_type]() 