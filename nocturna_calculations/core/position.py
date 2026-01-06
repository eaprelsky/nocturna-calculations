"""
Position class for astrological calculations
"""
from dataclasses import dataclass
from typing import Optional
from .constants import CoordinateSystem

@dataclass(frozen=True)
class Position:
    """Represents a position in astrological space"""
    
    longitude: float
    latitude: float
    distance: float
    system: CoordinateSystem
    speed_long: Optional[float] = None
    speed_lat: Optional[float] = None
    speed_dist: Optional[float] = None
    
    def __post_init__(self):
        """Validate position data"""
        # Normalize longitude to 0-360 range
        if self.longitude < 0:
            object.__setattr__(self, 'longitude', self.longitude + 360)
        elif self.longitude >= 360:
            object.__setattr__(self, 'longitude', self.longitude % 360)
        
        # Validate latitude
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        
        # Validate distance
        if self.distance < 0:
            raise ValueError("Distance cannot be negative")
    
    def angular_distance(self, other: 'Position') -> float:
        """
        Calculate angular distance between two positions
        
        Args:
            other: Another position
            
        Returns:
            Angular distance in degrees
        """
        # For now, we only handle ecliptic coordinates
        if self.system != CoordinateSystem.ECLIPTIC or other.system != CoordinateSystem.ECLIPTIC:
            raise NotImplementedError("Only ecliptic coordinates are supported for now")
        
        # Calculate angular distance
        diff = abs(self.longitude - other.longitude)
        return min(diff, 360 - diff)
    
    def is_applying_to(self, other: 'Position', aspect_angle: float) -> bool:
        """
        Check if this position is applying to another position
        
        Args:
            other: Another position
            aspect_angle: Angle of the aspect
            
        Returns:
            True if applying, False if separating
        """
        if self.system != CoordinateSystem.ECLIPTIC or other.system != CoordinateSystem.ECLIPTIC:
            raise NotImplementedError("Only ecliptic coordinates are supported for now")
        
        # Calculate angular distance
        diff = other.longitude - self.longitude
        
        # Normalize to -180 to 180 range
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        # Check if applying
        return abs(diff) < abs(aspect_angle) 