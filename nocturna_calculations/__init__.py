"""
Nocturna Calculations - A Python library for astrological calculations
"""

__version__ = "1.0.0"
__author__ = "Yegor Aprelsky"
__email__ = "yegor.aprelsky@gmail.com"

from .core import (
    Planet, AspectType, CoordinateSystem, FixedStar, Asteroid,
    LunarNode, ArabicPart, Harmonic, Midpoint, MidpointStructure,
    Antiscia, AntisciaType, Declination, DeclinationType,
    HouseSystem, SolarReturnType, SolarReturn, LunarReturnType,
    LunarReturn, ProgressionType, ProgressedChart, SolarArcDirection,
    Position, Aspect, Chart, ChartCalculator, Config
)
from .adapters import SwissEphAdapter
from .calculations import (
    BaseHouseSystem,
    PlacidusHouseSystem,
    KochHouseSystem,
    EqualHouseSystem,
    WholeSignHouseSystem,
    CampanusHouseSystem,
    RegiomontanusHouseSystem,
    MeridianHouseSystem,
    MorinusHouseSystem,
    get_house_system,
    calculate_sidereal_time,
    calculate_obliquity,
    calculate_ascendant,
    calculate_mc,
    normalize_angle,
    calculate_julian_day,
    calculate_nutation
)

__all__ = [
    'Planet', 'AspectType', 'CoordinateSystem', 'FixedStar', 'Asteroid',
    'LunarNode', 'ArabicPart', 'Harmonic', 'Midpoint', 'MidpointStructure',
    'Antiscia', 'AntisciaType', 'Declination', 'DeclinationType',
    'HouseSystem', 'SolarReturnType', 'SolarReturn', 'LunarReturnType',
    'LunarReturn', 'ProgressionType', 'ProgressedChart', 'SolarArcDirection',
    'Position', 'Aspect', 'Chart', 'ChartCalculator', 'Config',
    'SwissEphAdapter',
    'BaseHouseSystem',
    'PlacidusHouseSystem',
    'KochHouseSystem',
    'EqualHouseSystem',
    'WholeSignHouseSystem',
    'CampanusHouseSystem',
    'RegiomontanusHouseSystem',
    'MeridianHouseSystem',
    'MorinusHouseSystem',
    'get_house_system',
    'calculate_sidereal_time',
    'calculate_obliquity',
    'calculate_ascendant',
    'calculate_mc',
    'normalize_angle',
    'calculate_julian_day',
    'calculate_nutation'
] 