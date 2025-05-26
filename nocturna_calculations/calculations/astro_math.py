"""
Basic astronomical calculations
"""
import math
import swisseph as swe
from datetime import datetime
from typing import Tuple


def calculate_julian_day(date_time: datetime) -> float:
    """
    Calculate Julian day number for a given datetime.
    
    Args:
        date_time: Python datetime object
        
    Returns:
        Julian day number
    """
    return swe.swe_julday(
        date_time.year,
        date_time.month,
        date_time.day,
        date_time.hour + date_time.minute/60.0 + date_time.second/3600.0,
        swe.SE_GREG_CAL
    )


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


def calculate_nutation(julian_day: float) -> Tuple[float, float]:
    """
    Calculate the nutation in longitude and obliquity for a given Julian day.
    
    Args:
        julian_day: Julian day number
        
    Returns:
        Tuple of (nutation in longitude, nutation in obliquity) in degrees
    """
    # Get nutation values from Swiss Ephemeris
    nut_long, nut_obl = swe.swe_nut(julian_day)
    
    # Convert to degrees
    nut_long_deg = math.degrees(nut_long)
    nut_obl_deg = math.degrees(nut_obl)
    
    return nut_long_deg, nut_obl_deg 