"""
Utility functions for astronomical calculations
"""
import math
import swisseph as swe
from typing import Tuple, List

def calculate_sidereal_time(julian_day: float, longitude: float) -> float:
    """
    Calculate Local Sidereal Time (LST) for a given Julian day and longitude.
    
    Args:
        julian_day: Julian day number
        longitude: Geographic longitude in degrees
        
    Returns:
        Local Sidereal Time in degrees
    """
    # Get Greenwich Mean Sidereal Time from Swiss Ephemeris
    gmst = swe.swe_sidtime(julian_day)
    gmst_degrees = gmst * 15.0
    
    # Convert to Local Sidereal Time
    lst = (gmst_degrees + longitude) % 360
    return lst

def calculate_obliquity(julian_day: float) -> float:
    """
    Calculate the obliquity of the ecliptic for a given Julian day.
    
    Args:
        julian_day: Julian day number
        
    Returns:
        Obliquity in degrees
    """
    return swe.swe_get_planet_attr(swe.SE_ECL_NUT, julian_day)[0]

def calculate_ascendant(lst: float, latitude: float, obliquity: float) -> float:
    """
    Calculate the ascendant (rising sign) using spherical trigonometry.
    
    Args:
        lst: Local Sidereal Time in degrees
        latitude: Geographic latitude in degrees
        obliquity: Obliquity of the ecliptic in degrees
        
    Returns:
        Ascendant in degrees
    """
    # Convert to radians
    lst_rad = math.radians(lst)
    lat_rad = math.radians(latitude)
    obl_rad = math.radians(obliquity)
    
    # Calculate ascendant using spherical trigonometry
    tan_asc = (math.cos(obl_rad) * math.sin(lst_rad)) / (
        math.cos(lst_rad) * math.cos(lat_rad) - 
        math.sin(obl_rad) * math.sin(lat_rad)
    )
    
    # Handle polar regions
    if abs(latitude) >= 90:
        return lst
    
    # Convert back to degrees and normalize
    ascendant = math.degrees(math.atan2(tan_asc, 1))
    return (ascendant + 360) % 360

def calculate_mc(lst: float, obliquity: float) -> float:
    """
    Calculate the Midheaven (MC) using spherical trigonometry.
    
    Args:
        lst: Local Sidereal Time in degrees
        obliquity: Obliquity of the ecliptic in degrees
        
    Returns:
        Midheaven in degrees
    """
    # Convert to radians
    lst_rad = math.radians(lst)
    obl_rad = math.radians(obliquity)
    
    # Calculate MC using spherical trigonometry
    tan_mc = math.tan(lst_rad) / math.cos(obl_rad)
    
    # Convert back to degrees and normalize
    mc = math.degrees(math.atan2(tan_mc, 1))
    return (mc + 360) % 360

def normalize_angle(angle: float) -> float:
    """
    Normalize an angle to the range [0, 360).
    
    Args:
        angle: Angle in degrees
        
    Returns:
        Normalized angle in degrees
    """
    return angle % 360

def calculate_house_cusps(
    ascendant: float,
    mc: float,
    latitude: float,
    obliquity: float,
    house_system: str
) -> List[float]:
    """
    Calculate house cusps for a given house system.
    
    Args:
        ascendant: Ascendant in degrees
        mc: Midheaven in degrees
        latitude: Geographic latitude in degrees
        obliquity: Obliquity of the ecliptic in degrees
        house_system: House system identifier
        
    Returns:
        List of 12 house cusps in degrees
    """
    # Initialize cusps list
    cusps = [0.0] * 12
    
    # Set first house cusp to ascendant
    cusps[0] = ascendant
    
    # Set tenth house cusp to MC
    cusps[9] = mc
    
    # Calculate remaining cusps based on house system
    if house_system == 'P':  # Placidus
        for i in range(1, 9):
            cusps[i] = _calculate_placidus_cusp(i + 1, ascendant, mc, latitude, obliquity)
    elif house_system == 'K':  # Koch
        for i in range(1, 9):
            cusps[i] = _calculate_koch_cusp(i + 1, ascendant, mc, latitude, obliquity)
    elif house_system == 'E':  # Equal
        for i in range(1, 12):
            cusps[i] = (ascendant + i * 30) % 360
    elif house_system == 'W':  # Whole Sign
        for i in range(1, 12):
            cusps[i] = (ascendant + i * 30) % 360
    elif house_system == 'C':  # Campanus
        for i in range(1, 9):
            cusps[i] = _calculate_campanus_cusp(i + 1, ascendant, mc, latitude, obliquity)
    elif house_system == 'R':  # Regiomontanus
        for i in range(1, 9):
            cusps[i] = _calculate_regiomontanus_cusp(i + 1, ascendant, mc, latitude, obliquity)
    elif house_system == 'M':  # Meridian
        for i in range(1, 9):
            cusps[i] = _calculate_meridian_cusp(i + 1, ascendant, mc, latitude, obliquity)
    elif house_system == 'O':  # Morinus
        for i in range(1, 9):
            cusps[i] = _calculate_morinus_cusp(i + 1, ascendant, mc, latitude, obliquity)
    
    # Calculate opposite cusps
    for i in range(6, 12):
        cusps[i] = (cusps[i-6] + 180) % 360
    
    return cusps

def _calculate_placidus_cusp(
    house: int,
    ascendant: float,
    mc: float,
    latitude: float,
    obliquity: float
) -> float:
    """Calculate Placidus house cusp"""
    # Implementation details...
    pass

def _calculate_koch_cusp(
    house: int,
    ascendant: float,
    mc: float,
    latitude: float,
    obliquity: float
) -> float:
    """Calculate Koch house cusp"""
    # Implementation details...
    pass

def _calculate_campanus_cusp(
    house: int,
    ascendant: float,
    mc: float,
    latitude: float,
    obliquity: float
) -> float:
    """Calculate Campanus house cusp"""
    # Implementation details...
    pass

def _calculate_regiomontanus_cusp(
    house: int,
    ascendant: float,
    mc: float,
    latitude: float,
    obliquity: float
) -> float:
    """Calculate Regiomontanus house cusp"""
    # Implementation details...
    pass

def _calculate_meridian_cusp(
    house: int,
    ascendant: float,
    mc: float,
    latitude: float,
    obliquity: float
) -> float:
    """Calculate Meridian house cusp"""
    # Implementation details...
    pass

def _calculate_morinus_cusp(
    house: int,
    ascendant: float,
    mc: float,
    latitude: float,
    obliquity: float
) -> float:
    """Calculate Morinus house cusp"""
    # Implementation details...
    pass 