"""
Nocturna Calculations - A Python library for astrological calculations
"""

__version__ = "0.1.0"
__author__ = "Yegor Aprelsky"
__email__ = "yegor.aprelsky@gmail.com"

from nocturna_calculations.core.calculator import ChartCalculator
from nocturna_calculations.adapters.swisseph import SwissEphAdapter

__all__ = ["ChartCalculator", "SwissEphAdapter"] 