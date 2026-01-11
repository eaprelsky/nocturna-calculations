"""
Stateless calculations router for LLM-agent integration.

All endpoints in this router work without database access,
accepting complete chart data in the request body.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from ..schemas import (
    ChartDataInput,
    StatelessSynastryRequest,
    StatelessTransitRequest,
    StatelessProgressionRequest,
    StatelessCompositeRequest,
    StatelessReturnsRequest,
    StatelessDirectionsRequest,
    StatelessEclipsesRequest,
    StatelessIngressesRequest,
    StatelessSpecialPointsRequest,
    StatelessFixedStarsRequest,
    StatelessArabicPartsRequest,
    StatelessDignitiesRequest,
    StatelessAntisciaRequest,
    StatelessDeclinationsRequest,
    StatelessHarmonicsRequest,
    StatelessRectificationRequest,
    SimplePlanetaryPositionsResponse,
    SimpleAspectsResponse,
    SimpleHousesResponse,
)
from .auth import get_current_user
from ...core.chart import Chart as CoreChart

router = APIRouter()


def create_core_chart(chart_data: ChartDataInput) -> CoreChart:
    """Helper function to create CoreChart from ChartDataInput."""
    try:
        chart = CoreChart(
            date=chart_data.date,
            time=chart_data.time,
            latitude=chart_data.latitude,
            longitude=chart_data.longitude,
            timezone=chart_data.timezone
        )
        return chart
    except Exception as e:
        raise


def convert_to_sign_notation(longitude: float) -> Dict[str, Any]:
    """Convert longitude to sign/degree/minute/second format."""
    signs = ["ARIES", "TAURUS", "GEMINI", "CANCER", "LEO", "VIRGO",
             "LIBRA", "SCORPIO", "SAGITTARIUS", "CAPRICORN", "AQUARIUS", "PISCES"]
    
    sign_num = int(longitude // 30)
    sign = signs[sign_num]
    
    degree_in_sign = longitude % 30
    degree = int(degree_in_sign)
    minute = int((degree_in_sign - degree) * 60)
    second = int(((degree_in_sign - degree) * 60 - minute) * 60)
    
    return {
        "sign": sign,
        "degree": degree,
        "minute": minute,
        "second": second
    }


# Basic calculations (natal chart)
@router.post("/natal-chart")
async def calculate_natal_chart_stateless(
    request: ChartDataInput,
    current_user = Depends(get_current_user)
):
    """
    Calculate complete natal chart without database storage.
    
    Returns planets, houses, and aspects for the given chart data.
    Perfect for one-time calculations or LLM function calling.
    """
    try:
        core_chart = create_core_chart(request)
        
        # Calculate all components
        planets_data = core_chart.calculate_planetary_positions()
        houses_data = core_chart.calculate_houses(house_system=request.house_system)
        aspects_data = core_chart.calculate_aspects()
        
        # Format response
        return {
            "success": True,
            "data": {
                "planets": planets_data,
                "houses": houses_data,
                "aspects": aspects_data
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating natal chart: {str(e)}"
        )


# Synastry (two charts comparison)
@router.post("/synastry")
async def calculate_synastry_stateless(
    request: StatelessSynastryRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate synastry between two charts without database access.
    
    Compares two natal charts and returns aspects between them.
    Ideal for relationship compatibility analysis in LLM agents.
    """
    try:
        # Create both charts
        chart1 = create_core_chart(request.chart1)
        chart2 = create_core_chart(request.chart2)
        
        # Calculate synastry
        synastry_data = chart1.calculate_synastry_chart(
            chart2,
            orb=request.options.orb_multiplier if request.options else 1.0
        )
        
        return {
            "success": True,
            "data": synastry_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating synastry: {str(e)}"
        )


