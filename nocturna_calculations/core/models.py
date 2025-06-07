"""
Core models for celestial bodies and points
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CelestialBody(BaseModel):
    """Base class for celestial bodies"""
    name: str
    longitude: float
    latitude: float = 0.0
    distance: Optional[float] = None
    speed: Optional[float] = None
    is_retrograde: bool = False

class FixedStar(CelestialBody):
    """Model for fixed stars"""
    magnitude: float
    spectral_type: Optional[str] = None
    constellation: Optional[str] = None
    traditional_name: Optional[str] = None
    modern_name: Optional[str] = None

class Asteroid(CelestialBody):
    """Model for asteroids"""
    number: Optional[int] = None
    discovery_date: Optional[datetime] = None
    discoverer: Optional[str] = None
    orbital_period: Optional[float] = None

class LunarNode(CelestialBody):
    """Model for lunar nodes"""
    node_type: str = Field(..., description="Type of lunar node (NORTH or SOUTH)")
    draconic_month: Optional[float] = None
    eclipse_related: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "North Node",
                "node_type": "NORTH",
                "longitude": 45.0,
                "latitude": 0.0,
                "draconic_month": 27.2122,
                "eclipse_related": True
            }
        }
    } 