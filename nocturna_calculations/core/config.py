"""
Configuration for astrological calculations
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class Config(BaseModel):
    """Configuration for astrological calculations"""
    
    # House system configuration
    house_system: str = Field(default="Placidus", description="House system to use")
    
    # Aspect configuration
    orbs: Dict[str, float] = Field(
        default={
            "conjunction": 10.0,
            "opposition": 10.0,
            "trine": 8.0,
            "square": 8.0,
            "sextile": 6.0,
            "semisextile": 2.0,
            "semisquare": 2.0,
            "sesquisquare": 2.0,
            "quincunx": 2.0,
            "quintile": 2.0,
            "biquintile": 2.0
        },
        description="Orbs for different aspects"
    )
    
    # Calculation options
    include_minor_aspects: bool = Field(default=True, description="Include minor aspects in calculations")
    include_fixed_stars: bool = Field(default=True, description="Include fixed stars in calculations")
    include_arabic_parts: bool = Field(default=True, description="Include Arabic parts in calculations")
    
    # Additional options
    custom_options: Optional[Dict[str, Any]] = Field(default=None, description="Custom calculation options") 