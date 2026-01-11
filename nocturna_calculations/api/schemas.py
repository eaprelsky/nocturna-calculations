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

# Stateless schemas for LLM-agent integration
class ChartDataInput(BaseModel):
    """Universal chart data input for stateless calculations."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM:SS format")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    timezone: str = Field(default="UTC", description="Timezone identifier")
    house_system: Optional[str] = Field(default="PLACIDUS", description="House system to use")
    
class StatelessCalculationOptions(BaseModel):
    """Common options for stateless calculations."""
    planets: Optional[List[str]] = Field(default=None, description="List of planets to calculate")
    aspects: Optional[List[str]] = Field(default=None, description="List of aspects to calculate")
    orb_multiplier: float = Field(default=1.0, ge=0.1, le=3.0, description="Multiplier for aspect orbs")

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

# Stateless request schemas
class StatelessSynastryRequest(BaseModel):
    """Stateless synastry calculation request."""
    chart1: ChartDataInput = Field(..., description="First chart data (natal)")
    chart2: ChartDataInput = Field(..., description="Second chart data (partner)")
    options: Optional[StatelessCalculationOptions] = Field(default_factory=StatelessCalculationOptions)

class StatelessTransitRequest(BaseModel):
    """Stateless transit calculation request."""
    natal_chart: ChartDataInput = Field(..., description="Natal chart data")
    transit_date: str = Field(..., description="Transit date in YYYY-MM-DD format")
    transit_time: str = Field(..., description="Transit time in HH:MM:SS format")
    options: Optional[StatelessCalculationOptions] = Field(default_factory=StatelessCalculationOptions)

class StatelessProgressionRequest(BaseModel):
    """Stateless progression calculation request."""
    natal_chart: ChartDataInput = Field(..., description="Natal chart data")
    progression_date: str = Field(..., description="Progression date in YYYY-MM-DD format")
    progression_type: str = Field(default="secondary", description="Type of progression: secondary, tertiary, minor")
    options: Optional[StatelessCalculationOptions] = Field(default_factory=StatelessCalculationOptions)

class StatelessCompositeRequest(BaseModel):
    """Stateless composite chart calculation request."""
    chart1: ChartDataInput = Field(..., description="First chart data")
    chart2: ChartDataInput = Field(..., description="Second chart data")
    composite_type: str = Field(default="midpoint", description="Type of composite: midpoint, davison")
    options: Optional[StatelessCalculationOptions] = Field(default_factory=StatelessCalculationOptions)

class StatelessReturnsRequest(BaseModel):
    """Stateless returns calculation request."""
    natal_chart: ChartDataInput = Field(..., description="Natal chart data")
    return_date: str = Field(..., description="Return date in YYYY-MM-DD format")
    return_type: str = Field(default="solar", description="Type of return: solar, lunar, planetary")
    planet: Optional[str] = Field(default="SUN", description="Planet for return calculation")
    location: Optional[Dict[str, float]] = Field(default=None, description="Custom location for return chart")

class StatelessDirectionsRequest(BaseModel):
    """Stateless primary directions calculation request."""
    natal_chart: ChartDataInput = Field(..., description="Natal chart data")
    target_date: str = Field(..., description="Target date for directions")
    direction_type: str = Field(default="primary", description="Type of direction: primary, symbolic")
    key_rate: float = Field(default=1.0, description="Direction key rate (1° = 1 year)")

class StatelessEclipsesRequest(BaseModel):
    """Stateless eclipses calculation request."""
    natal_chart: ChartDataInput = Field(..., description="Natal chart data")
    start_date: str = Field(..., description="Start date for eclipse search")
    end_date: str = Field(..., description="End date for eclipse search")
    eclipse_type: Optional[str] = Field(default="all", description="Eclipse type: solar, lunar, all")

class StatelessIngressesRequest(BaseModel):
    """Stateless ingresses calculation request."""
    natal_chart: ChartDataInput = Field(..., description="Natal chart data")
    start_date: str = Field(..., description="Start date for ingress search")
    end_date: str = Field(..., description="End date for ingress search")
    planets: Optional[List[str]] = Field(default=None, description="Planets to track for ingresses")

class StatelessFixedStarsRequest(BaseModel):
    """Stateless fixed stars calculation request."""
    chart_data: ChartDataInput = Field(..., description="Chart data")
    orb: float = Field(default=1.0, description="Orb for fixed star conjunctions")
    magnitude_limit: Optional[float] = Field(default=2.0, description="Maximum magnitude for stars")

class StatelessArabicPartsRequest(BaseModel):
    """Stateless Arabic parts calculation request."""
    chart_data: ChartDataInput = Field(..., description="Chart data")
    parts: Optional[List[str]] = Field(default=None, description="Specific Arabic parts to calculate")

class StatelessDignitiesRequest(BaseModel):
    """Stateless dignities calculation request."""
    chart_data: ChartDataInput = Field(..., description="Chart data")
    dignity_system: str = Field(default="traditional", description="Dignity system: traditional, modern")

class StatelessAntisciaRequest(BaseModel):
    """Stateless antiscia calculation request."""
    chart_data: ChartDataInput = Field(..., description="Chart data")
    include_contra: bool = Field(default=True, description="Include contra-antiscia")

class StatelessDeclinationsRequest(BaseModel):
    """Stateless declinations calculation request."""
    chart_data: ChartDataInput = Field(..., description="Chart data")
    parallel_orb: float = Field(default=1.0, description="Orb for parallel aspects")

class StatelessHarmonicsRequest(BaseModel):
    """Stateless harmonics calculation request."""
    chart_data: ChartDataInput = Field(..., description="Chart data")
    harmonics: List[int] = Field(default=[2, 3, 4, 5, 7, 9], description="Harmonic numbers to calculate")

class StatelessRectificationRequest(BaseModel):
    """Stateless rectification calculation request."""
    chart_data: ChartDataInput = Field(..., description="Approximate chart data")
    events: List[Dict[str, Any]] = Field(..., description="Life events for rectification")

class StatelessSpecialPointsRequest(BaseModel):
    """Stateless special points calculation request (Nodes, Lilith, Selena)."""
    chart_data: ChartDataInput = Field(..., description="Chart data")
    include_nodes: bool = Field(default=True, description="Include lunar nodes")
    include_lilith: bool = Field(default=True, description="Include Black Moon Lilith")
    include_selena: bool = Field(default=True, description="Include White Moon (Selena)")
    use_true_node: bool = Field(default=False, description="Use true node instead of mean node")
    time_range_minutes: int = Field(default=120, description="Time range for search in minutes") 