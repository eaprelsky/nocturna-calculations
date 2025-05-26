# House System Calculations

This document describes the implementation of various house systems used in astrology.

## Overview

The house system calculations are implemented in two main files:
- `nocturna_calculations/calculations/house_systems.py`: Contains the house system classes
- `nocturna_calculations/calculations/utils.py`: Contains utility functions for astronomical calculations

## House Systems

The following house systems are implemented:

1. **Placidus House System**
   - Divides the diurnal and nocturnal arcs into equal time segments
   - Uses spherical trigonometry for cusp calculations
   - Most commonly used house system in Western astrology

2. **Koch House System**
   - Similar to Placidus but uses a different division of the ecliptic
   - Popular in German-speaking countries
   - More accurate for high latitudes

3. **Equal House System**
   - Divides the ecliptic into 12 equal segments of 30 degrees
   - First house cusp is the ascendant
   - Simple and easy to calculate

4. **Whole Sign House System**
   - Aligns house boundaries with sign boundaries
   - First house begins at 0 degrees of the sign containing the ascendant
   - Used in Hellenistic and Vedic astrology

5. **Campanus House System**
   - Divides the prime vertical into equal segments
   - Uses the prime vertical for house divisions
   - Good for high latitudes

6. **Regiomontanus House System**
   - Divides the celestial equator into equal segments
   - Uses the celestial equator for house divisions
   - Popular in medieval astrology

7. **Meridian House System**
   - Uses the meridian for house divisions
   - Similar to Regiomontanus but with different cusp calculations
   - Good for high latitudes

8. **Morinus House System**
   - Similar to Regiomontanus but uses a different cusp formula
   - Developed by Jean-Baptiste Morin
   - Good for high latitudes

## Implementation Details

### Base House System

The `BaseHouseSystem` class provides the foundation for all house system implementations:

```python
class BaseHouseSystem(ABC):
    def calculate_cusps(
        self,
        latitude: float,
        longitude: float,
        date_time: Optional[datetime] = None,
        obliquity: Optional[float] = None
    ) -> List[float]:
        # Calculate house cusps for the given location and time
```

### Utility Functions

The following utility functions are available in `utils.py`:

1. `calculate_sidereal_time(julian_day: float, longitude: float) -> float`
   - Calculates Local Sidereal Time (LST)
   - Uses Swiss Ephemeris for accurate calculations

2. `calculate_obliquity(julian_day: float) -> float`
   - Calculates the obliquity of the ecliptic
   - Uses Swiss Ephemeris for accurate calculations

3. `calculate_ascendant(lst: float, latitude: float, obliquity: float) -> float`
   - Calculates the ascendant using spherical trigonometry
   - Handles polar regions correctly

4. `calculate_mc(lst: float, obliquity: float) -> float`
   - Calculates the Midheaven (MC) using spherical trigonometry
   - Uses proper spherical trigonometry formulas

5. `calculate_house_cusps(ascendant: float, mc: float, latitude: float, obliquity: float, house_system: str) -> List[float]`
   - Calculates house cusps for a given house system
   - Supports all implemented house systems

## Usage Example

```python
from datetime import datetime
from nocturna_calculations.calculations.house_systems import get_house_system
from nocturna_calculations.core.constants import HouseSystem

# Create a house system calculator
system = get_house_system(HouseSystem.PLACIDUS)

# Calculate house cusps
cusps = system.calculate_cusps(
    latitude=40.7128,  # New York
    longitude=-74.0060,
    date_time=datetime(2024, 1, 1, 12, 0, 0)
)

# Print results
for i, cusp in enumerate(cusps, 1):
    print(f"House {i}: {cusp:.2f}°")
```

## Testing

The house system calculations are thoroughly tested in `tests/unit/test_house_systems.py`. The tests verify:

1. Accuracy of calculations against Swiss Ephemeris
2. Proper handling of polar regions
3. Validation of input coordinates
4. Correct implementation of each house system
5. Factory function behavior

## Future Improvements

1. Add support for more house systems
2. Implement caching for frequently used calculations
3. Add support for batch calculations
4. Improve performance for high-volume calculations
5. Add more comprehensive documentation and examples