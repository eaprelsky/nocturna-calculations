"""
Core chart class for astrological calculations
"""
from datetime import datetime, time
from typing import Dict, Any, Optional, Union, List, Tuple
import pytz
from pydantic import BaseModel, Field, validator

from .config import AstroConfig
from ..adapters.swisseph import SwissEphAdapter
from .constants import (
    FixedStar, Asteroid, LunarNode, ArabicPart, 
    Harmonic, Midpoint, MidpointStructure,
    Antiscia, AntisciaType, Declination, DeclinationType,
    Planet, HouseSystem, AspectType, Aspect,
    SolarReturnType
)

class Chart(BaseModel):
    """Core chart class for astrological calculations"""
    
    # Required fields
    date: Union[str, datetime] = Field(..., description="Chart date")
    time: Union[str, time] = Field(..., description="Chart time")
    latitude: float = Field(..., description="Geographic latitude in degrees")
    longitude: float = Field(..., description="Geographic longitude in degrees")
    
    # Optional fields
    timezone: str = Field(default="UTC", description="Timezone for calculations")
    config: Optional[AstroConfig] = Field(default=None, description="Calculation configuration")
    
    # Internal fields
    _adapter: Optional[SwissEphAdapter] = None
    _julian_day: Optional[float] = None
    
    @validator('latitude')
    def validate_latitude(cls, v):
        """Validate latitude value"""
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        """Validate longitude value"""
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v
    
    @validator('timezone')
    def validate_timezone(cls, v):
        """Validate timezone"""
        try:
            pytz.timezone(v)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone: {v}")
        return v
    
    def __init__(self, **data):
        """Initialize chart with validation"""
        super().__init__(**data)
        
        # Set default config if not provided
        if self.config is None:
            self.config = AstroConfig()
        
        # Initialize adapter
        self._adapter = SwissEphAdapter()
        
        # Calculate Julian day
        self._calculate_julian_day()
    
    def _calculate_julian_day(self):
        """Calculate Julian day for the chart"""
        import swisseph as swe
        
        # Convert date and time to datetime if needed
        if isinstance(self.date, str):
            date = datetime.strptime(self.date, "%Y-%m-%d")
        else:
            date = self.date
            
        if isinstance(self.time, str):
            time = datetime.strptime(self.time, "%H:%M:%S").time()
        else:
            time = self.time
        
        # Combine date and time
        dt = datetime.combine(date, time)
        
        # Convert to UTC if timezone is specified
        if self.timezone != "UTC":
            tz = pytz.timezone(self.timezone)
            dt = tz.localize(dt).astimezone(pytz.UTC)
        
        # Calculate Julian day
        self._julian_day = swe.julday(
            dt.year,
            dt.month,
            dt.day,
            dt.hour + dt.minute/60.0 + dt.second/3600.0
        )
    
    def calculate_planetary_positions(self) -> Dict[str, Any]:
        """Calculate planetary positions for the chart"""
        import swisseph as swe
        
        # Define planets to calculate
        planets = [
            swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
            swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO
        ]
        
        # Calculate positions
        positions = self._adapter.calculate_planetary_positions(
            self._julian_day,
            planets
        )
        
        # Convert to more readable format
        result = {}
        planet_names = {
            swe.SUN: "Sun",
            swe.MOON: "Moon",
            swe.MERCURY: "Mercury",
            swe.VENUS: "Venus",
            swe.MARS: "Mars",
            swe.JUPITER: "Jupiter",
            swe.SATURN: "Saturn",
            swe.URANUS: "Uranus",
            swe.NEPTUNE: "Neptune",
            swe.PLUTO: "Pluto"
        }
        
        for planet, pos in positions.items():
            result[planet_names[planet]] = pos
        
        return result
    
    def calculate_houses(self, system: str = None) -> Dict[str, Any]:
        """Calculate house cusps and angles"""
        # Use configured house system if not specified
        if system is None:
            system = self.config.house_system
        
        # Calculate houses
        houses = self._adapter.calculate_houses(
            self._julian_day,
            self.latitude,
            self.longitude
        )
        
        return houses
    
    def calculate_aspects(self) -> Dict[str, Any]:
        """Calculate aspects between planets"""
        # Get planetary positions
        positions = self.calculate_planetary_positions()
        
        # Calculate aspects
        aspects = self._adapter.calculate_aspects(
            positions,
            self.config.orbs
        )
        
        return aspects
    
    def calculate_fixed_stars(self, stars: List[FixedStar] = None) -> Dict[str, Any]:
        """
        Calculate fixed star positions for the chart
        
        Args:
            stars: List of fixed stars to calculate (default: all)
            
        Returns:
            Dict containing fixed star positions
        """
        # Calculate positions
        positions = self._adapter.calculate_fixed_stars(
            self._julian_day,
            stars
        )
        
        return positions
    
    def calculate_asteroids(self, asteroids: List[Asteroid] = None) -> Dict[str, Any]:
        """
        Calculate asteroid positions for the chart
        
        Args:
            asteroids: List of asteroids to calculate (default: all)
            
        Returns:
            Dict containing asteroid positions
        """
        # Calculate positions
        positions = self._adapter.calculate_asteroids(
            self._julian_day,
            asteroids
        )
        
        return positions
    
    def calculate_lunar_nodes(self, nodes: List[LunarNode] = None) -> Dict[str, Any]:
        """
        Calculate lunar node positions for the chart
        
        Args:
            nodes: List of lunar nodes to calculate (default: all)
            
        Returns:
            Dict containing lunar node positions
        """
        # Calculate positions
        positions = self._adapter.calculate_lunar_nodes(
            self._julian_day,
            nodes
        )
        
        return positions
    
    def calculate_arabic_parts(self, parts: List[ArabicPart] = None) -> Dict[str, float]:
        """
        Calculate Arabic parts positions for the chart
        
        Args:
            parts: List of Arabic parts to calculate (default: all)
            
        Returns:
            Dict containing Arabic parts positions
        """
        # Get house cusps for ASC and MC
        houses = self.calculate_houses()
        ascendant = houses['angles'][0]  # ASC is first angle
        mc = houses['angles'][1]  # MC is second angle
        
        # Get planetary positions
        planet_positions = self.calculate_planetary_positions()
        
        # Calculate parts
        positions = self._adapter.calculate_arabic_parts(
            self._julian_day,
            ascendant,
            mc,
            planet_positions,
            parts
        )
        
        return positions
    
    def calculate_harmonic_positions(
        self,
        positions: Optional[Dict[str, Dict[str, float]]] = None,
        harmonic: Union[int, Harmonic] = Harmonic.HARMONIC_1
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate harmonic positions for the chart
        
        Args:
            positions: Dict of positions to calculate harmonics for (default: planetary positions)
            harmonic: Harmonic number (1-12) or Harmonic enum value (default: HARMONIC_1)
            
        Returns:
            Dict containing harmonic positions
        """
        # Use planetary positions if none provided
        if positions is None:
            positions = self.calculate_planetary_positions()
        
        # Calculate harmonic positions
        harmonic_positions = self._adapter.calculate_harmonic_positions(
            positions,
            harmonic
        )
        
        return harmonic_positions
    
    def calculate_midpoints(
        self,
        positions: Optional[Dict[str, Dict[str, float]]] = None,
        points: Optional[List[Tuple[str, str]]] = None,
        orb: float = 1.0
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate midpoints for the chart
        
        Args:
            positions: Dict of positions to calculate midpoints for (default: planetary positions)
            points: List of point pairs to calculate midpoints for (default: all pairs)
            orb: Orb for midpoint structures in degrees (default: 1.0)
            
        Returns:
            Dict containing midpoint data
        """
        # Use planetary positions if none provided
        if positions is None:
            positions = self.calculate_planetary_positions()
        
        # Calculate midpoints
        midpoints = self._adapter.calculate_midpoints(
            positions,
            points,
            orb
        )
        
        return midpoints
    
    def calculate_antiscia(
        self,
        positions: Optional[Dict[str, Dict[str, float]]] = None,
        antiscia_type: AntisciaType = AntisciaType.DIRECT,
        points: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate antiscia points for the chart
        
        Args:
            positions: Dict of positions to calculate antiscia for (default: planetary positions)
            antiscia_type: Type of antiscia to calculate (default: DIRECT)
            points: List of points to calculate antiscia for (default: all)
            
        Returns:
            Dict containing antiscia data
        """
        # Use planetary positions if none provided
        if positions is None:
            positions = self.calculate_planetary_positions()
        
        # Calculate antiscia points
        antiscia_points = self._adapter.calculate_antiscia(
            positions,
            antiscia_type,
            points
        )
        
        return antiscia_points
    
    def calculate_declinations(
        self,
        positions: Optional[Dict[str, Dict[str, float]]] = None,
        points: Optional[List[str]] = None,
        orb: float = 1.0
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate declinations for the chart
        
        Args:
            positions: Dict of positions to calculate declinations for (default: planetary positions)
            points: List of points to calculate declinations for (default: all)
            orb: Orb for declination aspects in degrees (default: 1.0)
            
        Returns:
            Dict containing declination data
        """
        # Use planetary positions if none provided
        if positions is None:
            positions = self.calculate_planetary_positions()
        
        # Calculate declinations
        declinations = self._adapter.calculate_declinations(
            positions,
            points,
            orb
        )
        
        return declinations
    
    def calculate_solar_return(
        self,
        return_type: SolarReturnType = SolarReturnType.NEXT,
        target_year: Optional[int] = None,
        house_system: HouseSystem = HouseSystem.PLACIDUS
    ) -> Dict:
        """
        Calculate solar return chart
        
        Args:
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
        return self._adapter.calculate_solar_return(
            self.date,
            self.latitude,
            self.longitude,
            return_type,
            target_year,
            house_system
        ) 