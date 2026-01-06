"""
Base calculator class for astrological calculations
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel

class ChartData(BaseModel):
    """Data model for chart calculations"""
    date: str
    time: str
    latitude: float
    longitude: float
    options: Optional[Dict[str, Any]] = None

class ChartCalculator(ABC):
    """Base class for chart calculations"""
    
    def __init__(self, adapter: Any):
        """
        Initialize calculator with an adapter
        
        Args:
            adapter: Calculation adapter (e.g., SwissEphAdapter)
        """
        self.adapter = adapter
    
    @abstractmethod
    def calculate_natal_chart(self, data: ChartData) -> Dict[str, Any]:
        """
        Calculate natal chart
        
        Args:
            data: Chart calculation data
            
        Returns:
            Dict containing chart calculations
        """
        pass
    
    @abstractmethod
    def calculate_aspects(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate aspects for a chart
        
        Args:
            chart_data: Chart calculation data
            
        Returns:
            Dict containing aspect calculations
        """
        pass 