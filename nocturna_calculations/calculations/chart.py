"""
Chart calculations for astrological charts
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
import swisseph as swe
from ..core.constants import HouseSystem, AntisciaType
from .house_systems import get_house_system
from .astro_math import calculate_julian_day, calculate_obliquity
from ..core.models import FixedStar, Asteroid, LunarNode
from ..core.adapters import SwissEphAdapter

class Chart:
    """Class for calculating astrological chart data"""
    
    def __init__(
        self,
        latitude: float,
        longitude: float,
        date_time: datetime,
        house_system: HouseSystem = HouseSystem.PLACIDUS
    ):
        """
        Initialize chart calculations
        
        Args:
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            date_time: Date and time for calculation
            house_system: House system to use (default: Placidus)
        """
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
            
        self.latitude = latitude
        self.longitude = longitude
        self.date_time = date_time
        self.house_system = house_system
        
        # Calculate Julian day
        self.julian_day = calculate_julian_day(date_time)
        
        # Calculate obliquity
        self.obliquity = calculate_obliquity(self.julian_day)
        
        # Initialize house system calculator
        self.house_calculator = get_house_system(house_system)
        
        # Initialize adapter
        self._adapter = SwissEphAdapter()
    
    def calculate_houses(self) -> List[float]:
        """
        Calculate house cusps
        
        Returns:
            List of 12 house cusps in degrees
        """
        return self.house_calculator.calculate_cusps(
            self.latitude,
            self.longitude,
            self.date_time,
            self.obliquity
        )
    
    def calculate_planets(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate planetary positions
        
        Returns:
            Dictionary of planetary positions with their data
        """
        # Calculate positions using the adapter
        positions = self._adapter.calculate_planetary_positions(self.julian_day)
        
        # Add additional data for each planet
        for planet, data in positions.items():
            data.update({
                'house': self._calculate_house_position(data['longitude']),
                'sign': self._calculate_sign(data['longitude']),
                'retrograde': data.get('speed', 0) < 0
            })
        
        return positions
    
    def calculate_aspects(self) -> List[Dict[str, Any]]:
        """
        Calculate aspects between planets
        
        Returns:
            List of aspects with their data
        """
        # Get planetary positions
        positions = self.calculate_planets()
        
        # Calculate aspects using the adapter
        aspects = self._adapter.calculate_aspects(positions)
        
        # Add additional data for each aspect
        for aspect in aspects:
            aspect.update({
                'applying': self._is_aspect_applying(
                    positions[aspect['planet1']]['longitude'],
                    positions[aspect['planet2']]['longitude'],
                    aspect['angle']
                ),
                'orb': self._calculate_orb(
                    positions[aspect['planet1']]['longitude'],
                    positions[aspect['planet2']]['longitude'],
                    aspect['angle']
                )
            })
        
        return aspects
    
    def _calculate_house_position(self, longitude: float) -> int:
        """Calculate house number for a given longitude"""
        # Normalize longitude to 0-360 range
        longitude = longitude % 360
        # Each house is 30 degrees, starting from 0
        return int(longitude / 30) + 1
    
    def _calculate_sign(self, longitude: float) -> int:
        """Calculate sign number for a given longitude"""
        return int(longitude / 30) + 1
    
    def _is_aspect_applying(self, long1: float, long2: float, aspect_angle: float) -> bool:
        """Check if an aspect is applying"""
        diff = (long2 - long1) % 360
        return diff < aspect_angle
    
    def _calculate_orb(self, long1: float, long2: float, aspect_angle: float) -> float:
        """Calculate orb of an aspect"""
        diff = abs((long2 - long1) % 360)
        return min(diff, 360 - diff) 