"""
Aspect class for astrological calculations
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from .constants import AspectType, CoordinateSystem
from .position import Position

@dataclass(frozen=True)
class Aspect:
    """Represents an astrological aspect between two positions"""
    
    planet1: str
    planet2: str
    angle: float
    orb: float
    aspect_type: str
    applying: Optional[bool] = None
    
    def __post_init__(self):
        """Validate aspect data"""
        # Validate angle
        if not 0 <= self.angle <= 360:
            raise ValueError("Angle must be between 0 and 360 degrees")
        
        # Validate orb
        if self.orb < 0:
            raise ValueError("Orb cannot be negative")
        
        # Validate aspect type
        if self.aspect_type not in [t.name.lower() for t in AspectType]:
            raise ValueError(f"Invalid aspect type: {self.aspect_type}")
    
    @property
    def strength(self) -> float:
        """Calculate aspect strength based on orb"""
        # Get maximum orb for this aspect type
        max_orb = AspectType[self.aspect_type.upper()].value / 10
        
        # Avoid division by zero
        if max_orb <= 0:
            return 1.0 if self.orb == 0 else 0.0
        
        # Calculate strength (1.0 for exact aspect, 0.0 for orb >= max_orb)
        return max(0.0, 1.0 - (self.orb / max_orb))
    
    @property
    def is_partile(self) -> bool:
        """Check if aspect is partile (orb <= 1 degree)"""
        return self.orb <= 1.0
    
    @property
    def is_exact(self) -> bool:
        """Check if aspect is exact (orb = 0)"""
        return self.orb == 0.0
    
    @classmethod
    def detect(cls, pos1: Position, pos2: Position, orbs: Dict[str, float]) -> Optional['Aspect']:
        """
        Detect aspect between two positions
        
        Args:
            pos1: First position
            pos2: Second position
            orbs: Dictionary of orbs for different aspects
            
        Returns:
            Aspect if found, None otherwise
        """
        # Calculate angular distance
        distance = pos1.angular_distance(pos2)
        
        # Check each aspect type
        for aspect_type in AspectType:
            # Get orb for this aspect type
            orb = orbs.get(aspect_type.name.lower(), aspect_type.value / 10)
            
            # Check if positions are in aspect
            if abs(distance - aspect_type.value) <= orb:
                # Calculate exact orb
                exact_orb = abs(distance - aspect_type.value)
                
                # Determine if applying
                applying = pos1.is_applying_to(pos2, aspect_type.value)
                
                return cls(
                    planet1=pos1.planet if hasattr(pos1, 'planet') else "Unknown",
                    planet2=pos2.planet if hasattr(pos2, 'planet') else "Unknown",
                    angle=distance,
                    orb=exact_orb,
                    aspect_type=aspect_type.name.lower(),
                    applying=applying
                )
        
        return None
    
    @classmethod
    def detect_all(cls, pos1: Position, pos2: Position, orbs: Dict[str, float]) -> List['Aspect']:
        """
        Detect all aspects between two positions
        
        Args:
            pos1: First position
            pos2: Second position
            orbs: Dictionary of orbs for different aspects
            
        Returns:
            List of aspects
        """
        aspects = []
        
        # Calculate angular distance
        distance = pos1.angular_distance(pos2)
        
        # Check each aspect type
        for aspect_type in AspectType:
            # Get orb for this aspect type
            orb = orbs.get(aspect_type.name.lower(), aspect_type.value / 10)
            
            # Check if positions are in aspect
            if abs(distance - aspect_type.value) <= orb:
                # Calculate exact orb
                exact_orb = abs(distance - aspect_type.value)
                
                # Determine if applying
                applying = pos1.is_applying_to(pos2, aspect_type.value)
                
                aspects.append(cls(
                    planet1=pos1.planet if hasattr(pos1, 'planet') else "Unknown",
                    planet2=pos2.planet if hasattr(pos2, 'planet') else "Unknown",
                    angle=distance,
                    orb=exact_orb,
                    aspect_type=aspect_type.name.lower(),
                    applying=applying
                ))
        
        return aspects 