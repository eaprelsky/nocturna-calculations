"""
Example of using Nocturna Calculations Stateless API with LLM Agents.

This demonstrates how to integrate the stateless API with AI agents
like ChatGPT, Claude, or custom LLM applications.
"""

import requests
from typing import Dict, Any
from datetime import datetime


class NocturnaStatelessClient:
    """
    Client for Nocturna Stateless API - perfect for LLM function calling.
    
    All methods are stateless and don't require database access,
    making them ideal for AI agent integration.
    """
    
    def __init__(self, base_url: str, token: str):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API (e.g., "http://localhost:8000")
            token: Authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def calculate_natal_chart(
        self,
        date: str,
        time: str,
        latitude: float,
        longitude: float,
        timezone: str = "UTC",
        house_system: str = "PLACIDUS"
    ) -> Dict[str, Any]:
        """
        Calculate a complete natal chart.
        
        Args:
            date: Birth date in YYYY-MM-DD format
            time: Birth time in HH:MM:SS format
            latitude: Birth latitude (-90 to 90)
            longitude: Birth longitude (-180 to 180)
            timezone: Timezone identifier (default: UTC)
            house_system: House system to use (default: PLACIDUS)
            
        Returns:
            Dictionary with planets, houses, and aspects
        """
        response = requests.post(
            f"{self.base_url}/api/stateless/natal-chart",
            headers=self.headers,
            json={
                "date": date,
                "time": time,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone,
                "house_system": house_system
            }
        )
        response.raise_for_status()
        return response.json()
    
    def calculate_synastry(
        self,
        person1_data: Dict[str, Any],
        person2_data: Dict[str, Any],
        orb_multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate relationship compatibility between two people.
        
        Args:
            person1_data: First person's chart data
            person2_data: Second person's chart data
            orb_multiplier: Aspect orb multiplier (default: 1.0)
            
        Returns:
            Synastry analysis with aspects and compatibility metrics
        """
        response = requests.post(
            f"{self.base_url}/api/stateless/synastry",
            headers=self.headers,
            json={
                "chart1": person1_data,
                "chart2": person2_data,
                "options": {
                    "orb_multiplier": orb_multiplier
                }
            }
        )
        response.raise_for_status()
        return response.json()
    
    def calculate_transits(
        self,
        natal_chart: Dict[str, Any],
        transit_date: str,
        transit_time: str,
        orb_multiplier: float = 0.8
    ) -> Dict[str, Any]:
        """
        Calculate current planetary transits to natal chart.
        
        Args:
            natal_chart: Natal chart data
            transit_date: Transit date in YYYY-MM-DD format
            transit_time: Transit time in HH:MM:SS format
            orb_multiplier: Aspect orb multiplier (default: 0.8)
            
        Returns:
            Transit positions and aspects to natal chart
        """
        response = requests.post(
            f"{self.base_url}/api/stateless/transits",
            headers=self.headers,
            json={
                "natal_chart": natal_chart,
                "transit_date": transit_date,
                "transit_time": transit_time,
                "options": {
                    "orb_multiplier": orb_multiplier
                }
            }
        )
        response.raise_for_status()
        return response.json()
    
    def calculate_solar_return(
        self,
        natal_chart: Dict[str, Any],
        return_year: int,
        location: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate solar return for a given year.
        
        Args:
            natal_chart: Natal chart data
            return_year: Year for solar return
            location: Optional custom location (default: natal location)
            
        Returns:
            Solar return chart data
        """
        # Calculate return date (approximate - will be refined by API)
        return_date = f"{return_year}-01-01"
        
        response = requests.post(
            f"{self.base_url}/api/stateless/returns",
            headers=self.headers,
            json={
                "natal_chart": natal_chart,
                "return_date": return_date,
                "return_type": "solar",
                "planet": "SUN",
                "location": location
            }
        )
        response.raise_for_status()
        return response.json()


# Example usage for LLM function calling
def example_openai_function_definitions():
    """
    Example function definitions for OpenAI function calling.
    """
    return [
        {
            "name": "calculate_natal_chart",
            "description": "Calculate a complete natal astrology chart with planets, houses, and aspects",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Birth date in YYYY-MM-DD format"
                    },
                    "time": {
                        "type": "string",
                        "description": "Birth time in HH:MM:SS format"
                    },
                    "latitude": {
                        "type": "number",
                        "description": "Birth latitude in degrees (-90 to 90)"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Birth longitude in degrees (-180 to 180)"
                    },
                    "timezone": {
                        "type": "string",
                        "description": "Timezone identifier (e.g., 'America/New_York')",
                        "default": "UTC"
                    }
                },
                "required": ["date", "time", "latitude", "longitude"]
            }
        },
        {
            "name": "calculate_synastry",
            "description": "Calculate relationship compatibility between two people based on their birth data",
            "parameters": {
                "type": "object",
                "properties": {
                    "person1": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"}
                        }
                    },
                    "person2": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"}
                        }
                    }
                },
                "required": ["person1", "person2"]
            }
        },
        {
            "name": "calculate_transits",
            "description": "Calculate current planetary transits and their aspects to natal chart",
            "parameters": {
                "type": "object",
                "properties": {
                    "natal_date": {"type": "string"},
                    "natal_time": {"type": "string"},
                    "natal_latitude": {"type": "number"},
                    "natal_longitude": {"type": "number"},
                    "transit_date": {"type": "string"},
                    "transit_time": {"type": "string"}
                },
                "required": [
                    "natal_date", "natal_time", "natal_latitude", "natal_longitude",
                    "transit_date", "transit_time"
                ]
            }
        }
    ]


# Usage example
if __name__ == "__main__":
    # Initialize client
    client = NocturnaStatelessClient(
        base_url="http://localhost:8000",
        token="your_service_token_here"
    )
    
    # Example 1: Calculate natal chart
    print("Example 1: Natal Chart")
    natal = client.calculate_natal_chart(
        date="1990-01-15",
        time="14:30:00",
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York"
    )
    print(f"Success: {natal['success']}")
    print(f"Planets calculated: {len(natal['data']['planets'])}")
    
    # Example 2: Calculate synastry
    print("\nExample 2: Synastry")
    person1 = {
        "date": "1990-01-15",
        "time": "14:30:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York"
    }
    person2 = {
        "date": "1992-06-20",
        "time": "09:15:00",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "timezone": "America/Los_Angeles"
    }
    synastry = client.calculate_synastry(person1, person2)
    print(f"Success: {synastry['success']}")
    print(f"Aspects found: {len(synastry['data'].get('aspects', []))}")
    
    # Example 3: Calculate transits
    print("\nExample 3: Transits")
    transits = client.calculate_transits(
        natal_chart=person1,
        transit_date="2026-01-11",
        transit_time="12:00:00"
    )
    print(f"Success: {transits['success']}")
    print(f"Active transits: {len(transits['data'].get('aspects', []))}")
    
    # Example 4: Solar return
    print("\nExample 4: Solar Return")
    solar_return = client.calculate_solar_return(
        natal_chart=person1,
        return_year=2026
    )
    print(f"Success: {solar_return['success']}")