# Transits
@router.post("/transits")
async def calculate_transits_stateless(
    request: StatelessTransitRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate transits to natal chart without database access.
    
    Compares current/specified planetary positions with natal positions.
    Perfect for daily horoscopes and timing analysis.
    """
    try:
        # Create natal chart
        natal_chart = create_core_chart(request.natal_chart)
        
        # Create transit chart
        transit_chart = CoreChart(
            date=request.transit_date,
            time=request.transit_time,
            latitude=request.natal_chart.latitude,
            longitude=request.natal_chart.longitude,
            timezone=request.natal_chart.timezone
        )
        
        # Calculate transits (synastry between natal and current positions)
        transit_data = natal_chart.calculate_synastry_chart(
            transit_chart,
            orb=request.options.orb_multiplier if request.options else 1.0
        )
        
        # Add current transit positions
        transit_positions = transit_chart.calculate_planetary_positions()
        transit_data['transit_positions'] = transit_positions
        
        return {
            "success": True,
            "data": transit_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating transits: {str(e)}"
        )


# Progressions
@router.post("/progressions")
async def calculate_progressions_stateless(
    request: StatelessProgressionRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate secondary progressions without database access.
    
    Calculates progressed positions for a given date.
    Essential for predictive astrology in LLM applications.
    """
    try:
        from datetime import datetime
        natal_chart = create_core_chart(request.natal_chart)
        
        # Parse progression date
        target_date = datetime.strptime(request.progression_date, "%Y-%m-%d")
        
        # Calculate progressions
        progression_data = natal_chart.calculate_progressed_chart(
            target_date=target_date
        )
        
        return {
            "success": True,
            "data": progression_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating progressions: {str(e)}"
        )


# Composite charts
@router.post("/composite")
async def calculate_composite_stateless(
    request: StatelessCompositeRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate composite chart without database access.
    
    Creates a midpoint or Davison composite chart from two natal charts.
    Useful for relationship analysis in LLM agents.
    """
    try:
        chart1 = create_core_chart(request.chart1)
        chart2 = create_core_chart(request.chart2)
        
        # Calculate composite
        # Note: Current implementation uses midpoint method by default
        # composite_type parameter is accepted but not yet used in calculation
        composite_data = chart1.calculate_composite_chart(chart2)
        
        return {
            "success": True,
            "data": composite_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating composite: {str(e)}"
        )


# Returns (Solar/Lunar)
@router.post("/returns")
async def calculate_returns_stateless(
    request: StatelessReturnsRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate planetary returns without database access.
    
    Calculates solar, lunar, or planetary returns for a given date.
    Perfect for annual/monthly predictions in LLM agents.
    """
    try:
        from datetime import datetime
        natal_chart = create_core_chart(request.natal_chart)
        
        # Parse return date
        return_date = datetime.strptime(request.return_date, "%Y-%m-%d")
        target_year = return_date.year

        # Calculate return based on type
        if request.return_type.lower() == "solar":
            return_data = natal_chart.calculate_solar_return(
                target_year=target_year
            )
        elif request.return_type.lower() == "lunar":
            return_data = natal_chart.calculate_lunar_return(
                target_month=return_date
            )
        else:
            raise ValueError(f"Unsupported return type: {request.return_type}")
        
        return {
            "success": True,
            "data": return_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating returns: {str(e)}"
        )


# Primary Directions
@router.post("/directions")
async def calculate_directions_stateless(
    request: StatelessDirectionsRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate primary directions without database access.
    
    Calculates primary or symbolic directions for predictive work.
    Advanced feature for traditional astrology in LLM agents.
    """
    try:
        from datetime import datetime
        natal_chart = create_core_chart(request.natal_chart)
        
        # Parse target date
        target_date = datetime.strptime(request.target_date, "%Y-%m-%d")
        
        # Calculate solar arc directions
        directions_data = natal_chart.calculate_solar_arc_directions(target_date)
        
        return {
            "success": True,
            "data": directions_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating directions: {str(e)}"
        )


# Eclipses
@router.post("/eclipses")
async def calculate_eclipses_stateless(
    request: StatelessEclipsesRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate eclipses and their impact without database access.
    
    Finds eclipses in date range and their aspects to natal chart.
    Important for mundane and predictive astrology.
    
    NOTE: This is a placeholder implementation.
    Full eclipse calculation requires Swiss Ephemeris extended functionality.
    """
    try:
        # Placeholder implementation
        return {
            "success": True,
            "data": {
                "message": "Eclipse calculation endpoint is available but not yet fully implemented",
                "eclipses": []
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating eclipses: {str(e)}"
        )


# Ingresses
@router.post("/ingresses")
async def calculate_ingresses_stateless(
    request: StatelessIngressesRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate planetary ingresses without database access.
    
    Finds when planets enter new signs in date range.
    Useful for timing and mundane astrology.
    
    NOTE: This is a placeholder implementation.
    Full ingress calculation requires Swiss Ephemeris search functionality.
    """
    try:
        # Placeholder implementation
        return {
            "success": True,
            "data": {
                "message": "Ingress calculation endpoint is available but not yet fully implemented",
                "ingresses": []
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating ingresses: {str(e)}"
        )


# Fixed Stars
@router.post("/fixed-stars")
async def calculate_fixed_stars_stateless(
    request: StatelessFixedStarsRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate fixed stars positions and conjunctions without database access.

    Finds important fixed stars and their aspects to chart points.
    Essential for traditional and Vedic astrology.
    
    Note: Requires Swiss Ephemeris star data files to be installed.
    """
    try:
        chart = create_core_chart(request.chart_data)

        # Calculate fixed stars (requires swe star data files)
        try:
            stars_data = chart.calculate_fixed_stars()
        except Exception as star_err:
            # If star data files not available, return informative message
            if "could not find star name" in str(star_err).lower():
                return {
                    "success": False,
                    "error": "Fixed stars calculation requires Swiss Ephemeris star data files. "
                            "Install using: https://www.astro.com/swisseph/",
                    "data": None
                }
            raise

        return {
            "success": True,
            "data": stars_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating fixed stars: {str(e)}"
        )


# Arabic Parts
@router.post("/arabic-parts")
async def calculate_arabic_parts_stateless(
    request: StatelessArabicPartsRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate Arabic parts without database access.
    
    Calculates lots/parts like Part of Fortune, Spirit, etc.
    Important for Hellenistic and Medieval astrology.
    """
    try:
        chart = create_core_chart(request.chart_data)
        
        # Calculate Arabic parts (method exists in CoreChart)
        parts_data = chart.calculate_arabic_parts()
        
        return {
            "success": True,
            "data": parts_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating Arabic parts: {str(e)}"
        )


# Dignities
@router.post("/dignities")
async def calculate_dignities_stateless(
    request: StatelessDignitiesRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate planetary dignities without database access.
    
    Calculates essential dignities (rulership, exaltation, etc.).
    Core feature for traditional astrology.
    
    NOTE: This is a placeholder implementation.
    Full dignity calculation requires dignity tables and rules.
    """
    try:
        # Placeholder implementation
        return {
            "success": True,
            "data": {
                "message": "Dignity calculation endpoint is available but not yet fully implemented",
                "dignities": []
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating dignities: {str(e)}"
        )


# Antiscia
@router.post("/antiscia")
async def calculate_antiscia_stateless(
    request: StatelessAntisciaRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate antiscia points without database access.
    
    Calculates antiscia and contra-antiscia points.
    Important for traditional astrology.
    """
    try:
        chart = create_core_chart(request.chart_data)
        
        # Calculate antiscia (method exists in CoreChart)
        antiscia_data = chart.calculate_antiscia()
        
        return {
            "success": True,
            "data": antiscia_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating antiscia: {str(e)}"
        )


# Declinations
@router.post("/declinations")
async def calculate_declinations_stateless(
    request: StatelessDeclinationsRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate declinations and parallels without database access.
    
    Calculates out-of-sign aspects based on declination.
    Used in modern and traditional astrology.
    """
    try:
        chart = create_core_chart(request.chart_data)
        
        # Calculate declinations (method exists in CoreChart)
        declinations_data = chart.calculate_declinations()
        
        return {
            "success": True,
            "data": declinations_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating declinations: {str(e)}"
        )


# Harmonics
@router.post("/harmonics")
async def calculate_harmonics_stateless(
    request: StatelessHarmonicsRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate harmonic charts without database access.
    
    Creates harmonic charts (2nd, 3rd, 4th, etc.) from natal.
    Advanced technique in modern astrology.
    """
    try:
        chart = create_core_chart(request.chart_data)
        
        # Calculate multiple harmonics
        harmonics_results = []
        for harmonic in request.harmonics:
            harmonic_data = chart.calculate_harmonic_chart(harmonic)
            harmonics_results.append({
                "harmonic": harmonic,
                "data": harmonic_data
            })
        
        return {
            "success": True,
            "data": {"harmonics": harmonics_results}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating harmonics: {str(e)}"
        )


# Rectification
@router.post("/rectification")
async def calculate_rectification_stateless(
    request: StatelessRectificationRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate chart rectification without database access.
    
    Attempts to refine birth time based on life events.
    Advanced predictive technique for uncertain birth times.
    
    NOTE: This is a placeholder implementation.
    Full rectification requires complex event matching algorithms.
    """
    try:
        # Placeholder implementation
        return {
            "success": True,
            "data": {
                "message": "Rectification endpoint is available but not yet fully implemented",
                "suggested_times": []
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating rectification: {str(e)}"
        )


@router.post("/special-points")
async def calculate_special_points_stateless(
    request: StatelessSpecialPointsRequest,
    current_user = Depends(get_current_user)
):
    """
    Calculate special astrological points without database access.
    
    Includes:
    - Lunar Nodes (North/South, Mean/True)
    - Black Moon Lilith (Mean, True, Osculating)
    - White Moon Selena (Mean Apogee)
    
    These points are crucial for karmic and spiritual astrology.
    """
    try:
        import swisseph as swe
        chart = create_core_chart(request.chart_data)
        result = {}
        
        # Calculate Lunar Nodes
        if request.include_nodes:
            if request.use_true_node:
                # True nodes
                north_node, ret = swe.calc_ut(chart._julian_day, swe.TRUE_NODE, 0)
                result['north_node'] = {
                    'longitude': north_node[0],
                    'latitude': north_node[1],
                    'speed': north_node[3],
                    'type': 'true'
                }
                result['south_node'] = {
                    'longitude': (north_node[0] + 180) % 360,
                    'latitude': -north_node[1],
                    'speed': north_node[3],
                    'type': 'true'
                }
            else:
                # Mean nodes
                north_node, ret = swe.calc_ut(chart._julian_day, swe.MEAN_NODE, 0)
                result['north_node'] = {
                    'longitude': north_node[0],
                    'latitude': north_node[1],
                    'speed': north_node[3],
                    'type': 'mean'
                }
                result['south_node'] = {
                    'longitude': (north_node[0] + 180) % 360,
                    'latitude': -north_node[1],
                    'speed': north_node[3],
                    'type': 'mean'
                }
        
        # Calculate Black Moon Lilith
        if request.include_lilith:
            # Mean Lilith (most commonly used)
            mean_lilith, ret = swe.calc_ut(chart._julian_day, swe.MEAN_APOG, 0)
            result['lilith_mean'] = {
                'longitude': mean_lilith[0],
                'latitude': mean_lilith[1],
                'speed': mean_lilith[3],
                'type': 'mean'
            }
            
            # True/Osculating Lilith
            osc_lilith, ret = swe.calc_ut(chart._julian_day, swe.OSCU_APOG, 0)
            result['lilith_true'] = {
                'longitude': osc_lilith[0],
                'latitude': osc_lilith[1],
                'speed': osc_lilith[3],
                'type': 'osculating'
            }
        
        # Calculate White Moon Selena (Lunar Apogee)
        if request.include_selena:
            # Selena is the opposite point to Lilith
            if 'lilith_mean' in result:
                result['selena'] = {
                    'longitude': (result['lilith_mean']['longitude'] + 180) % 360,
                    'latitude': -result['lilith_mean']['latitude'],
                    'speed': result['lilith_mean']['speed'],
                    'type': 'mean_opposite'
                }
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating special points: {str(e)}"
        )
