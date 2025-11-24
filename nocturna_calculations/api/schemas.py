"""
Pydantic schemas for the Nocturna Calculations API.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field

# Base schemas
class CalculationRequest(BaseModel):
    """Base schema for calculation requests."""
    chart_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class DirectCalculationRequest(BaseModel):
    """Schema for direct calculation requests with date/time/location data."""
    date: str
    time: str
    latitude: float
    longitude: float
    timezone: str = "UTC"
    planets: Optional[List[str]] = None
    aspects: Optional[List[str]] = None
    house_system: Optional[str] = None

class CalculationResponse(BaseModel):
    """Base schema for calculation responses."""
    success: bool = True
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# Planetary positions
class PlanetaryPosition(BaseModel):
    """Planetary position data."""
    planet: str
    longitude: float
    latitude: float
    distance: float
    speed: float
    is_retrograde: bool
    house: Optional[int] = None
    sign: str
    degree: float
    minute: float
    second: float

class PlanetaryPositionsResponse(CalculationResponse):
    """Response for planetary positions calculation."""
    data: List[PlanetaryPosition]

# Aspects
class Aspect(BaseModel):
    """Aspect data."""
    planet1: str
    planet2: str
    aspect_type: str
    orb: float
    applying: bool
    exact_time: Optional[datetime] = None

class AspectsResponse(CalculationResponse):
    """Response for aspects calculation."""
    data: List[Aspect]

# Houses
class House(BaseModel):
    """House data."""
    number: int
    longitude: float
    latitude: float
    sign: str
    degree: float
    minute: float
    second: float

class HousesResponse(CalculationResponse):
    """Response for houses calculation."""
    data: List[House]

# Simple response schemas for API tests compatibility
class SimpleHousesResponse(BaseModel):
    """Simple response for houses calculation."""
    houses: List[House]

# Fixed stars
class FixedStar(BaseModel):
    """Fixed star data."""
    name: str
    longitude: float
    latitude: float
    magnitude: float
    constellation: str
    is_conjunct: bool
    orb: Optional[float] = None

class FixedStarsResponse(CalculationResponse):
    """Response for fixed stars calculation."""
    data: List[FixedStar]

# Arabic parts
class ArabicPart(BaseModel):
    """Arabic part data."""
    name: str
    longitude: float
    latitude: float
    sign: str
    degree: float
    minute: float
    second: float
    aspects: Optional[List[Aspect]] = None

class ArabicPartsResponse(CalculationResponse):
    """Response for Arabic parts calculation."""
    data: List[ArabicPart]

# Dignities
class Dignity(BaseModel):
    """Dignity data."""
    planet: str
    sign: str
    rulership: str
    exaltation: str
    detriment: str
    fall: str
    score: float

class DignitiesResponse(CalculationResponse):
    """Response for dignities calculation."""
    data: List[Dignity]

# Antiscia
class AntisciaPoint(BaseModel):
    """Antiscia point data."""
    planet: str
    longitude: float
    latitude: float
    sign: str
    degree: float
    minute: float
    second: float
    aspects: Optional[List[Aspect]] = None

class AntisciaResponse(CalculationResponse):
    """Response for antiscia calculation."""
    data: List[AntisciaPoint]

# Declinations
class Declination(BaseModel):
    """Declination data."""
    planet: str
    declination: float
    parallel: Optional[float] = None
    is_parallel: bool = False

class DeclinationsResponse(CalculationResponse):
    """Response for declinations calculation."""
    data: List[Declination]

# Harmonics
class HarmonicChart(BaseModel):
    """Harmonic chart data."""
    harmonic: int
    positions: List[PlanetaryPosition]
    aspects: Optional[List[Aspect]] = None

class HarmonicsResponse(CalculationResponse):
    """Response for harmonics calculation."""
    data: List[HarmonicChart]

# Rectification
class RectificationEvent(BaseModel):
    """Rectification event data."""
    description: str
    date: datetime
    confidence: float
    method: str

class RectificationResponse(CalculationResponse):
    """Response for rectification calculation."""
    data: List[RectificationEvent]

# Primary directions
class PrimaryDirection(BaseModel):
    """Primary direction data."""
    promissor: str
    significator: str
    arc: float
    date: datetime
    type: str
    mundane: bool

class PrimaryDirectionsResponse(CalculationResponse):
    """Response for primary directions calculation."""
    data: List[PrimaryDirection]

# Secondary progressions
class SecondaryProgression(BaseModel):
    """Secondary progression data."""
    date: datetime
    positions: List[PlanetaryPosition]
    aspects: Optional[List[Aspect]] = None
    houses: Optional[List[House]] = None

class SecondaryProgressionsResponse(CalculationResponse):
    """Response for secondary progressions calculation."""
    data: List[SecondaryProgression]

class SimplePlanetaryPositionsResponse(BaseModel):
    """Simple response for planetary positions calculation."""
    positions: List[PlanetaryPosition]

class SimpleAspectsResponse(BaseModel):
    """Simple response for aspects calculation."""
    aspects: List[Aspect]

class SimpleHousesResponse(BaseModel):
    """Simple response for houses calculation."""
    houses: List[House]

# Synastry and Transit schemas
class SynastryRequest(BaseModel):
    """Request schema for synastry calculation."""
    target_chart_id: str
    aspects: Optional[List[str]] = None
    orb_multiplier: float = 1.0

class SynastryAspect(BaseModel):
    """Aspect data for synastry."""
    planet1: str
    planet2: str
    aspect_type: str
    orb: float
    applying: Optional[bool] = None
    strength: float

class SynastryResponse(BaseModel):
    """Response schema for synastry calculation."""
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TransitRequest(BaseModel):
    """Request schema for transit calculation."""
    transit_date: str
    transit_time: str
    aspects: Optional[List[str]] = None
    orb_multiplier: float = 1.0

class TransitResponse(BaseModel):
    """Response schema for transit calculation."""
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None 